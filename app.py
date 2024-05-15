from flask import Flask, render_template, url_for, redirect, request ,session,flash
from flask_mysqldb import MySQL
import mysql.connector
from passlib.hash import sha256_crypt
from functools import wraps # extra 
from werkzeug.utils import secure_filename
import threading
import time

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tms'
app.config['SECRET_KEY'] = '5rfkgxeui56465edtyfyugkgyfyry'

UPLOAD_FOLDER = 'dynamic/Image'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)


ALLOWED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'svg', 'webp', 'ico', 'psd', 'ai', 'eps'
}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# this is also extra



def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'ulogged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('userlogin'))

    return wrap

def login_requireddriver(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'dlogged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('driverindex'))

    return wrap



def login_requiredadmin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'alogged_in' in session:  # Use 'alogged_in' for admin users
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('alogin'))  # Redirect to appropriate login page

    return wrap

# uptil here



# index session here


@app.route('/', methods=['POST','GET'])
def welcome():
 db = '''CREATE TABLE IF NOT EXISTS dst(
 dstId INT AUTO_INCREMENT PRIMARY KEY,
 dId INT,
 abtn INT,
 auth INT,
 tgl INT

 )'''
 cur = mysql.connection.cursor()
 cur.execute(db)
 return render_template('welcome.html')




# user session here



@app.route('/userlogin', methods=['POST','GET'])
def userlogin():
    
    db = '''CREATE TABLE IF NOT EXISTS user(
    id INT (11) PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200),
    username VARCHAR(100),
    password VARCHAR(100),
    phone VARCHAR(100)
    )'''

    res = mysql.connection.cursor()
    res.execute(db)
    res.close()
    if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM user WHERE username = %s" , [username])
      res = cur.fetchone()
        # cur.close()
      if res:
            pwd = res[3]
            if sha256_crypt.verify(password, pwd):
                session["ulogged_in"]=True
                session["userId"] = res[0]
                return redirect(url_for('userpage'))
            else:
                flash('You have Entered A Wrong Password, Try again')
                return redirect(url_for('userlogin'))
      else:
                flash('This User not Found ')
                flash('To Create Account Click on Sign Up button')
                return redirect(url_for('userregister'))
        

    return render_template('userlogin.html')







@app.route('/userlogout')
def userlogout():
    if 'ulogged_in' in session:
        
        # v= session['ulogged_in']
        session.pop('ulogged_in',None)
        session.pop('userId',None)
          # Clear the session for the specific user type
        return redirect(url_for('userlogin'))
    else:
        return redirect(url_for('userlogin'))









@app.route('/userregister', methods=['POST','GET'])
def userregister():


    if request.method == 'POST':
        # id = request.form['id']
        name = request.form['name']
        username = request.form['username']
        # phone = request.form['phone']
        phone = request.form['phone']
        pswd =  sha256_crypt.encrypt(str( request.form['password']))
        cur = mysql.connection.cursor()
        qr = '''INSERT INTO user(name, username,password,phone) VALUES (%s,%s,%s,%s)'''
        cur.execute(qr, [ name, username, pswd,phone])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('userlogin'))

    return render_template('user-register.html')


@app.route('/userpage' , methods=['POST','GET'])
@login_required
def userpage():
 userId = session['userId']
 cur=mysql.connection.cursor()
 cur.execute('SELECT * FROM user WHERE id =%s ',[userId])
 data = cur.fetchone()
 if data:
    name = data[1]
    
 return render_template('userdb.html', name = name)


@app.route('/booktype' , methods=['POST','GET'])
@login_required
def booktype():
    
 return render_template('booktype.html')





