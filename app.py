from flask import Flask, render_template, request,redirect, session
from models import *
from flask import jsonify
from datetime import datetime
import os
from sqlalchemy import and_

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://tynrnrzlhvclmx:e24c23f32f5d252acc414504116694b03de37bc40c05a4d1a08995ab1bb5de2b@ec2-54-211-160-34.compute-1.amazonaws.com:5432/d8u6b8lfuvoh9i"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
# creating main route, with name and dynamic name paths 
app.secret_key = "abcd"
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    if('email' in session):
        return render_template("dashboard.html",email=session['email'],fi=-1)
    return render_template("home.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method=="GET":
        return render_template("register.html")
    else:
        f_name=request.form.get('first_name')
        l_name=request.form.get('last_name')
        email=request.form.get('email')
        password=request.form.get('password')
        time1=datetime.now()
        print(time1)
        r=Register(fname=f_name,lname=l_name,email=email,password=password)
        db.session.add(r)
        # db.session.delete()
        db.session.commit()

        s=Register.query.all()
        # db.session.delete(s)
        # db.session.commit()
        # for i in s:
        #     print(f"{i.time}")
        
        return render_template("sample3.html",s=s)



@app.route("/login", methods=['GET','POST'])
def login():
    if('email' in session):
        return render_template("dashboard.html",email=session['email'],fi=-1)

    if request.method=="GET":
        return render_template("register.html")

    else:
        email1=request.form.get('email')
        password1=request.form.get('password')
        data=Register.query.all()
        # data = db.session.query(Register).filter(Register.email == email1)
        # sample=Register.query.filter_by(Register.email="abcd@gmail.com")
        e=0
        p=0
        for i in data:
            if i.email==email1:
                e=1
                if i.password==password1:
                    p=1
                    app.secret_key=i.email
                    session['email'] = app.secret_key
                    return redirect('/login/dashboard')
        if(e==0 and p==0):
            return render_template("register.html",e=0)
        if(e==1 and p==0):
            return render_template("register.html",p=0)



@app.route('/login/dashboard', methods=['GET','POST'])
def dashboard():
    if('email' in session and session['email'] ==app.secret_key):
        if request.method=="POST":
            d=request.form.get('isbn')
            # detail=Book.query.filter_by(isbn=d).all()
            # print(detail)
            val="%"+d+"%"
            b1=Book.query.filter(Book.isbn.like(val)).all()
            b2=Book.query.filter(Book.name.like(val)).all()
            b3=Book.query.filter(Book.author.like(val)).all()
            b4=Book.query.filter(Book.year.like(val)).all()
            b=b1+b2+b3+b4
            # detail=[]
            # detail1=Book.query.all()
            # for i in detail1:
            #     if(d in i.isbn):
            #         detail.append(i)
            #     elif(d in i.name):
            #         detail.append(i)
            #     elif(d in i.author):
            #         detail.append(i)
            #     elif(d in i.year):
            #         detail.append(i)
            # print(b)
            return render_template("dashboard.html",email=app.secret_key,l=b,fi=len(b))
        return render_template("dashboard.html",email=app.secret_key,fi=-1)
    

    return render_template("register.html")  



@app.route('/login/dashboard/bookdetails', methods=['GET','POST'])
def bookdetails():
    if('email' in session and session['email'] ==app.secret_key):
        if request.method=="POST":
            bdetails=request.form.get('detailbook')
            print(bdetails)
            detail=Book.query.filter_by(isbn=bdetails).all()
            l=Reviews.query.filter_by(isbn=bdetails).all()
            check=Reviews.query.filter(and_(Reviews.email == app.secret_key, Reviews.isbn == bdetails)).all()
            print(check)
            addsh=Myshelf2.query.filter(and_(Myshelf2.email == app.secret_key, Myshelf2.isbn == bdetails)).all()
            return render_template("bookdetails.html",bdetails=detail,clen=len(check),revlist=l,lenlist=len(l),Ulist=check,addl=len(addsh)) 

    return redirect('/login/dashboard')



@app.route('/login/dashboard/review', methods=['GET','POST'])
def review():
    if('email' in session and session['email'] ==app.secret_key):
        if request.method=="POST":
            re=request.form.get('review')
            reisbn=request.form.get('reisbn')
            star=request.form.get('star')
            l=Reviews.query.all()
            print(star)
            r=Reviews(id=len(l)+1,review=re,email=app.secret_key,isbn=reisbn,rating=star)
            db.session.add(r)
            db.session.commit()
            print(reisbn)
            l=Reviews.query.all()
            print(l)
            return redirect('/login/dashboard')
            
    return redirect('/login/dashboard')


@app.route('/login/myshelf', methods=['GET','POST'])
def myshelf():
    if('email' in session and session['email'] ==app.secret_key):
        m=Myshelf2.query.filter_by(email=app.secret_key).all()
        return render_template("myshelf.html",m=m)
    return render_template("register.html")  

@app.route('/login/dashboard/myshelfadd', methods=['GET','POST'])
def myshelfadd():
    m=Myshelf2.query.all()
    reisbn=request.form.get('shelf')
    de=Book.query.filter_by(isbn=reisbn).all()
    print(de[0].name)
    r=Myshelf2(id=len(m)+1,isbn=reisbn,name=de[0].name,author=de[0].author,year=de[0].year,email=app.secret_key)
    db.session.add(r)
    db.session.commit()
    return redirect('/login/myshelf')

@app.route('/login/dashboard/myshelfdel', methods=['GET','POST'])
def myshelfdel():
    reisbn=request.form.get('shelfd')
    r=Myshelf2.query.filter(and_(Myshelf2.email == app.secret_key, Myshelf2.isbn == reisbn)).delete()
    # db.session.add(r)
    db.session.commit()
    return redirect('/login/myshelf')

@app.route('/logout')
def logout():
    session.pop('email')       
    return redirect('/login')



@app.route("/api/search", methods=["POST"])
def searchAPI():
    requestData=request.get_json()
    value=requestData.get("search")
    print(value)
    val="%"+value+"%"
    b1=Book.query.filter(Book.isbn.like(val)).all()
    b2=Book.query.filter(Book.name.like(val)).all()
    b3=Book.query.filter(Book.author.like(val)).all()
    b4=Book.query.filter(Book.year.like(val)).all()
    b=b1+b2+b3+b4
    print(b)
    b[0].isbn
    li=[]
    for book in b:
        diction={}
        diction["isbn"]=book.isbn
        diction["name"]=book.name
        diction["author"]=book.author
        diction["year"]=book.year
        li.append(diction)
    return jsonify({"books":li}),200
   



            
        # print(data, email1)
        # if data==None:
        #     return "email not found"
        # else:
        #     return "email Found"


















    # if request.method=="GET":
    #     return render_template("register.html")
    # else:
    #     f_name=request.form.get('first_name')
    #     l_name=request.form.get('last_name')
    #     email=request.form.get('email')
    #     return render_template("details.html", f_name=f_name, l_name=l_name,email=email)

