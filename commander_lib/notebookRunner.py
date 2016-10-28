# -*- coding: utf-8 -*-
from Log import logger
import os
import random
from tools import shell
import requests

BASE_PORT = 10000
MAX_PORT = 20000

docker_mutiple_options = ["-e", "--env", "-v", "--volumn", "-p", "--port"]


def run_docker_image(port, image_name, username, command="jupyter notebook --config=chorus_notebook_config.py",
                     **kargs):
    options = ""
    for key, value in kargs.iteritems():
        if key in docker_mutiple_options:
            for item in value:
                options += key + "=" + item + " "
        else:
            options += key + "=" + value + " "
    command = "/bin/sh -c \"source ./pyenv_paths.sh && export CONTAINER_PORT=%d && %s\"" % (port, command)
    ret, stdout, stderr = shell(
        "docker run --name %s -d -p %d:8888 %s %s %s" % (username, port, options, image_name, command))
    if not ret == 0:
        raise Exception(stderr)
    container_name = username

    return (container_name, port)


def start_docker_container(container_name):
    ret, stdout, stderr = shell("docker start %s" % container_name)
    if not ret == 0:
        raise Exception(stderr)
    return stdout


def stop_docker_container(container_id):
    ret, stdout, stderr = shell("docker rm -f %s" % container_id)
    if not ret == 0:
        raise Exception(stderr)
    return stdout


def stop_docker_container_without_active_kernels(container_id, docker_host, enable_ssl):
    try:
        if len(get_list_of_active_kernels(container_id, docker_host, enable_ssl)) > 0:
            return
    except Exception as e:
        logger.debug(e)
        return

    return stop_docker_container(container_id)


def stop_all_docker_container(prefix):
    ret, stdout, stderr = shell("docker rm -f $(docker ps -qf name=%s)" % prefix)
    if not ret == 0:
        raise Exception(stderr)
    return stdout


def get_docker_exposed_port(container_name):
    ret, stdout, stderr = shell("docker port %s" % container_name)
    if not ret == 0:
        raise Exception(stderr)
    return int(stdout.split(":")[1])


def run_notebook_in_docker(image_name, username, **kargs):
    port = random.randint(BASE_PORT, MAX_PORT)
    while True:
        try:
            stop_docker_container(username)
        except:
            pass
        try:
            container_name, port = run_docker_image(port, image_name, username, **kargs)
        except Exception as e:
            if "port is already allocated" in str(e) or "address already in use" in str(e):
                port += 1
                continue
            else:
                raise e
        break
    return (container_name, port)


def get_list_of_notebooks(prefix, pattern="{{.Name}}: {{.Created}}"):
    ret, stdout, stderr = shell("docker ps -qf name=%s" % prefix)
    if not ret == 0:
        raise Exception(stderr)
    if stdout.strip() == "":
        return []
    ret, stdout, stderr = shell("docker inspect -f \"%s\" $(docker ps -qf name=%s)" % (pattern, prefix))

    return map(lambda x: x.strip().split(": "), stdout.strip().split("\n"))


def get_list_of_notebook_names(prefix):
    nbs = get_list_of_notebooks(prefix)
    return map(lambda x: x[0].lstrip("/"), nbs)


def get_list_of_active_kernels(container_id, docker_host, enable_ssl):
    container_port = get_docker_exposed_port(container_id)
    protocol = "https://" if enable_ssl else "http://"
    uri = protocol + docker_host + ":" + str(container_port) + "/nb_proxy/" + str(
        container_port) + "/api/kernels"
    logger.debug(uri)
    try:
        response = requests.get(uri, verify=False, timeout=5)
        logger.debug(response.content)
        if response.status_code not in range(200, 300):
            raise Exception(response.content)
    except requests.exceptions.Timeout as ce:
        logger.debug(ce)
        return []
    except Exception as e:
        raise Exception(e)
    return response.json()

if __name__ == "__main__":
    container_id, port = run_notebook_in_docker("http://10.0.0.28:8080", "alpinedata/chorus_commander", "hao5")
    print port
    stop_docker_container(container_id)
    container_id, port = run_notebook_in_docker("http://10.0.0.28:8080", "alpinedata/chorus_commander", "hao6")
    print port
    stop_docker_container(container_id)
