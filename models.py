from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default = False, nullable = False) 
    
    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("Bill", back_populates="author")

    def to_dict(self):

        #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}   
    
class Bill(db.Model):
    __tablename__ = "bills"
    id = db.Column(db.Integer, primary_key=True)
    
    #Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
   
    # name = db.Column(db.String(250), unique=True, nullable=False)
    folio = db.Column(db.String(250), nullable=False)
    document_type = db.Column(db.String(250), nullable = False)
    payment_date = db.Column(db.DateTime, nullable = False)
    bill_date = db.Column(db.DateTime, nullable = False)
    bill_concept = db.Column(db.Text, nullable = False)
    description = db.Column(db.Text, nullable = False)

    bill_pdf = db.Column(db.String(250), nullable=False)
    client_deposit_image = db.Column(db.String(250), nullable=False)
    deposit_image = db.Column(db.String(250), nullable=False)

    # comments = relationship("Comment", back_populates="parent_post")
    tag = relationship("Tag", back_populates="parent_bill")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)

    #make relationship with posts table
    #Create Foreign Key, "users.id" the users refers to the tablename of User.
    post_id = db.Column(db.Integer, db.ForeignKey("bills.id"))
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    parent_bill = relationship("Bill", back_populates="tag")

    name = db.Column(db.String(250), nullable=False)
