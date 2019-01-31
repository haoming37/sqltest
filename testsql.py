import psycopg2
import os
import glob
import re
import datetime
import ntpath
import shutil

FILE="list.txt"
dsn="postgresql://dev:password@localhost:5432/dev"

s_create_table="CREATE TABLE DIRECTORIES ( \
               id serial PRIMARY KEY,  \
               path text NOT NULL, \
               date timestamp NOT NULL, \
               UNIQUE(path) \
               )"

def create_backup(path,date) :
#    s_filepath_split=path.split('/')
#    print(s_filepath_split[len(s_filepath_split) - 2])
    filename=ntpath.basename(path)
    dirdate=date.strftime('%Y-%m-%d-%Hh%Mm%Ss')
    backupdir= "backup/" + filename + "/" + dirdate
    os.makedirs(backupdir)
    shutil.copy2(file, backupdir + "/" + filename)
    


with psycopg2.connect(dsn) as conn:
    with conn.cursor() as cur :
        #テーブルが存在しなかった場合に作成する
        cur.execute("""SELECT table_name FROM information_schema.tables
                       WHERE table_schema = 'public'""")
        if not ('directories',) in cur.fetchall():
            cur.execute(s_create_table)
            print("create table")
        #カレントディレクトリにあるファイルのタイムスタンプを監視
        #ToDo 監視ファイルリストの読み込み
        with open(FILE) as f :
            filelist=f.readlines()
            for file in filelist :
                file=file.strip()
                if os.path.exists(file) :
                    date= os.stat(file).st_mtime
                    dt=datetime.datetime.fromtimestamp(date) 
                    s_dt=dt.strftime('%Y-%m-%d %H:%M:%S')
                    path=file
                    s_search_path="SELECT * FROM directories where path='" + file + '\''
                    cur.execute(s_search_path)
                    cont=cur.fetchall()
                    if len(cont) != 0 :
                        s_dt_cont=cont[0][2].strftime('%Y-%m-%d %H:%M:%S')
                        if s_dt_cont != s_dt :
                            print("timestamp changed")
                            s_update_data = "UPDATE directories SET date =" + '\'' + s_dt + '\'' + "WHERE path =" + '\'' + path+ '\''
                            cur.execute(s_update_data)
                            #mkdir
                            create_backup(file, dt)
                            #ToDo if android
                            #ToDo if ios
                    else:
                        print("insert new item")
                        s_insert_data="INSERT INTO DIRECTORIES \
                                (date,path) \
                                VALUES(" + '\'' + s_dt + '\'' ',' + '\'' + path +'\'' + ")"
                        print(s_insert_data)
                        cur.execute(s_insert_data)
                        #mkdir
                        create_backup(file, dt)
                        #ToDo if android
                        #ToDo if ios
                else:
                    print("path does not exist")
        #DBの中身を表示
        cur.execute("SELECT * FROM directories")
        for cont in cur.fetchall():
            print(cont)
