#!/usr/bin/env python
'''Provides an interface with which to connect to the database and issue standard calls.'''
import sqlite3
import time
import os.path

class DatabaseConnection:
    '''Responsible for providing a database connection and interface for the scope within which it's initialized'''
    conn = None
    c = None

    def __init__(self):
        # The database has to be present and containing a basic structure, mark it for initializing otherwise
        if os.path.isfile("topology.db"):
            self.conn = sqlite3.connect("topology.db")
            self.c = self.conn.cursor()
        else:
            self.conn = sqlite3.connect("topology.db")
            self.c = self.conn.cursor()
            self.initializeDatabase()

    def initializeDatabase(self):
        print("-=- Database does not exist, initializing...")
        with open("creationScript.sql", "r") as creationScript:
            creationCommand = str(creationScript.read())

        self.c.execute(creationCommand)

    def query(self, query, params):
        return self.c.execute(query, params)

    def done(self):
        self.conn.commit()
        self.conn.close()
        print("-=- Transaction committed and DB closed!")

    def __del__(self):
        self.conn.close()
    
    def getEntriesFor(self, challengerMAC):
	   self.c.execute('SELECT mac, ip, alias, creationDate FROM topology WHERE mac=?', (challengerMAC,))
	   return self.c.fetchone()

    def addEntries(self,mac,ip,alias):
        print("Adding entry...")
        self.c.execute('''INSERT INTO topology(mac,ip,alias,creationDate)
                    VALUES(?,?,?,?)''', (mac, ip, alias, time.strftime("%c")))
        print("-=- A new acquisition! Welcome to the party, " + alias + "!")


if __name__ == '__main__':
	exit("-!- Not designed to be run as standalone but imported. Exiting.")