Interface (Policy Enforcement Point)
====================================

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   hide acentities
   hide object
   hide obligations
   hide objinf
   hide environment


We provide an interface to command line clients and webbrowsers.


Command line clients
********************

Command line clients cannot be redirected to the openid provider to ask for an
authorization. We enable the clients to supply an openid access token and we
use this access token to talk to the openid providers to receive the user
information.
The token can be supplied using the `Authorization` header as bearer token,
e.g. adding the HTTP header line `Authorization: bearer abcdef` for the access token `abcdef`.
If the access token is no JWT, the client must also supply the issuer, using
the `x-oidcproxy-issuer` HTTP header.
If the issuer is `https://openid.example.com/realms/master` then the header
`x-oidcproxy-issuer: https://openid.example.com/realms/master` must be added.
From there there, command line clients are treated the same way as webbrowsers.

Webbrowsers
***********

If the user tries to access a service which requires authorization, at least
one subject attribute will be missing. He is then asked to choose one of 
the provided openid providers and redirected to the provider to perform the login.
The openid provider redirects the user back to our proxy with an authorization code
which we use to receive an access token and an id token.

