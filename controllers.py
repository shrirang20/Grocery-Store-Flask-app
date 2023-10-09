from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from sqlalchemy import or_
from flask_migrate import Migrate
import os
from PIL import Image

from config import app
from models import db, User, Inventory, Customer


#Creating different routes

#--------------------- Root -------------------------
@app.route('/')
def display():
    user_logged_in = session.get('userloggedin', False)
    #listing the products on display page.
    if not user_logged_in:
        inventory_data = Inventory.query.all()
        categorized_products = {}
        for product in inventory_data:
            category = product.category
            if category not in categorized_products:
                categorized_products[category] = []
            categorized_products[category].append(product)
        inventory_categories = db.session.query(distinct(Inventory.category)).all()
        category_list = [category for (category,) in inventory_categories]
        return render_template('Displaypage.html', categorized_products=categorized_products,inventory=category_list)
    #flash("You are already logged in, redirected to home page")
    return redirect(url_for('home'))
        
#-------------------- Home Page ----------------------  
@app.route('/home',  methods=['POST','GET'])
def home():
    if session['userloggedin'] == True:
        user_id = session['user_id']
        
        #cart display functionality, only if the user is login.
        cart_items = db.session.query(Customer, Inventory).join(Inventory).filter(Customer.user_id==user_id).all() 
        if request.method == 'POST':
            for customer, inventory in cart_items:
                product_id = inventory.id
                new_quantity = int(request.form.get(f'quantity_{product_id}', customer.quantity))
                if new_quantity == 0:
                    db.session.delete(customer)
                else:
                    customer.quantity = new_quantity
                db.session.commit()
        updated_cart_items = db.session.query(Customer, Inventory).join(Inventory).filter(Customer.user_id==user_id).all()

        #categorizing products.
        inventory_data = Inventory.query.all()
        inventory_categories = db.session.query(distinct(Inventory.category)).all()
        category_list = [category for (category,) in inventory_categories]       
        categorized_products = {}
        for product in inventory_data:
            category = product.category
            if category not in categorized_products:
                categorized_products[category] = []
            categorized_products[category].append(product)
        return render_template('home.html', categorized_products=categorized_products,cart_items=updated_cart_items, inventory=category_list )
    
    else:
        flash('You are not logged in! Try login','error')
        return redirect(url_for('display'))

#-------------------- USER LOGIN ---------------------
@app.route('/userlogin', methods = ['POST', 'GET'])
def userlogin():
    user_logged_in = session.get('userloggedin', False)
    if not user_logged_in:
        if request.method == 'POST':
            username=request.form.get('username')
            password=request.form.get('password-login')

            query = User.query.filter_by(username=username).first()
            
            if query is not None:
                if query.password == password:
                    session['userloggedin'] = True
                    session['user_id'] = query.id
                    flash("Login Successful")
                    return redirect(url_for('home'))
                else:
                    flash("Enter the correct Username and Passowrd","error")
                    return render_template('userlogin.html')
            else:
                flash("User does not Exist, Create an account!","error")
                return redirect(url_for('userregister'))
        return(render_template('userlogin.html'))
    else:
        flash("You are already Logged in")
        return redirect(url_for('home'))

#-------------------- USER SIGNIN---------------------
@app.route('/userregister', methods = ['POST','GET'])
def userregister():
    user_logged_in = session.get('userloggedin', False)
    if not user_logged_in:
        if request.method == 'POST':

            name=request.form['name']
            username=request.form['username']
            number=request.form['number']
            password=request.form['password']
            confirm=request.form['confirm']
            
            existing_username = db.session.query(User).filter_by(username=username).first()
            existing_number = db.session.query(User).filter_by(number=number).first()

            if existing_username:
                flash("Username already exists. Please choose a different username.", "error")
                return redirect(url_for('userregister'))

            if existing_number:
                flash("Phone number already registered. Please use a different number.", "error")
                return redirect(url_for('userregister'))
            
            '''
            #checkinng if user exist
            if db.session.query(User).filter_by(username=username).first() is not None:
                flash("User already exist. Login Please!","error")
                return redirect(url_for('userlogin'))
            '''
                
            #Phone Number Validation
            if len(number) != 10:
                flash("Enter a valid number",'error')
                return redirect(url_for('userregister'))
            
            try:
                number = int(number)
            except ValueError:
                flash('Enter a valid number',"error")
                return redirect(url_for('userregister'))
            
            #Check if both the password and re-entered password matches
            if password !=confirm:
                flash("Password doesn't mactch. Try again!","error")
                return redirect(url_for('userregister'))
            
            #Password Lenght 
            if not(6 <= len(password) <=10):
                flash("Password should have min 6 and max 10 characters.","error")
                return redirect(url_for('userregister')) 
            
            #Adding user to database
            user = User(
                name = name,
                username = username,
                number = number,
                password = password,
                confirm = confirm
            )

            db.session.add(user)
            db.session.commit()
            
            flash ("You are registered and can now log in.","success")
            return redirect(url_for('userlogin'))
        else:
            return render_template('userregister.html')
    else:
        flash("You are already Logged in")
        return redirect(url_for('home'))

#--------------------- logout ------------------------
@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session['userloggedin'] = False
    flash('Logged Out successfully','success')
    session.clear()
    return redirect(url_for('display'))
        
