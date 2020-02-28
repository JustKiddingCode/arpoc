************
Obligations
************

.. uml::
   :scale: 40 %

   !include docs/overview.plantuml
   
   hide object
   hide user
   hide oidcprovider
   hide OIDC
   hide acentities
   hide objinf
   hide environment

Obligations are actions that must be executed successfully after the evaluation
of AC hierarchy. Every AC entity can specify a set of obligations which must
be executed if the target specifier of that entity was matched.
