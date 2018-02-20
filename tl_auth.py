class TL_auth(object):
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
        TL_auth.email_primary=email_primary
        TL_auth.uid=user.uid()

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
            xdata_phrase = "UPDATE accounts SET other=%s WHERE user_id='%s' and provider_id='%s'" % (extra_data,TL_auth.uid,provider_id)
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
    import sqlite3
    from datetime import datetime

    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()

    std_dict={} # used to map json response data to our db tables for writing.
    extra_data={} # used to capture json response content that is not yet utilised. passed a dictionary to our db.

    # get the last known refresh token for the user / provider combination
    c.execute("select r_token from accounts where user_id=? and provider_id=?", (TL_auth.uid,provider_id))
    refresh_token=c.fetchone()[0]
    payload = {'grant_type': 'refresh_token', 'client_id': TL_auth.client_id, \
               'client_secret': TL_auth.client_secret, 'refresh_token': refresh_token}
    r_lasttime=datetime.now()
    z=requests.post('https://auth.truelayer.com/connect/token', data=payload) # call truelayer to refresh the token and set the call time

    if z.status_code==200: #check if API call is a success
        #map the json response to our data structure
        temp_dict = z.json()

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
        phrase = "UPDATE accounts SET %s WHERE user_id = '%s' and provider_id = '%s'" % (phrase,TL_auth.uid,provider_id)
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
            if extra_data_update(extra_data,provider_id)==400:
                status={'code':201,'desc':'Partial success. Token update succeeded but extra data update failed.'}
                conn.close()
                return(status)
            else:
                status={'code':200,'desc':'Success'}
                conn.close()
                return(status)

    else:
        status = {'code': z.status_code, 'desc': 'Truelayer update failure'}
        print(z.status_code)
        return (status)
        #print('Refresh failed with status code %s ' % z.status_code)
        #return(z.status_code)

TL_auth("bill@fred.com")
print(refresh('mock'))


"""


access_code='dafbed9a729d46a51447f0849510f23a0f632ecca8e8af1fcba4676089507a75'
refresh_token='6c3a6a3acd3d058c9a814b12b202a5276245fc199417a98c9de362493167cad3'
my_file='/Users/jgoldader/Desktop/truelayer.txt'
my_dict={}
"""