import user
import tl_auth

import sqlite3

conn = sqlite3.connect('/Users/jgoldader/lbypl.db')
c = conn.cursor()

tl_auth.TL_auth("goldader@gmail.com")
#print(new_token('mock','12345'))
col_list=tl_auth.account_columns()
print("col_list = %s" % col_list)
cols=""
for i in range(0,len(col_list)):
    cols+="%s," % col_list[i]
print(cols)
values=('1','2','3','4','5','6','7','8','9')

new_dict={}
for i in range(0,len(col_list)):
    new_dict[col_list[i]]=""
print("new_dict = %s" % new_dict)

places="?,"*(len(col_list)-1)+'?'
print(places)
phrase = "INSERT INTO accounts VALUES (%s)" % (places)
phrase = phrase.strip()
print(phrase)

#c.execute("insert into accounts values (?,?,?,?,?,?,?,?,?)", values)
#conn.commit()

#c.execute("insert into accounts")

#tl_auth.TL_auth("bill@fred.com")
#tl_auth.refresh('mock')

#user.User("bill@fred.com")
#print(user.uid())
#print(user.f_name())
#print(user.l_name())
#print(user.email_secondary())
#print(user.gender())
#print(user.postcode())
#print(user.other())
#print(user.user_columns())

#updates={'f_name':'bobby','l_name':'smith'}
#updates={'f_name':'geoff','facebook_id':'l@l.com','old_id':'crap'}
#user.user_update(updates)
"""

#import tl_auth
#tl_auth.TL_auth('bill@fred.com')
#print(tl_auth.TL_auth)
#tl_auth.test()

"""
