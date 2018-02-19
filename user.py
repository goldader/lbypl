"""Users creates and updates user information. To be used during registration as well as updates
from sources such as bank data"""

class User(object):

    def __init__(self,email_primary):
        #initialise the class and creates a user_id if necessary
        self.email_primary=email_primary
        import uuid
        import sqlite3
        conn=sqlite3.connect('/Users/jgoldader/lbypl.db')
        c=conn.cursor()

        c.execute("SELECT * FROM users WHERE email_primary=?", [email_primary])
        if c.fetchone()==None:
            try:
                user_id=str(uuid.uuid4())
                #print(user_id,self.email_primary)
                c.execute("INSERT INTO users ('user_id','email_primary') VALUES (?,?)", (user_id,email_primary))
            except sqlite3.Error as e:
                conn.rollback()
                conn.close()
            finally:
                conn.commit()
                conn.close()
        #return(status)

    def __repr__(self):
        #returns the UUID associated with a user or a code 400 if they do not exist
        import sqlite3
        conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email_primary=?", [self.email_primary])
        id=c.fetchone()
        conn.close()
        if id == None:
            return('400')
        else:
            return(id[0])

def f_name(email):
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT f_name FROM users WHERE user_id=?", [uid(email)])
    return(c.fetchone()[0])

def l_name(email):
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT l_name FROM users WHERE user_id=?", [uid(email)])
    return(c.fetchone()[0])

def email_secondary(email):
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT email_secondary FROM users WHERE user_id=?", [uid(email)])
    return (c.fetchone()[0])

def postcode(email):
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT postcode FROM users WHERE user_id=?", [uid(email)])
    return (c.fetchone()[0])

def gender(email):
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT gender FROM users WHERE user_id=?", [uid(email)])
    return (c.fetchone()[0])

def other(email):
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT other FROM users WHERE user_id=?", [uid(email)])
    return (c.fetchone()[0])

def user_columns():
    #returns the columns in the users table as a list for simpler use in various user update routines.
    import sqlite3
    connection = sqlite3.connect('/Users/jgoldader/lbypl.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.execute('SELECT * FROM users')
    # instead of cursor.description:
    row = cursor.fetchone()
    col_list = row.keys()
    return(col_list)

def uid(email):
    #returns the UUID associated with a user or a code 400 if they do not exist
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE email_primary=?", [email])
    id = c.fetchone()
    conn.close()
    if id == None:
        return ('400')
    else:
        return (id[0])

def user_update(updates,user_id):
    #updates user information passed in via a dictionary with a corresponding user_id
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    col_list=user_columns()
    db_updates={}
    extra_data={}
    #delete user id from the dictionary if passed in for updates. these routines are for user attributes
    if 'user_id' in updates.keys():
        del updates['user_id']

    #strip extra data from the update string to be stored as a dictionary in the table
    for k in updates.keys():
        if k in col_list:
            db_updates[k]=updates[k]
        else:
            extra_data[k]=updates[k]

    #create the update query dynamically so we execute only 1 SQL update statement instead of a loop of them
    if len(db_updates)>1:
        count=1
        phrase=""
        for k in db_updates.keys():
            if count==1:
                phrase+="%s='%s'," % (k,db_updates[k])
                count+=1
            elif count<len(db_updates):
                phrase+="%s='%s'," % (k,db_updates[k])
                count+=1
            else:
                phrase+="%s='%s'" % (k,db_updates[k])
        phrase="UPDATE users SET %s WHERE user_id= '%s'" % (phrase, user_id)
        phrase=phrase.strip()
        try:
            c.execute(phrase)
        except sqlite3.Error as e:
            conn.rollback()
        finally:
            conn.commit()
            try:
                extra_data='"%s"' % extra_data
                extra_data=extra_data.replace("{","")
                extra_data=extra_data.replace("}","")
                xdata_phrase = "UPDATE users SET other=%s WHERE user_id='%s'" % (extra_data, user_id)
                c.execute(xdata_phrase)
            except sqlite3.Error as e:
                conn.rollback()
            finally:
                conn.commit()
    else:
        for k in db_updates.keys():
            phrase="UPDATE users SET %s='%s' WHERE user_id='%s'" % (k,db_updates[k],user_id)
            phrase=phrase.strip()
        try:
            c.execute(phrase)
        except sqlite3.Error as e:
            conn.rollback()
        finally:
            conn.commit()
            try:
                extra_data='"%s"' % extra_data
                extra_data=extra_data.replace("{","")
                extra_data=extra_data.replace("}","")
                xdata_phrase = "UPDATE users SET other=%s WHERE user_id='%s'" % (extra_data, user_id)
                c.execute(xdata_phrase)
            except sqlite3.Error as e:
                conn.rollback()
            finally:
                conn.commit()
    conn.close()


print(f_name('goldader@gmail.com'))
print(l_name('goldader@gmail.com'))
print(email_secondary("goldader@gmail.com"))
print(postcode("goldader@gmail.com"))
print(gender("goldader@gmail.com"))
print(other("goldader@gmail.com"))



""" Various Test calls are below. Delete when no longer necessary

new_user=User("goldader@gmail.com")
print(uid("goldader@gmail.com"))
col_list=user_columns()
print(col_list)

user=uid('goldader@gmail.com')

updates={'f_name':'fred','l_name':'george','email_secondary':'jgoldader@gmail.com','age':'45','facebook_id':'jgoldader'}
user_update(updates,user)

updates={'f_name':'frank','age':'72'}
user_update(updates,user)

"""