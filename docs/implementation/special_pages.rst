Special pages
=============

We currently provide two special pages: the *userinfo* and the *policy administration
point* (PAP).

userinfo
---------

.. figure:: /docs/userinfo.png
   :scale: 80%

   Screenshot of the userinfo special page

The userinfo prints the information that is available for the access control evaluation
in the subject dictionary. It is the same the reverse proxy gets from the openid connect
provider via the userinfo endpoint.

Policy Administration Point
---------------------------


The PAP provides information about all access control entities and can furthermore
be used to run the evaluation process with self-defined context data.
The view mode enables the user to collapse certain AC entities, like shown in the
next figure.

.. figure:: /docs/pap_view.png
   :scale: 80%

   Screenshot of the view functionality of the PAP

The evaluation results are presented on an AC entity level, i.e. for every entity
the result is shown: green for granted, red for denied, grey for no evaluation because
of none matching target specifier.

.. figure:: /docs/pap_testbed.png
   :scale: 80%

   Screenshot of the testing functionality of the PAP

.. figure:: /docs/pap_testbed_eval.png
   :scale: 80%

   Screenshot of the testing functionality of the PAP, with a rule evaluated
