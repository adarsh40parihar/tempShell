from flask import Flask,render_template, request, redirect, url_for, session, make_response
import mysql.connector, kubernetesg,runcmd
import os,hashlib,jwt,re,random
def validate(username,password,email,cursor,app,mydb):
        query='select * from users where username = "{}" or email= "{}" '.format(username, email)
        print(query)
        cursor.execute(query)
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
           
            hash = password+app.secret
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            
            cursor.execute('INSERT INTO users VALUES ( %s, %s, %s , NULL)', (username, password, email))
            mydb.commit()
            msg = 'You have successfully registered!'
        return(msg)
def pod_manager(cursor,request,app):
    cookie=request.cookies.get('Token')
    user=jwt.decode(jwt=cookie,key=app.secret,algorithms=["HS256"])
    query="select * from users where username = '"+user['User']+"' ;"
    
    cursor.execute(query)
    x=cursor.fetchone()
    if(not x):
        return redirect('/login.html')
    if(not x[3]):
        x=str(random.randint(1,1000000000))
        x=hashlib.sha1(x.encode()).hexdigest()
        kubernetesg.create_pod(x, "ubuntu")
        query="update users set shell= '"+x+"' where username = '"+user['User']+"' ;"
        cursor.execute(query)
        mydb.commit()
    
    