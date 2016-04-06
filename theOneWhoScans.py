#!/usr/bin/env python
import subprocess
import argparse
import time
import dbHandler
import signal

'''Be able to tell what people around you are staying put... and for how long. Runs nmap scans periodically, maps findings to names upon user
interaction, notifies on topology change.'''
parser = argparse.ArgumentParser(description='Can be run without arguments.')

class networkDetails:
    '''Initializing the object triggers pulling the network details data for use within scope of initialization'''
    network=""
    gw=""

    # Obtains the network parameters on instantiation. Uses two calls for parsing the lists is too complicated.
    def __init__(self):
        pattern = '''ip route | grep -E "/[0-9]{2} dev $(ip route | grep default | tail -1 | awk '{print $5}')" | awk '{print $1}' '''
        netInfoNetwork = subprocess.Popen(pattern, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        if netInfoNetwork:
            self.network = netInfoNetwork
        else:
            exit("-!- No connectivity, network scanning impossible!") 

def netAddrClass(netAddr):
    identifiers = netAddr.split(".")
    if identifiers[0] == "10":
        addrClass = "A"
    elif identifiers[0] == "172" and int(identifiers[1]) in range(16,32):
        addrClass = "B"
    elif identifiers[0] == "192" and identifiers[1] == "168":
        addrClass = "C"
    else: 
        addrClass = "Public"
    return(addrClass)

def exitHandler(sig, frame):
    print '-!- Exiting on user request (CTRL-C pressed)'
    exit(0)

def safetyCheck(netDetails):
    print("Class: " + netAddrClass(netDetails.network))
    if netAddrClass(netDetails.network) == "Public":
        print("-!- Running on a non-private network! Exiting.")
        exit(1)


def scan(network):
    '''Do an nmap scan. Returns a set of IP addresses and their corresponding MAC addresses found probing in string format,
    followed by a default name provided by NetBIOS query.'''
    sepCharacter='" => "' # Fixes quotation mark interpretation problems
    nmap_raw = "sudo nmap -sn " + network + " | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print "+sepCharacter+"$3;}'"
    nmap = subprocess.Popen(nmap_raw, shell=True, stdout=subprocess.PIPE)
    #netbiosComm = "nbtscan 
    return nmap.stdout.read()

def deepScan(ip):
    '''Launch tools to give good idea of who the target is'''
    print("-=- Running detailed analysis tools on the host... that might take a while.")
    netbios_raw = "nbtscan " + ip
    nmapAdv_raw = "sudo nmap -T4 -O -Pn " + ip
    netbios = subprocess.Popen(nmapAdv_raw, shell=True, stdout=subprocess.PIPE)
    nmapAdv = subprocess.Popen(netbios_raw, shell=True, stdout=subprocess.PIPE)
    print(netbios.stdout.read())
    print(nmapAdv.stdout.read())

def analyzeMatch(captureChunk):
    '''Given a chunk of capture and a file of previous captures, output conclusions.'''
    # Parse the newly identified hosts. 
    # Who are they? None of your business.
    challengerHosts = captureChunk.split("\n")
    challengerHosts = filter(None, challengerHosts)
    print("DEBUG: " + str(challengerHosts))

    # Call the database connection handler, to use when checking and adding
    dbconn = dbHandler.DatabaseConnection()
    # Interpret current chunk
    for c in challengerHosts:
        challenger = c.split(' => ')
        # Splits up as per the structure given by the nmapComm awk parsing
        challenger = filter(None, challenger)

        challengerIP = challenger[0]
        try:
            challengerMAC = challenger[1]
        except:
            challengerMAC = "MyOwnMAC"

        # Parse the familiar hosts
        familiar = dbconn.getEntriesFor(challengerMAC)
        if familiar:
            print("We know that one! Hello there [" + familiar[1] + "] Since: " + familiar[3] + " Known as: " + familiar[2] + " ["+familiar[0]+"]")
        else: # TODO: Some revision in obvious duplication...
            print("-=- Basic host info: ")
            print("    IP [" + challengerIP + "] and MAC [" + challengerMAC + "]")
            alias = raw_input("-?- Provide alias for new entry or type 'deep' for extensive scan.\n")
            while (alias == "deep"):

                #startTime = time.time()
                # BEGIN BENCHMARK

                deepScan(challengerIP)

                # END BENCHMARK
                #endTime = time.time()
                #diff = endTime-startTime
                #print("DEBUG: Benchmark time -> " + str(diff)[0:3])

                alias = raw_input("-?- Provide alias for new entry or type 'deep' for extensive scan.\n")

            dbconn.addEntries(challengerMAC, challengerIP, alias)

    dbconn.done()
            
def main():
    # Start trapping CTRL-C immediately
    signal.signal(signal.SIGINT, exitHandler)
    # Initializing the object triggers pulling the network details data
    netDetails = networkDetails();

    safetyCheck(netDetails);
    # Program runs continuously and rescans periodically until cancelled
    while True:
        print("-=- Sniffing new probes...")
        newChunk = scan(netDetails.network)

        print("-=- What do we know about this one...")
        analyzeMatch(newChunk)


if __name__ == '__main__':
    main()