import matplotlib.pyplot as plt
import pandas as pd
from astropy.coordinates import SkyCoord
import numpy as np

seps = []
seps_sma = []
results = pd.read_csv('validation_results/matching_ghost_jones+2018.csv')
data = validation_data = pd.read_csv(
    "../validation_data/jones+2018.tsv", skiprows=list(range(96)) + [97, 98], sep="|"
)

for _, match in results.iterrows():
    pred_ra, pred_dec = match['predicted_host_ra_deg'], match['predicted_host_dec_deg']
    actual_ra, actual_dec = match['host_ra_deg'], match['host_dec_deg']

    semi_major = data[data["SN"] == match["transient_name"]]["r-A"].values[0]
    semi_minor = data[data["SN"] == match["transient_name"]]["r-B"].values[0]
    if pred_ra is not None and actual_ra is not None:
        pred_pos = SkyCoord(ra=pred_ra, dec=pred_dec, unit='deg')
        actual_pos = SkyCoord(ra=actual_ra, dec=actual_dec, unit='deg')
        seps.append(pred_pos.separation(actual_pos).arcsec)
        seps_sma.append(pred_pos.separation(actual_pos).arcsec / semi_major)

seps = np.array(seps)
seps_sma = np.array(seps_sma)
seps = seps[np.logical_not(np.isnan(seps))]
seps_sma = seps_sma[np.logical_not(np.isnan(seps_sma))]



hist, bins = np.histogram(seps, bins=30)
logbins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
plt.hist(seps, bins=logbins, label='arcsec', histtype="step")
plt.hist(seps_sma, bins=logbins, label='host semi major axis')


thresh_seps = np.percentile(seps, 95)
thresh_seps_sma = np.percentile(seps_sma, 95)

plt.axvline(x=thresh_seps, c='tab:blue')
plt.axvline(x=thresh_seps_sma, c='tab:orange')

plt.legend()
plt.xlabel("GHOST - Jones+2018 Host Galaxy offset")
plt.xscale('log')
plt.ylabel("Count")
plt.savefig('validation_plots/ghost_host_sep_distribution.png')

