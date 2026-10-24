CREATE TABLE IF NOT EXISTS events (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ts TEXT DEFAULT (datetime('now', 'localtime')),
event_type TEXT NOT NULL,
description TEXT,
mode TEXT);
CREATE TABLE IF NOT EXISTS measurements (
id INTEGER PRIMARY KEY AUTOINCREMENT,
ts TEXT DEFAULT (datetime('now', 'localtime')),
mode TEXT, gate TEXT, distance INTEGER,
temperature REAL, humidity REAL, light INTEGER, status TEXT);