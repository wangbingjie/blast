#!/usr/bin/env python

import astropy.table as at
import os
import argparse

def main(
        batchfile,batchdir,
        blastdir='/n/holystore01/LABS/berger_lab/Lab/djones01/blast/app'):
    data = at.Table.read(batchfile)

    if not os.path.exists(batchdir):
        os.makedirs(batchdir)

    for d in data:
        slurmfile = f"{batchdir}/slurm_{d['transient_name']}.sh"

        with open('slurm_template.sh','r') as fin, \
             open(slurmfile,'w') as fout:
            for line in fin:
                line = line.\
                    replace('\n','').\
                    replace('<transient_name>',str(d['transient_name'])).\
                    replace('<transient_ra>',str(d['transient_ra'])).\
                    replace('<transient_dec>',str(d['transient_dec'])).\
                    replace('<outdir>',batchdir).\
                    replace('<blastdir>',blastdir)
                print(line,file=fout)
        os.system(f'sbatch {slurmfile}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='batch submission for slurm systems')
    parser.add_argument('batchfile', help='batch CSV with transient name,ra,dec')
    parser.add_argument('batchdir', help='output directory for logs, job scripts')
    args = vars(parser.parse_args())

    main(args['batchfile'],args['batchdir'])
