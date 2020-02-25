Configuration file
============================

The configuration file is a yaml file with four sections: 

#. openid_providers
#. proxy
#. services
#. access_control

openid_providers
----------------

Here you can specify each provider you want to support.
Each provider is a key under openid_providers and you must
submit the `configuration_url` and either `registration_token` and `registration_url`
or an `configuration_token`. With an `configuration_token` the client registers
as a new OpenID Connect Client, with a `registration_token` the client
access the registration data from the OpenID Connect Registration Endpoint.

.. literalinclude:: /docs/gen/sample_config.yml
   :linenos:
   :lineno-start: 10
   :language: yaml
   :lines: 10-17

proxy
-----

OpenID Connect requires the use of TLS. Therefore you need
an keyfile with the private key and a certificate file with
the TLS Certificate.
Under `contacts` you must submit a valid e-mail adress that will be used
during the registration with the OpenID Connect Providers
The `secrets` file is used to store the client secrets of the OpenID Connect
protocol.

.. literalinclude:: /docs/gen/sample_config.yml
   :linenos:
   :lineno-start: 12
   :language: yaml
   :lines: 18-35

services
--------

Each service (i.e. an URL that is accessible through a subfolder on the proxy)
must be listed here. You can specify authentication settings like
a client certificate that the proxy will use with every connection to the
service or a bearer token, that the proxy will use in the 'Authentication' field.
The `AC` key must specify a valid policy set that will evaluated on every access.

.. literalinclude:: /docs/gen/sample_config.yml
   :linenos:
   :lineno-start: 36
   :language: yaml
   :lines: 36-43

access_control
--------------

Here you can specify the list of directories where the proxy will load access
control entities.

.. literalinclude:: /docs/gen/sample_config.yml
   :linenos:
   :lineno-start: 1
   :language: yaml
   :lines: 1-3

misc
--------------

Other config option that hadn't fit into the other sections

.. literalinclude:: /docs/gen/sample_config.yml
   :linenos:
   :lineno-start: 1
   :language: yaml
   :lines: 4-9
