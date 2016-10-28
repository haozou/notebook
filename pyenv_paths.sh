export NOTEBOOK_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ ! -f "$NOTEBOOK_HOME/.production" ]]; then
	export PATH="$NOTEBOOK_HOME/.pyenv/bin:$PATH"
	export PYENV_ROOT="$NOTEBOOK_HOME/.pyenv"
	eval "$(pyenv init -)"
	pyenv shell project_env
else
	export PATH="$NOTEBOOK_HOME/notebook-current/bin:$PATH"
fi

