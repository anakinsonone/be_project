from __future__ import division, print_function
from flask import Flask, render_template, request,session,logging,flash,url_for,redirect,jsonify,Response
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import os
import numpy as np
#model
import sys
import os
import glob


# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from  tensorflow.keras.models import load_model
from  tensorflow.keras.preprocessing import image

with open('config.json', 'r') as c:
    params = json.load(c)["params"]
# Define a flask app
local_server = True
app = Flask(__name__,template_folder='template')
dic = {0 : 'Bacterial_spot', 1 : 'Early_blight' ,2:'Tomato_blight',3:'Leaf_mold',4:'Tomato_Healthy'}

model = load_model('model_vgg19.h5')

model.make_predict_function()

def predict_label(img_path):
    i = image.load_img(img_path, target_size=(224, 224))
    i = image.img_to_array(i)/255.0
    i = np.expand_dims(i, axis=0)
    p=model.predict(i) 
    p=np.argmax(p,axis=1)
    return dic[p[0]]

# MODEL_PATH = 'model_inception.h5'
# model = load_model(MODEL_PATH)

app.secret_key = 'super-secret-key'
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(80), nullable=False)

class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    mobile = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(80), nullable=False)



@app.route("/")
def home():
    return render_template('index.html',params=params)

@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/contact",methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        contact= request.form.get('contact')
        message= request.form.get('message')
        entry = Contact(name=name,email=email,contact=contact,message=message)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)
        

@app.route("/register",methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        mobile= request.form.get('mobile')
        password= request.form.get('password')
        user=Register.query.filter_by(email=email).first()
        if user:
            flash('Account already exist!Please login','success')
            return redirect(url_for('register'))
        if not(len(name)) >3:
            flash('length of name is invalid','error')
            return redirect(url_for('register'))
        if (len(mobile))<10:
            flash('invalid mobile number','error')
            return redirect(url_for('register'))
        if (len(password))<8:
            flash('length of password should be greater than 7','error')
            return redirect(url_for('register'))
        else:
            flash('You have registtered succesfully','success')
        entry = Register(name=name,mobile=mobile,email=email,password=password)
        db.session.add(entry)
        db.session.commit()
    return render_template('register.html',params=params) 

@app.route("/login",methods=['GET','POST'])
def login():
    if (request.method== "GET"):
        if('email' in session and session['email']):
            return redirect(url_for('leaf'))
        else:
            return render_template("login.html", params=params)
    if (request.method== "POST"):
        email = request.form["email"]
        password = request.form["password"]
        login = Register.query.filter_by(email=email, password=password).first()
        if login is not None:
            session['email']=email
            return redirect(url_for('leaf'))
        else:
            flash("plz enter right password",'error')
    return render_template('login.html',params=params)



@app.route("/leaf", methods = ['GET','POST'])
def leaf():
    return render_template('main.html',params=params)
@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
    if request.method == 'POST':
        img = request.files['my_image']

        img_path = "static/uploads/" + img.filename 
        img.save(img_path)

        p = predict_label(img_path)

    return render_template("main.html", prediction = p, img_path = img_path)

@app.route("/logout", methods = ['GET','POST'])
def logout():
    session.pop('email')
    return redirect(url_for('home'))

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('leafindex.html', params=params)






if __name__ == '__main__':
    app.run(debug=True)
