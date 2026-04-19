from user import User
from transaction import Transaction
from subscription import Subscription
from savings_goal import SavingsGoal
from admin import Admin
from system_maintainance import SystemMaintainer


class FinancialEntityFactory:
    @staticmethod
    def create(entity_type, **kwargs):
        creators = {
            "user": lambda: User.register(
                kwargs["user_id"],
                kwargs["username"],
                kwargs["email"],
                kwargs["password"]
            ),
            "google_user": lambda: User.google_login(
                kwargs["user_id"],
                kwargs["username"],
                kwargs["email"]
            ),
            "transaction": lambda: Transaction(
                kwargs["transaction_id"],
                kwargs["user_id"],
                kwargs["amount"],
                kwargs["category"],
                kwargs["date"],
                kwargs["tx_type"],
                kwargs.get("description", "")
            ),
            "subscription": lambda: Subscription(
                kwargs["subscription_id"],
                kwargs["user_id"],
                kwargs["title"],
                kwargs["cost"],
                kwargs["billing_date"]
            ),
            "savings_goal": lambda: SavingsGoal(
                kwargs["goal_id"],
                kwargs["user_id"],
                kwargs["goal_name"],
                kwargs["target_amount"],
                kwargs.get("current_amount", 0),
                kwargs.get("deadline", None)
            ),
            "admin": lambda: Admin(
                kwargs["admin_id"]
            ),
            "system_maintainer": lambda: SystemMaintainer(
                kwargs["maintainer_id"]
            ),
        }

        if entity_type not in creators:
            raise ValueError(
                f"Unknown entity type: '{entity_type}'. "
                f"Valid types: {list(creators.keys())}"
            )

        return creators[entity_type]()