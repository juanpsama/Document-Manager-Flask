from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField, DateField,
                      TextAreaField, RadioField, SelectMultipleField , MultipleFileField, BooleanField)

from wtforms.validators import DataRequired, URL, Email, InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES 

images = UploadSet('images', IMAGES)

# WTForm for creating a blog post
class CreateBillForm(FlaskForm):
     
    document_type = RadioField("Tipo de documento", validators=[DataRequired()])
    bill_date = DateField("Fecha de factura")

    bill_file_pdf = MultipleFileField('Factura', validators=[
        InputRequired()
    ])

    client_file_image = MultipleFileField('Deposito del cliente', validators=[
        InputRequired(),
        FileAllowed(images, 'Images only!')
    ])

    payment_date = DateField("Fecha de deposito del cliente")
    deposit_file_image = MultipleFileField('Deposito a empresa', validators=[
        InputRequired(),
        FileAllowed(images, 'Images only!')
    ])
    bill_concept = TextAreaField('Concepto de factura')
    description = TextAreaField('Descripción', validators=[DataRequired()])
    tags = SelectMultipleField("Etiquetas", coerce=int)
    

  
    submit = SubmitField("Guardar")

class CreateRoleForm(FlaskForm):
    role_title = StringField("Nombre de rol", validators=[DataRequired()])
    role_description = TextAreaField('Descripcion de Rol')
    
    can_view_users = BooleanField("Can view users")
    can_edit_users = BooleanField("Can edit users")
    can_delete_users = BooleanField("Can delete users")
    can_create_users = BooleanField("Can create users")

    can_view_bills = BooleanField("Can view bills")
    can_edit_bills = BooleanField("Can edit bills")
    can_delete_bills = BooleanField("Can delete bills")
    can_create_bills = BooleanField("Can create bills")

    can_view_tags = BooleanField("Can view tags")
    can_edit_tags = BooleanField("Can edit tags")
    can_delete_tags = BooleanField("Can delete tags")
    can_create_tags = BooleanField("Can create tags")

    can_view_roles = BooleanField("Can view roles")
    can_edit_roles = BooleanField("Can edit roles")
    can_delete_roles = BooleanField("Can delete roles")
    can_create_roles = BooleanField("Can create roles")

    can_manage_document_types = BooleanField("Can create roles")

    submit = SubmitField("Guardar Rol")

class RegisterForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    name = StringField("Nombre", validators=[DataRequired()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Guardar")


class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Login")

class TagForm(FlaskForm):
    name = StringField('Titulo', validators=[DataRequired()])
    submit = SubmitField("Crear Etiqueta")

class DocumentTypeForm(FlaskForm):
    name = StringField('Nuevo tipo de documento', validators=[DataRequired()])
    submit = SubmitField("Crear Tipo de Documento")
    