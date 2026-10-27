Interactive Shell
=================

Start a persistent diagnostics session with ``nadzoring --interactive`` or
``nadzoring -i``. The banner displays the installed package version, declared in
``pyproject.toml`` and read through ``importlib.metadata.version``. Enter normal
commands without the ``nadzoring`` prefix; all existing command groups remain
available, with the same options, output formatting, saving, and timeouts.

Installation and terminal support
---------------------------------

For the enhanced prompt and Tab completion, install the optional dependency:

.. code-block:: bash

   pip install 'nadzoring[interactive]'
   nadzoring -i

Without this extra, Nadzoring uses the standard-library readline module where
available, including command and option completion. If readline is unavailable,
the shell still works with bare ``input()`` but without line editing or completion.
Completion follows the existing Click command tree, including nested commands,
option names, and choice values, rather than maintaining a second command list.

Example session
---------------

.. code-block:: text

   nadzoring> dns resolve example.com
   nadzoring> set output json
   nadzoring> dns reverse 8.8.8.8 --save "reverse lookup.json"
   nadzoring> dns resolve example.org -o table
   nadzoring> help dns resolve
   nadzoring> quit

Built-in commands
-----------------

* ``help [command ...]`` shows normal Click help, including nested subcommands.
* ``set output FORMAT`` sets the default output format for this session only.
  Valid formats are ``table``, ``json``, ``csv``, ``html``, ``html_table``, and
  ``yaml``. Explicit command-level ``--output`` or ``-o`` takes precedence.
  ``--save`` remains a per-command option; it uses that command's selected format.
* ``clear`` clears the screen.
* ``exit``, ``quit``, or Ctrl-D leaves the shell.
* Ctrl-C cancels the current input or command and returns to the prompt.

Invalid commands, malformed quoting, and expected Click errors are reported without
ending the session. Starting another interactive shell inside the session is rejected.
Session defaults do not modify the CLI definitions or persist across sessions.

History and safety
------------------

Nonempty input lines are appended to ``~/.nadzoring_history`` and loaded on the next
session. All backends share this UTF-8, one-command-per-line file. New history files
are created with owner-only permissions on systems supporting Unix file modes.
An inaccessible or unwritable history file produces a warning, not a fatal error.
Bare-input mode saves history even though it cannot navigate previous commands.

History contains command arguments, which may include sensitive targets or proxy
credentials. Avoid entering secrets and delete the file when history is no longer
needed. Paths with spaces can be quoted. The shell parses arguments, but does not
perform environment expansion, pipelines, redirection, or execute operating-system
commands. Network commands retain their existing permissions and timeout behavior.

Developer reference
-------------------

The eager root option enters :mod:`nadzoring.shell`. Each input line is dispatched
with ``cli.main(..., standalone_mode=False)``. Nested Click ``default_map`` values
implement session output defaults without changing command decorators or domain
functions. Terminal adapters only handle input, completion, and history.

See :doc:`shell_api` for the shell API reference.
