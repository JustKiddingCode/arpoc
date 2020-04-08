Objects
====================================

.. uml::
   :scale: 40 %

   !include overview.plantuml


   hide OIDC
   hide oidcprovider
   hide user
   hide acentities
   hide obligations
   hide objinf
   hide environment


The purpose of a reverse proxy is to deliver websites that are available to
him using HTTP. These objects are referenced to by their URL.
The administrator of a reverse proxy decides on the path where the resource
will be available.
In some cases it might be necessary to provide some internal information to the user,
which cannot be done by proxying webpages.
For example the user might want to know about the data the reverse proxy 
knows about him, or to give information about the internal data like the ac entities
to users.
For this included webservices we use so-called "special pages".
A special page is protected like a normal webpage, but the content is generated
by the proxy itself. Special pages are referenced to by a string, which is not an URL,
e.g. "userinfo"
for information about the user and bound into the path tree like normal webpages,
i.e. the administrator can decide on the path where this special page will be
available.
