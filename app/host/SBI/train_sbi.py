#!/usr/bin/env python
# D. Jones - 5/26/23
"""Implementation of SBI++ training for Blast"""

import numpy as np
from host.models import *
from host.prospector import build_obs,build_model
from prospect.fitting import fit_model as fit_model_prospect
from prospect.fitting import lnprobfn
from prospect.io import write_results as writer
from prospect.models import SpecModel
from prospect.models.templates import TemplateLibrary
from prospect.sources import CSPSpecBasis
from prospect.utils.obsutils import fix_obs
from prospect.models import priors, transforms
from prospect.models import priors_beta as pb
import h5py
from django.db.models import Q
from astropy.cosmology import WMAP9 as cosmo
from scipy.interpolate import interp1d, UnivariateSpline
from scipy.stats import t
import pickle
# torch
import torch
import torch.nn as nn
import torch.nn.functional as F
from sbi import utils as Ut
from sbi import inference as Inference

from host.photometric_calibration import ab_mag_to_mJy,mJy_to_maggies

all_filters = Filter.objects.filter(~Q(name='DES_i') & ~Q(name='DES_Y'))
massmet = np.loadtxt('host/SBI/gallazzi_05_massmet.txt')
z_age, age = np.loadtxt('host/SBI/wmap9_z_age.txt', unpack=True)
f_age_z = interp1d(age, z_age)
z_b19, tl_b19, sfrd_b19 = np.loadtxt('host/SBI/behroozi_19_sfrd.txt', unpack=True)
spl_z_sfrd = UnivariateSpline(z_b19, sfrd_b19, s=0, ext=1)
spl_tl_sfrd = UnivariateSpline(tl_b19, sfrd_b19, s=0, ext=1) # tl in yrs

nhidden = 500 # architecture
nblocks = 15 # architecture

fanpe = 'host/SBI/SBI_model.pt' # name for the .pt file where the trained model will be saved
fsumm = 'host/SBI/SBI_model_summary.p' # name for the .p file where the training summary will be saved; useful if want to check the convergence, etc.

if torch.cuda.is_available(): device = 'cuda'
else: device = 'cpu'

def build_obs(**extras): ##transient, aperture_type):

    """
    This functions is required by prospector and should return
    a dictionary defined by
    https://prospect.readthedocs.io/en/latest/dataformat.html.

    """
    filters = []
    for filter in all_filters:

        filters.append(filter.transmission_curve())

    obs_data = dict(
        wavelength=None,
        spectrum=None,
        unc=None,
        mask=None,
        ##redshift=z,
        maggies=np.ones(len(all_filters)), #np.array(flux_maggies),
        maggies_unc=np.ones(len(all_filters)),
        filters=filters,
    )
    obs_data["phot_wave"] = np.array([f.wave_effective for f in obs_data["filters"]])
    obs_data["phot_mask"] = [True] * len(obs_data["filters"])

    return fix_obs(obs_data)


def build_model(observations=None,**extras):
    """
    Construct all model components
    """

    model_params = TemplateLibrary["parametric_sfh"]
    model_params.update(TemplateLibrary["nebular"])
    model_params["zred"]["init"] = 0.1
    model = SpecModel(model_params)
    sps = CSPSpecBasis(zcontinuous=1)
    noise_model = (None, None)

    return model ###{"model": model, "sps": sps, "noise_model": noise_model}

def build_sps(zcontinuous=2, compute_vega_mags=False, **extras):
    sps = CSPSpecBasis(
        zcontinuous=zcontinuous,
        compute_vega_mags=compute_vega_mags)  # special to remove redshifting issue
    return sps

def build_noise(**extras):
    return None, None

def loc(mass):
    return np.interp(mass, massmet[:, 0], massmet[:, 1])

def scale(mass):
    upper_84 = np.interp(mass, massmet[:, 0], massmet[:, 3])
    lower_16 = np.interp(mass, massmet[:, 0], massmet[:, 2])
    return (upper_84-lower_16)