@app.route('/advancebooking' , methods=['POST','GET'])
@login_required
def advancebooking():
    userId = session['userId']
    if request.method == 'POST':
    #   bookid = ''
      cid = request.form['cid']
      cname = request.form['cname']
      phone = request.form['phone']
      pickup = request.form['pickup']
      dropoff= request.form['dropoff']
      cartype = request.form['cartype']
      date = request.form['date']
      time = request.form['time']
      ticket = 'active'
      ctm = request.form['ctm']

      cur = mysql.connection.cursor()
      cur.execute('INSERT INTO advance (id,cid,ticket,name,phone,pickup,dropoff,cartype,pickupdate,pickuptime,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ',[userId,cid,ticket,cname,phone,pickup,dropoff,cartype,date,time,ctm])
      mysql.connection.commit()
      cur.close()
      return redirect(url_for('mybookings' ))

    
    return render_template('abpage.html')





@app.route('/currentbooking' , methods=['POST','GET'])
@login_required
def currentbooking():
    userId = session['userId']
    res = mysql.connection.cursor()
    res.execute('SELECT * FROM user WHERE id=%s', [userId])
    data = res.fetchall()
    for x in data:
       name = x[1]
       mobile = x[4]
    if request.method == 'POST':
      bookid = ''
      cid = request.form['cid']
      ticket = 'active'
      pickup = request.form['pickup']
      dropoff= request.form['dropoff']
      ctm = request.form['ctm']
      cartype = request.form['cartype']
      cur = mysql.connection.cursor()
      cur.execute('INSERT INTO current (id,cid,ticket,name,mobile,pickup,dropoff,cartype,time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s) ',[userId,cid,ticket,name,mobile,pickup,dropoff,cartype,ctm])
      mysql.connection.commit()
      cur.close()
      return redirect(url_for('ridejourneycu' ,cid = cid, pickup=pickup,droff=dropoff ))
   
    return render_template('cbpage.html', name = name, mobile= mobile)




@app.route('/sharetaxi' , methods=['POST','GET'])
@login_required
def sharetaxi():
 
    userId = session['userId']
    if request.method == 'POST':
      bookid = ''
      cid = request.form['cid']
      cname = request.form['cname']
      phone = request.form['phone']
      pickup = request.form['pickup']
      dropoff= request.form['dropoff']
      numberof= request.form['numberof']
      cartype = request.form['cartype']
      ticket = 'active'
      ctm = request.form['ctm']
    #   date = request.form['date']
    #   time = request.form['time']

      cur = mysql.connection.cursor()
      cur.execute('INSERT INTO share(id,cid,ticket,name,phone,pickup,dropoff,numof,cartype,time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ',[userId,cid,ticket,cname,phone,pickup,dropoff,numberof,cartype,ctm])
      mysql.connection.commit()
      cur.close()

      return redirect(url_for('ridejourneysh', cid=cid,pickup=pickup,dropoff=dropoff))
    return render_template('stbpage.html')


@app.route('/privatedrivers' , methods=['POST','GET'])
@login_required
def privatedrivers():
    userId = session['userId']
    if request.method == 'POST':
      bookid = ''
      cid = request.form['cid']
      cname = request.form['cname']
      phone = request.form['phone']
      address = request.form['address']
      state= request.form['state']
      city= request.form['city']
      ctm = request.form['ctm']
      pincode = request.form['pincode']
      timer = request.form['timer']
      ticket = 'active'
      cur = mysql.connection.cursor()
      cur.execute('INSERT INTO private (id,cid,ticket,name,phone,address,state,city,pincode,timerequired,time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ',[userId,cid,ticket,cname,phone,address,state,city,pincode,timer,ctm])
      mysql.connection.commit()
      cur.close()
      return redirect(url_for('privatebookingconfirm'))
    return render_template('pdpage1.html')






@app.route('/advance/ridejourney', methods=['POST','GET'])
def ridejourneyad():
   con = request.args.get('con')
   cur=mysql.connection.cursor()
   cur.execute('SELECT * FROM advance WHERE cid=%s',[con])
   data= cur.fetchall()
   cur.close()
   for x in data:
      status=x[3]
      cid=x[2]
      pickup=[6]
      dropoff=[7]
   return render_template('userjourney.html' ,cid=cid,pickup=pickup,dropoff=dropoff,status=status)


