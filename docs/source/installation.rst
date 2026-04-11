Installation
============

Requirements
------------

- **Python 3.12** or higher
- **pip** (bundled with Python 3.12+)
- Supported operating systems: **Linux**, **Windows**, **macOS**

Optional system utilities (needed for specific commands):

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Utility
     - Required by
   * - ``traceroute`` / ``tracepath``
     - ``network-base traceroute`` (Linux)
   * - ``tracert``
     - ``network-base traceroute`` (Windows — built-in)
   * - ``whois``
     - ``network-base whois``
   * - ``ip`` / ``ifconfig`` / ``route``
     - ``network-base params``, ``network-base route`` (Linux)
   * - ``ss``
     - ``network-base connections`` (Linux)
   * - ``net-tools`` (``route -n``)
     - ``network-base params`` on some Linux distros
   * - ``dig``
     - ``security check-email`` (DNS TXT lookups — used when ``dnspython``
       is not installed)
   * - ``nslookup``
     - ``security check-email`` (second fallback after ``dig``)

Optional Python packages:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Package
     - Required by
   * - ``dnspython``
     - ``security check-email`` (preferred; handles multi-chunk TXT records
       reliably).  Install with ``pip install dnspython``.

----

Stable Release (Recommended)
------------------------------

Install the latest stable version from PyPI:

.. code-block:: bash

   pip install nadzoring

Verify the installation:

.. code-block:: bash

   nadzoring --help

----

Development Version
-------------------

To install the latest development snapshot directly from GitHub:

.. code-block:: bash

   pip install git+https://github.com/alexeev-prog/nadzoring.git

Or clone and install in editable mode for contributing:

.. code-block:: bash

   git clone https://github.com/alexeev-prog/nadzoring.git
   cd nadzoring
   pip install -e ".[dev]"

----

Installing Optional System Dependencies
-----------------------------------------

**Linux (Debian / Ubuntu):**

.. code-block:: bash

   sudo apt update
   sudo apt install net-tools traceroute whois iproute2 dnsutils

**Linux (RHEL / CentOS / Fedora):**

.. code-block:: bash

   sudo dnf install net-tools traceroute whois iproute bind-utils

**macOS (Homebrew):**

.. code-block:: bash

   brew install iproute2mac whois

**Windows:**

``tracert`` and ``arp`` are built into Windows. No additional installs required
for basic functionality.

----

Installing Optional Python Dependencies
-----------------------------------------

For reliable email security checks (``security check-email``), install
``dnspython``:

.. code-block:: bash

   pip install dnspython

Without ``dnspython``, Nadzoring falls back to ``dig`` and then ``nslookup``
for DNS TXT record queries.  Multi-chunk TXT records (long SPF strings split
across multiple quoted segments) are handled correctly in all three cases, but
``dnspython`` is the most reliable option.

----

ARP Monitoring: Additional Setup
----------------------------------

The ``arp monitor-spoofing`` command uses `Scapy <https://scapy.net/>`_ for
raw packet capture, which requires elevated privileges on most systems.

**Linux** — grant raw-socket capability to avoid running as root:

.. code-block:: bash

   sudo setcap cap_net_raw+ep $(which python3)

Or simply run the command with ``sudo``.

**Windows** — run your terminal as Administrator.

**macOS** — run with ``sudo``.

----

Traceroute: Privilege Setup (Linux)
-------------------------------------

The ``network-base traceroute`` command requires raw-socket access on Linux.
Use one of the following approaches:

.. code-block:: bash

   # Option 1: run with sudo
   nadzoring network-base traceroute --sudo example.com

   # Option 2: grant capability to traceroute binary
   sudo setcap cap_net_raw+ep $(which traceroute)

   # Option 3: use tracepath (no root required — automatic fallback)
   # Nadzoring tries tracepath automatically if traceroute fails

----

Shell Completions
-----------------

Nadzoring provides tab-completion support for **bash**, **zsh**, **fish**, and
**PowerShell**. Enable it for your preferred shell using the commands below.

Bash
~~~~

Add to ``~/.bashrc`` (or ``~/.bash_profile`` on macOS):

.. code-block:: bash

   echo 'eval "$(nadzoring completion bash)"' >> ~/.bashrc
   source ~/.bashrc

