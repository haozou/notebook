import os, sys, getpass
import logging
log_path = os.path.join(os.path.expanduser("~"), "notebook.log")
def getLogger(name=getpass.getuser()):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    #create console handler and set level to info
    formatter = logging.Formatter("%(levelname)s : %(message)s")
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.INFO)
    consolehandler.setFormatter(formatter)
    logger.addHandler(consolehandler)

    #create file handler and set level to debug
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s:%(lineno)s - %(levelname)s : %(message)s')
    fileHandler = logging.FileHandler(log_path)
    fileHandler.setLevel(level=logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    os.chmod(log_path, 0777)
    return logger

logger = getLogger()