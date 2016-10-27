import chorusNotebookRunner as cnr
import os
from functools import wraps
from Log import logger
from flask import Flask, jsonify, request, abort
from tools import shell

docker_container_name_prefix = "chorus_notebook.tmp."
app = Flask(__name__)


def require_api_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        if request.args.get("session_id", None) == app.config.get("SECRET_KEY"):
            return jsonify({"error": "Access denied"}), 403
        return func(*args, **kwargs)

    return check_token


@app.route('/api/v1.0/get_container_for_user', methods=['GET'])
def get_container_for_user():
    username = request.args.get("username")
    if username == None:
        return jsonify({"error": "username cannot be None"}), 403
    logger.debug("username: " + username)

    running_containers = cnr.get_list_of_notebook_names(docker_container_name_prefix)
    logger.debug(running_containers)

    if (docker_container_name_prefix + username) in running_containers:
        container_name = docker_container_name_prefix + username
        port = cnr.get_docker_exposed_port(container_name)

        return jsonify({
            "running": True,
            "container_name": container_name,
            "port": port
        })
    else:
        return jsonify({
            "running": False
        })


@app.route('/api/v1.0/run_notebook_in_docker', methods=['POST'])
def run_notebook_in_docker():
    logger.debug(request.form.to_dict())
    username = request.form.get("username")
    if username == None:
        return jsonify({"error": "username cannot be None"}), 403
    logger.debug("username: " + username)

    chorus_address = request.form.get("chorus_address", "http://localhost:8080")
    if chorus_address == None:
        return jsonify({"error": "chorus_address cannot be None"}), 403
    logger.debug("chorus_address: " + chorus_address)

    image_name = request.form.get("image_name", "alpinedata/chorus_commander")
    if image_name == None:
        return jsonify({"error": "image_name cannot be None"}), 403
    logger.debug("image_name: " + image_name)

    command = request.form.get("command",
                               app.config.get("COMMAND", "jupyter notebook --config=chorus_notebook_config.py"))
    logger.debug("command: " + command)

    options = {}
    options["-e"] = ["CHORUS_ADDRESS=%s" % chorus_address, "PYTHONWARNINGS=\"ignore:Unverified HTTPS request\""]
    options["-v"] = []
    if chorus_address.startswith("https") and app.config.get("CERTFILE", "") is not "" and app.config.get("KEYFILE",
                                                                                                          "") is not "":
        with open(app.config.get("CERTFILE", "")) as f:
            cert = ""
            for line in f:
                cert += line.strip() + "\\n"
        with open(app.config.get("KEYFILE", "")) as f:
            key = ""
            for line in f:
                key += line.strip() + "\\n"

        options["-e"].append("CERTFILE=certfile")
        options["-e"].append("KEYFILE=keyfile")
        command = ("echo -e \'%s\' > certfile && echo -e \'%s\' > keyfile && " % (cert, key)) + command


    if app.config.get("MEM_LIMIT_PER_CONTAINER", "512m") is not "":
        options["--memory"] = app.config.get("MEM_LIMIT_PER_CONTAINER", "512m")
    if app.config.get("CPUSET_CPUS", "") is not "":
        options["--cpuset-cpus"] = app.config.get("CPUSET_CPUS", "")
    if app.config.get("NOTEBOOK_DATA_DIR", "") is not "":
        mounted_path = os.path.abspath(
            os.path.join(app.config.get("NOTEBOOK_DATA_DIR", ""), docker_container_name_prefix + username))
        shell("mkdir -p %s && chmod -R 777 %s" % (mounted_path, mounted_path))
        docker_path = "/home/chorus/ChorusCommander/" + docker_container_name_prefix + username
        options["-v"].append(mounted_path + ":" + docker_path)
        options["-e"].append("NOTEBOOK_DIR=%s" % docker_path)
    if app.config.get("ENV", "") is not "":
        for env in app.config.get("ENV", "").split(","):
            options["-e"].append("\"%s\"" % env)

    for key, value in request.form.to_dict().iteritems():
        if not key in ["username", "chorus_address", "image_name", "command", "session_id"]:
            if key in cnr.docker_mutiple_options:
                if options.has_key(key):
                    options[key].append(value)
                else:
                    options[key] = [value]
            else:
                options[key] = value

    logger.debug(options)
    try:
        max_concurrent_users = app.config.get("MAX_CONCURRENT_USERS", 100)
        running_containers = cnr.get_list_of_notebook_names(docker_container_name_prefix)
        logger.debug(running_containers)

        if (docker_container_name_prefix + username) in running_containers:
            container_name = docker_container_name_prefix + username
            port = cnr.get_docker_exposed_port(container_name)
        else:
            if len(running_containers) + 1 > max_concurrent_users:
                return jsonify({"error": "exceed the docker containers limitation %s" % max_concurrent_users}), 403

            container_name, port = cnr.run_notebook_in_docker(image_name,
                                                              docker_container_name_prefix + username,
                                                              command=command,
                                                              **options)
    except Exception as e:
        logger.debug(e)
        return jsonify({"error": "%s" % e}), 403

    response = {
        "container_name": container_name,
        "port": port
    }
    return jsonify(response), 201


