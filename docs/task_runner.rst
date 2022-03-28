.. toctree::
   :maxdepth: 2

Task Runners
++++++++++++

This page walks you through how to write a TaskRunner. A TaskRunner performs a
given computational task on a transient ingested into the blast database. An
example of TaskRunner would be finding a Host galaxy match for a given
transient.

All TaskRunners should inherit from the TaskRunner class. This abstract base
class takes care of all the house keeping associated with running as task in
blast, allowing you to just write the task code.

There are four class methods that need to be implemented in a TaskRunner, we
will briefly run through them.

Process method
------------------

The _run_process method is where the your task code should go. This method
should contain all the necessary computations and saves to the database for your
task to be completed. It task a Transient object as an argument and must return
a Status object which indicates the status of the computation task.
