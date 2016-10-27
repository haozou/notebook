#!/usr/bin/env bash
CHORUS_NOTEBOOK_VERSION=${CHORUS_NOTEBOOK_VERSION:-1.0.0.0}

function head_sha() {
	echo "$(git rev-parse --short=9 HEAD)"
}

function build_number() {
	if [ "${BUILD_NUMBER}" != "" ]; then
		echo "${BUILD_NUMBER}"
	else
		echo ""
	fi
}

function build_tag() {
	echo "chorus_notebook-${CHORUS_NOTEBOOK_VERSION}-$(build_number)-$(head_sha)"
}

function do_package() {
	GZIP='--fast' packaging/vendor/makeself/makeself.sh --follow --nox11 --nowait "${staging_dir}" "$(build_tag).sh" "Chorus Notebook installer $(build_tag)" ./scripts/install "$(build_tag)"
}

function clean() {
	rm -rf "packaging/staging"
}

function prepare() {
	export staging_dir="packaging/staging/$(build_tag)"
	rm -f chorus_commander-*.sh
	rm -f packaging.log
	rm -rf "packaging/staging"
	export packaging=true
	source setup_env.sh
	mkdir -p "${staging_dir}"

	if [[ $(ls chorus_commander_docker_image*.tar.gz 2> /dev/null | wc -l) != "0" ]]; then
		echo "packaging with notebook docker image"
		cp -rf chorus_commander_docker_image*.tar.gz ${staging_dir}
	fi

	cp -rf LICENSE ${staging_dir}
	cp -rf README.md ${staging_dir}
	cp -rf commander_lib ${staging_dir}
	cp -rf pyenv_paths.sh ${staging_dir}
	#cp -rf stop-notebook ${staging_dir}
	cp -rf chorus_notebook_config.py ${staging_dir}
	#cp -rf requirements ${staging_dir}
	#cp -rf setup_env.sh ${staging_dir}
	#cp -rf start-notebook ${staging_dir}
	cp -rf start-notebook-server ${staging_dir}
	cp -rf stop-notebook-server ${staging_dir}
	cp -rf ./packaging/scripts ${staging_dir}
	#cp -rf pip-selfcheck.json ${staging_dir}
	cp -r .pyenv/versions/2.7.6/lib/python2.7/* lib/python2.7/
	cp -rf lib ${staging_dir}
	cp -rf share ${staging_dir}
	cp -rf bin ${staging_dir}
	cp -rf include ${staging_dir}
	echo "$(build_tag)" > ${staging_dir}/version
	#cp -rf .pyenv ${staging_dir}
}

prepare
do_package
clean
