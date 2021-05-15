from app import app, mysql
from flask import render_template, flash, request, redirect, url_for, session, logging
from passlib.hash import sha256_crypt
from functools import wraps
#from models import Member
from forms import RegisterForm, ArticleForm
import os
from werkzeug.utils import secure_filename

import PyPDF2
import textract
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from flask_mysqldb import MySQL
import os
import pygal
import numpy as np
import matplotlib.pyplot as plt
import requests
from matplotlib.backends.backend_pdf import PdfPages

import csv
import re
import spacy
from nltk.tokenize import word_tokenize
import sys
import importlib
importlib.reload(sys)
import pandas as pd
# sys.setdefaultencoding('utf8')
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import sys, getopt
import numpy as np
from bs4 import BeautifulSoup
# import urllib2
from urllib.request import urlopen

nltk.download('punkt')

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#Function converting pdf to string
def convert(fname,pages=None):
    if not pages:
        pagenums=set()
    else:
        pagenums=set(pages)

    output=StringIO()
    manager=PDFResourceManager()
    converter=TextConverter(manager, output, laparams=LAParams())
    interpreter=PDFPageInterpreter(manager,converter)

    infile = open(fname,'rb')
    for page in PDFPage.get_pages(infile,pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text=output.getvalue()
    output.close
    return text



def extract_phone_numbers(string):
    r= re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers=r.findall(string)
    return [re.sub(r'\D', '', number) for number in phone_numbers]

#Function to extract Email address from a string using regex
def extract_email_addresses(string):
    r=re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)

#Function to extract all Decimals
def extract_decimals(strings):
    r=re.compile(r"\d+\.\d+\d")
    return r.findall(strings)

#converting pdf to string

#information extraction function

with open('college.csv','r') as f:
    reader=csv.reader(f)
    college_list=list(reader)

name=[]
email=[]
cpi=[]
hsc=[]
ssc=[]
phone_number=[]
institution=[]
skills=[]
length=0

def getdata(filename):
    resume_string=convert(filename)
    resume_string1=resume_string
    resume_string=resume_string.replace(',',' ')

    resume_string=resume_string.lower()
    tokens=word_tokenize(resume_string1)
    name.append(tokens[0] +" "+ tokens[1])

    y=extract_phone_numbers(resume_string)
    y1=[]
    for i in range(len(y)):
        if(len(y[i])>9):
            y1.append(y[i])
    phone_number.append(y1[0])

    email.append(extract_email_addresses(resume_string)[0])

    scores=extract_decimals(resume_string)

    ssc.append(scores[2])
    hsc.append(scores[1])
    cpi.append(scores[0])

    for college in college_list:
        if college[0].lower() in resume_string:
            institution.append(college[0])
    print(institution[0])


def getStatistics(string,field):
    csvFileName = field +".csv"
    with open(csvFileName,'rt') as f:
        reader=csv.reader(f)
        parameter_list=list(reader)

    hits=0
    paraList=[]
    for parameter in parameter_list:
        if parameter[0] in string:
            hits=hits+1
            paraList.append(parameter[0])
    skills.append(hits)
    print(skills[0])
    print("The hit parameters are:")
    print(paraList)
    return hits

#ends here

#@app.route('/')
#def index():
#	firstmember = Member.query.first()
#	return '<h1>The first member is:'+ firstmember.name +'</h1>'
#Index


@app.route('/')
def index():
    return render_template('home.html')
# # About
# @app.route('/about')
# def about():
#     return render_template('about.html')
#Articles
@app.route('/articles')
def articles():
    #Create Cursor
    cur=mysql.connection.cursor()
    #get articles
    result=cur.execute("SELECT * FROM articles")
    articles=cur.fetchall()
    if result>0:
        return render_template('articles.html',articles=articles)
    else:
        msg='No Articles Found'
        return render_template('articles,html',msg=msg)
    cur.close()

#Single Article
@app.route('/article/<string:id>/')
def article(id):
    #Create cursor
    cur=mysql.connection.cursor()
    #Get article
    result=cur.execute("SELECT * FROM articles WHERE id=%s", [id])
    article=cur.fetchone()
    return render_template('article.html',article=article)

