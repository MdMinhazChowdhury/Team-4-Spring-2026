import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import app


class SecurityTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_invalid_email_registration(self):

        response = self.client.post('/register',
            json={
                "username": "testuser",
                "email": "bademail",
                "password": "password123"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_empty_password(self):

        response = self.client.post('/register',
            json={
                "username": "testuser",
                "email": "test@test.com",
                "password": ""
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_login(self):

        self.client.post('/register',
            json={
                "username": "user1",
                "email": "user1@test.com",
                "password": "password123"
            }
        )

        response = self.client.post('/login',
            json={
                "email": "user1@test.com",
                "password": "wrongpassword"
            }
        )

        self.assertEqual(response.status_code, 401)

    def test_missing_json(self):

        response = self.client.post('/register',
            data="plain text request"
        )

        self.assertEqual(response.status_code, 415)


if __name__ == '__main__':
    unittest.main()
