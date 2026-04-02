.. nadzoring documentation master file

Welcome to Nadzoring's Documentation!
======================================

Nadzoring (from Russian "надзор" — supervision/oversight + English "-ing" suffix) is a free and open-source command-line tool for detecting website blocks, monitoring service availability, and network analysis. It helps you investigate network connectivity issues, check if websites are accessible, analyze network configurations with comprehensive DNS diagnostics — including reverse DNS, DNS poisoning detection, ARP spoofing monitoring, SSL/TLS certificate analysis, HTTP security header auditing, email security validation (SPF/DKIM/DMARC), subdomain discovery, and much more.

.. code-block:: bash

   pip install nadzoring
   nadzoring --help

----

Key Features
------------

- **DNS Analysis** — resolve, trace, compare, health-check, benchmark DNS servers
- **Reverse DNS** — PTR record lookups for IPv4 and IPv6
- **DNS Poisoning Detection** — detect censorship, CDN routing, or manipulation
- **Network Diagnostics** — ping, traceroute, port scanning, HTTP probing, WHOIS,
  comprehensive domain information
- **Security Auditing** — SSL/TLS certificate inspection, HTTP security headers,
  SPF/DKIM/DMARC validation, subdomain discovery, continuous certificate monitoring
- **ARP Security** — cache inspection, spoofing detection, real-time monitoring
- **Timeout Configuration** — per-operation lifetime, connect, and read timeouts
- **Multiple Output Formats** — ``table``, ``json``, ``csv``, ``html``, ``html_table``, ``yaml``.
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
   commands/security
   commands/arp

.. toctree::
   :maxdepth: 2
   :caption: Python API Reference

   api/dns_lookup
   api/network_base
   api/security
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
       ``domain-info``, ``connections``, ``traceroute``, ``route``
   * - ``security``
     - ``check-ssl``, ``check-headers``, ``check-email``,
       ``subdomains``, ``watch-ssl``
   * - ``arp``
     - ``cache``, ``detect-spoofing``, ``monitor-spoofing``

----

Quick Examples
--------------

.. code-block:: bash

   # Resolve a hostname to IP
   nadzoring network-base host-to-ip example.com

   # Comprehensive domain information (WHOIS + DNS + geo + reverse DNS)
   nadzoring network-base domain-info example.com

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

   # Check SSL/TLS certificate
   nadzoring security check-ssl example.com

   # Audit HTTP security headers
   nadzoring security check-headers https://example.com

   # Validate SPF, DKIM, DMARC
   nadzoring security check-email example.com

   # Discover subdomains
   nadzoring security subdomains example.com

   # Real-time ARP spoofing monitor
   nadzoring arp monitor-spoofing --interface eth0

   # Custom timeouts for slow networks
   nadzoring dns resolve --connect-timeout 10 --read-timeout 20 example.com

----

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
