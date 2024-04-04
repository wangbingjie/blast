#!/bin/env bash

set -o pipefail
set -e

# Create data folders on persistent volume and symlink to expected paths
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "${SCRIPT_DIR}"

bash initialize_data_dirs.sh

cd /tmp

if [[ "${USE_DATA_ARCHIVE}" == "true" ]]; then
  ##
  ## Install data files from compiled archive
  ##

  # TODO: These are not comprehensive data integrity checks; 
  # we are only spot-checking the data directories.
  if [[ "${FORCE_DATA_DOWNLOAD}" != "true" && \
        -f "/fsps/README.md" && \
        -f "/sbipp_phot/sbi_phot_local.h5" && \
        -f "/transmission/2MASS_H.txt" ]]
  then
      echo "Required data files already downloaded."
  else
    if [[ "${USE_LOCAL_ARCHIVE_FILE}" == "true" ]]; then
        echo "Installing data from archive file \"${DATA_ARCHIVE_FILE}\"..."
      if [[ ! -f "${DATA_ARCHIVE_FILE}" ]]; then
        echo "Data archive file \"${DATA_ARCHIVE_FILE}\" not found. Aborting."
        exit 1
      fi
    else
      if [[ -f "${DATA_ARCHIVE_FILE}" ]]; then
        echo "Data archive file already downloaded."
      else
        echo "Downloading data archive file from \"${DATA_ARCHIVE_FILE_URL}\"..."
        curl -LJO "${DATA_ARCHIVE_FILE_URL}"
        echo "Download complete."
      fi
    fi

    # Extract and install the data files
    echo "Extracting data archive..."
    tar -xzf "${DATA_ARCHIVE_FILE}"
    echo "Data extracted. Installing data files..."
    rsync -va data/cutout_cdn/2010ag/ /data/cutout_cdn/2010ag/
    rsync -va data/cutout_cdn/2010ai/ /data/cutout_cdn/2010ai/
    rsync -va data/cutout_cdn/2010H/  /data/cutout_cdn/2010H/
    rsync -va data/sed_output/2010H/  /data/sed_output/2010H/
    rsync -va data/sbipp/             /sbipp/
    rsync -va data/transmission/      /transmission/
    rsync -va data/fsps/              /fsps/
    rsync -va data/sbipp_phot/        /sbipp_phot/
    echo "Data installed."

    # Clean up temporary files
    if [[ "${USE_LOCAL_ARCHIVE_FILE}" != "true" ]]; then
      rm -f "${DATA_ARCHIVE_FILE}"
    fi
    rm -rf data
  fi

else

  ##
  ## Install data files from original sources
  ##

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

cd "${SCRIPT_DIR}"/..
python init_data.py

echo "Data initialization complete."
