"""
Route tests for the publishers API endpoint.
"""
import unittest
import json
from typing import Dict, Any
from flask import Flask, Response
from models import Publisher, db
from routes.publishers import publishers_bp


class TestPublishersRoutes(unittest.TestCase):
    TEST_DATA: Dict[str, Any] = {
        "publishers": [
            {"name": "DevGames Inc", "description": "Publisher focused on developer-themed strategy games"},
            {"name": "Scrum Masters", "description": "Publisher shipping collaborative games for agile teams"}
        ]
    }

    PUBLISHERS_API_PATH: str = '/api/publishers'

    def setUp(self) -> None:
        """Set up test database and seed data."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.app.register_blueprint(publishers_bp)
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
        """Seed publishers for route tests."""
        publishers = [Publisher(**publisher_data) for publisher_data in self.TEST_DATA["publishers"]]
        db.session.add_all(publishers)
        db.session.commit()

    def _get_response_data(self, response: Response) -> Any:
        """Parse JSON response data."""
        return json.loads(response.data)

    def test_get_publishers_success(self) -> None:
        """Return all publishers with id and name."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), len(self.TEST_DATA["publishers"]))

        for index, publisher in enumerate(data):
            self.assertIn('id', publisher)
            self.assertIn('name', publisher)
            self.assertEqual(publisher['name'], self.TEST_DATA["publishers"][index]["name"])
            self.assertIsInstance(publisher['id'], int)

    def test_get_publishers_empty_database(self) -> None:
        """Return an empty list when no publishers exist."""
        with self.app.app_context():
            db.session.query(Publisher).delete()
            db.session.commit()

        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_get_publishers_response_shape(self) -> None:
        """Ensure endpoint returns only id and name fields for each publisher."""
        response = self.client.get(self.PUBLISHERS_API_PATH)
        data = self._get_response_data(response)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        for publisher in data:
            self.assertEqual(set(publisher.keys()), {'id', 'name'})


if __name__ == '__main__':
    unittest.main()
