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
        if row==None: # fix this later by adding a row and then deleting it. use a random identifier to accomplish
            return(400)
        else:
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
                col_phrase+="'%s' TEXT," % col_nms[i].lower()
            elif i == len(col_nms)-1:
                col_phrase+="'%s' TEXT" % col_nms[i].lower()
        phrase="create table %s (%s);" % (Tbl_maint.tbl_name,col_phrase)
        #print(phrase)
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

    def append_tbl(data):
        """ this function will append columns to truelayer tables with fields that appear in json repsonses.
            it should not be utilised directly for other table maintenance.
            'data' should be a dictionary generally the flattened truelayer json
        """
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        c = conn.cursor()

        # get the columns of the table to be checked. requires class initialisation
        col_list = Tbl_maint.columns()
        if col_list==400: # this should be removed later when the col_list features is updated
            status={'code':400,'desc':'Alter failed. add temp data to table to resolve and then delete temp data'}
            return(status)
        else:
            # check each key in the data to see if a column exists
            for k in data.keys():
                if k.lower() in col_list:
                    pass
                # if a column does not exist corresponding to the key, create it
                else:
                    phrase="alter table %s add column '%s' text" % (Tbl_maint.tbl_name,k.lower())
                    try:
                        c.execute(phrase)
                    except sqlite3.Error as e:
                        conn.rollback()
                        status = {'code': 400, 'desc': 'Table append failed. DB error.'}
                        return (status)
                    finally:
                        conn.commit()
            status = {'code': 200, 'desc': 'Success'}
            conn.close()
            return(status)

    def user_info_update(primary_email):
        # Updates db with truelayer user information and calls necessary routines for table maintenance
        import requests
        from auth import Auth, access_token
        from json_iter import json_output
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        c = conn.cursor()

        # identify the user and then call the truelayer apis for the dataset
        Auth(primary_email)
        user=Auth.uid
        c.execute("select provider_id from accounts where user_id=?",[user])
        token = access_token(c.fetchone()[0])

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
            Tbl_maint.append_tbl(user_data)

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

Auth('goldader@gmail.com')
token=access_token('hsbc')

#info_url="https://api.truelayer.com/data/v1/info"
#token_phrase="Bearer %s" % token
#headers = {'Authorization': token_phrase}

#z=requests.get(info_url, headers=headers)

#all_results=z.json()
#results=all_results['results']

#user_data=json_output(results[1])

#print(user_data)
Tbl_maint('tl_user_info')
#print(Tbl_maint.create_tbl(columns))
#print(Tbl_maint.append_tbl({'ag':1,'fe':2,'x':3}))
print(Tbl_maint.user_info_update("goldader@gmail.com"))
"""