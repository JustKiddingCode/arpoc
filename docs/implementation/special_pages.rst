Special pages
=============

We currently provide two special pages: the *userinfo* and the *policy administration
point* (PAP).

The userinfo prints the information that is available for the access control evaluation
in the subject dictionary. It is the same the reverse proxy gets from the openid connect
provider via the userinfo endpoint.

The PAP provides information about all access control entities and can furthermore
be used to run the evaluation process with self-defined context data.
The evaluation results are presented on an AC entity level, i.e. for every entity
the result is shown: green for granted, red for denied, grey for no evaluation because
of none matching target specifier.