#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name = form.name.data
        email=form.email.data
        username=form.username.data
        password= sha256_crypt.encrypt(str(form.password.data))
        #create cursor
        cur = mysql.connection.cursor()
        #execute query
        cur.execute("INSERT INTO users(name , email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        #commit to DB
        mysql.connection.commit()
        #close
        cur.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        #GEt form fields(not using WTForms)
        username=request.form['username']
        password_candidate=request.form['password']
        #create cursor
        cur=mysql.connection.cursor()
        #Get user by username
        result=cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result>0:
            #GEt Stored HASH
            data=cur.fetchone()
            password=data[3]
            #compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed
                session['logged_in']=True
                session['username']=username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error="IInvelid Login"
                return render_template('login.html', error=error)
                #close
                cur.close()
        else:
            error="Userame not found"
            render_template('login.html', error=error)
    return render_template('login.html')

#apply
ALLOWED_EXTENSIONS=set(['pdf'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gitRepoCount(username):
    url = "https://api.github.com/users/"+ username +"/repos"
    r=requests.get(url)
    data=r.json()
    return len(data)

def gitFollower(username):
    url= "https://api.github.com/users/"+ username
    r=requests.get(url)
    data=r.json()
    return data['followers']

def gitLocation(username):
    url="https://api.github.com/users/"+ username
    r=requests.get(url)
    data=r.json()
    return data['location']

def pdf_folder(foldername):
    for files in os.listdir(foldername):
        if file.endswith(".pdf"):
            file_name=os.path.join("./uploads", file)

def user_performance_graph(ssc,hsc,cpi,followers,repos,name):
    my_path='.'
    with PdfPages(my_path + '/allpdf/' + str(name) + '.pdf') as pdf:
        given_title="user's performance"
        y_axis=[]
        y_axis.append(repos)
        y_axis.append(hsc)
        y_axis.append(cpi)
        y_axis.append(followers)

        x_axis=['GIT REPOSITORIES','HSC','CPI','GIT FOLLOWERS']
        ind=np.arrange(len(x_axis))
        plt.bar(ind,y_axis)
        plt.xticks(ind,x_axis)
        plt.title(given_title,color='r')
        plt.rcParams['figure.figsize']=(10,6)
        pdf.savefig()

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method=='POST':
        #get form fields(not using wtforms)
        #resume=request.form[resume]
        github_username=request.form['github_username']
        if github_username=='':
            flash('Please enter your github username','danger')
            return render_template('apply.html')
        if 'file' not in request.files:
            flash('Please upload your resume', 'danger')
            return render_template('apply.html')
        file = request.files['file']
        if file.filename=='':
            flash('Please upload your resume', 'danger')
            return render_template('apply.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            foldername="./uploads/"
            getdata(foldername+filename)
            pdf_text=convert(foldername+filename)
            skillA = getStatistics(pdf_text, "techAtt")
            skillB = getStatistics(pdf_text, "bdAtt")
            skillC = getStatistics(pdf_text, "samAtt")
            skillD = getStatistics(pdf_text, "afAtt")
            location = gitLocation(github_username)
            followers = gitFollower(github_username)
            numRepos = gitRepoCount(github_username)

            print(cpi[0])
            cur = mysql.connection.cursor()
            cur1 = mysql.connection.cursor()
            x=0
            print(skillA)
            print(skillB)
            print(skillC)
            print(skillD)
            '''print(location)
			print(followers)
			print(numRepos)'''

            '''user_performance_graph(ssc[x],hsc[x],cpi[x],followers,numRepos,name)'''
            cur.execute("Insert into candidate_details Values('"+str(name[x])+"','"+str(email[x])+"','"+str(phone_number[x])+"','"+str(skillA)+"','"+str(skillB)+"','"+str(skillC)+"','"+str(skillD)+"','"+str(ssc[x])+"','"+str(hsc[x])+"','"+str(cpi[x])+"','"+str(institution[x])+"','"+str(followers)+"','"+str(numRepos)+"','0')")
            # cur.execute("commit")
            cur1.execute("commit")
            flash("INSERTED")
            flash('Successfully Uploaded '+str(github_username), 'success')
        else:
            flash('Please upload a valid format', 'danger')
    return render_template('apply.html')

# @app.route('/insert')
# def insert():
#     cur = mysql.connection.cursor()
#     cur1 = mysql.connection.cursor()
#     x=0
#     cur.execute("Insert into candidate_details Values('"+str(name[x])+"','"+str(email[x])+"','"+str(phone_number[x])+"','"+str(skills[x])+"','"+str(ssc[x])+"','"+str(hsc[x])+"','"+str(cpi[x])+"','"+str(institution[x])+"','0',0,'0')")
#     cur1.execute("commit")
#     return "INSERTED INTO DATABASE"

#Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()
    # Get articles
    cur.execute("select name,email,phone,no_of_repo,no_of_followers from candidate_details")
    articles = cur.fetchall()
    if len(articles) > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    #Close Connection
    cur.close()

# Analyze
@app.route('/analyze', methods=['GET', 'POST'])
@is_logged_in
def analyze():
    if request.method == 'POST':
        nop = request.form['nop']
        skilla, skillb, skillc, skilld = 0, 0, 0, 0
        if request.form.get('skilla'):
            skilla = 1
        if request.form.get('skillb'):
            skillb = 1
        if request.form.get('skillc'):
            skillc = 1
        if request.form.get('skilld'):
            skilld = 1

        # session['nop'] = nop
        session['nop'], session['skilla'], session['skillb'], session['skillc'], session['skilld'] = nop, skilla, skillb, skillc, skilld
        # flash(str(nop)+" "+str(skilla)+" "+str(skillb)+" "+str(skillc)+" "+str(skilld), 'success')
        return redirect(url_for('results'))

    # # Create cursor
	# cur = mysql.connection.cursor()
 	# # Get articles
	# result = cur.execute("SELECT * FROM articles WHERE author=%s", (session['username'],))
 	# articles = cur.fetchall()
 	# if result > 0:
	# 	return render_template('analyze.html', articles=articles)
	# else:
	# 	msg = 'No Articles Found'
	# 	return render_template('analyze.html', msg=msg)
	# # Close connection
	# cur.close()

    return render_template('analyze.html')

# Results
@app.route('/results')
@is_logged_in
def results():
    nop, skilla, skillb, skillc, skilld = session.get('nop'), session.get('skilla'), session.get('skillb'), session.get('skillc'), session.get('skilld', None)
    # flash(str(nop)+" "+str(skilla)+" "+str(skillb)+" "+str(skillc)+" "+str(skilld), 'success')
    # flash('str(nop)', 'success')

    # flash('str(nop)', 'success')
    # Create cursor
    cur = mysql.connection.cursor()
    # Get articles
    cur.execute("select NAME,EMAIL,PHONE,((8*CPI+4*HSC+3*SSC+10*No_of_followers+3*No_of_Repo+50*No_of_skills+10*skill_b+6*skill_d+4*skill_c)*'"+str(skilla)+"'+(8*CPI+4*HSC+3*SSC+10*No_of_followers+3*No_of_Repo+12*No_of_skills+50*skill_b+4*skill_d+1*skill_c)*'"+str(skillb)+"'+(8*CPI+4*HSC+3*SSC+10*No_of_followers+3*No_of_Repo+6*No_of_skills+10*skill_b+50*skill_d+6*skill_c)*'"+str(skillc)+"'+(8*CPI+4*HSC+3*SSC+10*No_of_followers+3*No_of_Repo+6*No_of_skills+4*skill_b+10*skill_d+50*skill_c)*'"+str(skilld)+"') as score from candidate_details order by score desc limit "+str(nop)+" ")

    # flash("INSERTED")
    articles = cur.fetchall()
    print(articles)
    if len(articles) > 0:
        return render_template('results.html', articles=articles)
    else:
        msg = 'No Results Found'
        return render_template('results.html', msg=msg)
    # Close connection
    cur.close()

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        # Create cursor
        cur = mysql.connection.cursor()
        # Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)
# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()
    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id=%s", [id])
    article = cur.fetchone()
    # Get form
    form = ArticleForm(request.form)
    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        # Create cursor
        cur = mysql.connection.cursor()
        # Execute
        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)
# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()
    # Execute
    cur.execute("DELETE FROM articles WHERE id=%s", [id])
    # Commit to DB
    mysql.connection.commit()
    # Close connection
    cur.close()
    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))