Alternative — save to a file and source it:

.. code-block:: bash

   nadzoring completion bash > ~/.nadzoring-complete.bash
   echo 'source ~/.nadzoring-complete.bash' >> ~/.bashrc

Zsh
~~~

Add to ``~/.zshrc``:

.. code-block:: bash

   echo 'eval "$(nadzoring completion zsh)"' >> ~/.zshrc
   source ~/.zshrc

Or save to a file in your ``fpath``:

.. code-block:: bash

   nadzoring completion zsh > "${fpath[1]}/_nadzoring"

Fish
~~~~

Save directly to Fish completions directory:

.. code-block:: bash

   nadzoring completion fish > ~/.config/fish/completions/nadzoring.fish

Or source it temporarily:

.. code-block:: bash

   nadzoring completion fish | source

PowerShell
~~~~~~~~~~

Add to your PowerShell profile (``$PROFILE``):

.. code-block:: powershell

   nadzoring completion powershell >> $PROFILE

To reload the profile immediately:

.. code-block:: powershell

   . $PROFILE

Or use it in the current session only:

.. code-block:: powershell

   nadzoring completion powershell | Invoke-Expression

Testing Completions
~~~~~~~~~~~~~~~~~~~

After installation, type ``nadzoring `` followed by **TAB** to see available
commands:

.. code-block:: bash

   nadzoring [TAB]
   # Should show: arp  completion  dns  network-base  security

Type a command followed by space and **TAB** to see options:

.. code-block:: bash

   nadzoring dns [TAB]
   # Should show: resolve  reverse  check  trace  compare  health  benchmark  poisoning  monitor

Manual Activation (without saving to profile)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you don't want to modify your shell profile, you can activate completions
manually:

.. code-block:: bash

   # Bash / Zsh
   source <(nadzoring completion bash)

   # Fish
   nadzoring completion fish | source

   # PowerShell
   nadzoring completion powershell | Invoke-Expression

Troubleshooting Completions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Completions not working?** Check these common issues:

1. **Shell not reloaded** — restart your terminal or run
   ``source ~/.bashrc`` (bash) / ``source ~/.zshrc`` (zsh)

2. **Wrong shell** — ensure you're using the correct completion command for
   your shell

3. **PATH issue** — verify ``nadzoring`` is in your PATH: ``which nadzoring``

4. **Completion not registered** — run the activation command directly to see
   if there are any errors

**Debugging bash completions:**

.. code-block:: bash

   # Enable debug output
   set -x
   nadzoring [TAB]
   set +x

**Check if completion is registered:**

.. code-block:: bash

   # Bash
   complete -p | grep nadzoring
   # Should output: complete -o nosort -F _nadzoring_completion nadzoring

   # Zsh
   echo $fpath | grep nadzoring

**Show installation hints:**

.. code-block:: bash

   nadzoring completion hints bash      # For bash
   nadzoring completion hints zsh       # For zsh
   nadzoring completion hints fish      # For fish
   nadzoring completion hints powershell  # For PowerShell

Completions Commands Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - Description
   * - ``nadzoring completion bash``
     - Generate bash completion script
   * - ``nadzoring completion zsh``
     - Generate zsh completion script
   * - ``nadzoring completion fish``
     - Generate fish completion script
   * - ``nadzoring completion powershell``
     - Generate PowerShell completion script
   * - ``nadzoring completion hints <shell>``
     - Show detailed installation hints

----

Verifying the Installation
--------------------------

Run a quick smoke test after installing:

.. code-block:: bash

   # Check tool is reachable
   nadzoring --help

   # Resolve a well-known domain
   nadzoring dns resolve google.com

   # Reverse DNS lookup
   nadzoring dns reverse 8.8.8.8

   # Ping a host
   nadzoring network-base ping 1.1.1.1

   # Show local network parameters
   nadzoring network-base params

   # Check an SSL certificate
   nadzoring security check-ssl example.com

   # Audit HTTP security headers
   nadzoring security check-headers https://example.com

   # Validate email security records
   nadzoring security check-email example.com

   # Test timeout configuration (slow operation will abort)
   nadzoring dns resolve --timeout 2 google.com

   # Test shell completions (if enabled)
   nadzoring [TAB]
