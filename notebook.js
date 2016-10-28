define(function() {
    var CHORUS = {
        notebookSaved: function(e) {
            parent.postMessage({action: 'notebook_saved'}, '*');
        },

        notebookSaveVersion: function() {
            parent.postMessage({action: 'notebook_new_version'}, '*');
        },

        showDatasetChooser: function() {
            parent.postMessage({action: 'open_chooser'}, '*');
        },

        setDirty: function(e) {
            parent.postMessage({action: 'is_dirty'}, '*');
        },

        initializeNotebook: function() {
            parent.postMessage({action: 'initialize_notebook'}, '*');
        },

        closeNotebook: function() {
            if (IPython.notebook.kernel_busy === true) {
                if (!confirm('Kernel is busy. Are you sure you want to close the notebook?')) {
                    return;
                }
            }

            var close_window = function () {
                parent.postMessage({action: 'close_notebook'}, '*');
            };

            // finish with close on success or failure
            IPython.notebook.session.delete(close_window, close_window);
        }
    };

    CHORUS.EVENT_HANDLERS = {};

    // Handler for when chorus provides session initialization info.
    CHORUS.EVENT_HANDLERS['session'] = function(response) {
        CHORUS.sessionId = response.data.sessionId;
        CHORUS.chorusAddress = response.data.chorusAddress;

        if (IPython.notebook.kernel.is_connected()) {
            console.log("Initializing ipython kernel with Chorus variables...");
            var kernel_init_commands = [
                "CHORUS_SESSION_ID = '" + CHORUS.sessionId + "'",
                "CHORUS_ADDRESS = '" + CHORUS.chorusAddress + "'",
                "from commander_lib.ChorusCommander import ChorusCommander",
                "cc = ChorusCommander(CHORUS_SESSION_ID, \"\")"
            ];

            for (var i in kernel_init_commands) {
                console.log("Evaluated: " + kernel_init_commands[i]);
                IPython.notebook.kernel.execute(kernel_init_commands[i], {}, {silent:false});
            }
        } else {
            console.log("Couldn't initialize Chorus variables as kernel not ready yet...");
        }
    };

    // Handler fpr when chorus wants to insert a code cell in the notebook.
    CHORUS.EVENT_HANDLERS['code_insert'] = function(response) {
        var new_cell = IPython.notebook.insert_cell_below("code");
        new_cell.set_text(response.data);
        // new_cell.execute();
    };

    function customize_dom() {
        // Remove buttons
        $('#ipython_notebook img').replaceWith("");
        $('#copy_notebook').replaceWith("");
        $('#rename_notebook').replaceWith("");
        $('#new_notebook').replaceWith("");
        $('#open_notebook').replaceWith("");
        $('#download_pdf').replaceWith("");

        // Rewire save_checkpoint button
        $('#save_checkpoint a').text("Save New Version");

        $('#kill_and_exit').on('click', CHORUS.closeNotebook);

        // Prevent the click-to-rename functionality
        $('#notebook_name').off();

        // Add import data source menu item
        var data_dropdown_html = '<li class="dropdown"> \
                                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" aria-expanded="false">Data</a> \
                                    <ul id ="data_menu" class="dropdown-menu"> \
                                        <li id="import_chorus_dataset" title="Import data from Chorus"> \
                                            <a href=#>Import Dataset into Notebook</a> \
                                        </li>  \
                                    </ul> \
                                </li>';
        $(data_dropdown_html).insertAfter($('#file_menu').parent())

        var documentation_link_html = '<li> \
                                        <a rel="noreferrer" href="https://alpine.atlassian.net/wiki/display/V6/Using+Alpine+Chorus+Notebooks" target="_blank" title="Help using Alpine Chorus Notebooks"> \
                                        <i class="fa fa-external-link menu-icon pull-right"></i> \
                                            Alpine Notebook Help \
                                        </a> \
                                    </li>';

        $(documentation_link_html).insertAfter($('#help_menu').children('.divider').first())

        $('#import_chorus_dataset').on('click', CHORUS.showDatasetChooser)


        // Prevent backspace: http://stackoverflow.com/questions/1495219/how-can-i-prevent-the-backspace-key-from-navigating-back
        $(document).on('keydown', function (event) {
            var doPrevent = false;
            if (event.keyCode === 8) {
                var d = event.srcElement || event.target;
                if ((d.tagName.toUpperCase() === 'INPUT' && 
                     (
                         d.type.toUpperCase() === 'TEXT' ||
                         d.type.toUpperCase() === 'PASSWORD' || 
                         d.type.toUpperCase() === 'FILE' || 
                         d.type.toUpperCase() === 'SEARCH' || 
                         d.type.toUpperCase() === 'EMAIL' || 
                         d.type.toUpperCase() === 'NUMBER' || 
                         d.type.toUpperCase() === 'DATE' )
                     ) || 
                     d.tagName.toUpperCase() === 'TEXTAREA') {
                    doPrevent = d.readOnly || d.disabled;
                }
                else {
                    doPrevent = true;
                }
            }

            if (doPrevent) {
                event.preventDefault();
            }
        });
    }

    function hook_events() {
        $([IPython.events]).on("notebook_saved.Notebook", CHORUS.notebookSaved);
        $([IPython.events]).on("checkpoint_created.Notebook", CHORUS.notebookSaveVersion);
        $([IPython.events]).on("set_dirty.Notebook", CHORUS.setDirty);
        $([IPython.events]).on("kernel_ready.Kernel", CHORUS.initializeNotebook);
    }

    function _ensure_init(c) {
        c.initializeNotebook();

        if (IPython.notebook.kernel.is_connected() && c.sessionId != null) {
            window.clearInterval(c._INIT_TIMER_ID);
        }
    }

    function _on_load() {
        console.log("Loaded Chorus notebook extension. " + Date());

        customize_dom();

        hook_events();
        
        window.addEventListener('message', function(event) {
            //if (event.origin === 'http://127.0.0.1:8080') {
            var response = event.data;
            if (!response || !("action" in response)) {
                return;
            }

            var chorus_event_type = response.action;

            console.log("Received message from Chorus with event type \"" + chorus_event_type + "\"");
            console.log(event);

            if (chorus_event_type in CHORUS.EVENT_HANDLERS) {
                CHORUS.EVENT_HANDLERS[chorus_event_type](response);
            } else {
                console.log("ERROR: No event handler for event type \"" + chorus_event_type + "\".");
            }
        });

        CHORUS._INIT_TIMER_ID = window.setInterval(_ensure_init, 500, CHORUS);
    }

    return {
        load_ipython_extension: _on_load
    };
});
