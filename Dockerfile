FROM resin/rpi-raspbian
USER root

RUN apt-get update && \
    apt-get -qy install ca-certificates python python-pip sqlite3 && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get -qy clean all

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code
WORKDIR /code

ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

RUN mkdir -p /code/static

# Collect our static media.
RUN /code/manage.py collectstatic --noinput

RUN /code/manage.py makemigrations
RUN /code/manage.py migrate --run-syncdb

# Run the container.
CMD ["/code/misc/prod_run.sh"]