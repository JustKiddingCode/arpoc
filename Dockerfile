FROM debian:stable

#
RUN apt-get update && apt-get install -y ca-certificates runit python3-pip python3-coverage python3-pytest
#RUN pip3 install oic # will also install requests
ADD ./  /opt/python-oidc
WORKDIR /opt/python-oidc
RUN pip3 install -r requirements.txt
# Copy

COPY certs/CA.pem /tmp/own-ca.pem
RUN cat /tmp/own-ca.pem >> /etc/ssl/certs/ca-certificates.crt && rm /tmp/own-ca.pem

COPY certs/cert.crt /etc/ssl/private/
COPY certs/key.pem /etc/ssl/private/

RUN echo "export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt" >> /etc/bash.bashrc

# Entrypoints
ENTRYPOINT ["/usr/bin/runsvdir", "/etc/sv"]
