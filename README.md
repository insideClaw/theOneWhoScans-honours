The One Who Scans
======

Be able to tell what people in your network are staying put... and for how long.

A development conducted for the Honours project of "Re-using Smartphones as Network Monitoring Devices". Proven to run on a smartphone after the appropriate Linux environment has been exposed.

## Dependencies:
1. Python 2.x
2. nmap
3. sqlite

## Install and Usage:
1. Download and extract to a suitable place for the script. Example: ~/inf/python/
2. In a terminal, run:
> cd <programDir>
> python theOnesWhoScans.py

  * There are no switches that can be passed to the application, all interactivity is done during execution.

## How it works:

![Functionality Flowchart](https://github.com/insideClaw/theOneWhoScans-honours/blob/master/flowchart.png)

* Runs nmap on the currently connected network to construct topology.

* Uses a mysqli database to note down known hosts and assign aliases to them per user interaction.

* Continuously scans and reports what familiar hosts are online and adds new entries upon discovery. 

