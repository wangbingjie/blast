#!/bin/env bash

if [[ -f data/sbipp_phot/sbi_phot_global.h5 ]]
then
    echo "SBI/files already downloaded"
else
  echo "downloading SBI files"
  mkdir data/sbipp_phot
  curl -LJO https://zenodo.org/records/10703208/files/sbi_phot_global.h5 &&
  curl -LJO https://zenodo.org/records/10703208/files/sbi_phot_local.h5 &&
  mv sbi_phot_global.h5 data/sbipp_phot/ &&
  mv sbi_phot_local.h5 data/sbipp_phot/
fi

