FROM ubuntu:trusty
MAINTAINER Daniel Salinas <imsplitbit@gmail.com>

# Install necessary packages
ENV DEBIAN_FRONTEND noninteractive
RUN echo "force-unsafe-io" > /etc/dpkg/dpkg.cfg.d/02apt-speedup &&\
    echo "Acquire::http {No-Cache=True;};" > /etc/apt/apt.conf.d/no-cache
RUN apt-get update
RUN apt-get install -y python-pip python-dev build-essential

RUN mkdir /opt/app
ADD . /opt/app/
RUN pip install -r /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements-test.txt

EXPOSE 5000
WORKDIR /opt/app
CMD sudo ./app.py