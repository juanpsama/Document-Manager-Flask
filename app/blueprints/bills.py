from datetime import datetime
import os

from flask import Blueprint, render_template, abort, url_for, redirect, flash, request, send_from_directory
from jinja2 import TemplateNotFound
from sqlalchemy import and_, or_

from ..config import APP_ROOT_PATH
from ..models.models import Bill, File, FileGroup, DocumentType, Tag, User, db
from ..forms.forms import CreateBillForm, FilterBillForm
from .auth import login_required, permission_required, current_user



# TODO: Rename to Bills -> Document
bills_blueprint = Blueprint('bills', __name__, template_folder = 'templates')

def get_id_name_pair(option_class):
    return [(option.id, option.name) for option in option_class]

def make_filename(file: File, index: int):
    # Create filenames based of the original name and the current 
    file_extension = os.path.splitext(file.filename)[1]
    file_name = str(datetime.now()).replace(" ", "_").replace(":",".")
    filename = f'{index}{file_name}{current_user.id}{file_extension}'
    return filename

def save_files_into_file_group(files: list) -> FileGroup:
    file_paths = [os.path.join(
                    'files/', 
                    make_filename(file, i)) 
                    for i, file in enumerate(files)]
    
    # Save all the files 
    for i in range(len(files)):
        files[i].save(os.path.join(APP_ROOT_PATH, file_paths[i]))

    file_group = FileGroup()
    # Store file paths in the database
    for path in file_paths:
        new_file = File(
            file_url = path,
            file_group = file_group  
        )
        db.session.add(new_file) 

    return file_group

def get_filter(filter_form : FilterBillForm):
    folio = filter_form.folio.data
    tag_id = filter_form.tags.data
    author_id = filter_form.author.data
    document_type_id = filter_form.document_type.data

    condition_folio = Bill.folio.like(f'{folio}%') if folio != None else True

    condition_author = Bill.author_id==author_id if (
        author_id != None and  int(author_id) > 0
        ) else True
    
    condition_type = Bill.document_type_id==document_type_id if (
        document_type_id != None and int(document_type_id) > 0
        ) else True
    
    condition_tag = Bill.tags.any(id = tag_id) if (
        tag_id != None and int(tag_id) > 0
        ) else True

    filter = and_(condition_type, condition_author, condition_folio, condition_tag)

    return filter

@bills_blueprint.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    root_path = APP_ROOT_PATH
    filename = db.get_or_404(File, file_id)
    
    return send_from_directory(root_path, filename.file_url)

@bills_blueprint.route('/')
@login_required
@permission_required('can_view_bills')
def get_all():
    filter_form = FilterBillForm(request.args)

    document_types = db.session.execute(db.select(DocumentType)).scalars().all()
    tags = db.session.execute(db.select(Tag)).scalars().all()
    users = db.session.execute(db.select(User)).scalars().all()
    
    # Transform tags and document_types to tuple lists to send as options to the form 
    # based of the database registers
    filter_form.tags.choices = get_id_name_pair(tags)
    filter_form.document_type.choices = get_id_name_pair(document_types)
    filter_form.author.choices = get_id_name_pair(users)
    
    # Get filter for the query
    filter = get_filter(filter_form)

    page = request.args.get('page', 1, type=int)
    per_page = 10

    bills = Bill.query.filter(filter).order_by(Bill.folio.desc()).paginate(page=page, per_page=per_page, error_out=False)
    # bills = Bill.query.order_by(Bill.folio.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("index.html", all_posts=bills, filter_form = filter_form)

@bills_blueprint.route("/<int:bill_id>", methods=["GET", "POST"])
@login_required
@permission_required('can_view_bills')
def show(bill_id):
    requested_bill = db.get_or_404(Bill, bill_id)
    return render_template("post.html", post=requested_bill)


@bills_blueprint.route("/create", methods=["GET", "POST"])
@login_required
@permission_required('can_create_bills')
def add_new_bill():
    form = CreateBillForm()
    
    document_types = db.session.execute(db.select(DocumentType).where(DocumentType.is_active)).scalars().all()
    tags = db.session.execute(db.select(Tag).where(Tag.is_active)).scalars().all()
    
    # Transform tags and document_types to tuple lists to send as options to the form 
    # based of the database registers
    # form.document_type.choices = [('option_id_1', 'option_name_1'), ('option_id_2', 'option_name_2')]
    form.tags.choices = get_id_name_pair(tags)
    form.document_type.choices = get_id_name_pair(document_types)

    if form.validate_on_submit():
        # The multiple file field returns a list of files 
        # Assigning all the list to variables
        bill_files_pdf = form.bill_file_pdf.data
        client_deposit_images = form.client_file_image.data
        deposit_images = form.deposit_file_image.data

        bill_file_group = save_files_into_file_group(bill_files_pdf)
        client_images_group = save_files_into_file_group(client_deposit_images)
        deposit_images_group = save_files_into_file_group(deposit_images)
                        
        document_type_selected = db.get_or_404(DocumentType, form.document_type.data)
        new_bill = Bill(
            author = current_user,
            folio = str(datetime.now()).replace(' ', '_'),
            document_type = document_type_selected,
            
            payment_date = form.payment_date.data,
            bill_date = form.bill_date.data,
            bill_concept = form.bill_concept.data,
            description = form.description.data,
            # Assingning each group of files to the columns in bills
            bill_pdf = bill_file_group,
            client_deposit_image = client_images_group,
            deposit_image = deposit_images_group
        )
        db.session.add(new_bill)

        # 'form.tags.data' is a list of the tags selected
        for tag_id in form.tags.data:
            tag_selected = db.get_or_404(Tag, tag_id)
            new_bill.tags.append(tag_selected)

        db.session.commit()

        return redirect(url_for("bills.get_all"))
    return render_template("make-post.html", form=form)

@bills_blueprint.route("/edit/<int:bill_id>", methods=["GET", "POST"])
@login_required
@permission_required('can_edit_bills')
def edit(bill_id):
    bill = db.get_or_404(Bill, bill_id)

    edit_form = CreateBillForm(
        document_type = bill.document_type,
        payment_date = bill.payment_date,
        bill_date = bill.bill_date,
        bill_concept = bill.bill_concept,
        description = bill.description
    )

    if edit_form.validate_on_submit():
        bill.document_type = edit_form.document_type.data
        bill.payment_date = edit_form.payment_date.data
        bill.bill_date = edit_form.bill_date.data
        bill.bill_concept = edit_form.bill_concept.data
        bill.description = edit_form.description.data
        db.session.commit()
        return redirect(url_for("show_post", bill_id=bill.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

def delete_files_groups(file_group):
    files = file_group.files
    # Deleting file_group from the db
    db.session.delete(file_group)

    for file in files:
        # Deleting file from the db
        db.session.delete(file)
        file_full_path = os.path.join(APP_ROOT_PATH, file.file_url)

        # Check if the file exists, then delete it
        if os.path.exists(file_full_path):

            print('File deleted at: ')
            print(file_full_path)

            # Deleting from the directory
            os.remove(file_full_path)
        else:
            print("The file does not exist")

    db.session.commit()
    
@bills_blueprint.route("/delete/<int:bill_id>")
@login_required
@permission_required('can_delete_bills')
def delete_bill(bill_id):

    bill_to_delete = db.get_or_404(Bill, bill_id)

    delete_files_groups(bill_to_delete.bill_pdf)
    delete_files_groups(bill_to_delete.client_deposit_image)
    delete_files_groups(bill_to_delete.deposit_image)
    
    db.session.delete(bill_to_delete)
    db.session.commit()
    return redirect(url_for('bills.get_all'))


