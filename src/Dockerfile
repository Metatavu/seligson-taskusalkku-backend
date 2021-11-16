
FROM python:3.9.4-alpine AS base


WORKDIR /usr/src/app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt /usr/src/app/requirements.txt


RUN set -eux \
    && apk add --no-cache mariadb-connector-c-dev \
    && apk add --no-cache --virtual .build-deps build-base \
        libressl-dev libffi-dev gcc musl-dev python3-dev \
    && apk add curl \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /usr/src/app/requirements.txt \
    && rm -rf /root/.cache/pip


FROM base AS development
COPY ./requirements-dev.txt /usr/src/app/requirements-dev.txt
RUN set -eux \
    && pip install -r /usr/src/app/requirements-dev.txt \
    && rm -rf /root/.cache/pip
COPY . /usr/src/app/
HEALTHCHECK CMD curl --fail http://127.0.0.1:8000/v1/system/ping || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


FROM base AS test
COPY ./requirements-dev.txt /usr/src/app/requirements-dev.txt
RUN set -eux \
    && pip install -r /usr/src/app/requirements-dev.txt \
    && rm -rf /root/.cache/pip
COPY . /usr/src/app/
CMD ["pytest"]


FROM base AS production
COPY . /usr/src/app/
HEALTHCHECK CMD curl --fail http://127.0.0.1:8000/v1/system/ping || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



