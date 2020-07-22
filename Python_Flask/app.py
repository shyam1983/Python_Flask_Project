from flask import Flask, render_template, request,session, redirect, url_for,flash,logging
from flask_mysqldb import MySQL
from getpass import getpass
from string import punctuation
from passlib.hash import sha256_crypt
import MySQLdb.cursors
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your secret key'

  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'BloodBank'  
mysql = MySQL(app) 
 

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        details = request.form
        fullname = details.get('fullname')
        emailid = details.get('emailid')
        mobileno = details.get('mobile_number')
        address = details.get('address')
        password = details.get('password')
        confirm = details.get('confirm')
        secure_password = sha256_crypt.encrypt(str(password))
        if " " in password:
            flash('There is a space in your password')
            return render_template("register1.html","danger")

        if len(password) not in range(5,11):
            flash("Password should be b/w 5 and 10 chars","danger")
            render_template("register1.html")

        special_chars=[True for x in password if x in punctuation]
        if len(special_chars)==0:
            flash("Your password should have atleat 1 special char","danger")
            return render_template("register1.html")

        nums=any(x.isdigit() for x in password)
        if not nums:
            flash("You should have at least 1 number","danger")
            return render_template("register1.html")
        try:
            if password == confirm:
                cur = mysql.connection.cursor()
                cur.execute("CREATE DATABASE IF NOT EXISTS Bloodbank")
                cur.execute("CREATE TABLE IF NOT EXISTS log(FULLNAME Varchar(40),EMAILID Varchar(40),MOBILENO Varchar(12),ADDRESS Varchar(255),PASSWORD Varchar(12))")
                cur.execute("INSERT INTO log(FULLNAME,EMAILID,MOBILENO,ADDRESS,PASSWORD) VALUES (%s, %s, %s,%s, %s)", (fullname,emailid,mobileno,address,password))
                mysql.connection.commit()
                cur.close()
                flash("Account Created")
                return redirect(url_for('login'))
            else:
                flash("password does not match","danger")
                return render_template("register1.html")
        except Exception as err:
            flash("Please Create Database Manualy As BloodBank","danger")
    return render_template("register1.html")
        
                



@app.route("/login" , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password1 = request.form['password2']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM log WHERE EMAILID = %s AND PASSWORD = %s', (username, password1))
        account = cursor.fetchone()
        mysql.connection.commit()
        if account:
            session['loggedin'] = True
            session['log'] = True
            session['password1'] = account['PASSWORD']
            session['username'] = account['EMAILID']

            flash("Logged in successfully","success")
            return redirect(url_for("home"))
        else:
            flash("Incorrect username/password","danger")
            return render_template('login.html')          
    return render_template("login.html")


@app.route("/donate" , methods=['GET', 'POST'])
def donate():
    if request.method == "POST":
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        phone = request.form['phone']
        bloodgroup = request.form['blood']
        lastbld= request.form['lastbld']
        dtt = datetime.now()
        cur = mysql.connection.cursor()
        if cur:
            cur.execute("CREATE TABLE IF NOT EXISTS donar(name Varchar(40),dob Date,email Varchar(40),phone Varchar(15),bloodgroup Varchar(5),lastblooddt Date,date Date)")
            cur.execute("INSERT INTO donar(name,dob, email, phone, bloodgroup,lastblooddt,date) VALUES (%s,%s,%s,%s,%s,%s,%s)",(name,dob,email,phone,bloodgroup,lastbld,dtt))
            mysql.connection.commit()
            cur.close()
            flash("Donar Has Been Added Successfully","success")
            return render_template("donate.html") 
    return  render_template("donate.html")


@app.route('/search')
def search():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM donar")
    data = cur.fetchall()
    cur.close()
    return render_template('search.html', donar=data )





@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        b_data = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        phone = request.form['phone']
        blood = request.form['blood']
        bldtm = request.form['bldtm']
        cur = mysql.connection.cursor()
        cur.execute("""
               UPDATE donar
               SET dob=%s, email=%s, phone=%s, bloodgroup=%s, lastblooddt=%s
               WHERE name=%s
            """, (dob, email, phone, blood, bldtm, b_data))
        flash("Donars Details Updated Successfully","success")
        mysql.connection.commit()
        cur.close()
        return render_template("update.html")
    return render_template("update.html")    




@app.route('/delete/<string:b_data>', methods = ['GET'])
def delete1(b_data):
    flash("Donar Has Been Deleted Successfully","success")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM donar WHERE name=%s", (b_data,))
    mysql.connection.commit()
    return redirect(url_for("search"))

                 


@app.route('/logout')
def signout():
   session.clear()
   flash("You Are  Logged Successfully","success")
   return render_template("logout.html")  
 


if __name__ == '__main__':
    app.run(debug=True)


    