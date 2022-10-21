import matplotlib.pyplot as plt
import pandas as pd
from astropy.coordinates import SkyCoord
import numpy as np

seps = []
results = pd.read_csv('validation_results/matching_ghost_jones+2018.csv')

for _, match in results.iterrows():
    pred_ra, pred_dec = match['predicted_host_ra_deg'], match['predicted_host_dec_deg']
    actual_ra, actual_dec = match['host_ra_deg'], match['host_dec_deg']

    if pred_ra is not None and actual_ra is not None:
        pred_pos = SkyCoord(ra=pred_ra, dec=pred_dec, unit='deg')
        actual_pos = SkyCoord(ra=actual_ra, dec=actual_dec, unit='deg')
        seps.append(pred_pos.separation(actual_pos).arcsec)

seps = np.array(seps)
seps = seps[np.logical_not(np.isnan(seps))]
hist, bins = np.histogram(seps, bins=30)
logbins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
plt.hist(seps, bins=logbins)
plt.xlabel("GHOST - Jones+2018 Host offset [arcsec]")
plt.xscale('log')
plt.axvline(x=1.0)
plt.ylabel("Count")
plt.savefig('validation_plots/ghost_host_sep_distribution.png')

