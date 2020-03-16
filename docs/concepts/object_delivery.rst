*****************
Object delivery
*****************

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml

   hide user
   hide oidcprovider
   hide acentities
   hide objinf
   hide obligations
   hide environment

Reverse proxies should be transparent to the user, i.e. in the best case
an user cannot tell if he is connected to a proxy or to the real service.
If the access was granted, we therefore connect to the service using the same HTTP method
and passing all request headers and body from the user.
Since authorization was already done by the proxy, we remove the authorization
header and as the proxy should use few memory ressources we do not
support the HTTP 'keep-alive' option, i.e.. we close the connection after every
request.
To establish secure connections between the service and proxy we support two options:
Bearer Tokens and TLS client certificates.
The bearer token is used in the `authorization` header and the TLS client certificate
is used during opening the TCP connection to the service.
