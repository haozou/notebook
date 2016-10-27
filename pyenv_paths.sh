export CHORUS_NOTEBOOK_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ ! -f "$CHORUS_NOTEBOOK_HOME/.production" ]]; then
	export PATH="$CHORUS_NOTEBOOK_HOME/.pyenv/bin:$PATH"
	export PYENV_ROOT="$CHORUS_NOTEBOOK_HOME/.pyenv"
	eval "$(pyenv init -)"
	pyenv shell project_env
else
	export PATH="$CHORUS_NOTEBOOK_HOME/chorus_notebook-current/bin:$PATH"
fi

