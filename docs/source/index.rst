.. nadzoring documentation master file

Welcome to Nadzoring's Documentation!
======================================

**Nadzoring** (from Russian "надзор" — supervision/oversight + English "-ing" suffix)
is a free and open-source command-line tool for detecting website blocks,
monitoring service availability, and performing comprehensive network analysis.

It helps you investigate connectivity issues, check whether websites are accessible,
detect DNS poisoning and censorship, analyze ARP spoofing, and run automated
network diagnostics — all from a single CLI.

.. code-block:: bash

   pip install nadzoring
   nadzoring --help

----

Key Features
------------

- **DNS Analysis** — resolve, trace, compare, health-check, and benchmark DNS servers
- **Reverse DNS** — PTR record lookups for IPv4 and IPv6 addresses
- **DNS Poisoning Detection** — detect censorship, CDN routing, or manipulation
- **Network Diagnostics** — ping, traceroute, port scanning, HTTP probing, WHOIS
- **ARP Security** — cache inspection, spoofing detection, real-time monitoring
- **Multiple Output Formats** — table, JSON, CSV, HTML, html_table
- **Cross-Platform** — Linux, Windows, and macOS support

----

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 3
   :caption: Command Reference

   commands/dns
   commands/network
   commands/arp

.. toctree::
   :maxdepth: 2
   :caption: Python API Reference

   api/dns_lookup
   api/network_base
   api/arp

.. toctree::
   :maxdepth: 1
   :caption: Project

   changelog
   contributing
   license

----

Command Groups at a Glance
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Group
     - Commands
   * - ``dns``
     - ``resolve``, ``reverse``, ``check``, ``trace``, ``compare``, ``health``, ``benchmark``, ``poisoning``
   * - ``network-base``
     - ``ping``, ``http-ping``, ``host-to-ip``, ``geolocation``, ``params``, ``port-scan``, ``port-service``, ``whois``, ``connections``, ``traceroute``, ``route``
   * - ``arp``
     - ``cache``, ``detect-spoofing``, ``monitor-spoofing``

----

Quick Examples
--------------

.. code-block:: bash

   # Resolve a hostname to IP
   nadzoring network-base host-to-ip example.com

   # Reverse DNS lookup
   nadzoring dns reverse 8.8.8.8

   # Full DNS health check
   nadzoring dns health example.com

   # Trace DNS delegation chain
   nadzoring dns trace example.com

   # Detect DNS poisoning
   nadzoring dns poisoning example.com

   # Scan common ports
   nadzoring network-base port-scan example.com

   # Real-time ARP spoofing monitor
   nadzoring arp monitor-spoofing --interface eth0

----

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
