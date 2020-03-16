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

The user can access our reverse proxy using a HTTP client.
We distinguish here between the use intended for non-interactive
command line clients (e.g. curl) and
interactive webbrowsers (e.g. Mozilla Firefox, Google Chrome, Lynx).
However, if the webbrowser gives the user the possibility to add or edit HTTP request
headers, it can be used as if it was a comman line client.

Webbrowsers
***********

Webbrowsers allow the user to interact with the services via keyboard or mouse
input (e.g. clicking on a link), so missing information can be asked when needed.
If the not logged-in user tries to access a service which requires authorization, 
at least one subject attribute will be marked as missing in the process of 
access control evaluation.
Then the needed scopes are calculated and the user gets redirected to the
openid connect provider, or if there are more than one provider allowed, he can
choose in a list of the supported openid connect provider.
The openid provider redirects the user back to our proxy with an authorization code
which we use to receive an access token and an id token.


Command line clients
********************

Command line clients should not be redirected to the openid provider to ask for an
authorization. Instead, the client should be able to supply all information
beforehand.
In the case of openid connect this is an access token. The access token can
then be used to get the user information from the userinfo endpoint.
The token can be supplied using the `Authorization` header as bearer token,
e.g. adding the HTTP header line `Authorization: bearer abcdef` for the access token `abcdef`.
If the access token is a JWT, the data gets unpacked and the issuer field `iss`
is used to connect to the openid provider.
If the access token is no JWT, the client must also supply the issuer, using
the `x-oidcproxy-issuer` HTTP header.
If the issuer is `https://openid.example.com/realms/master` then the header
`x-oidcproxy-issuer: https://openid.example.com/realms/master` must be added.
From there on command line clients are treated the same way as webbrowsers.

