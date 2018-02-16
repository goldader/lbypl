import requests
import uuid
import sqlite3

url="https://auth.truelayer.com/api/providers"
conn=sqlite3.connect('/Users/jgoldader/lbypl.db')
c=conn.cursor()
table='providers'

z=requests.get(url)
providers=(z.json())
my_dict={}

def populate_providers():
    c.execute("SELECT COUNT(*) FROM providers")
    if c.rowcount != -1:
        status={'code':400,'desc':'Disallowed Purge of Providers. Try Update instead'}
        return(status)
    else:
        z = requests.get(url)
        providers = (z.json())
        for i in range(0,len(providers)):
            my_dict=providers[i]
            provider_uuid=uuid.uuid4()
            my_dict['provider_uuid'] = str(provider_uuid)
            c.execute("INSERT INTO providers (provider_id,display_name,logo_url,scopes,provider_UUID) VALUES (?,?,?,?,?)" \
                  , (my_dict['provider_id'], my_dict['display_name'], my_dict['logo_url'], str(my_dict['scopes']),
                     my_dict['provider_uuid']))
        conn.commit()
        status={'code':200,'desc':'Success'}
        return(status)

def reset_providers(confirm):
    if confirm=="Yes. Reset the table.":
        c.execute("DELETE FROM providers")
        conn.commit()
        status={'code':200,'desc':'Success'}
        return(status)
    else:
        status={'code':400,'desc':'You have not reset the table.'}
        return(status)


def update_providers():
    z = requests.get(url)
    providers = (z.json())
    count=1
    for i in range(0,len(providers)):
        my_dict=providers[i]
        c.execute("SELECT * FROM providers WHERE provider_id=?",[my_dict['provider_id']])
        if c.fetchone()==None:
            provider_uuid=uuid.uuid4()
            my_dict['provider_uuid'] = str(provider_uuid)
            c.execute("INSERT INTO providers (provider_id,display_name,logo_url,scopes,provider_UUID) VALUES (?,?,?,?,?)" \
                  , (my_dict['provider_id'], my_dict['display_name'], my_dict['logo_url'], str(my_dict['scopes']),
                     my_dict['provider_uuid']))
            conn.commit()
        else:
            c.execute("UPDATE providers SET display_name=?, logo_url=?, scopes=? WHERE provider_id=?" \
                      , (my_dict['display_name'], my_dict['logo_url'], str(my_dict['scopes']), my_dict['provider_id']))
            conn.commit()
    status = {'code': 200, 'desc': 'Success'}
    return(status)
