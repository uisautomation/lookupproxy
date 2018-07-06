# Lookup Proxy API

[![Build
Status](https://travis-ci.org/uisautomation/lookupproxy.svg?branch=master)](https://travis-ci.org/uisautomation/lookupproxy)
[![codecov](https://codecov.io/gh/uisautomation/lookupproxy/branch/master/graph/badge.svg)](https://codecov.io/gh/uisautomation/lookupproxy)

This is a proxy API for the University of Cambridge Lookup service. It must be
hosted within the CUDN but may be used to provide access to the Lookup service
for clients outside of the CUDN.

Clients are authorised by means of an OAuth2 token with appropriate scope. See
[the documentation](https://uisautomation.github.io/lookupproxy) for further
details.

## Dockerfile

This application ships with a basic packaging using Docker. It makes use of
[gunicorn](http://gunicorn.org/) to serve the docker application and, via
[whitenoise](http://whitenoise.evans.io/en/stable/), to serve static files. The
container is configured to use lookupproxy.settings.docker by default as the
Django settings. In use you probably want to override this with a settings
module which includes at least the OAuth2 configuration and SECRET_KEY setting.

The following environment variables are mapped to the corresponding Django
settings:

* ``OAUTH2_TOKEN_URL``
* ``OAUTH2_INTROSPECT_URL``
* ``OAUTH2_CLIENT_ID``
* ``OAUTH2_CLIENT_SECRET``
* ``OAUTH2_INTROSPECT_SCOPES`` (scopes should be separated by spaces)
