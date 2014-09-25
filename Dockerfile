FROM ubuntu:14.04
MAINTAINER Alex Lubbock <alex.lubbock@ed.ac.uk>

RUN apt-get update
RUN apt-get install -y python python-dev python-pip wget libblas-dev liblapack-dev gfortran libsuitesparse-dev git swig python-numpy python-scipy python-networkx python-decorator python-jinja2 python-pyparsing python-markupsafe

RUN git clone https://github.com/stefanv/umfpack.git
RUN cd umfpack && sudo python setup.py install && cd ..

RUN wget ftp://ftp.ncbi.nlm.nih.gov/pub/qmbpmn/qmbpmn-tools/src/qmbpmn-tools-1.5.3.tar.gz
RUN tar xzf qmbpmn-tools-1.5.3.tar.gz
RUN cd qmbpmn-tools-1.5.3/ && python setup.py install && cd ..

RUN rm -rf master.zip umfpack qmbpmn-tools-1.5.3.tar.gz qmbpmn-tools-1.5.3

RUN git clone https://github.com/alubbock/itmprobe-wrapper.git infflow

WORKDIR /infflow
