import matplotlib.pyplot as plt
import pandas as pd
from astropy.coordinates import SkyCoord
import numpy as np
import sys
from matplotlib.colors import PowerNorm
from astropy.wcs import WCS
from astropy.io import fits
from astropy.visualization import PercentileInterval, AsinhStretch
import os
sys.path.append("app/host")
from cutout_images import panstarrs_cutout


results = pd.read_csv('validation_results/matching_ghost_jones+2018.csv')
"""
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
    fits_filename = f'validation_data/jones+18_panstarrs_g_cutouts/{transient_name.strip()}_panstarrs_g.fits'

    if os.path.exists(fits_filename):
        print(f"{transient_name} cutout exists")
        image = fits.open(fits_filename)
    else:
        print(f"{transient_name} cutout does not exist, downloading...")
        image = panstarrs_cutout(transient_position, image_size=250, filter="g")
        image.writeto(fits_filename)

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

    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

plt.subplots_adjust(wspace=-0.5, hspace=-0.5)
plt.tight_layout()
plt.savefig("validation_plots/GHOST_jones18_match_mosaic.pdf", dpi=150)
plt.clf()
"""

results = pd.read_csv('validation_results/matching_ghost_jones+2018.csv')

success = []
failed = []

for _, match in results.iterrows():
    pred_ra, pred_dec = match['predicted_host_ra_deg'], match['predicted_host_dec_deg']
    actual_ra, actual_dec = match['host_ra_deg'], match['host_dec_deg']
    transient_ra, transient_dec = match['transient_ra_deg'], match['transient_dec_deg']
    transient_name = match['transient_name']

    transient_position = SkyCoord(ra=transient_ra, dec=transient_dec, unit="deg")
    ghost_position = SkyCoord(ra=pred_ra, dec=pred_dec, unit="deg")
    jones_position = SkyCoord(ra=actual_ra, dec=actual_dec, unit="deg")
    fits_filename = f'validation_data/jones+18_panstarrs_g_cutouts/{transient_name.strip()}_panstarrs_g.fits'

    current = {}
    current['transient_position'] = transient_position
    current['predicted_position'] = ghost_position
    current['actual_position'] = jones_position
    current['transient_name'] = match['transient_name']

    if ghost_position.separation(jones_position).arcsec < 2.0:
        success.append(current)
    else:
        failed.append(current)

plt.clf()

fig, axs = plt.subplots(2, 6, figsize=(20, 20*2/6))
bad_ax = axs.reshape(-1)[:6]
good_ax = axs.reshape(-1)[6:]

failed.reverse()

for axes, match_set in zip([bad_ax, good_ax], [failed, success]):
    for match, ax in zip(match_set, axes):
        transient_name = match['transient_name'].strip()
        fits_filename = f'validation_data/jones+18_panstarrs_g_cutouts/{transient_name}_panstarrs_g.fits'
        transient_position = match['transient_position']
        ghost_position = match["predicted_position"]
        jones_position = match["actual_position"]

        if os.path.exists(fits_filename):
            print(f"{transient_name} cutout exists")
            image = fits.open(fits_filename)
        else:
            print(f"{transient_name} cutout does not exist, downloading...")
            image = panstarrs_cutout(match['transient_position'], image_size=250, filter="g")
            image.writeto(fits_filename)

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

        ax.scatter(sn_x, sn_y, marker="+", c="purple", label='Transient', s=200)
        ax.scatter(ghost_x, ghost_y, s=200, facecolors='none', edgecolors='r', label='Host (GHOST)')
        ax.scatter(jones_x, jones_y, facecolors='none', edgecolors='b', marker="^", label='Host (Jones+18)', s=200)

        sep = round(ghost_position.separation(jones_position).arcsec, 1)

        ax.text(0.05, 0.95, transient_name, horizontalalignment='left',
                verticalalignment='top', transform=ax.transAxes, backgroundcolor="white", fontsize=12)
        #ax.text(0.05, 0.05, f'{sep} arcsec' , horizontalalignment='left',
        #            verticalalignment='top', transform=ax.transAxes, backgroundcolor="white", fontsize=12)
        ax.xaxis.set_ticks([])
        ax.yaxis.set_ticks([])
        ax.axis('off')

ax.legend(loc="upper center", bbox_to_anchor=(-2.15, -0.1), frameon=False, ncol=3, fontsize=14)

plt.tight_layout()
plt.subplots_adjust(wspace=0.05, hspace=0.05)
plt.savefig("validation_plots/GHOST_jones18_success_failed_match_mosaic.pdf", dpi=150,bbox_inches='tight')
plt.clf()

