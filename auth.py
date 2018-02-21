class Auth(object):
    """TL_auth creates and/or updates tokens for user accounts via truelayer.
        for more information on truelayer see http://docs.truelayer.com/"""
    email_primary=""
    uid=""
    client_id="goldader-znsm"
    client_secret="xlbucdespuhv4zsdf8y2z"
    token_url="https://auth.truelayer.com/connect/token"
    red_url="https://console.truelayer.com/redirect-page"

    def __init__(self, email_primary):
        self.email_primary = email_primary
        import user

        user.User(email_primary)
        Auth.email_primary=email_primary
        Auth.uid=user.uid()

def account_columns():
    # returns the columns in the accounts table as a list for simpler use in various update routines.
    import sqlite3
    connection = sqlite3.connect('/Users/jgoldader/lbypl.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.execute('SELECT * FROM accounts')
    # instead of cursor.description:
    row = cursor.fetchone()
    col_list = row.keys()
    return (col_list)

def extra_data_update(extra_data,provider_id):
    # sub-routine to the main update routine for submitting additional data acquired from truelayer.
    # requires extra_data to be submitted as a dictionary
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    if len(extra_data) > 0:
        try:
            extra_data = '"%s"' % extra_data
            extra_data = extra_data.replace("{", "")
            extra_data = extra_data.replace("}", "")
            xdata_phrase = "UPDATE accounts SET other=%s WHERE user_id='%s' and provider_id='%s'" % (extra_data, Auth.uid, provider_id)
            c.execute(xdata_phrase)
        except sqlite3.Error as e:
            conn.rollback()
            status={'code':'400','desc':'db write failed'}
            return(status)
        finally:
            conn.commit() #no close is called as that is left for the main body of code
            status={'code':'200','desc':'success'}
            return(status)

def refresh(provider_id):
    # use to refresh the authorisation token from truelayer and update it in the database
    import requests
    from datetime import datetime

    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()

    std_dict={} # used to map json response data to our db tables for writing.
    extra_data={} # used to capture json response content that is not yet utilised. passed a dictionary to our db.

    # get the last known refresh token for the user / provider combination
    c.execute("select r_token from accounts where user_id=? and provider_id=?", (Auth.uid, provider_id))
    refresh_token=c.fetchone()[0]
    payload = {'grant_type': 'refresh_token', 'client_id': Auth.client_id, \
               'client_secret': Auth.client_secret, 'refresh_token': refresh_token}
    r_lasttime=datetime.now()
    z=requests.post('https://auth.truelayer.com/connect/token', data=payload) # call truelayer to refresh the token and set the call time

    if z.status_code==200: #check if API call is a success
        #map the json response to our data structure
        temp_dict = z.json()
        #print(z.json()) # leave this line in the code for potential future debugging

        # translate a portion of the json response into a dictionary mathing our table. The rest goes into extra_data
        map_dict={'access_token':'a_token','expires_in':'r_sec','refresh_token':'r_token'} #later, change this to a mapping table and generate dynamically
        std_dict={'a_token':'','r_sec':'','r_token':''}
        for k in temp_dict.keys():
            if k in map_dict.keys():
                std_dict[map_dict[k]]=str(temp_dict[k]) #creates the std_dict to be unpacked for writing later
            else:
                extra_data[k]=str(temp_dict[k])
        std_dict['r_lasttime']=str(r_lasttime)

        # create a SQL execution phrase
        count=1
        phrase=""
        for k in std_dict.keys():
            if count == 1:
                phrase += "%s='%s'," % (k, str(std_dict[k]))
                count += 1
            elif count < len(std_dict):
                phrase += "%s='%s'," % (k, str(std_dict[k]))
                count += 1
            else:
                phrase += "%s='%s'" % (k, str(std_dict[k]))
        phrase = "UPDATE accounts SET %s WHERE user_id = '%s' and provider_id = '%s' and r_token= '%s'" % (phrase, Auth.uid, provider_id, refresh_token)
        phrase = phrase.strip()

        # write data to the database
        try:
            c.execute(phrase)
        except sqlite3.Error as e:
            conn.rollback()
            status={'code':400,'desc':'db update failed'}
            return(status)
        finally:
            conn.commit()
            if len(extra_data) > 0:
                if extra_data_update(extra_data, provider_id) == 400:
                    status = {'code': 201,'desc': 'Partial success. Token update succeeded but extra data update failed.'}
                    conn.close()
                    return(status)
                else:
                    status = {'code': 200, 'desc': 'Success'}
                    conn.close()
                    return (status)
            else:
                status = {'code': 200, 'desc': 'Success'}
                conn.close()
                return(status)

    else:
        status = {'code': z.status_code, 'desc': 'Truelayer update failure'}
        # print(z.status_code) # leave in the code for potential debugging
        return (status)

def new_token(provider_id,access_code):
    # use to acquire a new access token from truelayer and update it in the database
    # requires the front end to have already been provided an authorisation token

    import requests
    from datetime import datetime

    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()

    std_dict={} # used to map json response data to our db tables for writing.
    extra_data={} # used to capture json response content that is not yet utilised. passed a dictionary to our db.

    # determine if the user / provider combination already exist
    c.execute("select * from accounts where user_id=? and provider_id=?", (Auth.uid, provider_id))
    if c.fetchone()!=None:
        status = {'code': 400, 'desc': 'User/provider combination already exist. Use refresh instead'}
        conn.close()
        return (status)

    # the user does not exist so call Truelayer and exchange code for access token
    else:
        payload = {'grant_type': 'authorization_code', 'client_id': Auth.client_id, \
                   'client_secret': Auth.client_secret, 'redirect_uri': Auth.red_url, 'code': access_code}
        r_lasttime=datetime.now()
        z=requests.post(Auth.token_url, data=payload) # call truelayer to get the token and set the call time

        # check the api response and process or fail out
        if z.status_code==200: #check if API call is a success
            temp_dict = z.json()
            #temp_dict={"access_token": "JWT-ACCESS-TOKEN-HERE","expires_in": 3600,"token_type": "Bearer","refresh_token": "REFRESH-TOKEN-HERE"}
            # delete this comment and the line above when done testing

            # translate a portion of the json response into a dictionary mathing our table. The rest goes into extra_data
            map_dict={'access_token':'a_token','expires_in':'r_sec','refresh_token':'r_token'} #later, change this to a mapping table and generate dynamically
            std_dict={'a_token':'','r_sec':'','r_token':''}
            for k in temp_dict.keys():
                if k in map_dict.keys():
                    std_dict[map_dict[k]]=str(temp_dict[k]) #creates the std_dict to be unpacked for writing later
                else:
                    extra_data[k]=str(temp_dict[k])
            std_dict['r_lasttime']=str(r_lasttime)
            std_dict['user_id']=str(Auth.uid)
            std_dict['provider_id']=str(provider_id)

            # create a value set from the dictionary that is in the exact order of the table columns
            col_list = account_columns()
            values=[]
            for i in range(0,len(col_list)):
                if col_list[i] in std_dict.keys():
                    values.append(std_dict[col_list[i]])
                    #print("values = %s" % values) # delete after testing
                else:
                    values.append("")
                    #print("values = %s "% values) # delete after testing

            # create variable places for use in the SQL insert statement to ensure the insert works correctly
            places = "?," * (len(col_list) - 1) + '?'

            # create a SQL execution phrase
            phrase = "INSERT INTO accounts VALUES (%s)" % (places)
            phrase = phrase.strip()

            # write data to the database
            try:
                c.execute(phrase,values)
            except sqlite3.Error as e:
                conn.rollback()
                status={'code':400,'desc':'db update failed'}
                return(status)
            finally:
                conn.commit()
                if len(extra_data) > 0:
                    if extra_data_update(extra_data, provider_id) == 400:
                        status = {'code': 201,'desc': 'Partial success. Token update succeeded but extra data update failed.'}
                        conn.close()
                        return(status)
                    else:
                        status = {'code': 200, 'desc': 'Success'}
                        conn.close()
                        return (status)
                else:
                    status = {'code': 200, 'desc': 'Success'}
                    conn.close()
                    return(status)
        else:
            status = {'code': z.status_code, 'desc': z.json()}
            return(status)

def access_token(provider_id):
    from datetime import datetime,timedelta

    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()

    # get the expiry value for the current token
    c.execute("select r_lasttime, r_sec, a_token from accounts where user_id=? and provider_id=?", (Auth.uid, provider_id))
    v=(c.fetchone())
    r_lasttime=v[0]
    r_sec=v[1]-120 # use an expiry somewhat shorter in case processing time expires a token prior to using it
    # set expiry value
    expiry=timedelta(seconds=r_sec)+datetime.strptime(r_lasttime.split(".")[0],'%Y-%m-%d %H:%M:%S')
    # compare now to the expiry to determine if the old token is usable or a new one is required
    if datetime.now() < expiry: # issue the existing code
        return(v[2])
    else: # requests a new token, save it to the db, and issue it
        refresh(provider_id)
        c.execute("select a_token from accounts where user_id=? and provider_id=?", (Auth.uid, provider_id))
        return(c.fetchone()[0])



#Various testing calls - delete when not required any longer

#Auth("bill@fred.com")
#new_token('mock','f73283d2a1eb8cdf026a9ca1543263e9906a622005dff3950d4d809939321de0')