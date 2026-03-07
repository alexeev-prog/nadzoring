.. nadzoring documentation master file

Welcome to Nadzoring's Documentation!
======================================

**Nadzoring** (от русского «надзор» + английский суффикс «-ing») —
свободный инструмент командной строки для обнаружения блокировок
сайтов, мониторинга доступности сервисов и комплексного сетевого анализа.

.. code-block:: bash

   pip install nadzoring
   nadzoring --help

----

Key Features
------------

- **DNS Analysis** — resolve, trace, compare, health-check, benchmark DNS servers
- **Reverse DNS** — PTR record lookups for IPv4 and IPv6
- **DNS Poisoning Detection** — detect censorship, CDN routing, or manipulation
- **Network Diagnostics** — ping, traceroute, port scanning, HTTP probing, WHOIS
- **ARP Security** — cache inspection, spoofing detection, real-time monitoring
- **Multiple Output Formats** — ``table``, ``json``, ``csv``, ``html``, ``html_table``
- **Cross-Platform** — Linux, Windows, macOS

----

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   error_handling
   monitoring_dns

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
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Developer Guide

   architecture
   contributing

----

Command Groups at a Glance
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Group
     - Commands
   * - ``dns``
     - ``resolve``, ``reverse``, ``check``, ``trace``, ``compare``,
       ``health``, ``benchmark``, ``poisoning``, ``monitor``,
       ``monitor-report``
   * - ``network-base``
     - ``ping``, ``http-ping``, ``host-to-ip``, ``geolocation``,
       ``params``, ``port-scan``, ``port-service``, ``whois``,
       ``connections``, ``traceroute``, ``route``
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
