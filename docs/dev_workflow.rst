Developer workflow
==================

General workflow
----------------

To add or change code on blast we use git and github. If you are unfamiliar with
these two pieces of software, a great place to start would be to watch this
introduction to git and github on youtube
`here <https://www.youtube.com/watch?v=RGOj5yH7evk>`_.

The normal develop workflow of blast is to branch off main, commit and push
changes, and then merge into the main branch with a pull request. Finally, after
the pull request has been approved and your changes have been merged you can delete
your branch.

Starting from scratch, the typical development workflow would be the following.
Clone the blast git repository

.. code:: none

    git clone https://github.com/astrophpeter/blast.git

Create your own branch with the following naming convention.

.. code:: none

    git checkout -b <your first name>-<one or two word description of what you are doing>

For example, if you were called Joe and wanted to contribute to documentation on
blast your branch might be called joe-docs. Then set the remote of your
new branch to github.

.. code:: none

    git push --set-upstream origin <your branch name>

This means you can push changes to github where they can be saved before you
are ready for a pull request. Now you can make your changes and additions to the
code and push changes to github.

Next go to to the blast github repository page and go to the pull requests tab.

.. image:: _static/contributing_pull_request_tab.png

Then open a new draft pull request.

.. image:: _static/contributing_new_pull_request.png

Create a pull request with your branch and main.

.. image:: _static/contributing_create_pull_request.png

Fill in the title and describe what you are trying to do in the description, and
open a draft pull request.

.. image:: _static/contributing_draft_pull_request.png

As you commit and push changes to your branch on github they will show up
in the draft pull request. When you are a happy for you changes to be reviewed
and then eventually merged into develop, click ready for review.

.. image:: _static/contributing_ready_for_review.png

Your code will now be reviewed and when it is accepted it will be merged into
develop. After your branch has been merged, delete the branch from your local
repository.

.. code:: none

    git branch -d <your branch name>

Then delete the branch from Github.

.. code:: none

    git push -d origin <your branch name>
