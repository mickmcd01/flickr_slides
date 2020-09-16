import os
from datetime import datetime
import sqlalchemy

slides_directory = '/home/mick/slides'

now = datetime.now()
time_string = now.strftime("%Y-%02m-%02d")

folders = os.listdir(slides_directory)
folders.sort()

db_folders = []

engine = sqlalchemy.create_engine("sqlite:////home/mick/airflow/wallpaper.db")
with engine.connect() as con:
    rs = con.execute('SELECT * FROM current')

    for row in rs:
        current_folder = row['folder']

with engine.connect() as con:
    rs = con.execute('SELECT * FROM folders')

    for row in rs:
        print(row)
        db_folders.append(row['folder'])

db_folders.sort()

s = set(folders)
old_folders = [x for x in db_folders if x not in s]

s = set(db_folders)
new_folders = [x for x in folders if x not in s]

with engine.connect() as con:
    print(new_folders)
    for entry in new_folders:
        query = 'INSERT INTO folders (folder, time) values ("%s", "%s")' % (entry, time_string)
        print(query)
        rs = con.execute(query)

    print(old_folders)
    for entry in old_folders:
        query = 'DELETE FROM folders WHERE folder="%s"' % entry
        print(query)
        rs = con.execute(query)

try:
    index = folders.index(current_folder)
    if index >= len(folders):
        index = 0
    else:
        index += 1
except:
    index = 0

new_current_folder = folders[index]
with engine.connect() as con:
    query = 'DELETE FROM current'
    print(query)
    rs = con.execute(query)
    query = 'INSERT INTO current (folder, update_time) values ("%s", "%s")' % (new_current_folder, time_string)
    print(query)
    rs = con.execute(query)
