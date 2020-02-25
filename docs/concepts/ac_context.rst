Attribut Retrieval
======================

Subject
*******

The subject dictionary is filled with attributes or as they are called in the
OpenID Connect Context `claims`.
The subject dictionary is equal to the information from the OpenID Connect
Userinfo Endpoint.
The scopes are requested on-demand. If an access control rule tries to access
a not existing claim, this claim is saved and - if the evaluation was not
successful (`GRANT`) - the scopes are requested from the userinfo endpoint.

Object
*******

The object dictionary is populated using so-called `objectsetters`.
The objectsetters can be freely implemented and activated using the configuration
file. All object setters are run before the access control rules are evaluated.


Environment
***********

The environment variables are also populated with plugins. In contrast to the
objectsetters, each environment plugin specifies the attribute it shows and
the plugin is only called when this attribute is requested.

Access
******

The access dictionary is populated with the HTTP headers, the body (if present)
and HTTP method from the current access.
