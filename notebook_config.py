import os

master_address = os.getenv("MASTER_ADDRESS", "http://127.0.0.1:8080")
container_port = os.getenv("CONTAINER_PORT", "8888")

print container_port
c = get_config()

c.NotebookApp.open_browser = False
c.NotebookApp.tornado_settings = {
        'headers': {
                    'Content-Security-Policy': 'frame-ancestors ' + "*" #,
                    #'X-Frame-Options': 'ALLOW-FROM ' + "*"
                }
}
#c.NotebookApp.base_url = '/nb_proxy/%s/' % container_port
c.NotebookApp.allow_origin = master_address
c.NotebookApp.log_level = 'INFO'
c.NotebookApp.ip="*"
c.NotebookApp.notebook_dir = os.getenv("NOTEBOOK_DIR", "./")
if os.getenv("CERTFILE", None) is not None and os.getenv("KEYFILE", None) is not None:
    c.NotebookApp.certfile = os.getenv("CERTFILE")
    c.NotebookApp.keyfile = os.getenv("KEYFILE")

import notebook.nbextensions
notebook.nbextensions.install_nbextension('./notebook.js', user=True, overwrite=True)

from notebook.services.config import ConfigManager
js_cm = ConfigManager()
js_cm.update('notebook', {"load_extensions": {'notebook': True}})
#js_cm.update('notebook', {"load_extensions": {'chorus_notebook/notebook': True}})
#js_cm.update('tree', {"load_extensions": {'chorus_notebook/dashboard': True}})
#js_cm.update('edit', {"load_extensions": {'chorus_notebook/editor': True}})