@app.route('/current/ridejourney/', methods=['POST','GET'])
def ridejourneycu():
   cid = request.args.get('cid')
   pickup = request.args.get('pickup')
   dropoff = request.args.get('dropoff')
   cur=mysql.connection.cursor()
   cur.execute('SELECT * FROM current WHERE cid=%s',[cid])
   data= cur.fetchall()
   cur.close()
   for x in data:
    status=x[3]
   return render_template('userjourneycu.html' ,cid=cid,pickup=pickup,dropoff=dropoff,status=status)

@app.route('/sharetaxi/ridejourney', methods=['POST','GET'])
def ridejourneysh():
   cid = request.args.get('cid')
   pickup = request.args.get('pickup')
   dropoff = request.args.get('dropoff')
   cur=mysql.connection.cursor()
   cur.execute('SELECT * FROM share WHERE cid=%s',[cid])
   data= cur.fetchall()
   cur.close()
   for x in data:
      status=x[3]
   return render_template('userjourneysh.html' ,cid=cid,pickup=pickup,dropoff=dropoff,status=status)






@app.route('/My_Bookings')
def mybookings():
   userId = session['userId']
   ad =mysql.connection.cursor()
   cu=mysql.connection.cursor()
   sh =mysql.connection.cursor()
   pr =mysql.connection.cursor()
   ad.execute('SELECT * FROM advance WHERE id=%s ',[userId])
   cu.execute('SELECT * FROM current WHERE id=%s ',[userId])
   sh.execute('SELECT * FROM share WHERE id=%s ',[userId])
   pr.execute('SELECT * FROM private WHERE id=%s ',[userId])

   adv = ad.fetchall()
   cur = cu.fetchall()
   sha = sh.fetchall()
   pri = pr.fetchall()

   ad.close()
   cu.close()
   sh.close()
   pr.close()

   return render_template('Userbookinglist.html' ,advance = adv, current = cur, share=sha, private=pri)




@app.route('/booking_confirm')
def privatebookingconfirm():
   return render_template('pdpage1.1.html')




@app.route('/about' , methods=['POST','GET'])
# @login_required
def about():
 return render_template('about2.html')



@app.route('/aboutpage' , methods=['POST','GET'])
@login_required
def aboutpage():
 return render_template('about1.html')


# before login

@app.route('/readmore' , methods=['POST','GET'])
# @login_required
def readmore():
 return render_template('readmore2.html')


# after login

@app.route('/moreabout' , methods=['POST','GET'])
@login_required
def moreabout():
 return render_template('readmore.html')


@app.route('/service' , methods=['POST','GET'])
# @login_required
def service():
 return render_template('service.html')


@app.route('/service/currentbooking-readmore' , methods=['POST','GET'])
# @login_required
def currentbookingreadmore():
 return render_template('cbrm.html')


@app.route('/service/advancebooking-readmore' , methods=['POST','GET'])
# @login_required
def advancebookingreadmore():
    
 return render_template('abrm.html')


@app.route('/service/sharetaxibooking-readmore' , methods=['POST','GET'])
# @login_required
def sharetaxireadmore():
 return render_template('stbrm.html')


@app.route('/service/privatedriver-readmore' , methods=['POST','GET'])
# @login_required
def privatedriverreadmore():
 return render_template('pdrm.html')

# before login

@app.route('/ouravailability' , methods=['POST','GET'])
# @login_required
def ouravailability():
 return render_template('availability2.html')

# after login  

@app.route('/availability' , methods=['POST','GET'])
# @login_required
def availability():
 return render_template('availability.html')


@app.route('/auto-readmore' , methods=['POST','GET'])
# @login_required
def autoreadmore():
 return render_template('auto.html')



@app.route('/nano-readmore' , methods=['POST','GET'])
# @login_required
def nanoreadmore():
 return render_template('nano.html')

@app.route('/minicooper-readmore' , methods=['POST','GET'])
def minicooperreadmore():
 return render_template('minicooper.html')


