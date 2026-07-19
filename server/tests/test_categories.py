"""
Route tests for the categories API endpoint.
"""
import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Category, db
from routes.categories import categories_bp


class TestCategoriesRoutes(unittest.TestCase):
    TEST_DATA: Dict[str, Any] = {
        "categories": [
            {"name": "Strategy", "description": "Strategic planning games for methodical players"},
            {"name": "Card Game", "description": "Deck-building and tactical card battles"}
        ]
    }

    CATEGORIES_API_PATH: str = '/api/categories'

    def setUp(self) -> None:
        """Set up test database and seed data."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.app.register_blueprint(categories_bp)
        self.client = self.app.test_client()

        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()
            self._seed_test_data()

    def tearDown(self) -> None:
        """Clean up test database and ensure proper connection closure."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def _seed_test_data(self) -> None:
        """Seed categories for route tests."""
        categories = [Category(**category_data) for category_data in self.TEST_DATA["categories"]]
        db.session.add_all(categories)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Parse JSON response data."""
        return json.loads(response.data)

    def test_get_categories_success(self) -> None:
        """Return all categories with id and name."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["categories"]))

        for index, category in enumerate(data):
            self.assertIn('id', category)
            self.assertIn('name', category)
            self.assertEqual(category['name'], self.TEST_DATA["categories"][index]["name"])
            self.assertIsInstance(category['id'], int)

    def test_get_categories_empty_database(self) -> None:
        """Return an empty list when no categories exist."""
        with self.app.app_context():
            db.session.query(Category).delete()
            db.session.commit()

        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_get_categories_response_shape(self) -> None:
        """Ensure endpoint returns only id and name fields for each category."""
        response = self.client.get(self.CATEGORIES_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        for category in data:
            self.assertEqual(set(category.keys()), {'id', 'name'})


if __name__ == '__main__':
    unittest.main()