def expe_logsfr_ratios(this_z, this_m, shift=True, rtn_sfr=False):

    if shift:
        age_shifted = np.log10(cosmo.age(this_z).value) + pb.delta_t_dex(this_m)
        age_shifted = 10**age_shifted

        zmin_thres = 1e-4
        zmax_thres = 20
        if age_shifted < age[-1]:
            z_shifted = zmax_thres * 1
        elif age_shifted > age[0]:
            z_shifted = zmin_thres * 1
        else:
            z_shifted = f_age_z(age_shifted)
            if z_shifted > zmax_thres:
                z_shifted = zmax_thres * 1
    else:
        z_shifted = this_z * 1

    agebins_in_yr_rescaled_shifted = pb.z_to_agebins_rescale(z_shifted)
    agebins_in_yr_rescaled_shifted = 10**agebins_in_yr_rescaled_shifted
    agebins_in_yr_rescaled_shifted_ctr = np.mean(agebins_in_yr_rescaled_shifted, axis=1)

    nsfrbins = agebins_in_yr_rescaled_shifted.shape[0]

    sfr_shifted = np.zeros(nsfrbins)
    sfr_shifted_ctr = np.zeros(nsfrbins)
    for i in range(nsfrbins):
        a = agebins_in_yr_rescaled_shifted[i,0]
        b = agebins_in_yr_rescaled_shifted[i,1]
        sfr_shifted[i] = spl_tl_sfrd.integral(a=a, b=b)
        sfr_shifted_ctr[i] = spl_tl_sfrd(agebins_in_yr_rescaled_shifted_ctr[i])

    logsfr_ratios_shifted = np.zeros(nsfrbins-1)
    with np.errstate(invalid='ignore', divide='ignore'):
        for i in range(nsfrbins-1):
            logsfr_ratios_shifted[i] = np.log10(sfr_shifted[i]/sfr_shifted[i+1])
    logsfr_ratios_shifted = np.clip(logsfr_ratios_shifted, -5.0, 5.0)

    if not np.all(np.isfinite(logsfr_ratios_shifted)):
        # set nan accord. to its neighbor
        nan_idx = np.isnan(logsfr_ratios_shifted)
        finite_idx = np.min(np.where(nan_idx==True))-1
        neigh = logsfr_ratios_shifted[finite_idx]
        nan_idx = np.arange(6-finite_idx-1) + finite_idx + 1
        for i in range(len(nan_idx)):
            logsfr_ratios_shifted[nan_idx[i]] = neigh * 1.
    import pdb; pdb.set_trace()
    if rtn_sfr:
        print('delta', delta_t_dex(this_m), 'age_shifted', age_shifted, 'z_shifted', z_shifted)
        return (agebins_in_yr_rescaled_shifted_ctr, sfr_shifted_ctr)
    else:
        return logsfr_ratios_shifted


def draw_thetas():
    # draw a zred from pdf(z)
    # redshifts up to 0.2
    #zred = priors.FastUniform(a=0.0, b=0.2).sample()
    #import pdb; pdb.set_trace()
    ##zred = u #???
    #zred = finterp_cdf_z(u)

    # draw from the mass function at the above zred
    mass = priors.LogUniform(mini=100000000.0,maxi=1000000000000.0).sample()
    # given mass from above, draw logzsol
    logzsol = priors.FastUniform(a=-2,b=0.19).sample()

    # dust
    dust2 = priors.FastUniform(a=0.0,b=2.0).sample()

    # tage
    tage = priors.FastUniform(a=0.001,b=13.8).sample()

    # tau
    tau = priors.LogUniform(mini=0.1,maxi=30).sample()

    return np.concatenate(
        [np.atleast_1d(mass),np.atleast_1d(logzsol),np.atleast_1d(dust2),np.atleast_1d(tage),np.atleast_1d(tau)])

