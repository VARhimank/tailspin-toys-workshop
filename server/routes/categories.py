"""
API routes for retrieving game categories used by filtering controls.
"""
from flask import jsonify, Response, Blueprint
from models import db, Category
from sqlalchemy.orm import Query

# Create a Blueprint for categories routes
categories_bp = Blueprint('categories', __name__)


def get_categories_base_query() -> Query:
    return db.session.query(Category)


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    categories_query = get_categories_base_query().all()
    categories_list = [{'id': category.id, 'name': category.name} for category in categories_query]
    return jsonify(categories_list)
