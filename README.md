The One Who Scans
======

Be able to tell what people in your network are staying put... and for how long.

**Very early in development, prone to change**

##How it (currently) works:

* Runs nmap on the currently connected network to construct topology.

* Uses a mysqli database to note down known hosts and assign aliases to them per user interaction.

* Continuously scans and reports what familiar hosts are online and adds new entries upon discovery. 

* Under development for my Honours project of "Re-using Smartphones as Network Monitoring Devices"
