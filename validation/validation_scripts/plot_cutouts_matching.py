import matplotlib.pyplot as plt
import pandas as pd
from astropy.coordinates import SkyCoord
import numpy as np
import sys
from matplotlib.colors import PowerNorm
from astropy.wcs import WCS
from astropy.visualization import PercentileInterval, AsinhStretch

sys.path.append("app/host")
from cutout_images import panstarrs_cutout

results = pd.read_csv('validation_results/matching_ghost_jones+2018.csv')




n = 6
m = 45
fig, axs = plt.subplots(m, n, figsize=(20, 20*45/6))

for (_, match), ax in zip(list(results.iterrows()), axs.reshape(-1)):
    pred_ra, pred_dec = match['predicted_host_ra_deg'], match['predicted_host_dec_deg']
    actual_ra, actual_dec = match['host_ra_deg'], match['host_dec_deg']
    transient_ra, transient_dec = match['transient_ra_deg'], match['transient_dec_deg']
    transient_name = match['transient_name']

    transient_position = SkyCoord(ra=transient_ra, dec=transient_dec, unit="deg")
    ghost_position = SkyCoord(ra=pred_ra, dec=pred_dec, unit="deg")
    jones_position = SkyCoord(ra=actual_ra, dec=actual_dec, unit="deg")



    image = panstarrs_cutout(transient_position, image_size=250, filter="g")
    image_data = image[0].data
    image_data[np.isnan(image_data)] = 0.0
    # set contrast to something reasonable
    transform = AsinhStretch() + PercentileInterval(99.5)
    image_data = transform(image_data)

    wcs = WCS(image[0].header)
    ax.imshow(image_data, cmap='Greys', origin='lower')
    image.close()

    sn_x, sn_y = transient_position.to_pixel(wcs)
    ghost_x, ghost_y = ghost_position.to_pixel(wcs)
    jones_x, jones_y = jones_position.to_pixel(wcs)

    ax.scatter(sn_x, sn_y, marker="+", c="purple")
    ax.scatter(ghost_x, ghost_y, label='GHOST', s=200, facecolors='none', edgecolors='r')
    ax.scatter(jones_x, jones_y, facecolors='none', edgecolors='b', marker="^")

    ax.text(0.05, 0.95, transient_name, horizontalalignment='left',
         verticalalignment='top', transform=ax.transAxes, backgroundcolor="white")

    #ax.set_title(transient_name)
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

plt.subplots_adjust(wspace=-0.5, hspace=-0.5)
plt.tight_layout()
plt.savefig("validation_plots/GHOST_jones18_match_mosaic.pdf", dpi=150)