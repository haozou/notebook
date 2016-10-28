Notebook
======
 
the IPython notebook web service

Prerequisites:
=====
Docker need to be installed on both dev and production machine and you need to pull the zh331873541/notebook docker image after intalling docker.

On dev machine:

If you are using mac. Follow the instruction on https://docs.docker.com/engine/installation/mac/ to install docker.
Then run the command: docker pull zh331873541/notebook to pull the image.

On production machine:

1. curl -fsSL https://get.docker.com/ | sh.

2. sudo usermod -aG docker ${user}.

3. sudo /etc/init.d/docker start.

4. su - ${user} and docker pull alpinedata/chorus_commander.


Dev Setup
=====

1. Run "source setup_env.sh" to setup a compatible python environment locally.

2. Run "source pyenv_paths.sh" to get into the correct python environment.

3. Run "./bin/start_notebook_server" to start service.

Production Setup
=====
Run "./packaging/make-package.sh" to build the production installer.
It will generate a chorus_notebook-${version}-${build_number}-${tag_hash}.sh installer.
Use this installer to install on production machine.
Currently, it only supports redhat and suse kernel.

After installation, run ./bin/start-notebook-server to start the service.







