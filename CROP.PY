from flask import Flask, render_template, request,session,logging,flash,url_for,redirect,jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import os
import secrets
import json

from sklearn.externals import joblib 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

with open('config.json', 'r') as c:
    params = json.load(c)["params"]
# Define a flask app
local_server = True
app = Flask(__name__,template_folder='template')
app.secret_key = 'super-secret-key'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

model = joblib.load('model.pkl')  

class Register(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    rno = db.Column(db.Integer, primary_key=True)
    rname = db.Column(db.String(80), nullable=False)
    remail = db.Column(db.String(20), nullable=False)
    rpassword = db.Column(db.String(12), nullable=False)
    rcpassword = db.Column(db.String(120), nullable=False)

class Contact(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    return render_template('index.html',params=params)

  
@app.route("/about")
def about():
    return render_template('about.html',params=params)  


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    sendmessage=""
    errormessage=""
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone_num = request.form.get('phone_num')
        message = request.form.get('message')
        try:
            entry = Contact(name=name, phone_num= phone_num, message = message, email = email,date= datetime.now() )
            db.session.add(entry)
            sendmessage="Thank you for contacting us !.Your message has been sent."
        except Exception as e:
            errormessage="Error : "+ str(e)
        finally:
             db.session.commit()


    return render_template('contact.html',params=params ,sendmessage=sendmessage,errormessage=errormessage)


@app.route("/register", methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        name = request.form.get('user')
        email = request.form.get('email')
        password = request.form.get('pass')
        password2 = request.form.get('conpass')
        if (password==password2):
            entry = Register(rname=name, remail=email, rpassword=password, rcpassword=password2)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash("plz enter right password")
    return render_template('register.html', params=params)

@app.route("/login", methods=['GET','POST'])
def login():
    if('email' in session and session['email']):
        return render_template('crop.html', params=params)

    if (request.method== "POST"):
        email = request.form["email"]
        password = request.form["password"]
        login = Register.query.filter_by(remail=email, rpassword=password).first()
        if login is not None:
            session['email']=email
            return render_template('crop.html', params=params)
        else:
            flash("plz enter right password")
    return render_template('login.html', params=params)

  
@app.route("/predict", methods=['GET','POST'])
def predict():
    import pdb;pdb.set_trace();
    if (request.method =='POST'):
        Latitude=float(request.form['Latitude'])
        Longitude=float(request.form['Longitude'])
        ATMAX=float(request.form['ATMAX'])
        ATMIN=float(request.form['ATMIN'])
        Humidity=float(request.form['humidity'])
        Pressure=float(request.form['Pressure'])
        Tempmax=float(request.form['Tempmax'])
        Tempmin=float(request.form['Tempmin'])
        
       
        pred_args=[Latitude,Longitude,ATMAX,ATMIN,Humidity,Pressure,Tempmax,Tempmin]
        print(pred_args)
        pred_args_arr=np.array(pred_args)
        pred_args_arr=pred_args_arr.reshape(1,-1)

        decision_from_joblib = joblib.load('xgboot.pkl')  
        print(decision_from_joblib)
        
        predictions = decision_from_joblib.predict(pred_args_arr)
        print(predictions)
        
        result=round(float(predictions),2)
        print(result)
        result=str(result)
        print(result)
        return render_template('predict.html',params=params, prediction_text=result)

    return render_template('predict.html',params=params)
       

@app.route("/logout", methods = ['GET','POST'])
def logout():
    session.pop('email')
    return redirect(url_for('home'))

    
if __name__ == '__main__':
    app.run(debug=True)
