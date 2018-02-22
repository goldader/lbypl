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

    def create_tbl(json_output):
        # a set of json output from the json_output function
        # creates a basic table with all fields as TEXT to be tuned later
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        #conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # use the json to generate a list of column names
        col_nms=[]
        col_nms.append('user_id')
        for k in json_output.keys():
            col_nms.append(k)

        # set a phrase to be used in the table creation statement
        col_phrase=""
        for i in range(0,len(col_nms)):
            if i < len(col_nms)-1:
                col_phrase+="'%s' TEXT," % col_nms[i].lower()
            elif i == len(col_nms)-1:
                col_phrase+="'%s' TEXT" % col_nms[i].lower()
        phrase="create table %s (%s);" % (Tbl_maint.tbl_name,col_phrase)
        #print(phrase)

        #write the data to the database creating a new table from the json input
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

        # identify the user and the provider id related to the access token
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

    def user_account_update(primary_email):
        # Updates db with truelayer account information and calls necessary routines for table maintenance
        import requests
        from auth import Auth, access_token
        from json_iter import json_output
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        c = conn.cursor()

        # identify the user and the provider id related to the access token
        Auth(primary_email)
        user=Auth.uid
        c.execute("select provider_id from accounts where user_id=?",[user])
        token = access_token(c.fetchone()[0])

        # call truelayer for user info updates
        info_url = "https://api.truelayer.com/data/v1/accounts"
        token_phrase = "Bearer %s" % token
        headers = {'Authorization': token_phrase}
        z = requests.get(info_url, headers=headers)
        results = z.json()['results']

        for i in range(0,len(results)):
            # call json parser to flatten data
            account_data = json_output(results[i])
            #print(account_data)

            # Call the append routine in case new user data has additional columns
            Tbl_maint.append_tbl(account_data)

            # add user to the account_data for db referencing
            account_data['user_id']=user

            # create a SQL execution phrase and determine update or insert
            c.execute("select * from tl_account_info where user_id=? and account_id=?",(user,account_data['account_id']))
            if c.fetchone()==None:
                print("insert statement")
                # 'insert' option
                # align the user data to the columns in order so the inserts work correctly
                user_values = Tbl_maint.data_col_match(account_data)
                # define the number of inserts
                places = "?," * (len(Tbl_maint.columns()) - 1) + '?'
                # set the insert phrase
                phrase = "INSERT INTO tl_account_info VALUES (%s)" % (places)
                phrase = phrase.strip()

                # insert new data
                try:
                    c.execute(phrase, user_values)
                except sqlite3.Error as e:
                    conn.rollback()
                    status = {'code': 400, 'desc': 'User info update failed. DB error.'}
                    return (status)
                finally:
                    conn.commit()
                    status = {'code': 200, 'desc': 'Success'}
                    #return (status)

            else:
                print("update statement")
                # 'update' option
                update_set=""
                count=1
                # create the data update construct avoiding user and account identifiers
                for k,v in account_data.items():
                    if k == 'user_id' or k == 'account_id':
                        pass
                    else:
                        if count==len(account_data)-2:
                            update_set+="'%s' = '%s'" % (k,v)
                            count+=1
                        else:
                            update_set+="'%s' = '%s'," % (k,v)
                            count+=1
                # create the update phrase
                phrase = "update tl_account_info set %s where user_id='%s' and account_id='%s'" % (update_set,user,account_data['account_id'])
                phrase = phrase.strip()

                # update existing data
                try:
                    c.execute(phrase)
                except sqlite3.Error as e:
                    conn.rollback()
                    status = {'code': 400, 'desc': 'User info update failed. DB error.'}
                    return (status)
                finally:
                    conn.commit()
                    status = {'code': 200, 'desc': 'Success'}
                    #return (status)
        status = {'code': 200, 'desc': 'Success'}
        conn.close()
        return(status)

    def user_account_balance(primary_email):
        import requests
        from auth import Auth, access_token
        from json_iter import json_output
        import sqlite3
        conn = sqlite3.connect(Tbl_maint.db)
        c = conn.cursor()

        # identify the user and the provider id related to the access token
        Auth(primary_email)
        user=Auth.uid
        c.execute("select provider_id from accounts where user_id=?",[user])
        token = access_token(c.fetchone()[0])

        # setup the truelayer API for balance requests
        token_phrase = "Bearer %s" % token
        headers = {'Authorization': token_phrase}

        # get the account_ids associated with the user
        c.execute("select account_id from tl_account_info where user_id=?", [user])
        accounts=c.fetchall()
        for i in range(0,len(accounts)):
            account_id=accounts[i]
            info_url="https://api.truelayer.com/data/v1/accounts/%s/balance" % account_id[0]
            z = requests.get(info_url, headers=headers)
            results = z.json()['results']

            # parse results for writing to tables
            for i in range(0, len(results)):
                balance_data = json_output(results[i])
                balance_data['user_id']=user
                balance_data['account_id']=account_id[0]

                # Call the append routine in case new user data has additional columns
                Tbl_maint.append_tbl(balance_data)

                # create variable places for use in the SQL insert statement to ensure the insert works correctly
                places = "?," * (len(Tbl_maint.columns()) - 1) + '?'

                # create a SQL execution phrase
                phrase = "INSERT INTO tl_account_balance VALUES (%s)" % (places)
                phrase = phrase.strip()

                # align the user data to the columns in order so the inserts work correctly
                balance_values = Tbl_maint.data_col_match(balance_data)

                # write the balance data to the table for update
                try:
                    c.execute(phrase,balance_values)
                except sqlite3.Error as e:
                    conn.rollback()
                    status = {'code': 400, 'desc': 'User info update failed. DB error.'}
                    return (status)
                finally:
                    conn.commit()
                    status = {'code': 200, 'desc': 'Success'}
        return (status)


Tbl_maint('tl_account_balance')
Tbl_maint.user_account_balance('goldader@gmail.com')

"""
import requests
from auth import Auth,access_token
from json_iter import json_output

Auth('bill@fred.com')
token=access_token('mock')

info_url="https://api.truelayer.com/data/v1/accounts"
token_phrase="Bearer %s" % token
headers = {'Authorization': token_phrase}

z=requests.get(info_url, headers=headers)

all_results=z.json()
results=all_results['results']

# instantiate the class
Tbl_maint("tl_account_info")

#Tbl_maint.user_account_update('bill@fred.com')
#value=json_output(results[0])
#print(value)
#Tbl_maint.create_tbl(value)
"""