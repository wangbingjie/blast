import sys

import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
import matplotlib.pyplot as plt


sys.path.append("app/host")

from matching import ghost

validation_data = pd.read_csv(
    "../validation_data/jones+2018.tsv", skiprows=list(range(96)) + [97, 98], sep="|"
)


matches = []

for _, match in validation_data.iterrows():
    transient_ra, transient_dec = match["RAJ2000"], match["DEJ2000"]
    transient_position = SkyCoord(
        ra=transient_ra, dec=transient_dec, unit=(u.hourangle, u.deg)
    )

    host_ra, host_dec = match["RAH"], match["DEH"]
    host_position = SkyCoord(ra=host_ra, dec=host_dec, unit=(u.hourangle, u.deg))

    current_match = {}
    current_match["transient_position"] = transient_position
    current_match["host_position"] = host_position
    matches.append(current_match)


for num, match in enumerate(matches):
    print(f"Matching {num} of {len(matches)} transients")
    host_data = ghost(match["transient_position"])
    match["predicted_host_position"] = host_data["host_position"]


transient_ra_deg, transient_dec_deg = [], []
host_ra_deg, host_dec_deg = [], []
predicted_host_ra_deg, predicted_host_dec_deg = [], []

for match in matches:
    transient_ra_deg.append(match["transient_position"].ra.deg)
    transient_dec_deg.append(match["transient_position"].dec.deg)

    host_ra_deg.append(match["host_position"].ra.deg)
    host_dec_deg.append(match["host_position"].dec.deg)

    if match["predicted_host_position"] is not None:
        predicted_host_ra_deg.append(match["predicted_host_position"].ra.deg)
        predicted_host_dec_deg.append(match["predicted_host_position"].dec.deg)
    else:
        predicted_host_ra_deg.append(None)
        predicted_host_dec_deg.append(None)

results = {
    "transient_ra_deg": transient_ra_deg,
    "transient_dec_deg": transient_dec_deg,
    "host_ra_deg": host_ra_deg,
    "host_dec_deg": host_dec_deg,
    "predicted_host_ra_deg": predicted_host_ra_deg,
    "predicted_host_dec_deg": predicted_host_dec_deg,
}

results = pd.DataFrame(results)
results.to_csv(
    "validation_results/matching_ghost_jones+2018.csv", index=False
)