@app.route('/hyundaisantro-readmore' , methods=['POST','GET'])
def hyundaisantroreadmore():
 return render_template('hyundaisantro.html')


@app.route('/innova-readmore' , methods=['POST','GET'])
def innovareadmore():
 return render_template('innova.html')


@app.route('/tatawinger-readmore' , methods=['POST','GET'])
def tatawingerreadmore():
 return render_template('tatawinger.html')


@app.route('/autobookingtype' , methods=['POST','GET'])
def autobookingtype():
 return render_template('autobooktype.html')


@app.route('/nanobookingtype' , methods=['POST','GET'])
def nanobookingtype():
 return render_template('autobooktype.html')


@app.route('/minicooperbookingtype' , methods=['POST','GET'])
def minicooperbookingtype():
 return render_template('minicooperbooktype.html')


@app.route('/hyundaisantrobookingtype' , methods=['POST','GET'])
def hyundaisantrobookingtype():
 return render_template('minicooperbooktype.html')


@app.route('/innovabookingtype' , methods=['POST','GET'])
def innovabookingtype():
 return render_template('minicooperbooktype.html')


@app.route('/tatawingerbookingtype' , methods=['POST','GET'])
def tatawingerbookingtype():
 return render_template('stbpage.html')


@app.route('/contact' , methods=['POST','GET'])
def contact():
 return render_template('contact.html')


@app.route('/feedback' , methods=['POST','GET'])
def feedback():
 return render_template('feedback.html')


@app.route('/menu' , methods=['POST','GET'])
def menu():
 return render_template('menu.html')


@app.route('/safety' , methods=['POST','GET'])
def safety():
 
 return render_template('safety.html')


@app.route('/do-dont' , methods=['POST','GET'])
def dodont():
 return render_template('do.html')


@app.route('/user/mybookings' , methods=['POST','GET'])
def mybooking():
 return render_template('userbookingslist.html')








@app.route('/driverindex')
def driverindex():


    
    cur = mysql.connection.cursor()
    dr = '''CREATE TABLE IF NOT EXISTS driver(
              id INT AUTO_INCREMENT PRIMARY KEY,
              name VARCHAR(100),
              drivername VARCHAR(100),
              phone INT(11),
              password VARCHAR(100),
              gender VARCHAR(100),
              address VARCHAR(100),
              age INT,
              experience VARCHAR(100),
              driving_license VARCHAR(100),
              aadhar VARCHAR(100),
              
              v1 INT,
              v2 INT,
              dimg VARCHAR(100),
              daadhar VARCHAR(100),
              ddl VARCHAR(100)
              

              )'''
   
    
    cur.execute(dr)    
    drhistory='''CREATE TABLE IF NOT EXISTS driveract(
    actid INT PRIMARY KEY AUTO_INCREMENT,
    id INT,
    cid INT,
    btyp VARCHAR(100),
    ridename VARCHAR(100),
    pickup VARCHAR(100),
    dropoff VARCHAR(100),
    cartype VARCHAR(100),
    accept VARCHAR(100),
    reject VARCHAR(100)

    
    
    )'''

    cur.execute(drhistory)
    cur.close()

    return render_template('driverindex.html')


@app.route('/driverlogin', methods=['GET', 'POST'])
def dlogin(): 
    if request.method == 'POST':
        
        name = request.form['name']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM driver WHERE drivername = %s" , [name])
        res = cur.fetchone()
        # cur.close()
        if res:
            pwd = res[4]
            if sha256_crypt.verify(password, pwd):
                session["dlogged_in"]=True
                session["driverId"] = res[0]
                return redirect(url_for('driverdashboard'))
            else:
                flash('You have Entered A Wrong Password, Try again')
                return redirect(url_for('driverindex'))
        else:
                flash('This User not Found ')
                flash('To Create Account Click on Sign Up button')
                return redirect(url_for('driverindex'))
        
    return render_template('driverlogin.html')






