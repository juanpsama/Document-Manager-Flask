from flask import Blueprint, render_template, abort, url_for, redirect, flash, request, send_from_directory
from jinja2 import TemplateNotFound

from ..models.models import Tag, db
from ..forms.forms import  TagForm
from .auth import login_required, permission_required

tags_blueprint = Blueprint('tags', __name__, template_folder = 'templates')

# Operations for tags and types
@tags_blueprint.route('/', methods = ['GET', 'POST'])
@login_required
@permission_required('can_view_tags')
@permission_required('can_create_tags')
def get_post_tag():
    form = TagForm()
    if request.method == 'POST':
        new_tag = Tag( name = form.name.data, is_active = True )
    
        db.session.add(new_tag)
        db.session.commit()

    result = db.session.execute(db.select(Tag).where(Tag.is_active!=False))
    tags = result.scalars().all()
    return render_template('tag-manager.html', form = form, items = tags)

@tags_blueprint.route("/delete/<int:tag_id>")
@login_required
@permission_required('can_delete_tags')
def delete(tag_id):
    tag_to_delete = db.get_or_404(Tag, tag_id)
    tag_to_delete.is_active = False
    # db.session.delete(tag_to_delete)
    db.session.commit()
    return redirect(url_for('tags.get_post_tag'))