FROM python:3.6

# Do everything relative to /usr/src/app which is where we install our
# application.
WORKDIR /usr/src/app

# Copy entrypoint script
ADD ./compose/start-devserver.sh /tmp/

# Install any explicit requirements
ADD ./requirements*.txt ./
RUN pip install -r ./requirements_developer.txt

# The webapp source will be mounted here as a volume
VOLUME /usr/src/app

# By default, use the Django development server to serve the application and use
# developer-specific settings.
#
# *DO NOT DEPLOY THIS TO PRODUCTION*
ENV DJANGO_SETTINGS_MODULE lookupproxy.settings_developer
ENTRYPOINT ["/tmp/start-devserver.sh"]
