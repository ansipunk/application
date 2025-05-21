FROM python:3.13

WORKDIR /app

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y postgresql-client

COPY pyproject.toml .
COPY alembic.ini .
COPY Makefile .
COPY application/ application/
COPY scripts/ scripts/

RUN make bootstrap

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["make", "-C", "/app", "serve"]
