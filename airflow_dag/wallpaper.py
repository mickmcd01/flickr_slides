import os
import time
from datetime import datetime, timedelta
from shutil import copyfile
from builtins import range
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
import sqlalchemy


args = {
    'owner': 'Airflow',
}

dag = DAG(
    dag_id='wallpaper',
    default_args=args,
    start_date=datetime(2020, 9, 1),
    schedule_interval='@daily',
    tags=[]
)

slides_directory = '/home/mick/slides'

def folder_processing():
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
        for entry in new_folders:
            query = 'INSERT INTO folders (folder, time) values ("%s", "%s")' % (entry, time_string)
            print(query)
            rs = con.execute(query)

        for entry in old_folders:
            query = 'DELETE FROM folders WHERE folder="%s"' % entry
            print(query)
            rs = con.execute(query)

    try:
        index = folders.index(current_folder)
        if index >= len(folders) - 1:
            index = 0
        else:
            index += 1
    except:
        index = 0

    new_current_folder = folders[index]
    with engine.connect() as con:
        query = 'DELETE FROM current'
        rs = con.execute(query)
        query = 'INSERT INTO current (folder, update_time) values ("%s", "%s")' % (new_current_folder, time_string)
        rs = con.execute(query)

def build_xml():
    xml_destination = '/home/mick/.local/share/shotwell/wallpaper/wallpaper.xml'
    xml_temp = '/home/mick/wallpaper.xml'

    engine = sqlalchemy.create_engine("sqlite:////home/mick/airflow/wallpaper.db")
    with engine.connect() as con:
        rs = con.execute('SELECT * FROM current')

        for row in rs:
            current_folder = row['folder']

    slides_path = os.path.join(slides_directory, current_folder)

    file_list = []
    for pic in os.listdir(slides_path):
        if pic.endswith(".jpg"):
            file_list.append(pic)

    with open(xml_temp, 'w') as xml:
        xml.write('<background>\n\t<static>\n\t\t<duration>60.00</duration>\n')
        full_path = os.path.join(slides_path, file_list[0])
        xml.write('\t\t<file>%s</file>\n\t</static>\n' % full_path)
        from_path = full_path

        for idx, entry in enumerate(file_list):
            if idx == 0:
                continue

            xml.write('\t<transition>\n\t\t<duration>2.00</duration>\n')
            xml.write('\t\t<from>%s</from>\n' % from_path)
            to_path = os.path.join(slides_path, entry)
            xml.write('\t\t<to>%s</to>\n' % to_path)
            xml.write('\t</transition>\n')
            from_path = to_path

            xml.write('\t<static>\n\t\t<duration>60.00</duration>\n')
            xml.write('\t\t<file>%s</file>\n' % to_path)
            xml.write('\t</static>\n')

        xml.write('</background>\n')

    copyfile(xml_temp, xml_destination)

    print('New slideshow is %s' % current_folder)


step1 = PythonOperator(
    task_id='wallpaper_folder_processing',
    python_callable=folder_processing,
    dag=dag,
)

step2 = PythonOperator(
    task_id='wallpaper_build_xml',
    python_callable=build_xml,
    dag=dag,
)

step2.set_upstream(step1)

