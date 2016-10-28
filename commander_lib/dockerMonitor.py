from threading import Thread
import time
import notebookRunner as cnr
from datetime import datetime
from dateutil import parser
from Log import logger
import requests


class DockerMonitor(Thread):
    def __init__(self, prefix, delay=600, timeout=3600 * 24, docker_host="localhost", enable_ssl=False):
        """

        Parameters
        ----------
        prefix
        delay
        timeout
        docker_host
        enable_ssl
        """
        Thread.__init__(self, name="docker-moniter-thread")
        self.prefix = prefix
        self.delay = delay
        self.timeout = timeout
        self.docker_host = docker_host
        self.enable_ssl = enable_ssl

    def run(self):

        while True:
            try:
                notebooks = cnr.get_list_of_notebooks(self.prefix)
                logger.debug(notebooks)
                for container_name, container_created_time in notebooks:
                    container_name = container_name.lstrip("/")
                    container_created_time = parser.parse(container_created_time, fuzzy=True)
                    now = datetime.now(tz=container_created_time.tzinfo)
                    running_time = (now - container_created_time).total_seconds()
                    logger.debug(container_name + ", " + str(container_created_time) + ", " + str(running_time))
                    if running_time > self.timeout:
                        try:
                            if len(cnr.get_list_of_active_kernels(container_name, self.docker_host, self.enable_ssl)) is 0:
                                logger.debug("stopping " + container_name)
                                cnr.stop_docker_container(container_name)
                        except Exception as e:
                            logger.debug(e.message)
            except Exception as e:
                logger.debug(e.message)
            finally:
                time.sleep(self.delay)
