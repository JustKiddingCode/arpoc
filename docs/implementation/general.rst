.. _implementation_general:

General Implementation
=======================

This section describes the libraries and frameworks we used to built our reverse
proxy.

Python 3
--------

The reverse proxy was developed using Python 3 :cite:`python3`.
Python includes a large library and many libraries are written for Python applications.
In the follow sections we name the most import python-native libraries we use.

argparse
^^^^^^^^^^^

For command line arguments we use argparse (:cite:`argparse`). This way, users can display all
recognized command line parameters with `--help`.

logging
^^^^^^^^^^^

Almost every library uses the python-native logging library :cite:`logging`.
The default log level we capture is `INFO`. However, this can be changed
in the configuration file as well as the log file.

typing
^^^^^^^^^^^

Our complete project uses Python type hints. This way static sanity checks can be
done to reduce the amount of bugs in the source code. An example for such a static
code check application is MyPy. The type hints are done with the typing module (:cite:`typing`)

json
^^^^^^^^^^^

All AC entities use the JSON format. The file can be parsed into dictionaries with
the json module (:cite:`json`).


pytest
------

pyyaml
------


jinja2
-------

cherrypy
--------

Cherrypy is "a minimalist python web framework" (TODO: Quote from website).
Dispatcher
Used plugins: dropprivileges, daemonizer, pidfile

https://cherrypy.org/

OpenID Connect pyoidc
---------------------

pyjwkest
----------------------

requests
--------


