#!/bin/env bash

set -o pipefail

cd /tmp

# TODO: These are not comprehensive data integrity checks; 
# we are only spot-checking the data directories.

if [[ "${USE_DATA_ARCHIVE}" == "true" ]]; then

  if [[ "${FORCE_DATA_DOWNLOAD}" != "true" && \
        -f "/fsps/README.md" && \
        -f "/sbipp_phot/sbi_phot_local.h5" && \
        -f "data/transmission/2MASS_H.txt" ]]
  then
      echo "Required data files already downloaded."
  else
    set -x
    curl -LJO "https://js2.jetstream-cloud.org:8001/swift/v1/blast-astro-data/${DATA_ARCHIVE}"
    tar -xzf "${DATA_ARCHIVE}"
    rsync -va data/cutout_cdn/2010ag/ /data/cutout_cdn/2010ag/
    rsync -va data/cutout_cdn/2010ai/ /data/cutout_cdn/2010ai/
    rsync -va data/cutout_cdn/2010H/  /data/cutout_cdn/2010H/
    rsync -va data/sed_output/2010H/  /data/sed_output/2010H/
    rsync -va data/sbipp/             /sbipp/
    rsync -va data/transmission/      /transmission/
    rsync -va data/fsps/              /fsps/
    rsync -va data/sbipp_phot/        /sbipp_phot/
    rm -f "${DATA_ARCHIVE}"
    set +x
  fi

else

  if [[ -f "/fsps/README.md" ]]
  then
      echo "fsps files already downloaded"
  else
    echo "downloading fsps files"
    set -e
    git clone https://github.com/cconroy20/fsps.git /fsps
    set +e
    rm -rf /fsps/.git
  fi

  if [[ -f "/sbipp_phot/sbi_phot_local.h5" ]]
  then
      echo "SBI/files already downloaded"
  else
    echo "downloading SBI files"
    set -e
    curl -LJO https://zenodo.org/records/10703208/files/sbi_phot_global.h5
    curl -LJO https://zenodo.org/records/10703208/files/sbi_phot_local.h5
    mv sbi_phot_global.h5 /sbipp_phot/
    mv sbi_phot_local.h5 /sbipp_phot/
    set +e
  fi

  if [[ -f "data/transmission/2MASS_H.txt" ]]
  then
      echo "Remaining data already downloaded"
  else
    set -e
    git clone https://github.com/astrophpeter/blast.git /tmp/blast
    cd /tmp/blast
    rsync -va data/cutout_cdn/2010ag/ /data/cutout_cdn/2010ag/
    rsync -va data/cutout_cdn/2010ai/ /data/cutout_cdn/2010ai/
    rsync -va data/cutout_cdn/2010H/  /data/cutout_cdn/2010H/
    rsync -va data/sed_output/2010H/  /data/sed_output/2010H/
    rsync -va data/sbipp/             /sbipp/
    rsync -va data/transmission/      /transmission/
    set +e
    rm -rf /tmp/blast
  fi

fi

echo "Data initialization complete."
