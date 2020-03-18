.. _implementation_general:

General Implementation
=======================

This section describes the libraries and frameworks we used to built our reverse
proxy.

.. uml::
   :width:  40%

   [pyoidc]
   [cherrypy]
   [pyyaml]
   [argparse]
   [json]
   [jinja2]
   [ARPOC]
   [requests]
   [pyjwkest]
   [logging]
   
   Actor User
   Actor Administrator
   
   node "OIDC Provider" as oidcp
   node Webservice
   database "AC Entities" as ace
   database Templates
   database Configuration
   database Logs
   
   User -- cherrypy
   Administrator -- argparse
   argparse -- ARPOC
   cherrypy -- ARPOC
   ARPOC -- pyoidc
   pyoidc -- oidcp
   ARPOC - json
   json - ace
   jinja2 - ARPOC
   Templates - jinja2
   Administrator - Configuration
   Configuration -- pyyaml
   pyyaml -- ARPOC
   ARPOC -- requests
   requests -- Webservice
   ARPOC -- pyjwkest : JWT
   logging -- ARPOC
   Logs -- logging

   Caption Overview over the used libraries

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


json
^^^^^^^^^^^

All AC entities use the JSON format. The file can be parsed into dictionaries with
the json module (:cite:`json`).


pyyaml
------

We want to make the configuration as easy as possible. Therefore, our configuration
file is in YAML (todo: ref) syntax. To parse the configuration file, we use
pyyaml (:cite:`pyyaml`). PyYAML parses the configuration into a dictionary which
we use in our `config` module.


jinja2
-------

Every object that is created via our reverse proxy and not requested from a web
server should be in HTML format so web browsers can render it.
To seperate data and code, we use a template engine to create HTML output.
For this we use jinja (:cite:`jinja`).

cherrypy
--------

A reverse proxy is not different to a normal webserver in tasks like session
handling, listening on ports or parsing HTTP requests. The only difference is
that the objects it serves are not files or outputs of applications on the server
but the output of another webserver.
For all tasks of a normal HTTP server we use cherrypy (:cite:`cherrypy`).
Cherrypy is "a minimalist python web framework" (:cite:`cherrypy`).
To increase the security of our application, we run the webserver with reduced
privileges. We do this by using the `dropprivileges` plugin (:cite:`cherrypy_dropprivileges`).
Also the use case for our webserver is to run as a daemon. This is done with the
`daemonizer` plugin (:cite:`cherrypy_daemonizer`).
After parsing the requests the URL request must handled by the application.
The connector between CherryPy and the application is the dispatcher.
Based on the URL that was requested, the dispatcher selects a method and calls
it. We used the `RoutesDispatcher` (:cite:`cherrypy_routes`) that assigns
the methods with matches.
Every service gets connected with an instance of a `ServiceProxy` (todo: link) class,
special pages with their class, and pages to require authentication or redirect
pages for the OpenID connect provider with the `OIDCHandler` (todo: link) object. 

pyoidc
---------------------

All subject attributes are claims of the openid connect provider.
Therefore we need to communicate with OpenID Connect Provider, act as
a relying party and comply with the respective standards.
The library pyoidc (:cite:`pyoidc`) enables us to comply with the standard
without implementing it on our own.

pyjwkest
----------------------

If the user does a request with an access token included, we need to contact
the issuer of this access token to ensure, that the access token is valid.
Because many issuers (TODO: cite/prove) use JWTs we can parse them and contact
the issuer that is stated inside the JWT.
`pyoidc` uses for this task the library `pyjwkest` (:cite:`pyjwkest`) 
which we use as well.

requests
--------

In the object delivery phase, we need to request the object from a different web
server, copy the response header and data and transmit the object to the requesting
users. This would require building a HTTP request, including encoding characters
to comply standars, opening a connection to the web server, and parsing the
response.
Furthermore, we would need to implement TLS certificate checks.
All this tasks are performed by the requests library (:cite:`requests`).
