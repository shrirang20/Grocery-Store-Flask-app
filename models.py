from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False, unique=True)
    username = db.Column(db.String(50),nullable=False, unique=True)
    password = db.Column(db.String(10),nullable=False)
    confirm = db.Column(db.String(10), nullable=False)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    product_name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.String(10), nullable=True)
    rate = db.Column(db.Float(), nullable=False)
    unit = db.Column(db.String(),nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    category = db.Column(db.String(),nullable=False)
    subcategory = db.Column(db.String(),nullable=False)
    measure = db.Column(db.String(),nullable=True)
    weight = db.Column(db.Float(),nullable=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
 
#migrate = Migrate(app, db)