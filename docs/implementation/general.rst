.. _implementation_general:

General Implementation
=======================


This section describes the libraries and frameworks we used to built our reverse
proxy. Like the next figure shows, we use the libraries or frameworks
`cherrypy`,
`argparse`,
`pyyaml`,
`logging`,
`jinja2`,
`json`,
`pyoidc`,
`requests`,
and `pyjwkest`. (TODO: `Lark` is missing here)
We explain the usage of the libraries in the parts where the library is used.
Here we explain the parts that are used throughout the whole application.

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
   
   User -- cherrypy : HTTP Request
   Administrator -- argparse : options
   argparse -- ARPOC
   cherrypy -- ARPOC
   ARPOC -- pyoidc
   pyoidc -- oidcp
   ARPOC - json
   json - ace
   jinja2 - ARPOC
   Templates - jinja2
   Administrator - Configuration : writes
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


logging
--------

Without message from the application, it is hard to find errors in the configuration or to understand
the process of an application.
These messages that are not intended for the user but the administrator are called
log messages.
Almost every library uses the python-native logging library :cite:`logging`.
Log messages are usually combined with a `log level` indicating how important
the reason of the log level is. The log levels are, from least to most important:
`DEBUG`,
`INFO`,
`WARNING`,
`ERROR`,
`CRITICAL`.
The default log level we capture is `INFO`. This can be changed
in the configuration file as well as the log file.
Using the python-native module, we also capture the log messages of the different
Python Libraries we use. The origin of a log message can be seen on the module
prefix in the log message.


jinja2
-------

Every object that is created via our reverse proxy and not requested from a web
server should be in HTML format so web browsers can render it.
To seperate data and code, we use a template engine to create HTML output.
A template engine takes data and a template and generates a document.
We use `jinja` as our template engine (:cite:`jinja`).
The templates are used for the provider selection list, special pages like 
the userinfo or policy administration point or error messages.
