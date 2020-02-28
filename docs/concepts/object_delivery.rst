************
Object delivery
************

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   hide user
   hide OIDC
   hide acentities
   hide objinf
   hide obligations
   hide environment

If the access was granted, we connect to the service using the same HTTP method
and passing all request headers and body from the user.
Some restrictions apply though: we remove the authorization header and we do not
support the HTTP 'keep-alive' option, e.g. we close the connection after every
request.
Furthermore we allow to specify a bearer token which is used in the `authorization`
header to the HTTP client and to use a TLS client certificate which is used on 
opening the connection to the object.