@app.route('/api/v1.0/stop_notebook_docker_container', methods=['POST'])
def stop_notebook_docker_container():
    username = request.form.get("username")
    if username == None:
        return jsonify({"error": "username cannot be None"}), 403
    logger.debug("username: " + username)

    try:
        container_name = cnr.stop_docker_container_without_active_kernels(docker_container_name_prefix + username,
                                                                          app.config.get("DOCKER_HOST",
                                                                                         app.config.get('HOST',
                                                                                                        "0.0.0.0")),
                                                                          app.config.get("CERTFILE",
                                                                                         "") is not "" and app.config.get(
                                                                              "KEYFILE", "") is not ""
                                                                          )
    except Exception as e:
        logger.debug(e)
        return jsonify({"error": "%s" % e}), 403

    response = {"container_name": container_name}
    return jsonify(response), 202


@app.route('/api/v1.0/stop_all_notebook_docker_container', methods=['POST'])
def stop_all_notebook_docker_container():
    prefix = request.args.get("prefix", docker_container_name_prefix)
    if prefix == None:
        return jsonify({"error": "prefix cannot be None"}), 403
    logger.debug("prefix: " + prefix)
    try:
        container_name = cnr.stop_all_docker_container(docker_container_name_prefix)
    except Exception as e:
        logger.debug(e)
        return jsonify({"error": "%s" % e}), 403
    response = {"container_name": container_name}
    return jsonify(response), 202

@app.route('/api/v1.0/uploads', methods=['POST'])
def uploads():
    target_dir = request.args.get("target_dir", None)
    if target_dir == None:
        return jsonify({"error": "target_dir cannot be None"}), 403
    logger.debug("target_dir: " + target_dir)
    ret, stdout, stderr = shell("mkdir -p %s" % target_dir)
    if ret is not 0:
        raise Exception(stderr)
    file = request.files['file']
    file.save(os.path.join(target_dir, file.filename))
    response = {file.filename: "uploaded"}
    return jsonify(response), 201

if __name__ == "__main__":
    app.config.from_pyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_settings.cfg"))
    if os.path.exists(os.path.join(os.getenv("CHORUS_NOTEBOOK_HOME", "."), 'settings.cfg')):
        app.config.from_pyfile(os.path.join(os.getenv("CHORUS_NOTEBOOK_HOME", "."), 'settings.cfg'))
    with open(os.path.join(os.getenv("CHORUS_NOTEBOOK_HOME", "."), '.notebook.port'), 'w') as f:
        f.write(str(app.config.get('PORT', 8000)))
    if app.config.get("ENABLE_MONITOR", False):
        from dockerMonitor import DockerMonitor

        dockerMonitor = DockerMonitor(docker_container_name_prefix,
                                      app.config.get("MONITOR_DELAY", 60 * 60),
                                      app.config.get("NOTEBOOK_CONTAINER_TIMEOUT", 3600 * 24),
                                      app.config.get("DOCKER_HOST", app.config.get('HOST', "0.0.0.0")),
                                      app.config.get("CERTFILE", "") is not "" and app.config.get("KEYFILE", "") is not "")
        dockerMonitor.daemon = True
        dockerMonitor.start()

    app.run(host=app.config.get('HOST', "0.0.0.0"), port=app.config.get('PORT', 8000))
