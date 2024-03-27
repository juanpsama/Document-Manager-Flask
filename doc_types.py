from flask import Blueprint, render_template, abort, url_for, redirect, flash, request, send_from_directory
from jinja2 import TemplateNotFound

from models import DocumentType, db
from forms import  DocumentTypeForm
from auth import login_required, permission_required

doc_types_blueprint = Blueprint('doc_types', __name__, template_folder = 'templates')

# Operations for document_types
@doc_types_blueprint.route('/', methods = ['GET', 'POST'])
@login_required
@permission_required('can_manage_document_types')
def get_post_document_types():
    form = DocumentTypeForm()
    if request.method == 'POST':
        new_tag = DocumentType( name = form.name.data )

        db.session.add(new_tag)
        db.session.commit()

    result = db.session.execute(db.select(DocumentType))
    document_type = result.scalars().all()

    # Se necesita otro template para cada vista tag y type
    return render_template('type-manager.html', form = form, items = document_type)

@doc_types_blueprint.route("/delete/<int:type_id>")
@login_required
@permission_required('can_manage_document_types')
def delete_document_type(type_id):
    tag_to_delete = db.get_or_404(DocumentType, type_id)
    db.session.delete(tag_to_delete)
    db.session.commit()
    return redirect(url_for('doc_types.get_post_document_types'))