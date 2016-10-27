FROM centos:latest

RUN yum -y install git

RUN yum -y groupinstall "Development tools"

RUN yum -y install readline-devel

RUN yum -y install zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel
RUN yum -y install freetype-devel
RUN yum -y install libpng-devel
RUN yum -y install libffi-devel
RUN yum -y install postgresql-devel

RUN useradd --create-home --home-dir /home/chorus --shell /bin/bash chorus

USER chorus
ENV HOME=/home/chorus
ENV SHELL=/bin/bash

WORKDIR /home/chorus/
RUN mkdir -p /home/chorus/ChorusCommander
ADD setup_env.sh /home/chorus/ChorusCommander/setup_env.sh
WORKDIR /home/chorus/ChorusCommander
RUN source ./setup_env.sh
ADD notebook_requirements /home/chorus/ChorusCommander/requirements
ADD pyenv_paths.sh /home/chorus/ChorusCommander/pyenv_paths.sh
RUN source ./pyenv_paths.sh && cat requirements | awk '{system("pip install " $1);}'
RUN mkdir -p /home/chorus/ChorusCommander/commander_lib
ADD commander_lib /home/chorus/ChorusCommander/commander_lib
ADD chorus_notebook.js /home/chorus/ChorusCommander/chorus_notebook.js
ADD chorus_notebook_config.py /home/chorus/ChorusCommander/chorus_notebook_config.py
RUN ln -sf /home/chorus/ChorusCommander/commander_lib .pyenv/versions/project_env/lib/python2.7/commander_lib

USER root
RUN chown -R chorus:chorus /home/chorus/ChorusCommander
USER chorus
ENV USER=chorus
CMD source ./pyenv_paths.sh && echo $CHORUS_ADDRESS && jupyter notebook --config=chorus_notebook_config.py

