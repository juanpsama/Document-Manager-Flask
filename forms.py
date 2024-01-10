from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateTimeField, TextAreaField, RadioField, SelectMultipleField ,MultipleFileField, Field    
from wtforms.widgets import TextInput
from wtforms.validators import DataRequired, URL, Email
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES

images = UploadSet('images', IMAGES)

# WTForm for creating a blog post
class CreateBillForm(FlaskForm):
     
    # name = db.Column(db.String(250), unique=True, nullable=False)
    # folio = db.Column(db.String(250), nullable=False)
    # document_type = db.Column(db.String(250), nullable = False)
    # payment_date = db.Column(db.DateTime, nullable = False)
    # bill_date = db.Column(db.DateTime, nullable = False)
    # bill_concept = db.Column(db.Text, nullable = False)
    # description = db.Column(db.Text, nullable = False)

    # bill_pdf = db.Column(db.String(250), nullable=False)
    # client_deposit_image = db.Column(db.String(250), nullable=False)
    # deposit_image = db.Column(db.String(250), nullable=False)

    # comments = relationship("Tags", back_populates="parent_post")
    # name = StringField("Blog Post Title", validators=[DataRequired()])


    document_type = RadioField("Tipo de documento", choices=['Tipo 1', 'Tipo 2', 'Tipo 3', 'Tipo 4'], validators=[DataRequired()])
    payment_date = DateTimeField("Fecha de factura", validators=[DataRequired()])
    bill_date = DateTimeField("Fecha de factura")
    bill_concept = TextAreaField('Concepto de factura')
    description = TextAreaField('Descripcion', validators=[DataRequired()])
    tags = SelectMultipleField("Tags", choices=['Tag 1', 'Tag 2', 'Tag 3'], validators=[DataRequired()])
    

    bill_file_pdf = FileField ('Factura')
    client_file_image = FileField('Deposito a cliente', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])
    deposit_file_image = FileField('Deposito a empresa', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])
    submit = SubmitField("Submit Post")

# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

# TODO: Create a CommentForm so users can leave comments below posts
class TagForm(FlaskForm):
    title = StringField('titulo',validators=[DataRequired()])
    submit = SubmitField("Submit comment")