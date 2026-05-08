import pytest
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

RESPONSE_TIME_LIMIT = 200

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def registered_user(client):
    client.post('/register', json={
        "username": "PerfUser",
        "email": "perf@test.com",
        "password": "pass123"
    })
    return 1


class TestPerformanceRoutes:

    def test_home_route_response_time(self, client):
        start = time.time()
        res = client.get('/')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_register_response_time(self, client):
        start = time.time()
        res = client.post('/register', json={
            "username": "TimingUser",
            "email": "timing@test.com",
            "password": "pass123"
        })
        duration = (time.time() - start) * 1000
        assert res.status_code in [201, 409]
        assert duration < RESPONSE_TIME_LIMIT

    def test_login_response_time(self, client, registered_user):
        start = time.time()
        res = client.post('/login', json={
            "email": "perf@test.com",
            "password": "pass123"
        })
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_dashboard_response_time(self, client, registered_user):
        start = time.time()
        res = client.get(f'/dashboard/{registered_user}')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_add_transaction_response_time(self, client, registered_user):
        start = time.time()
        res = client.post('/transactions', json={
            "user_id": registered_user,
            "amount": 50.0,
            "category": "Food",
            "date": "2026-05-05",
            "tx_type": "expense",
            "description": "Lunch"
        })
        duration = (time.time() - start) * 1000
        assert res.status_code == 201
        assert duration < RESPONSE_TIME_LIMIT

    def test_get_transactions_response_time(self, client, registered_user):
        start = time.time()
        res = client.get(f'/transactions/{registered_user}')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_add_subscription_response_time(self, client, registered_user):
        start = time.time()
        res = client.post('/subscriptions', json={
            "user_id": registered_user,
            "title": "Netflix",
            "cost": 15.99,
            "billing_date": "2026-06-01"
        })
        duration = (time.time() - start) * 1000
        assert res.status_code == 201
        assert duration < RESPONSE_TIME_LIMIT

    def test_get_subscriptions_response_time(self, client, registered_user):
        start = time.time()
        res = client.get(f'/subscriptions/{registered_user}')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_add_savings_goal_response_time(self, client, registered_user):
        start = time.time()
        res = client.post('/savings-goals', json={
            "user_id": registered_user,
            "goal_name": "Vacation",
            "target_amount": 2000.0,
            "current_amount": 500.0,
            "deadline": "2026-12-01"
        })
        duration = (time.time() - start) * 1000
        assert res.status_code == 201
        assert duration < RESPONSE_TIME_LIMIT

    def test_get_savings_goals_response_time(self, client, registered_user):
        start = time.time()
        res = client.get(f'/savings-goals/{registered_user}')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_get_calendar_response_time(self, client, registered_user):
        start = time.time()
        res = client.get(f'/calendar/{registered_user}')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_google_login_response_time(self, client):
        start = time.time()
        res = client.post('/google-login', json={
            "username": "GoogleUser",
            "email": "google@test.com"
        })
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_multiple_transactions_dashboard_still_fast(self, client, registered_user):
        for i in range(10):
            client.post('/transactions', json={
                "user_id": registered_user,
                "amount": float(i + 1) * 10,
                "category": "Food",
                "date": f"2026-05-{str(i + 1).zfill(2)}",
                "tx_type": "expense",
                "description": f"Transaction {i + 1}"
            })
        start = time.time()
        res = client.get(f'/dashboard/{registered_user}')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT

    def test_multiple_goals_response_still_fast(self, client, registered_user):
        for i in range(5):
            client.post('/savings-goals', json={
                "user_id": registered_user,
                "goal_name": f"Goal {i + 1}",
                "target_amount": 1000.0,
                "current_amount": 100.0
            })
        start = time.time()
        res = client.get(f'/savings-goals/{registered_user}')
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        assert duration < RESPONSE_TIME_LIMIT