home_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
git clone git://github.com/yyuu/pyenv.git .pyenv
git clone git://github.com/yyuu/pyenv-virtualenv.git ./.pyenv/plugins/pyenv-virtualenv
export PYENV_ROOT="$home_dir/.pyenv"
export PATH="$home_dir/.pyenv/bin:$PATH"
PYTHON_VERSION=2.7.6
eval "$(pyenv init -)"
pyenv install $PYTHON_VERSION
pyenv global $PYTHON_VERSION
pyenv rehash
if [[ -z $packaging ]]; then
	pyenv virtualenv $PYTHON_VERSION project_env
	pyenv shell project_env
	if [[ -z $docker ]]; then
	    cat requirements | awk '{system("pip install " $1);}'
	fi
else
	pip install virtualenv
	virtualenv .
	source bin/activate
	cat requirements | awk '{system("pip install " $1);}'
	virtualenv --relocatable .
fi
