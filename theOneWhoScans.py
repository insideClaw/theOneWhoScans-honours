#!/usr/bin/env python
import subprocess
import argparse
import sqlite3
import time
import sys

'''Be able to tell what people around you are staying put... and for how long. Runs nmap scans periodically, maps findings to names upon user
interaction, notifies on topology change.'''

# Initial derived variables, global scope
parser = argparse.ArgumentParser(description='Can be run without arguments.')

class networkDetails:
	network=""
	gw=""

	# Obtains the network parameters on instantiation. Uses two calls for parsing the lists is too complicated.
	def __init__(self):
		netInfoNetwork = subprocess.Popen("ip route | head -2 | tail -1 | awk '{print $1}'", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
		if netInfoNetwork:
			self.network = netInfoNetwork
		else:
			exit("-!- No connectivity, network scanning impossible!") 
		# TODO: Make that proper verification and not just hitting the first viable line, and it seeming fine even with no net

class topologyDB:
    conn = None
    c = None

    def __init__(self):
        self.conn = sqlite3.connect("topology.db")
        self.c = self.conn.cursor()

    def query(self, query, params):
        return self.c.execute(query, params)

    def __del__(self):
        self.conn.close()


def scan(network):
	'''Do a nmap scan. Returns a set of IP addresses and their corresponding MAC addresses found probing in string format. '''
	sepCharacter='" => "' # Fixes quotation mark interpretation problems
	captureComm = "sudo nmap -sn " + network + " | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print "+sepCharacter+"$3;}'"
	scannedChunk = subprocess.Popen(captureComm, shell=True, stdout=subprocess.PIPE)
	return scannedChunk.stdout.read()

def analyzeMatch(captureChunk):
	'''Given a chunk of capture and a file of previous captures, output conclusions.'''
	# Parse the newly identified hosts. 
	# Who are they? None of your business.
	challengerHosts = captureChunk.split("\n")
	challengerHosts = filter(None, challengerHosts)

	print("Loading Database...")
	db = topologyDB()

	# Interpret current chunk
	for c in challengerHosts:
		challenger = c.split(' => ')
		challenger = filter(None, challenger)

		challengerIP = challenger[0]
		try:
			challengerMAC = challenger[1]
		except:
			challengerMAC = "It's me"

		# Parse the familiar hosts
		db.c.execute('SELECT mac, ip, alias, creationDate FROM topology WHERE mac=?', (challengerMAC,))
		familiar = db.c.fetchone()
		if familiar:
			print("We know that one! Hello there [" + familiar[1] + "] Since: " + familiar[3] + " Known as: " + familiar[2] + " ["+familiar[0]+"]")
		else:
			alias = raw_input("\n-?- Provide alias for new entry with IP " + challengerIP + ":\n")
			db.query('''INSERT INTO topology(mac,ip,alias,creationDate)
						VALUES(?,?,?,?)''', (challengerMAC, challengerIP, alias, time.strftime("%c")))
			print("-=- A new acquisition! Welcome to the party, " + alias + "!")

	print("-=- Closing database...")
	db.conn.commit()
	db.conn.close()
	print("-=- Database closed.")
				
# Fills the netDetails object with info with a pull at initialize
netDetails = networkDetails();
while True:
	print("-=- Sniffing new probes...")
	newChunk = scan(netDetails.network)
	print("-=- What do we know about this one...")
	analyzeMatch(newChunk)
	time.sleep(3)