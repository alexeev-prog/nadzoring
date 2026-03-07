ARP Commands
============

The ``arp`` group provides ARP cache inspection and spoofing detection.

.. code-block:: bash

   nadzoring arp --help

.. warning::
   ARP monitoring requires raw-socket privileges.  On Linux, either run
   with ``sudo`` or grant the Python binary the ``cap_net_raw`` capability::

       sudo setcap cap_net_raw+ep $(which python3)

   On Windows, run the terminal as Administrator.  On macOS, run with
   ``sudo``.

----

arp cache
---------

Display the current ARP cache table.

.. code-block:: text

   nadzoring arp cache [OPTIONS]

.. code-block:: bash

   nadzoring arp cache
   nadzoring arp cache -o json --save arp_cache.json

Output columns: ``ip_address``, ``mac_address``, ``interface``, ``state``.

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError

   try:
       cache = ARPCache()
       entries = cache.get_cache()
   except ARPCacheRetrievalError as exc:
       print("Cannot read ARP cache:", exc)
   else:
       for entry in entries:
           print(
               f"{entry.ip_address}  "
               f"{entry.mac_address or '(incomplete)'}  "
               f"{entry.interface}  "
               f"{entry.state.value}"
           )

----

arp detect-spoofing
-------------------

Analyse the ARP cache for potential spoofing patterns (duplicate MAC or
duplicate IP across multiple entries).

.. code-block:: text

   nadzoring arp detect-spoofing [OPTIONS] [INTERFACE ...]

If no interfaces are specified, all interfaces are checked.

.. code-block:: bash

   nadzoring arp detect-spoofing
   nadzoring arp detect-spoofing eth0 wlan0
   nadzoring arp detect-spoofing -o json --save spoofing.json

Alert types:

- ``duplicate_mac`` — same MAC address mapped to multiple IPs
- ``duplicate_ip``  — same IP address claimed by multiple MACs (strong
  indicator of active spoofing)

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.arp.cache import ARPCache, ARPCacheRetrievalError
   from nadzoring.arp.detector import ARPSpoofingDetector

   try:
       cache = ARPCache()
       detector = ARPSpoofingDetector(cache)
       alerts = detector.detect()
   except ARPCacheRetrievalError as exc:
       print("ARP cache error:", exc)
   else:
       if not alerts:
           print("No spoofing detected")
       for alert in alerts:
           print(f"[{alert.alert_type}] {alert.description}")

----

arp monitor-spoofing
--------------------

Monitor ARP packets in real time and alert on IP-to-MAC mapping changes.

.. code-block:: text

   nadzoring arp monitor-spoofing [OPTIONS]

Options
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Option
     - Default
     - Description
   * - ``--interface / -i``
     - all
     - Network interface to monitor
   * - ``--count / -c``
     - ``10``
     - Number of ARP packets to capture (0 = unlimited)
   * - ``--timeout / -t``
     - ``30``
     - Capture timeout in seconds (0 = no timeout)

Examples
~~~~~~~~

.. code-block:: bash

   # Monitor all interfaces, 30s timeout
   nadzoring arp monitor-spoofing

   # Specific interface, 200 packets
   nadzoring arp monitor-spoofing --interface eth0 --count 200 --timeout 60

   # Save alerts for forensic analysis
   nadzoring arp monitor-spoofing -o json --save arp_alerts.json

Python API
~~~~~~~~~~

.. code-block:: python

   from nadzoring.arp.realtime import ARPRealtimeDetector

   detector = ARPRealtimeDetector()
   alerts = detector.monitor(
       interface="eth0",
       count=100,
       timeout=30,
   )

   print(f"Processed {detector.stats['packets_processed']} packets")
   print(f"Detected {detector.stats['alerts_generated']} alerts")

   for alert in alerts:
       print(
           f"[{alert['timestamp']}] "
           f"{alert['src_mac']} — {alert['message']}"
       )

Custom callback (non-blocking integration)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from scapy.all import ARP, Ether
   from nadzoring.arp.realtime import ARPRealtimeDetector

   detector = ARPRealtimeDetector()

   def on_packet(packet: Ether, alert: str | None) -> None:
       if alert:
           # Integrate with alerting system here
           print("ALERT:", alert)

   detector.monitor(
       interface=None,  # all interfaces
       count=0,         # capture indefinitely
       timeout=0,       # no timeout
       packet_callback=on_packet,
   )