@app.route('/driverlogout')
def driverlogout():
    if 'dlogged_in' in session:
        
        # v= session['ulogged_in']
        session.pop('dlogged_in',None)
        session.pop('driverId',None)
          # Clear the session for the specific user type
        return redirect(url_for('driverindex'))
    else:
        return redirect(url_for('driverindex'))




@app.route('/Driver_register', methods=['POST'])
def driverregister():
    if request.method == 'POST':
        # id = request.form['id']
        name = request.form['name']
        drivername = request.form['drivername']
        # phone = request.form['phone']
        phone = request.form['phone']
        v1 = 0
        v2 = 0
        pswd =  sha256_crypt.encrypt(str( request.form['password']))
        cur = mysql.connection.cursor()
        qr = '''INSERT INTO driver(name,drivername,phone,password,v1,v2) VALUES (%s,%s,%s,%s,%s,%s)'''
        cur.execute(qr, [ name,drivername, phone, pswd,v1,v2])
        mysql.connection.commit()

        cur.execute("SELECT * FROM driver WHERE drivername = %s" , [drivername])
        res = cur.fetchall()
        for x in res:
         session["dlogged_in"]=True
         session["driverId"] = x[0]
        
        cur.close()

    return redirect(url_for('popupload'))






@app.route('/drivertemp', methods=['POST','GET'])
def popupload():
 dId = session['driverId']
 
 abtn = 0
 auth = 0
 tgl = 0
 cur = mysql.connection.cursor()
 cur.execute('INSERT INTO dst (dId,abtn,auth,tgl) VALUES(%s,%s,%s,%s)', [dId,abtn,auth,tgl])
 mysql.connection.commit()
 return render_template('popup.html')




@app.route('/admindriverpage', methods=['GET'])
def admindriverpage():
    cur = mysql.connection.cursor()
    qr = '''SELECT * FROM driver '''
    cur.execute(qr)
    asma = cur.fetchall()
    cur.close()
    return render_template('admindriverpage.html', noor=asma)

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/link')
def link():
    return render_template('link.html')

@app.route('/title')
def title():
    return render_template('title.html')

@app.route('/driverhomepage', methods=['GET'])
@login_requireddriver
def driverdashboard():

        
    db = mysql.connection.cursor()
    advance= '''CREATE TABLE IF NOT EXISTS advance(
    bookid INT AUTO_INCREMENT PRIMARY KEY,
    id INT,
    cid INT,
    ticket VARCHAR(100),
    name VARCHAR(100),
    phone VARCHAR(100),
    pickup VARCHAR(100),
    dropoff VARCHAR(100),
    cartype VARCHAR(100),
    km INT,
    price INT,
    pickupdate VARCHAR(100),
    pickuptime VARCHAR(100),
    time VARCHAR(100)

    ) '''

    current= '''CREATE TABLE IF NOT EXISTS current(
    bookid INT AUTO_INCREMENT PRIMARY KEY,
    id INT,
    cid INT,
    ticket VARCHAR(100),
    name VARCHAR(100),
    mobile VARCHAR(100),
    pickup VARCHAR(100),
    dropoff VARCHAR(100),
    km INT,
    cartype VARCHAR(100),
    price INT,
    time VARCHAR(100)


    ) '''

    share= '''CREATE TABLE IF NOT EXISTS share(
    bookid INT AUTO_INCREMENT PRIMARY KEY,
    id INT,
    cid INT,
    ticket VARCHAR(100),
    name VARCHAR(100),
    phone VARCHAR(100),
    pickup VARCHAR(100),
    dropoff VARCHAR(100),
    numof VARCHAR(100),
    km INT,
    price INT,
    cartype VARCHAR(100),
    time VARCHAR(100)


    ) '''

    private= '''CREATE TABLE IF NOT EXISTS private(
    bookid INT AUTO_INCREMENT PRIMARY KEY,
    id INT,
    cid INT,
    ticket VARCHAR(100),
    name VARCHAR(100),
    phone VARCHAR(100),
    address VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    pincode VARCHAR(100),
    hr INT,
    price INT,
    timerequired VARCHAR(100),
    time VARCHAR(100)
    
    ) '''
    db.execute(advance )
    db.execute(current )
    db.execute(share )
    db.execute(private)


    did = session['driverId']
    val = 'active'
    adv = mysql.connection.cursor()
    curr =mysql.connection.cursor()
    sha =mysql.connection.cursor()
    home = mysql.connection.cursor()
    home2 = mysql.connection.cursor()
    adv.execute("SELECT * FROM advance WHERE ticket=%s" , [val])
    curr.execute("SELECT * FROM current WHERE ticket=%s" , [val])
    sha.execute("SELECT * FROM share WHERE ticket=%s" , [val])
    home.execute("SELECT * FROM driver WHERE id=%s" , [did])
    home2.execute("SELECT * FROM dst WHERE dId=%s" , [did])
    
    advance = adv.fetchall()
    current = curr.fetchall()
    share = sha.fetchall()
    driver = home2.fetchall()

    adv.close()
    curr.close()
    sha.close()
    home.close()
    home2.close()
    


    # cur.execute("SELECT * FROM pri ")

    return render_template('driverhomepage.html' ,advance=advance, current=current,share=share, driver = driver)