class TrainSBI:
    def __init__(self):
        pass

    def build_all(self,**kwargs):
        return (build_obs(**kwargs), build_model(**kwargs),
                build_sps(**kwargs),
                build_noise(**kwargs))

    def main(self):

        # parameters
        needed_size=5000
        run_params = {'ichunk':0,
                      'needed_size':needed_size}
        run_params["add_duste"] = True
        run_params["add_igm"] = True
        run_params["add_neb"] = True
        run_params["dynesty"] = False
        run_params["optmization"] = False
        run_params["emcee"] = False

        obs, model, sps, noise = self.build_all(**run_params)

        run_params["sps_libraries"] = sps.ssp.libraries
        run_params["param_file"] = __file__

        # get the minimum, maximum magnitudes
        cat_min,cat_max,cat_full = {},{},{}
        for f in all_filters:
            mag,snr = np.loadtxt(f'host/SBI/snrfiles/{f.name}_magvsnr.txt',unpack=True)
            #mag = ab_mag_to_mJy(mag)*10 ** (-0.4 * filter.ab_offset)
            #mJy = mJy_to_maggies(mag)

            cat_min[f.name] = np.min(mag)
            cat_max[f.name] = np.max(mag)
            cat_full[f.name] = (mag,snr)

        ### start putting together the synthetic data
        list_thetas = []
        list_mfrac = []
        list_phot = []
        while len(list_phot) < needed_size:
            theta = draw_thetas()

            # call prospector
            # generate the model SED at given theta
            zred = priors.FastUniform(a=0.0, b=0.2).sample()
            model.params['zred'] = np.atleast_1d(zred)
            spec, phot, mfrac = model.predict(theta, obs=obs, sps=sps)
            predicted_mags = -2.5*np.log10(phot)

            flag = True
            for i,f in enumerate(all_filters):
                # probably gonna have some unit issues here
                flag &= (predicted_mags[i] >= cat_min[f.name]) & (predicted_mags[i] <= cat_max[f.name])

            # if all phot is within valid range, we can proceed
            if not flag: continue
            
            list_thetas.append(theta)
            list_mfrac.append(mfrac)

            # simulate the noised-up photometry
            list_phot_single = np.array([])
            for i,f in enumerate(all_filters):
                snr = np.interp(predicted_mags[i],cat_full[f.name][0],cat_full[f.name][1])
                phot_err = phot[i]/snr
                phot_random = np.random.normal(phot[i],phot_err)

                list_phot_single = np.append(list_phot_single,[phot_random,phot_err])
            list_phot.append(list_phot_single)
            print(len(list_phot))
        x_train = np.array(list_thetas); y_train = np.array(list_phot)
        #import pdb; pdb.set_trace()
        # now do the training
        anpe = Inference.SNPE(
            density_estimator=Ut.posterior_nn('maf', hidden_features=nhidden, num_transforms=nblocks),
            device=device)
        # because we append_simulations, training set == prior
        anpe.append_simulations(
            torch.as_tensor(x_train.astype(np.float32), device='cpu'),
            torch.as_tensor(y_train.astype(np.float32), device='cpu'))
        p_x_y_estimator = anpe.train()

        # save trained ANPE
        torch.save(p_x_y_estimator.state_dict(), fanpe)

        # save training summary
        pickle.dump(anpe._summary, open(fsumm, 'wb'))
        print(anpe._summary)

        save_phot = True
        if save_phot:
            hf_phot = h5py.File('host/SBI/sbi_phot.h5', 'w')
            hf_phot.create_dataset('wphot', data=obs["phot_wave"])
            hf_phot.create_dataset('phot', data=list_phot)
            hf_phot.create_dataset('mfrac', data=list_mfrac)
            hf_phot.create_dataset('theta', data=list_thetas)

            try:
                hf_phot.close()
            except(AttributeError):
                pass

            print('Finished.')

if __name__ == "__main__":
    ts = TrainSBI()
    ts.main()