#-------------------- Admin Login -------------------- 
@app.route('/adminlogin', methods = ['POST','GET'])
def adminlogin():
    if not session.get('adminloggedin', False):
        if request.method == 'POST':
            username=request.form.get('username')
            password=request.form.get('password-login')

            if username == 'admin' and password == 'BossGT1':
                session['adminloggedin'] = True
                return redirect(url_for('admindashboard'))
            else:
                flash("Wrong Credentials","error")
                return render_template('adminlogin.html')
    return redirect(url_for('admindashboard'))

#------------------- Admin Logout --------------------
@app.route("/adminlogout", methods=['POST','GET'])
def adminlogout():
    try:
        if session['adminloggedin'] == True:
            session['adminloggedin'] = False
            flash('Logged out successfully')
            return render_template('adminlogin.html')
    except KeyError:
        flash('You are not logged in')
    return redirect(url_for('admindashboard'))

#------------------ Admin Dashboard ------------------
@app.route('/admindashboard')
def admindashboard():
    adminloggedin = session.get('adminloggedin', False)
    if adminloggedin:
        all_inventory = Inventory.query.all()
        return render_template('admindashboard.html',inventory=all_inventory)
    else:
        flash("You need to login","error")
        return render_template('adminlogin.html')

#----------------- image validation ------------------
REQUIRED_DIMENSIONS = (250,250)
def image_validation(image):
    with Image.open(image) as img:
        width,height=img.size
        return width == REQUIRED_DIMENSIONS[0] and height == REQUIRED_DIMENSIONS[1]

#----------------- Insert -----------------------------
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        product_name = request.form['product name']
        expiry = request.form['expiry']
        weight = request.form['weight']
        measure =  request.form['measure']
        rate = float(request.form['rate'])
        unit= request.form['unit']
        quantity = int(request.form['quantity'])
        category = request.form['category']
        subcategory=request.form['subcategory']
        image = request.files['image']

        product_exist = Inventory.query.filter_by(product_name=product_name, expiry_date=expiry, rate=rate, category=category,subcategory=subcategory,weight=weight,measure=measure).first()

        if product_exist:
            product_exist.quantity += quantity
            db.session.commit()
            flash("Product added Successfully")
        else: 
            inventory = Inventory(
                product_name = product_name,
                expiry_date = expiry,
                weight=weight,
                measure=measure,
                rate = rate,
                unit=unit,
                quantity = quantity,
                category = category,
                subcategory = subcategory
            )
        
        if not image:
            flash('Image not found. Please upload an image to add the product to inventory.',"error")
            return redirect(url_for('admindashboard'))


        if not image_validation(image):
            flash("Error, Image Dimensions should be 250px x 250px","warning")
            return redirect(url_for('admindashboard'))
        
        if image:
            image = Image.open(image)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], f'{product_name}.png'))

            db.session.add(inventory)
            db.session.commit()

            flash("Product added Successfully")

        return redirect(url_for('admindashboard'))

#---------------- Update ------------------------------
@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        row_id = request.form.get('id')
        product_name = request.form['product name']
        expiry = request.form['expiry']
        rate = request.form['rate']
        unit = request.form['unit']
        quantity = request.form['quantity']
        category = request.form['category']
        subcategory = request.form['subcategory']
        measure = request.form['measure']
        weight = request.form['weight']

        data_update = Inventory.query.get(row_id)

        if data_update:
            if (data_update.product_name == product_name 
            and data_update.rate == rate 
            and data_update.expiry_date == expiry 
            and data_update.category == category 
            and data_update.subcategory == subcategory 
            and data_update.measure == measure 
            and data_update.weight == weight):
                data_update.quantity += quantity
            else:
                existing_product = Inventory.query.filter_by(product_name=product_name, 
                                                             expiry_date=expiry, rate=rate, 
                                                             category=category, 
                                                             subcategory=subcategory, 
                                                             measure=measure, 
                                                             weight=weight).first()

                if existing_product:
                    existing_product.quantity += int(quantity)
                    db.session.commit()
                else:
                    data_update.product_name = product_name
                    data_update.expiry_date = expiry
                    data_update.rate = rate
                    data_update.unit = unit
                    data_update.quantity = quantity
                    data_update.category = category
                    data_update.subcategory = subcategory 
                    data_update.measure = measure
                    data_update.weight = weight

            db.session.commit()
            flash("Inventory Updated Successfully")
        else:
            flash("Record not found. Update failed.","error")

    return redirect(url_for('admindashboard'))

#---------------- Delete ------------------------------
@app.route('/delete/<id>',methods=['GET','POST'])
def delete(id):
    prod_to_delete = Inventory.query.get(id)
    db.session.delete(prod_to_delete)
    db.session.commit()
    flash("Product Delete Successfully")

    return redirect(url_for('admindashboard'))

#---------------- Add to cart function ----------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if session["userloggedin"]==True:
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        user_id = session['user_id']
        existing = Customer.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing:
            existing.quantity += quantity
        else:
            cart_item = Customer(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()
        flash('Item added to cart', 'success')
    else:
        flash('Please log in first', 'error')
    return redirect(url_for('home'))  # Redirect back to the home page

#--------------- Search -------------------------------
@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search', '')  # Get the search query from the form
    results = []  # To store search results

    if search_query:
        # Query the database for products or categories matching the search query
        results = Inventory.query.filter(
            (Inventory.product_name.like(f'%{search_query}%')) |
            (Inventory.category.like(f'%{search_query}%')) |
            (Inventory.subcategory.like(f'%{search_query}%') |
            (Inventory.expiry_date.like(f'%{search_query}%')) )
        ).all()

    return render_template('search.html', results=results)
