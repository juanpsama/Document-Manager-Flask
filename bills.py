from datetime import datetime
import os

from flask import Blueprint, render_template, abort, url_for, redirect, flash, request, send_from_directory
from jinja2 import TemplateNotFound

from models import Bill, File, FileGroup, DocumentType, Tag, db
from forms import CreateBillForm
from auth import login_required, permission_required, current_user

# TODO: Rename to Bills -> Document
bills_blueprint = Blueprint('bills', __name__, template_folder = 'templates')

@bills_blueprint.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    filename = db.get_or_404(File, file_id)
    uploads = bills_blueprint.root_path
    
    return send_from_directory(uploads, filename.file_url)

@bills_blueprint.route('/')
@login_required
@permission_required('can_view_bills')
def get_all():
    #TODO: render a form to filter between all the documents 
    page = request.args.get('page', 1, type=int)

    per_page = 10
    bills = Bill.query.order_by(Bill.folio.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("index.html", all_posts=bills)

@bills_blueprint.route("/<int:bill_id>", methods=["GET", "POST"])
@login_required
@permission_required('can_view_bills')
def show(bill_id):
    requested_bill = db.get_or_404(Bill, bill_id)
    return render_template("post.html", post=requested_bill)

def get_id_name_pair(option_class):
    return [(option.id, option.name) for option in option_class]

def make_filename(file: File):
    file_extension = os.path.splitext(file.filename)[1]
    file_name = str(datetime.now()).replace(" ", "_").replace(":",".")
    filename = f'{file_name}{current_user.id}{file_extension}'
    return filename

def save_files_into_file_group(files: list) -> FileGroup:
    # TODO: 
    # Create filenames based of the original name and the current 
    file_paths = [os.path.join(
                    'files/', 
                    make_filename(file) ) 
                    for file in files]
    
    # Save all the files 
    for i in range(len(files)):
        files[i].save(os.path.join(bills_blueprint.root_path, file_paths[i]))

    file_group = FileGroup()
    # Store file paths in the database
    for path in file_paths:
        new_file = File(
            file_url = path,
            file_group = file_group  
        )
        db.session.add(new_file) 

    return file_group

@bills_blueprint.route("/create", methods=["GET", "POST"])
@login_required
@permission_required('can_create_bills')
def add_new_bill():
    form = CreateBillForm()
    
    document_types = db.session.execute(db.select(DocumentType)).scalars().all()
    tags = db.session.execute(db.select(Tag)).scalars().all()
    
    # Transform tags and document_types to tuple lists to send as options to the form 
    # based of the database registers
    # form.document_type.choices = [('option_id_1', 'option_name_1'), ('option_id_2', 'option_name_2')]
    form.tags.choices = get_id_name_pair(tags)
    form.document_type.choices = get_id_name_pair(document_types)

    if form.validate_on_submit():
        # TODO: Quit and Refactor naming of all file groups
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

@bills_blueprint.route("/delete/<int:bill_id>")
@login_required
@permission_required('can_delete_bills')
def delete_bill(bill_id):
    #TODO: delete also the files associated with the bill
    # import os

    # # Specify the file path
    # file_path = "/path/to/your/file.txt"

    # # Check if the file exists, then delete it
    # if os.path.exists(file_path):
    #     os.remove(file_path)
    # else:
    #     print("The file does not exist")

    bill_to_delete = db.get_or_404(Bill, bill_id)
    db.session.delete(bill_to_delete)
    db.session.commit()
    return redirect(url_for('bills.get_all'))


