from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user
from markdown import markdown

from . import db
from .data_models import Blog

blogs = Blueprint('blogs', __name__)

# routes
@blogs.route('/blogs', methods=['GET'])
def blogs_list():
    blogs = Blog.query.all()
    sorted_blogs = sorted(blogs, key=lambda x: x.updated_date, reverse=True)

    blog_info = []

    for blog in sorted_blogs:
        blog_info.append({
            'title': blog.title,
            'date': blog.updated_date.strftime('%b %d, %Y'),
            'description': blog.description,
            'file_name': blog.file_name
        })

    return render_template('blogs_list.html',
                           blog_info=blog_info,
                           user=current_user)


@blogs.route('/blogs/<file_name>', methods=['GET'])
def blog(file_name):
    columns = db.session.query(Blog.file_name, Blog.title).all()

    blog_catalog = []

    for column in columns:
        blog_catalog.append({
            'title': column.title,
            'file_name': column.file_name
        })

    blog = Blog.query.filter_by(file_name=file_name).first()

    blog_data = {
        'title': blog.title,
        'creation_date': blog.creation_date.strftime('%b %d, %Y'),
        'update_date': blog.updated_date.strftime('%b %d, %Y'),
        'description': blog.description,
        'content': markdown(blog.content),
        'file_name': blog.file_name
    }

    return render_template('blogs.html',
                           blog=blog_data,
                           blog_catalog=blog_catalog,
                           user=current_user)