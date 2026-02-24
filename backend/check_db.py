import sqlite3

conn = sqlite3.connect('pm_system.db')
cursor = conn.cursor()

print("Projects table structure:")
cursor.execute('PRAGMA table_info(projects)')
for row in cursor.fetchall():
    print(row)

print("\n\nProjects data:")
cursor.execute('SELECT id, project_no, name, city, expected_arrival_time, status FROM projects')
for row in cursor.fetchall():
    print(row)

conn.close()
