FROM uisautomation/django:2.0-py3.6
RUN apk add --no-cache bash

WORKDIR /usr/src/app

ADD ./requirements*.txt /usr/src/app/
RUN pip install -r ./requirements_docker.txt

ADD ./ /usr/src/app/

ENV DJANGO_SETTINGS_MODULE=lookupproxy.settings.docker
ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
