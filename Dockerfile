FROM centos:latest

RUN yum -y install git

RUN yum -y groupinstall "Development tools"

RUN yum -y install readline-devel

RUN yum -y install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel
RUN yum -y install freetype-devel
RUN yum -y install libpng-devel
RUN yum -y install libffi-devel
RUN yum -y install postgresql-devel

RUN useradd --create-home --home-dir /home/notebook --shell /bin/bash notebook

USER notebook
ENV HOME=/home/notebook
ENV SHELL=/bin/bash

WORKDIR /home/chorus/
RUN mkdir -p /home/notebook/notebook
ENV docker true
ADD setup_env.sh /home/notebook/notebook/setup_env.sh
WORKDIR /home/notebook/notebook
RUN source ./setup_env.sh
ADD notebook_requirements /home/notebook/notebook/requirements
ADD pyenv_paths.sh /home/notebook/notebook/pyenv_paths.sh
RUN source ./pyenv_paths.sh && cat requirements | awk '{system("pip install " $1);}'
RUN mkdir -p /home/notebook/notebook/commander_lib
ADD commander_lib /home/notebook/notebook/commander_lib
ADD notebook.js /home/notebook/notebook/notebook.js
ADD notebook_config.py /home/notebook/notebook/notebook_config.py
RUN ln -sf /home/notebook/notebook/commander_lib .pyenv/versions/project_env/lib/python2.7/commander_lib

USER root
RUN chown -R notebook:notebook /home/notebook/notebook
USER notebook
ENV USER=notebook
CMD source ./pyenv_paths.sh && echo $MASTER_ADDRESS && jupyter notebook --config=notebook_config.py

