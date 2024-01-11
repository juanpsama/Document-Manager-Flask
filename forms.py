from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, TextAreaField, RadioField, SelectMultipleField ,MultipleFileField, DateTimeLocalField
from wtforms.validators import DataRequired, URL, Email
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES

images = UploadSet('images', IMAGES)

# WTForm for creating a blog post
class CreateBillForm(FlaskForm):
     
    document_type = RadioField("Tipo de documento", choices=['Tipo 1', 'Tipo 2', 'Tipo 3', 'Tipo 4'], validators=[DataRequired()])
    payment_date = DateField("Fecha de factura")
    bill_date = DateField("Fecha de factura")
    bill_concept = TextAreaField('Concepto de factura')
    description = TextAreaField('Descripcion', validators=[DataRequired()])
    tags = SelectMultipleField("Tags", choices=['Tag 1', 'Tag 2', 'Tag 3'], validators=[DataRequired()])
    

    bill_file_pdf = MultipleFileField('Factura')
    client_file_image = MultipleFileField('Deposito a cliente', validators=[
        FileAllowed(images, 'Images only!')
    ])
    deposit_file_image = MultipleFileField('Deposito a empresa', validators=[
        FileAllowed(images, 'Images only!')
    ])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class TagForm(FlaskForm):
    title = StringField('titulo',validators=[DataRequired()])
    submit = SubmitField("Submit comment")