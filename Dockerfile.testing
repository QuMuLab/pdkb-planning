
FROM ubuntu:18.04

#maintainer information
LABEL maintainer="Christian Muise (christian.muise@queensu.ca)"

# update the apt package manager
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get update && apt-get -y install locales

# install common packages
RUN apt-get install -y \
        build-essential \
        vim \
        git \
        bison \
        flex \
        bc

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y expect

# install python and related
RUN apt-get install -y python3 python3-dev python3-pip python3-venv
RUN pip3 install --upgrade pip
RUN yes | pip3 install numpy
RUN yes | pip3 install matplotlib
RUN yes | pip3 install scipy

# Get the PDKB library
RUN mkdir /MEP
WORKDIR /MEP
RUN git clone https://github.com/QuMuLab/pdkb-planning.git
WORKDIR /MEP/pdkb-planning
RUN chmod 777 pdkb/planners/*
RUN python3 setup.py install

# Get the MEPK library
RUN git clone https://github.com/sysulic/MEPK.git /MEP/MEPK
WORKDIR /MEP/MEPK/src
RUN make


WORKDIR /MEP

# default command to execute when container starts
CMD /bin/bash
