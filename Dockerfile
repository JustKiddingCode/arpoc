FROM debian:stable

#
RUN apt-get update && apt-get install -y ca-certificates runit python3-pip
#RUN pip3 install oic # will also install requests
ADD python-oidc/  /opt/python-oidc
WORKDIR /opt/python-oidc
RUN pip3 install -r requirements.txt
# Copy

COPY certs/CA/CA.pem /tmp/own-ca.pem
RUN cat /tmp/own-ca.pem >> /etc/ssl/certs/ca-certificates.crt && rm /tmp/own-ca.pem

COPY certs/certs/python-proxy.example.com.crt /etc/ssl/private/
COPY certs/keys/python-proxy.example.com.key /etc/ssl/private/

RUN echo "export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt" >> /etc/bash.bashrc

# Entrypoints
ENTRYPOINT ["/usr/bin/runsvdir", "/etc/sv"]
