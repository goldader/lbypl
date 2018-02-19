"""Users creates and updates user information. To be used during registration as well as updates
from sources such as bank data"""

class User(object):

    import sqlite3
    conn=sqlite3.connect('/Users/jgoldader/lbypl.db')
    c=conn.cursor()

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

    def john(self,email):
        #returns the UUID associated with a user or a code 400 if they do not exist
        import sqlite3
        conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email_primary=?", [email])
        id = c.fetchone()
        conn.close()
        if id == None:
            return ('400')
        else:
            return (id[0])
        print('fucking anything')

""" - work in progress to create a list of the fiels in the table so we can update them programmatically
    def columns(self):
        import sqlite3
        connection = sqlite3.connect('/Users/jgoldader/lbypl.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.execute('SELECT * FROM users')
        # instead of cursor.description:
        row = cursor.fetchone()
        names = row.keys()
        #print(names)
        return(names)
"""

#new_user=User("goldader@gmail.com")

