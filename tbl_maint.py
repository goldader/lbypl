class Tbl_maint(object):
    """Allows for the updating of tables directly related to Truelayer data"""

    db='/Users/jgoldader/lbypl.db'
    tbl_name=""

    def __init__(self,tbl_name):
        #import sqlite3
        self.tbl_name=tbl_name
        Tbl_maint.tbl_name=tbl_name
        #self.conn=sqlite3.connect('/Users/jgoldader/lbypl.db')
        #self.c=conn.cursor()

    def columns():
        # returns the columns in the users table as a list for simpler use in various user update routines.
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        phrase="select * from %s" % Tbl_maint.tbl_name
        c.execute(phrase)
        row = c.fetchone()
        col_list = row.keys()
        return (col_list)

    def create_tbl(nm,col_nms):
        # takes name as a list of names and creates a basic table with all fields as TEXT to be tuned later
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        col_phrase=""
        for i in range(0,len(col_nms)):
            if i < len(col_nms)-1:
                col_phrase+="%s TEXT," % col_nms[i]
            elif i == len(col_nms)-1:
                col_phrase+="%s TEXT" % col_nms[i]
        phrase="create table %s (%s);" % (nm,col_phrase)
        try:
            c.execute(phrase)
        except sqlite3.Error as e:
            conn.rollback()
            status = {'code': 400, 'desc': 'Table creation failed. DB error.'}
            conn.close()
            return (status)
        finally:
            conn.commit()
            status = {'code': 200, 'desc': 'Success'}
            conn.close()
            return (status)


import auth
import requests
import json_iter

auth.Auth('bill@fred.com')
token=auth.access_token('mock')

info_url="https://api.truelayer.com/data/v1/info"
token_phrase="Bearer %s" % token
headers = {'Authorization': token_phrase}

z=requests.get(info_url, headers=headers)

all_results=z.json()
results=all_results['results']

col_list=[]
for i in range(0,len(results)):
    output=json_iter.json_output(results[i])
    print(output)
    if len(output)>len(col_list):
        col_list=output.keys()

print("final column list = %s" % col_list)

#Tbl_maint("providers")
