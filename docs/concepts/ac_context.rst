Attribut Retrieval
======================

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   hide user
   hide object
   hide obligations
   hide acentities

.. _concepts_attribute_retrival_subject:

Subject
*******

The subject dictionary is filled with attributes or as they are called in the
OpenID Connect Context `claims`.
The subject dictionary is equal to the information from the OpenID Connect
Userinfo Endpoint.
The scopes are requested on-demand. If an access control rule tries to access
a not existing claim, this claim is saved and - if the evaluation was not
successful (`GRANT`) - the scopes providing the missing claims
are requested from the userinfo endpoint.
For self-defined scopes the user can provide a mapping from claim to scope.

Object
*******
The object dictionary is initialized with the following keys:

* `path`: The requested path excluding the proxy path ( `/serviceA/foo` -> `/foo` )
* `target_url`: The url that is proxied, if access is granted
* `service`: The service name configured by oidcproxy configuration


The rest of the object dictionary is populated using so-called `objectsetters`.
The objectsetters can be freely implemented and activated using the configuration
file. All object setters are run when the first ac entities requests a 
key that is not in the dictionary.

Environment
***********

The environment variables are also populated with plugins. In contrast to the
objectsetters, each environment plugin specifies the attribute it shows and
the plugin is only called when this attribute is requested.
The value of the plugin is cached, so repeated requests of the same variable will
return the same value.

Access
******

The access dictionary is populated with the HTTP headers, the body (if present)
and HTTP method from the current access.
The following keys are present:

* `method`: The HTTP method (GET,POST,PUT,DELETE,PATCH)
* `body`: The request body
* `headers`: The request headers
* `query_dict`: The parsed query string (everything after the first '?' in the URL)