@app.route('/driveradvance/<content>', methods=['POST','GET'])
def driveradvance(con):
#    if request.method=="POST":
      
    cur =mysql.connection.cursor()
    cur.execute('DELETE FROM advance WHERE cid = %s;', [con,])
    # cur.execute('DELETE FROM current WHERE cid = %s;' [con,])
    # cur.execute('DELETE FROM share WHERE cid = %s;' [con,])
        
        
        
      
    return redirect(url_for('driverdashboard'))




@app.route('/drivercurrent/<content>', methods=['POST','GET'])
def drivercurrent(con):
#    if request.method=="POST":
      
    cur =mysql.connection.cursor()
    cur.execute('DELETE FROM current WHERE cid = %s;', [con,])
    # cur.execute('DELETE FROM current WHERE cid = %s;' [con,])
    # cur.execute('DELETE FROM share WHERE cid = %s;' [con,])
        
        
        
      
    return redirect(url_for('driverdashboard'))

import os
# from werkzeug.utils import secure_filename
@app.route('/driver/credential_details', methods=['POST'])
def credentials():
   dId =session['driverId']


   if not os.path.exists(app.config['UPLOAD_FOLDER']):
          os.makedirs(app.config['UPLOAD_FOLDER'])

   if request.method=='POST':
      name = request.form['name']
      driverphoto =request.files['driverphoto']
      driveraadhar =request.files['driveraadhar']
      driverdl =request.files['driverdl']
      phone = request.form['phone']
      gender = request.form['gender']
      address = request.form['address']
      age = request.form['age']
      experience = request.form['experience']
      dl = request.form['dl']
      aadhar = request.form['aadhar']
      v1 = 0
      v2 = 1
      driverpic = driverphoto.filename
      driveraad = driveraadhar.filename
      driverd = driverdl.filename
      driverphoto.save(os.path.join(app.config['UPLOAD_FOLDER'], driverpic))
      driveraadhar.save(os.path.join(app.config['UPLOAD_FOLDER'], driveraad))
      driverdl.save(os.path.join(app.config['UPLOAD_FOLDER'], driverd))
      cur = mysql.connection.cursor()


      

      
      cur.execute('''
    UPDATE driver
    SET                 
  name =%s,            
  phone =%s ,
  gender =%s ,
  address = %s,
  age =%s ,
  experience = %s,
  driving_license = %s,
  aadhar = %s,
  v1=%s,
  v2=%s,
    dimg=%s,
    daadhar=%s,
    ddl=%s                
WHERE id=%s''',[name,phone,gender,address,age,experience,dl,aadhar,v1,v2,driverpic,driveraad,driverd,dId])
      mysql.connection.commit()
      abtn = 1
      auth = 0
      res = mysql.connection.cursor()
      res.execute('''UPDATE dst
                  SET 
                  abtn=%s,
                  auth=%s
                  WHERE  dId=%s ''', [abtn,auth,dId])
      
      mysql.connection.commit()          
   return redirect(url_for('driverdashboard')) 



