#!/usr/bin/env python
# D. Jones - 4/5/23
# django cron to be called by slurm
# should run a single transient all 
# the way through.  data saved to sqlite
# and we can figure out how to export it
# later

from django_cron import CronJobBase, Schedule
from host import tasks
from host.models import Transient, Task, TaskRegister, Status
import os
import datetime
transient_name = os.environ['BLAST_TRANSIENT_NAME']
transient_ra = os.environ['BLAST_TRANSIENT_RA']
transient_dec = os.environ['BLAST_TRANSIENT_DEC']

tasks_in_order = ['Transient MWEBV',
                  'Host match',
                  'Host MWEBV',
                  'Cutout download',
                  'Host information',
                  'Transient information',
                  'Global aperture construction',
                  'Global aperture photometry',
                  'Local aperture photometry',
                  'Global host SED inference',
                  'Local host SED inference']

class run_single(CronJobBase):

    RUN_EVERY_MINS = 3

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'host.slurm.run_single_transient.run_single'

    def do(self):
        
        self.run()

    def run(self):

        transients = Transient.objects.filter(name=transient_name)
        if not len(transients):
            transient = Transient.objects.create(
                name=transient_name,ra_deg=transient_ra,dec_deg=transient_dec,tns_id=1)
        else:
            transient = transients[0]

        task_count = 0
        for t in tasks.periodic_tasks:
            if t.task_name == tasks_in_order[task_count]:

                task = Task.objects.get(name__exact=t.task_name)
                task_register = TaskRegister.objects.all()
                task_register = task_register.filter(transient=transient, task=task)

                if not len(task_register):
                    task_register = TaskRegister.objects.create(
                        transient=transient,task=task,status=Status.objects.get(message='not processed'),
                        last_modified=datetime.datetime.now(),last_processing_time_seconds=0)
                else:
                    task_register = task_register[0]

                status = t.run_process(task_register)
                task_count += 1
