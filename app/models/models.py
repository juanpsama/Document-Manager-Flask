from flask_login import UserMixin
from sqlalchemy.orm import relationship

from ..extensions import db

class BaseSoftDeletion(db.Model):
    __abstract__ = True
    is_active = db.Column(db.Boolean, nullable=False, default = True)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    
    #Create Foreign Key to "roles.id" .
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    role = relationship("Role", back_populates="users")

    #This will act like a List of BlogPost objects attached to each User. 
    #The "author" refers to the author property in the BlogPost class.
    posts = relationship("Bill", back_populates="author")

    def to_dict(self):

        #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}   

class Role(BaseSoftDeletion):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    role_title = db.Column(db.String(100), unique=True, nullable = False)
    role_description = db.Column(db.Text, nullable = True) 

    # Permissions for users
    can_view_users = db.Column(db.Boolean, default=False, nullable=False)
    can_edit_users = db.Column(db.Boolean, default=False, nullable=False)
    can_delete_users = db.Column(db.Boolean, default=False, nullable=False)
    can_create_users = db.Column(db.Boolean, default=False, nullable=False)

    # Permissions for bills
    can_view_bills = db.Column(db.Boolean, default=False, nullable=False)
    can_edit_bills = db.Column(db.Boolean, default=False, nullable=False)
    can_delete_bills = db.Column(db.Boolean, default=False, nullable=False)
    can_create_bills = db.Column(db.Boolean, default=False, nullable=False)

    # Permissions for tags
    can_view_tags = db.Column(db.Boolean, default=False, nullable=False)
    can_edit_tags = db.Column(db.Boolean, default=False, nullable=False)
    can_delete_tags = db.Column(db.Boolean, default=False, nullable=False)
    can_create_tags = db.Column(db.Boolean, default=False, nullable=False)
    
    # Permissions for roles
    can_view_roles = db.Column(db.Boolean, default=False, nullable=False)
    can_edit_roles = db.Column(db.Boolean, default=False, nullable=False)
    can_delete_roles = db.Column(db.Boolean, default=False, nullable=False)
    can_create_roles = db.Column(db.Boolean, default=False, nullable=False)

    can_manage_document_types = db.Column(db.Boolean, default=False, nullable=False)

    # Relationship to User
    users = relationship("User", back_populates="role")  

class DocumentType(BaseSoftDeletion):
    __tablename__ = 'document_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    bills = relationship("Bill", back_populates="document_type")

class Bill(db.Model):
    __tablename__ = "bills"
    id = db.Column(db.Integer, primary_key=True)
    
    #Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
   
    document_type_id = db.Column(db.Integer, db.ForeignKey("document_types.id"))
    document_type = relationship("DocumentType", back_populates='bills')

    folio = db.Column(db.String(250), nullable=False)

    payment_date = db.Column(db.Date, nullable = False)
    bill_date = db.Column(db.Date, nullable = False)
    bill_concept = db.Column(db.Text, nullable = False)
    description = db.Column(db.Text, nullable = False)

    # bill_pdf = db.Column(db.String(250), nullable=False)
    bill_pdf_id = db.Column(db.Integer, db.ForeignKey('files_groups.id'))
    bill_pdf = relationship("FileGroup", foreign_keys="Bill.bill_pdf_id")

    client_deposit_image_id = db.Column(db.Integer, db.ForeignKey('files_groups.id'))
    client_deposit_image = relationship("FileGroup", foreign_keys="Bill.client_deposit_image_id")

    deposit_image_id = db.Column(db.Integer, db.ForeignKey('files_groups.id'))
    deposit_image = relationship("FileGroup", foreign_keys = "Bill.deposit_image_id")

    tags = db.relationship('Tag', secondary = 'bill_tag', back_populates = 'bills')

# Join table for stablishing a many to many relationship between Bill and Tag
bill_tag = db.Table(
  'bill_tag',
   db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
   db.Column('bill_id', db.Integer, db.ForeignKey('bills.id'))
) 

class Tag(BaseSoftDeletion):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)

    bills = db.relationship('Bill', secondary = 'bill_tag', back_populates = 'tags')

class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    file_url = db.Column(db.String(250), nullable=False)

    # Make a relationship between file and file group 
    # Foreign key
    id_group = db.Column(db.Integer, db.ForeignKey("files_groups.id"))
    file_group = relationship("FileGroup", back_populates = 'files')

class FileGroup(db.Model):
    __tablename__ = "files_groups"
    id = db.Column(db.Integer, primary_key=True)\
    
    #TODO: rename this variable form files to file
    files = relationship("File", back_populates='file_group')
