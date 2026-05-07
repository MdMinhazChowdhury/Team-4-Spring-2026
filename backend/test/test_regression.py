import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from transaction import Transaction
from user import User


class RegressionTests(unittest.TestCase):

    def test_transaction_creation(self):

        transaction = Transaction(
            transaction_id=1,
            user_id=1,
            amount=100,
            category="Transportation",
            date="2026-05-07",
            tx_type="expense"
        )

        self.assertEqual(transaction.amount, 100)

    def test_user_registration(self):

        user = User.register(
            user_id=1,
            username="testuser",
            email="test@test.com",
            password="password123"
        )

        self.assertEqual(user.username, "testuser")

    def test_signed_amount_expense(self):

        transaction = Transaction(
            transaction_id=2,
            user_id=1,
            amount=50,
            category="Transportation",
            date="2026-05-07",
            tx_type="expense"
        )

        self.assertEqual(transaction.signed_amount(), -50)

    def test_signed_amount_income(self):

        transaction = Transaction(
            transaction_id=3,
            user_id=1,
            amount=500,
            category="Income",
            date="2026-05-07",
            tx_type="income"
        )

        self.assertEqual(transaction.signed_amount(), 500)


if __name__ == '__main__':
    unittest.main()
