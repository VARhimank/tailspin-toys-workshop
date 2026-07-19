"""
API routes for retrieving game publishers used by filtering controls.
"""
from flask import jsonify, Response, Blueprint
from models import db, Publisher
from sqlalchemy.orm import Query

# Create a Blueprint for publishers routes
publishers_bp = Blueprint('publishers', __name__)


def get_publishers_base_query() -> Query:
    return db.session.query(Publisher)


@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    publishers_query = get_publishers_base_query().all()
    publishers_list = [{'id': publisher.id, 'name': publisher.name} for publisher in publishers_query]
    return jsonify(publishers_list)