.. _network-base-commands:

Network Base Commands
=====================

The ``network-base`` command group provides basic network operations and diagnostics.

.. _network-base-ping:

ping
----

Ping one or more addresses to check reachability.

**Usage:**

.. code-block:: bash

   nadzoring network-base ping [OPTIONS] ADDRESSES...

**Arguments:**

* ``ADDRESSES...`` — One or more IP addresses or hostnames (required)

**Examples:**

.. code-block:: bash

   # Ping single address
   nadzoring network-base ping 8.8.8.8

   # Multiple addresses
   nadzoring network-base ping google.com cloudflare.com 1.1.1.1

   # JSON output
   nadzoring network-base ping -o json github.com

.. _network-base-geolocation:

geolocation
-----------

Get geolocation information for IP addresses.

**Usage:**

.. code-block:: bash

   nadzoring network-base geolocation [OPTIONS] IPS...

**Arguments:**

* ``IPS...`` — One or more IP addresses (required)

**Output includes:**

* Latitude/Longitude
* Country
* City

**Examples:**

.. code-block:: bash

   # Geolocate IPs
   nadzoring network-base geolocation 8.8.8.8 1.1.1.1

   # Save results
   nadzoring network-base geolocation --save locations.json 8.8.8.8