@app.route("/driverform")
def driverform():

    dId = session['driverId']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM driver WHERE id=%s  ' ,[dId]) 
    val = cur.fetchall()
    for x in val:
       name = x[1]
       phone = x[3]
       
    return render_template("driverform.html", name=name,phone=phone)


@app.route('/drivershare/<content>', methods=['POST','GET'])
def drivershare(con):
     
    cur =mysql.connection.cursor()
    cur.execute('DELETE FROM share WHERE cid = %s;', [con,])
      
        
        
      
    return redirect(url_for('driverdashboard'))




@app.route('/driverreject/<content>')
def driverreject():
   return redirect(url_for('driverdashboard'))

@app.route("/driverprofile")
def driverprofile():
    driverId = session['driverId']
    cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM booking WHERE id=%s" , [userId])

    # cur = mysql.connection.cursor()
    qur =''' SELECT * FROM driver WHERE id = %s  '''



    cur.execute(qur,  [driverId])





    res = cur.fetchall()

    return render_template("profile.html", data = res)



@app.route("/RideHistoryPage")
def RideHistoryPage():

    
    return render_template("RideHistoryPage.html")


@app.route("/driversettings")
def driversettings():
    return render_template("driversettings.html")



@app.route('/logout')
def logout():
    
    session.clear()
    return redirect(url_for('userpage'))


# @app.route("/logout")
# def logout():
#     return render_template("logout.html")



@app.route('/driverjourney/active/', methods=['POST','GET'])
def driverjourney():
   cid = request.args.get('cid')
   pickup = request.args.get('pickup')
   drop = request.args.get('drop')
   return render_template('drjourney.html', cid = cid, pickup=pickup,drop=drop )
@app.route('/driver/rideover')
def rideover():
   return redirect('')

# dba= mysql.connection.cursor()

@app.route('/driver/ridecancleadvance/<string:val>')
def ridecancleadvance(val):
   dba= mysql.connection.cursor()
   dba.execute('DELETE FROM advance WHERE cid =%s',[val])
   mysql.connection.commit()
   dba.close()
   return redirect('mybookings')


@app.route('/driver/ridecanclecurrent/<string:val>')
def ridecanclecurrent(val):
   dba= mysql.connection.cursor()
   dba.execute('DELETE FROM current WHERE cid =%s',[val])
   mysql.connection.commit()
   return redirect('mybookings')


@app.route('/driver/ridecancleshare/<val>')
def ridecancleshare(val):
   dba= mysql.connection.cursor()
   dba.execute('DELETE FROM share WHERE cid =%s',[val])
   mysql.connection.commit()
   return redirect('mybookings')





@app.route('/driver/ad/<data>/<val>', methods = ['GET', 'POST'])
def adaccept(data,val):
    status = 'accepted'
    cur = mysql.connection.cursor()
    if val == 'no':
        result = 'expired'
        cur.execute("UPDATE share SET ticket=%s WHERE cid =%s",[result,data,])
        mysql.connection.commit()
    else:
        cur.execute("UPDATE advance SET ticket=%s WHERE cid =%s",[status,data,])
        mysql.connection.commit()

    cur.execute('SELECT * FROM advance WHERE cid=%s',[data])
    adv = cur.fetchall()
    cur.execute('INSERT INTO ')
    for x in adv:
       pickup =x[6]
       drop =x[7]
    cur.close()
    return redirect(url_for('driverjourney', cid = data, pickup=pickup,drop=drop ))  



