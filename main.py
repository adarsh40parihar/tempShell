from flask import Flask,render_template, request, redirect, url_for, session, make_response
import mysql.connector, kubernetesg,runcmd
import os,hashlib,jwt,re,random,time
from dotenv import load_dotenv
load_dotenv()
pwd=os.getcwd().strip()
host_point = os.getenv('HOST')
secret_key = os.getenv('SECRET')
session = os.getenv('SESSION')
passwd= os.getenv('PASSWORD')
db_user = os.getenv('DB_USER')  
db_name = os.getenv('DB_NAME')  
print(pwd)
mydb = mysql.connector.connect(
  host=host_point,
  user=db_user,
  password=passwd,
  auth_plugin='mysql_native_password',
  database=db_name
)
# mydb = mysql.connector.connect(
#   host=host_point,
#   user="avnadmin",
#   password=passwd, port=11493,database="defaultdb"
# )


cursor = mydb.cursor()

app = Flask(__name__)
app.secret=secret_key
app.session=session
def createtable():
    create_table_sql = """
    CREATE TABLE  users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(63) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(127) NOT NULL,
    shell VARCHAR(100) DEFAULT NULL
);"""
    cursor.execute(create_table_sql)
    time.sleep(5)
    print(cursor.execute("show tables;").fetchone())

#createtable()

def validate(username,password,email):
        query='select * from users where username = %s or email= %s;'
        print(query)
        cursor.execute(query,(username,email))
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
            
            cursor.execute('INSERT INTO users (username, password, email, shell) VALUES ( %s, %s, %s , NULL)', (username, password, email))
            mydb.commit()
            msg = 'You have successfully registered!'
        return(msg)
    
@app.route('/',methods=['GET'])
def home():
    path='index.html'
    return render_template(path,msg='')
@app.route('/shell',methods=['GET','POST'])
def shell():
    if(request.method=='GET'):
        try:
                cookie=request.cookies.get('Token')
                user=jwt.decode(jwt=cookie,key=app.secret,algorithms=["HS256"])
                # print(user)
                query="select * from users where username = %s ;"
                # print(query)
                cursor.execute(query,(user['User'],))
                x=cursor.fetchone()
                if(not x):
                    return redirect('/login') 
                print(x[4])
                if(not x[4]):
                     
                     x=str(random.randint(1,1000000000))
                     x=hashlib.sha1(x.encode()).hexdigest()
                     print(x)
                     kubernetesg.create_pod(x, "ubuntu")
                     query="update users set shell= %s where username = %s ;"
                     cursor.execute(query,(x,user['User']))
                     mydb.commit()
                    #  print(x)   
                return render_template('/shell.html',msg='Login Done!') 
        except:
            return redirect('/login') 
    if(request.method=='POST'):
        CMD=request.form['cmd']
        print(CMD)
        try:
            cookie=request.cookies.get('Token')
            user=jwt.decode(jwt=cookie,key=app.secret,algorithms=["HS256"])
            query="select * from users where username = %s ;"
            
            cursor.execute(query,(user['User'],))
            x=cursor.fetchone()
            print(x)
            if(not x):
                return redirect('/login.html')
            print(x[4])
            if(not x[4]):
                 x=str(random.randint(1,1000000000))
                 x=hashlib.sha1(x.encode()).hexdigest()
                 kubernetesg.create_pod(x, "ubuntu")
                 query="update users set shell= %s where username = %s ;"
                 cursor.execute(query,(x,user['User']))
                 mydb.commit()
            else:
                 x=x[4]
            return render_template('/shell.html',msg=runcmd.runner(x,"ubuntu",CMD))
        except:
            return redirect('/login.html') 
@app.route('/signup',methods=['GET','POST'])
def signup():
    if(request.method=='GET'):
         return render_template('signup.html')
    elif (request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form):
        
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        msg=validate(username,password,email)
        return render_template('signup.html',msg=msg)
    elif (request.method=='POST'):
         msg='All the fields are mandatory'

@app.route('/logout',methods=['GET'])
def logout():
    cookie = request.cookies.get('Token')
    user = jwt.decode(cookie, app.secret, algorithms=["HS256"])
    print(user)
    query = "SELECT shell FROM users WHERE username = %s;"
    cursor.execute(query, (user['User'],))
    shell_id = cursor.fetchone()[0]
    if shell_id:
        query = "UPDATE users SET shell = NULL WHERE username = %s ;"
        cursor.execute(query,(user['User'],))
        mydb.commit()
        kubernetesg.delete_pod(shell_id)
    resp=make_response(redirect('login'))
    resp.set_cookie('Token','7',max_age=0)
    return resp
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
            resp = make_response(render_template('login.html',msg=''))
            
            return resp
       
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']+app.secret
        hash = hashlib.sha1(password.encode())
        password = hash.hexdigest()
        query='SELECT * FROM users WHERE username = %s AND password = %s ;'

        print(query,(username,password))
        cursor.execute(query,(username,password))
        user=cursor.fetchone()
        if user:
            cookie=jwt.encode({"User":username},app.secret,algorithm="HS256")
            resp = make_response(render_template('login.html',msg='Login Successful.'))
            resp.set_cookie('Token', cookie)
            return resp
        else:
             return render_template('login.html',msg="Wrong Password")
app.run()