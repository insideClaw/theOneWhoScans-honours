#!/usr/bin/env python
import sqlite3
conn = sqlite3.connect('topology.db')
c = conn.cursor()
# Create table
c.execute('''CREATE TABLE IF NOT EXISTS topology (
 			    mac TEXT PRIMARY KEY NOT NULL,
			    ip TEXT,
			    alias TEXT,
				creationDate TEXT)
				''')