@app.route('/driver/cu/<data>/<val>', methods = ['GET', 'POST'])
def cuaccept(data,val):
    status = 'accepted'
    cur = mysql.connection.cursor()
    res = mysql.connection.cursor()
    res.execute('SELECT * FROM current WHERE cid=%s',[data])
    adv = res.fetchall()
    for x in adv:
        pickup =x[6]
        drop =x[7]
    if val == 'no':
        result = 'expired'
        cur.execute("UPDATE current SET ticket=%s WHERE cid =%s",[result,data,])
        mysql.connection.commit()
        cur.close()
        

         
        return redirect(url_for('driverdashboard'))
        
    elif(val == 'yes'):
        cur.execute("UPDATE current SET ticket=%s WHERE cid =%s",[status,data,])
        mysql.connection.commit()
        return redirect(url_for('driverjourney', cid = data, drop=drop,pickup=pickup ))  
   



@app.route('/driver/sh/<data>/<val>', methods = ['GET', 'POST'])
def shaccept(data,val):
    
    cur = mysql.connection.cursor()
    if val == 'no':
        result = 'expired'
        cur.execute("UPDATE share SET ticket=%s WHERE cid =%s",[result,data,])
        mysql.connection.commit()
    else:
        status = 'accepted'
        cur.execute("UPDATE share SET ticket=%s WHERE cid =%s",[status,data,])
        mysql.connection.commit()
    
    cur.execute('SELECT * FROM share WHERE cid=%s',[data])
    adv = cur.fetchall()
    for x in adv:
       pickup =x[6]
       drop =x[7]
    cur.close()
    return redirect(url_for('driverjourney', cid = data, pickup=pickup,drop=drop ))  



@app.route('/deletebookingadvance/<string:id_data>', methods = ['GET', 'POST'])
def deletebookingad(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM advance WHERE cid =%s",[id_data])
    mysql.connection.commit()
    flash("User Has Been Deleted Successfully")
    return redirect(url_for('driverdashboard'))  



@app.route('/deletebookingcurrent/<string:id_data>', methods = ['GET', 'POST'])
def deletebookingcu(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM current WHERE cid =%s",[id_data])
    mysql.connection.commit()
    flash("User Has Been Deleted Successfully")
    return redirect(url_for('driverdashboard'))  


@app.route('/deletebookingshare/<string:id_data>', methods = ['GET', 'POST'])
def deletebookingsh(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM share WHERE cid =%s",[id_data])
    mysql.connection.commit()
    flash("User Has Been Deleted Successfully")
    return redirect(url_for('driverdashboard'))  



@app.route("/userdetails")
def userdetails():
    return render_template("userdetails.html")


@app.route("/driverdetails")
def driverdetails():
    return render_template("driverdetails.html")


@app.route("/authorization")
def authorization():
    return redirect(url_for(''))



@app.route('/admin/driver_authorization')
def adriverauth():
   cur = mysql.connection.cursor()
   cur.execute('SELECT * FROM driver')
   data = cur.fetchall()
   cur.close()
   return render_template('adminauthorize.html',data=data)








































@app.route('/admin/dac/<val>')
def adc(val):
   cur= mysql.connection.cursor()
   abtn = 0
   auth = 1
   cur.execute('''UPDATE dst
               SET
               abtn=%s,
               auth=%s
                WHERE
               dId =%s
                 ''',[abtn,auth,val])
   mysql.connection.commit()
   cur.close()
   return redirect('')
   



@app.route('/admin/dar/<val>')
def adr(val):
   cur= mysql.connection.cursor()
   abtn = 0
   auth = 0
   dt = val
   cur.execute('''UPDATE dst
               SET
               abtn=%s,
               auth=%s
                WHERE
               dId =%s
                 ''',[abtn,auth,dt])
   mysql.connection.commit()
   cur.close()
   return redirect('')
   


   

@app.route('/admin/dap/<val>')
def adp(val):
   cur= mysql.connection.cursor()
   abtn = 0
   auth = 2
   cur.execute('''UPDATE dst
               SET
               abtn=%s,
               auth=%s
                WHERE
               dId =%s
                 ''',[abtn,auth,val])
   mysql.connection.commit()
   cur.close()
   return redirect('')






if __name__ == '__main__':
    app.run(debug=True)



