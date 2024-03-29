FROM python:3.9.4-alpine AS base


WORKDIR /usr/src/app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /usr/src/app/requirements.txt

RUN set -eux \
    && apk add --no-cache mariadb-connector-c-dev freetds-dev curl \
    && apk add --no-cache --virtual .build-deps build-base libressl-dev libffi-dev gcc musl-dev python3-dev

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /usr/src/app/requirements.txt
RUN rm -rf /root/.cache/pip

FROM base AS development
COPY ./requirements-dev.txt /usr/src/app/requirements-dev.txt
RUN set -eux \
    && pip install -r /usr/src/app/requirements-dev.txt \
    && rm -rf /root/.cache/pip
COPY . /usr/src/app/
RUN chmod a+x /usr/src/app/docker/entrypoint.sh
CMD ["/usr/src/app/docker/entrypoint.sh"]


FROM base AS production
COPY . /usr/src/app/
RUN chmod a+x /usr/src/app/docker/entrypoint.sh
HEALTHCHECK --start-period=5s --interval=30s --timeout=5s CMD curl -f http://localhost:8000/v1/system/ping || exit 1
CMD ["/usr/src/app/docker/entrypoint.sh"]


FROM base AS command
COPY . /usr/src/app/