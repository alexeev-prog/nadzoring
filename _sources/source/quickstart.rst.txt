Quick Start
===========

After installation, you can start using Nadzoring immediately.

Basic Commands
--------------

Check your network configuration:

.. code-block:: bash

   nadzoring network-base params

Ping a host:

.. code-block:: bash

   nadzoring network-base ping google.com

Resolve DNS records:

.. code-block:: bash

   nadzoring dns resolve example.com

Check for DNS poisoning:

.. code-block:: bash

   nadzoring dns poisoning example.com

Getting Help
------------

To see all available commands:

.. code-block:: bash

   nadzoring --help

For help with a specific command:

.. code-block:: bash

   nadzoring network-base ping --help
