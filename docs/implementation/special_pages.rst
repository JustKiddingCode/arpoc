Special pages
=============

We currently provide two special pages: the *userinfo* and the *policy administration
point* (PAP).

userinfo
---------

.. figure:: /userinfo.png
   :scale: 80%

   Screenshot of the userinfo special page

The userinfo prints the information that is available for the access control evaluation
in the subject dictionary. It is the same the reverse proxy gets from the OpenID Connect
provider via the userinfo endpoint.

Policy Administration Point
---------------------------


The PAP provides information about all access control entities and can furthermore
be used to run the evaluation process with self-defined context data.
The view mode enables the user to collapse certain AC entities, like shown in the
next figure with the `com.example.rules.is_workingtime` entity.

.. figure:: /pap_view.png
   :scale: 80%

   Screenshot of the view functionality of the PAP

The testbed mode allow to evaluate AC entities with arbitrary AC context.
The evaluation results are presented on an AC entity level, i.e. for every entity
the result is shown: green for granted, red for denied, grey for no evaluation because
of the target specifier did not match.

.. figure:: /pap_testbed.png
   :scale: 70%

   Screenshot of the testing functionality of the PAP

.. figure:: /pap_testbed_eval.png
   :scale: 80%

   Screenshot of the testing functionality of the PAP, with a rule evaluated
