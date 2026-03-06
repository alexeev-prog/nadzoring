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
   sudo apt install net-tools traceroute whois iproute2

**Linux (RHEL / CentOS / Fedora):**

.. code-block:: bash

   sudo dnf install net-tools traceroute whois iproute

**macOS (Homebrew):**

.. code-block:: bash

   brew install iproute2mac whois

**Windows:**

``tracert`` and ``arp`` are built into Windows. No additional installs required
for basic functionality.

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

Verifying the Installation
----------------------------

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
