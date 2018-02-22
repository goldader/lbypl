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

    def create_tbl(col_nms):
        # takes name as a list of names and creates a basic table with all fields as TEXT to be tuned later
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        col_phrase=""
        for i in range(0,len(col_nms)):
            if i < len(col_nms)-1:
                col_phrase+="'%s' TEXT," % col_nms[i]
            elif i == len(col_nms)-1:
                col_phrase+="'%s' TEXT" % col_nms[i]
        phrase="create table %s (%s);" % (Tbl_maint.tbl_name,col_phrase)
        print(phrase)
        try:
            c.execute(phrase)
        except sqlite3.Error as e:
            conn.rollback()
            status = {'code': 400, 'desc': 'Table creation failed. DB error.'}
            #conn.close()
            return (status)
        finally:
            conn.commit()
            status = {'code': 200, 'desc': 'Success'}
            #conn.close()
            return (status)

    def data_col_match(values):
        """ this function will align values from a dictionary with fields for proper data insertion.
            values should be a dictionary where keys=db_fields and values=data to be written
            before using this function, you should call append to ensure the data structure is complete
        """
        col_list = Tbl_maint.columns()
        #print(col_list) # delete after testing
        output_values = []
        for i in range(0, len(col_list)):
            if col_list[i] in values.keys():
                output_values.append(values[col_list[i]])
                #print("values = %s" % output_values) # delete after testing
            else:
                output_values.append("")
                #print("values = %s "% output_values) # delete after testing
        return(output_values)

    def append_tbl(tbl_nm,data):
        #check if data keys are in the columns names.  if not, append the table with the column names
        #use tbl_nm to call columns
        #compare using in
        #write a list with anything not in
        #append that list to columns (order doesn't matter truly)
        pass

    def user_info_update(primary_email): #update to receive a user email and get user_data from an api call inside the function
        import requests
        from auth import Auth, access_token
        from json_iter import json_output
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        c = conn.cursor()

        # identify the user and then call the truelayer apis for the dataset
        Auth(primary_email)
        user=Auth.uid
        token = access_token('mock')

        # call truelayer for user info updates
        info_url = "https://api.truelayer.com/data/v1/info"
        token_phrase = "Bearer %s" % token
        headers = {'Authorization': token_phrase}
        z = requests.get(info_url, headers=headers)
        results = z.json()['results']

        for i in range(0,len(results)):
            # call json parser to flatten data
            user_data = json_output(results[i])

            # Call the append routine in case new user data has additional columns
            #append_tbl('tl_user_info',data)

            # create variable places for use in the SQL insert statement to ensure the insert works correctly
            user_data['user_id']=user
            places = "?," * (len(Tbl_maint.columns()) - 1) + '?'

            # create a SQL execution phrase
            phrase = "INSERT INTO tl_user_info VALUES (%s)" % (places)
            phrase = phrase.strip()

            # align the user data to the columns in order so the inserts work correctly
            user_values = Tbl_maint.data_col_match(user_data)

            # write the user values to the table for update
            try:
                c.execute(phrase,user_values)
            except sqlite3.Error as e:
                conn.rollback()
                status = {'code': 400, 'desc': 'User info update failed. DB error.'}
                return (status)
            finally:
                conn.commit()
                status = {'code': 200, 'desc': 'Success'}
        conn.close()
        return(status)

"""
import requests
from auth import Auth,access_token
from json_iter import json_output

Auth('bill@fred.com')
token=access_token('mock')

info_url="https://api.truelayer.com/data/v1/info"
token_phrase="Bearer %s" % token
headers = {'Authorization': token_phrase}

z=requests.get(info_url, headers=headers)

all_results=z.json()
results=all_results['results']

col_list=[]

for i in range(0,len(results)):
    output=json_output(results[i])
    #print(output)
    if len(output)>len(col_list):
        col_list=[*output]
col_list.insert(0,'user_id')
print("col_list = %s" % col_list)
"""

#user_data=json_output(results[1])
#print(user_data)
Tbl_maint("tl_user_info")
print(Tbl_maint.user_info_update('bill@fred.com'))