class User(object):
    """Users creates and updates user information. To be used during registration as well as updates
    from sources such as bank data"""

    user=""

    def __init__(self, email_primary):
        self.email_primary = email_primary
        User.user=email_primary

def create_user():
    # creates a user_id if necessary
    import uuid
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email_primary=?", [User.user])
    if c.fetchone() == None:
        try:
            user_id = str(uuid.uuid4())
            c.execute("INSERT INTO users ('user_id','email_primary') VALUES (?,?)", (user_id, User.user))
        except sqlite3.Error as e:
            conn.rollback()
            status={'code':400,'desc':'User creation failed. DB error.'}
            conn.close()
            return(status)
        finally:
            conn.commit()
            status={'code':200,'desc':'Success'}
            conn.close()
            return(status)
    else:
        status = {'code': 200, 'desc': 'User exists'}
        return (status)

def uid():
        # returns the UUID associated with a user or a code 400 if they do not exist
        import sqlite3
        conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE email_primary=?", [User.user])
        id = c.fetchone()
        conn.close()
        if id == None:
            return ('400')
        else:
            return (id[0])

def f_name():
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT f_name FROM users WHERE user_id=?", [uid()])
    return (c.fetchone()[0])

def l_name():
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT l_name FROM users WHERE user_id=?", [uid()])
    return (c.fetchone()[0])

def email_secondary():
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT email_secondary FROM users WHERE user_id=?", [uid()])
    return (c.fetchone()[0])

def postcode():
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT postcode FROM users WHERE user_id=?", [uid()])
    return (c.fetchone()[0])

def gender():
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT gender FROM users WHERE user_id=?", [uid()])
    return (c.fetchone()[0])

def other():
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    c.execute("SELECT other FROM users WHERE user_id=?", [uid()])
    return (c.fetchone()[0])

def user_columns():
    # returns the columns in the users table as a list for simpler use in various user update routines.
    import sqlite3
    connection = sqlite3.connect('/Users/jgoldader/lbypl.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.execute('SELECT * FROM users')
    # instead of cursor.description:
    row = cursor.fetchone()
    col_list = row.keys()
    return (col_list)

def extra_data_update(extra_data):
    # sub-routine to the main update routine for submitting additional data acquired from users.
    # requires extra_data to be submitted as a dictionary
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    user=uid()
    if len(extra_data) > 0:
        try:
            extra_data = '"%s"' % extra_data
            extra_data = extra_data.replace("{", "")
            extra_data = extra_data.replace("}", "")
            xdata_phrase = "UPDATE users SET other=%s WHERE user_id='%s'" % (extra_data, user)
            c.execute(xdata_phrase)
        except sqlite3.Error as e:
            conn.rollback()
            status = {'code': '400', 'desc': 'db write failed'}
            return (status)
        finally:
            conn.commit()  # no close is called as that is left for the main body of code
            status = {'code': '200', 'desc': 'success'}
            return (status)

def user_update(updates):
    # updates user information passed in via a dictionary with a corresponding user_id
    import sqlite3
    conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
    c = conn.cursor()
    col_list = user_columns()
    db_updates = {}
    extra_data = {}
    user=uid()
    # delete user id from the dictionary if passed in for updates. these routines are for user attributes
    if 'user_id' in updates.keys():
        del updates['user_id']

    # strip extra data from the update string to be stored as a dictionary in the table
    for k in updates.keys():
        if k in col_list:
            db_updates[k] = updates[k]
        else:
            extra_data[k] = updates[k]

    # create the update query dynamically so we execute only 1 SQL update statement instead of a loop of them
    if len(db_updates) > 1:
        count = 1
        phrase = ""
        for k in db_updates.keys():
            if count == 1:
                phrase += "%s='%s'," % (k, db_updates[k])
                count += 1
            elif count < len(db_updates):
                phrase += "%s='%s'," % (k, db_updates[k])
                count += 1
            else:
                phrase += "%s='%s'" % (k, db_updates[k])
        phrase = "UPDATE users SET %s WHERE user_id= '%s'" % (phrase, user)
        phrase = phrase.strip()
        try:
            c.execute(phrase)
        except sqlite3.Error as e:
            conn.rollback()
            status = {'code': 400, 'desc': 'db update failed.'}
            conn.close()
            return (status)
        finally:
            conn.commit()
            if extra_data_update(extra_data)==400:
                status={'code':201,'desc':'Partial success. User update succeeded but extra data update failed.'}
                conn.close()
                return(status)
            else:
                status={'code':200,'desc':'Success'}
                conn.close()
                return(status)

    else:
        for k in db_updates.keys():
            phrase = "UPDATE users SET %s='%s' WHERE user_id='%s'" % (k, db_updates[k], user)
            phrase = phrase.strip()
        try:
            c.execute(phrase)
        except sqlite3.Error as e:
            conn.rollback()
            status = {'code': 400, 'desc': 'db update failed.'}
            conn.close()
            return (status)
        finally:
            conn.commit()
            if extra_data_update(extra_data)==400:
                status={'code':201,'desc':'Partial success. User update succeeded but extra data update failed.'}
                conn.close()
                return(status)
            else:
                status={'code':200,'desc':'Success'}
                conn.close()
                return(status)
    conn.close()



""" Various Test calls are below. Delete when no longer necessary

new_user=User("goldader@gmail.com")
updates={'f_name':'John','l_name':'Goldader','email_secondary':'jgoldader@gmail.com','age':'45','facebook_id':'jgoldader'}
user_update(updates)


print(uid("goldader@gmail.com"))
col_list=user_columns()
print(col_list)

user=uid('goldader@gmail.com')

user_update(updates,user)

updates={'f_name':'frank','age':'72'}

"""

