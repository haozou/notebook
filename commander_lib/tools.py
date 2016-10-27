from Log import logger
import subprocess
import os
def shell(command):
    logger.debug(command)
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stdout:
        logger.debug(stdout)
    if stderr:
        logger.debug(stderr)
    return p.returncode, stdout, stderr
