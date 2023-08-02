#!/usr/bin/env python
# D. Jones - 5/26/23
"""SED-fitting implementation with SBI++"""
import os
import signal
import sys
import time
import warnings

from host.models import SEDFittingResult

# recommend running the full script without the line below first
# if an error is threw, then uncomment this line
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
import numpy as np
from numpy.random import normal, uniform
from scipy.interpolate import interp1d

# torch
import torch
import torch.nn as nn
import torch.nn.functional as F
from sbi import utils as Ut
from sbi import inference as Inference
from host.prospector import build_obs
from host.models import Transient, Filter
from django.db.models import Q
from host.SBI.train_sbi import maggies_to_asinh

# plot
import corner
import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline

matplotlib_inline.backend_inline.set_matplotlib_formats("retina")

# all the functions implementing SBI++ are contained in `sbi_pp.py`
from host.SBI import sbi_pp
import h5py

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

run_params = {
    "nmc": 50,  # number of MC samples
    "nposterior": 50,  # number of posterior samples per MC drawn
    "np_baseline": 500,  # number of posterior samples used in baseline SBI
    "ini_chi2": 5,  # chi^2 cut usedi in the nearest neighbor search
    "max_chi2": 500,  # the maximum chi^2 to reach in case we Incremently increase the chi^2
    # in the case of insufficient neighbors
    "noisy_sig": 3,  # deviation from the noise model, above which the measuremnt is taked as OOD
    "tmax_per_obj": 120000,  # max time spent on one object / mc sample in secs
    "tmax_all": 600000,  # max time spent on all mc samples in mins
    "outdir": "output",  # output directory
    "verbose": True,
    "tmax_per_iter": 20,
}

sbi_params = {
    "anpe_fname": "../data/sbipp/SBI_model.pt",  # trained sbi model
    "train_fname": "../data/sbipp/sbi_phot.h5",  # training set
    # "test_fname": "host/SBI/test.i20.npz",  # testing set
    # "noise_fname": "host/SBI/toy_noise_xy.i20.txt",  # toy model used in training
    # this files contains the median and the 1 sigma values
    # of uncertainties in magnitude bins
    "nhidden": 500,  # architecture of the trained density estimator
    "nblocks": 15,  # architecture of the trained density estimator
}

all_filters = Filter.objects.filter(~Q(name="DES_i") & ~Q(name="DES_Y"))


def main():

    # training set
    data = h5py.File(sbi_params["train_fname"], "r")
    x_train = np.array(data["theta"])  # physical parameters
    y_train = np.array(data["phot"])  # fluxes & uncertainties

    # we will only need the lower & upper limits to be passed to sbi as "priors"
    # here we simply read in the bounds from the training set
    prior_low = sbi_pp.prior_from_train("ll", x_train=x_train)
    prior_high = sbi_pp.prior_from_train("ul", x_train=x_train)
    lower_bounds = torch.tensor(prior_low).to(device)
    upper_bounds = torch.tensor(prior_high).to(device)
    prior = Ut.BoxUniform(low=lower_bounds, high=upper_bounds, device=device)

    # density estimater
    anpe = Inference.SNPE(
        prior=prior,
        density_estimator=Ut.posterior_nn(
            "maf",
            hidden_features=sbi_params["nhidden"],
            num_transforms=sbi_params["nblocks"],
        ),
        device=device,
    )
    x_tensor = torch.as_tensor(x_train.astype(np.float32)).to(device)
    y_tensor = torch.as_tensor(y_train.astype(np.float32)).to(device)
    anpe.append_simulations(x_tensor, y_tensor)
    p_x_y_estimator = anpe._build_neural_net(x_tensor, y_tensor)
    p_x_y_estimator.load_state_dict(
        torch.load(sbi_params["anpe_fname"], map_location=torch.device(device))
    )
    anpe._x_shape = Ut.x_shape_from_simulation(y_tensor)
    hatp_x_y = anpe.build_posterior(p_x_y_estimator, sample_with="rejection")

    # toy noise model
    meds_sigs, stds_sigs = [], []
    for f in all_filters:
        toy_noise_x, toy_noise_y = np.loadtxt(
            f"host/SBI/snrfiles/{f}_magvsnr.txt", dtype=float, unpack=True
        )
        meds_sigs += [
            interp1d(
                toy_noise_x,
                1.0857 * 1 / toy_noise_y,
                kind="slinear",
                fill_value="extrapolate",
            )
        ]
        stds_sigs += [
            interp1d(
                toy_noise_x,
                1.0857 * 1 / toy_noise_y,
                kind="slinear",
                fill_value="extrapolate",
            )
        ]

    # prepare to pass the reconstructed model to sbi_pp
    sbi_params["y_train"] = y_train
    sbi_params["hatp_x_y"] = hatp_x_y
    sbi_params["toynoise_meds_sigs"] = meds_sigs
    sbi_params["toynoise_stds_sigs"] = stds_sigs

    for transient_name in np.loadtxt(
        "host/slurm/hostgalmasses_list.csv",
        unpack=True,
        usecols=[0],
        delimiter=",",
        dtype=str,
    )[1:]:
        print(transient_name)
        if transient_name != '2020fhs': continue
        
        np.random.seed(200)  # make results reproducible
        pobs = build_obs(Transient.objects.get(name=transient_name), "global")

        # a testing object of which the noises are OOD
        mags, mags_unc, filternames = np.array([]), np.array([]), np.array([])
        for f in all_filters:
            if f.name in pobs["filternames"]:
                iflt = np.array(pobs["filternames"]) == f.name
                mags = np.append(mags, maggies_to_asinh(pobs["maggies"][iflt]))
                mags_unc = np.append(
                    mags_unc,
                    2.5
                    / np.log(10)
                    * pobs["maggies_unc"][iflt]
                    / pobs["maggies"][iflt],
                )
            else:
                mags = np.append(mags, np.nan)
                mags_unc = np.append(mags_unc, np.nan)
            filternames = np.append(filternames, f.name)

        obs = {}
        obs["mags"] = mags  ##np.array([maggies_to_asinh(p) for p in pobs['maggies']])
        obs["mags_unc"] = mags_unc  ##2.5/np.log(10)*pobs['maggies_unc']/pobs['maggies']
        obs["redshift"] = pobs["redshift"]

        # Run SBI++
        chain, obs, flags = sbi_pp.sbi_pp(
            obs=obs, run_params=run_params, sbi_params=sbi_params
        )
        try:
            print(
                transient_name,
                np.mean(chain[:, 1]),
                SEDFittingResult.objects.get(
                    transient__name=transient_name, aperture__type="global"
                ).log_mass_50,
            )
        except:
            print(
                transient_name,
                np.mean(chain[:, 1]),None)

