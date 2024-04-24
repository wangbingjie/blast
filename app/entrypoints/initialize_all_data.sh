#!/bin/env bash

set -o pipefail
set -e

# Create data folders on persistent volume and symlink to expected paths
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
cd "${SCRIPT_DIR}"

bash initialize_data_dirs.sh

cd /tmp

extract_data_archive_file() {
  local file_path=$1
  local extract_dir=$2
  local original_dir=$(pwd)
  echo "INFO: Installing data from archive file \"${file_path}\"..."
  if [[ ! -f "${file_path}" ]]; then
    echo "ERROR: Data archive file \"${file_path}\" not found. Aborting."
    return 1
  fi
  echo "Extracting data archive..."
  # Data archive file has top-level directory "data"
  cd "${extract_dir}"
  tar --strip-components=1 -xzf "${DATA_ARCHIVE_FILE}"
  cd "${original_dir}"
}

verify_data_integrity() {
  # Verify data file integrity.
  local data_root_dir=$1
  local original_dir=$(pwd)
  cd "${data_root_dir}"
  set +e
  md5sum --check --status "${SCRIPT_DIR}/blast-data.md5sums"
  DATA_INTEGRITY_VALID=$?
  set -e
  cd "${original_dir}"
  if [[ "${DATA_INTEGRITY_VALID}" == "0" ]]
  then
    echo "INFO: Required data files pass integrity check."
    return 0
  else
    echo "ERROR: Required data files failed integrity check."
    return 1
  fi
}

download_data_archive() {
  local data_root_dir=$1
  echo "INFO: Downloading data from archive..."
  mc alias set blast https://js2.jetstream-cloud.org:8001 anonymous
  # The trailing slashes are important!
  mc mirror --overwrite --json blast/blast-astro-data/v1/data/ "$(readlink -f "${data_root_dir}")/"
}

# Verify data file integrity and attempt to (re)install required files if necessary
if ! verify_data_integrity "${DATA_ROOT_DIR}"
then
  # Download and install data from archive
  if [[ "${USE_LOCAL_ARCHIVE_FILE}" == "true" ]]
  then
    # Extract data from local archive file
    extract_data_archive_file "${DATA_ARCHIVE_FILE}" "${DATA_ROOT_DIR}"
  else
    # Download data from remote archive
    download_data_archive "${DATA_ROOT_DIR}"
  fi
  # Verify data file integrity
  if ! verify_data_integrity "${DATA_ROOT_DIR}"
  then
    echo "ERROR: Downloaded/extracted data files failed integrity check. Aborting."
    exit 1
  fi
  # # Install data in target locations
  # echo "Data extracted. Installing data files..."
  # rsync -va "${DATA_ROOT_DIR}"/cutout_cdn/2010ag/ "${CUTOUT_ROOT}"/2010ag/
  # rsync -va "${DATA_ROOT_DIR}"/cutout_cdn/2010ai/ "${CUTOUT_ROOT}"/2010ai/
  # rsync -va "${DATA_ROOT_DIR}"/cutout_cdn/2010H/  "${CUTOUT_ROOT}"/2010H/
  # rsync -va "${DATA_ROOT_DIR}"/sed_output/2010H/  "${SED_OUTPUT_ROOT}"/2010H/
  # rsync -va "${DATA_ROOT_DIR}"/sbipp/             "${SBIPP_ROOT}"/
  # rsync -va "${DATA_ROOT_DIR}"/transmission/      "${TRANSMISSION_CURVES_ROOT}"/
  # rsync -va "${DATA_ROOT_DIR}"/fsps/              "${SPS_HOME}"/
  # rsync -va "${DATA_ROOT_DIR}"/tns_staging/       "${TNS_STAGING_ROOT}"/
  # rsync -va "${DATA_ROOT_DIR}"/sbipp_phot/        "${SBIPP_PHOT_ROOT}"/
  # rsync -va "${DATA_ROOT_DIR}"/dustmaps/          "${DUSTMAPS_DATA_ROOT}"/
  # rsync -va "${DATA_ROOT_DIR}"/ghost_data/        "${GHOST_DATA_ROOT}"/
  # rsync -va "${DATA_ROOT_DIR}"/sbi_training_sets/ "${SBI_TRAINING_ROOT}"/
  echo "Data installed."
fi

# Skip redundant installation of dustmap data and config file, where "init_data.py"
# executes "app/entrypoints/initialize_dustmaps.py", which downloads SFD files
# if they are missing and initializes a ".dustmapsrc" file.
# cd "${SCRIPT_DIR}"/..
# python init_data.py

echo "Data initialization complete."
