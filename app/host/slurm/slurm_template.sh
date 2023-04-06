#!/bin/bash -l
#SBATCH --job-name=blast_transient_<transient_name>
#SBATCH --time=34:00:00
#SBATCH --ntasks=2
#SBATCH --array=1-2
#SBATCH --cpus-per-task=1
#SBATCH --output=blast_transient.log
#SBATCH --mem=12GB
#SBATCH -p shared

export BLAST_TRANSIENT_NAME=<transient_name>
export BLAST_TRANSIENT_RA=<transient_ra>
export BLAST_TRANSIENT_DEC=<transient_dec>

python manage.py runcrons host.slurm.run_single_transient.run_single --force
