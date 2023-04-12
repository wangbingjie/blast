# Utils and wrappers for the prospector SED fitting code
import os

import extinction
import numpy as np
import prospect.io.read_results as reader
from django.conf import settings
from prospect.fitting import fit_model as fit_model_prospect
from prospect.fitting import lnprobfn
from prospect.io import write_results as writer
from prospect.models import SpecModel
from prospect.models.templates import TemplateLibrary
from prospect.sources import CSPSpecBasis
from prospect.utils.obsutils import fix_obs
from scipy.special import gamma
from scipy.special import gammainc

from .host_utils import get_dust_maps
from .models import AperturePhotometry
from .models import Filter
from .models import hdf5_file_path
from .photometric_calibration import mJy_to_maggies  ##jansky_to_maggies


def get_CI(chain):
    chainlen = len(chain)
    chainsort = np.sort(chain)
    return (
        chainsort[int(chainlen * 0.16)],
        chainsort[int(chainlen * 0.50)],
        chainsort[int(chainlen * 0.84)],
    )


# I don't remember where this came from
# somewhere in the prospector docs
def psi_from_sfh(mass, tage, tau):
    return (
        mass
        * (tage / tau**2)
        * np.exp(-tage / tau)
        / (gamma(2) * gammainc(2, tage / tau))
        * 1e-9
    )


def build_obs(transient, aperture_type):

    """
    This functions is required by prospector and should return
    a dictionary defined by
    https://prospect.readthedocs.io/en/latest/dataformat.html.

    """

    photometry = AperturePhotometry.objects.filter(
        transient=transient, aperture__type__exact=aperture_type, is_validated=True
    )

    if not photometry.exists():
        raise ValueError(f"No host photometry of type {aperture_type}")

    if transient.host is None:
        raise ValueError("No host galaxy match")

    z = transient.best_redshift

    filters, flux_maggies, flux_maggies_error = [], [], []

    for filter in Filter.objects.all():
        try:
            datapoint = photometry.get(filter=filter)
        except AperturePhotometry.DoesNotExist:
            # sometimes data just don't exist, we can ignore
            continue
        except AperturePhotometry.MultipleObjectsReturned:
            raise

        # correct for MW reddening
        if aperture_type == "global":
            mwebv = transient.host.milkyway_dust_reddening
            if mwebv is None:
                # try once more
                mwebv = get_dust_maps(transient.host.sky_coord)
        elif aperture_type == "local":
            mwebv = transient.milkyway_dust_reddening
            if mwebv is None:
                # try once more
                mwebv = get_dust_maps(transient.sky_coord)
        else:
            raise ValueError(
                f"aperture_type must be 'global' or 'local', currently set to {aperture_type}"
            )
        wave_eff = filter.transmission_curve().wave_effective
        ext_corr = extinction.fitzpatrick99(np.array([wave_eff]), mwebv * 3.1, r_v=3.1)[
            0
        ]
        flux_mwcorr = datapoint.flux * 10 ** (-0.4 * filter.ab_offset) * 10 ** (0.4 * ext_corr)
        fluxerr_mwcorr = datapoint.flux_error * 10 ** (-0.4 * filter.ab_offset) * 10 ** (0.4 * ext_corr)

        filters.append(filter.transmission_curve())
        flux_maggies.append(mJy_to_maggies(flux_mwcorr))
        flux_maggies_error.append(mJy_to_maggies(fluxerr_mwcorr))

    obs_data = dict(
        wavelength=None,
        spectrum=None,
        unc=None,
        redshift=z,
        maggies=np.array(flux_maggies),
        maggies_unc=np.array(flux_maggies_error),
        filters=filters,
    )

    return fix_obs(obs_data)


def build_model(observations):
    """
    Construct all model components
    """

    model_params = TemplateLibrary["parametric_sfh"]
    model_params.update(TemplateLibrary["nebular"])
    model_params["zred"]["init"] = observations["redshift"]
    model = SpecModel(model_params)
    sps = CSPSpecBasis(zcontinuous=1)
    noise_model = (None, None)

    return {"model": model, "sps": sps, "noise_model": noise_model}


def fit_model(observations, model_components, fitting_kwargs):
    """Fit the model"""

    output = fit_model_prospect(
        observations,
        model_components["model"],
        model_components["sps"],
        optimize=False,
        dynesty=True,
        lnprobfn=lnprobfn,
        noise=model_components["noise_model"],
        **fitting_kwargs,
    )
    return output


def prospector_result_to_blast(
    transient,
    aperture,
    prospector_output,
    model_components,
    observations,
    sed_output_root=settings.SED_OUTPUT_ROOT,
):

    # write the results
    hdf5_file = (
        f"{sed_output_root}/{transient.name}/{transient.name}_{aperture.type}.h5"
    )

    if not os.path.exists(f"{sed_output_root}/{transient.name}"):
        os.makedirs(f"{sed_output_root}/{transient.name}/")
    if os.path.exists(hdf5_file):
        # prospector won't overwrite, which causes problems
        os.remove(hdf5_file)

    writer.write_hdf5(
        hdf5_file,
        {},
        model_components["model"],
        observations,
        prospector_output["sampling"][0],
        None,
        sps=model_components["sps"],
        tsample=prospector_output["sampling"][1],
        toptimize=0.0,
    )

    # load up the hdf5 file to get the results
    resultpars, obs, _ = reader.results_from(hdf5_file, dangerous=False)

    # logmass, age, tau
    logmass = np.log10(
        resultpars["chain"][
            ..., np.where(np.array(resultpars["theta_labels"]) == "mass")[0][0]
        ]
    )
    logmass16, logmass50, logmass84 = get_CI(logmass)
    age = resultpars["chain"][
        ..., np.where(np.array(resultpars["theta_labels"]) == "tage")[0][0]
    ]
    age16, age50, age84 = get_CI(age)
    tau = resultpars["chain"][
        ..., np.where(np.array(resultpars["theta_labels"]) == "tau")[0][0]
    ]
    tau16, tau50, tau84 = get_CI(tau)

    # sfr, ssfr
    sfr = psi_from_sfh(
        resultpars["chain"][
            ..., np.where(np.array(resultpars["theta_labels"]) == "mass")[0][0]
        ],
        resultpars["chain"][
            ..., np.where(np.array(resultpars["theta_labels"]) == "tage")[0][0]
        ],
        resultpars["chain"][
            ..., np.where(np.array(resultpars["theta_labels"]) == "tau")[0][0]
        ],
    )
    logsfr = np.log10(sfr)
    logssfr = np.log10(sfr) - logmass
    logsfr16, logsfr50, logsfr84 = get_CI(logsfr)
    logssfr16, logssfr50, logssfr84 = get_CI(logssfr)

    prosp_results = {
        "transient": transient,
        "aperture": aperture,
        "posterior": hdf5_file,
        "log_mass_16": logmass16,
        "log_mass_50": logmass50,
        "log_mass_84": logmass84,
        "log_sfr_16": logsfr16,
        "log_sfr_50": logsfr50,
        "log_sfr_84": logsfr84,
        "log_ssfr_16": logssfr16,
        "log_ssfr_50": logssfr50,
        "log_ssfr_84": logssfr84,
        "log_age_16": age16,
        "log_age_50": age50,
        "log_age_84": age84,
        "log_tau_16": tau16,
        "log_tau_50": tau50,
        "log_tau_84": tau84,
    }

    return prosp_results
