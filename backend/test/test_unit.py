import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from user import User
from transaction import Transaction
from subscription import Subscription
from savings_goal import SavingsGoal
from admin import Admin
from system_maintainance import SystemMaintainer


# ─────────────────────────────────────────────
# USER TESTS
# ─────────────────────────────────────────────

class TestUser:

    # Sunny Day
    def test_email_password_login_success(self):
        """Standard login from the login page form."""
        user = User(1, "JohnD", "john@email.com", "pass123")
        assert user.login("john@email.com", "pass123") == True

    def test_register_creates_user(self):
        """Sign Up form creates a new user with username, email, password."""
        user = User.register(1, "JohnD", "john@email.com", "pass123")
        assert user.username == "JohnD"
        assert user.email == "john@email.com"
        assert user.google_auth == False

    def test_google_login_creates_user(self):
        """'Continue with Google' button creates a Google auth user."""
        user = User.google_login(2, "JaneD", "jane@gmail.com")
        assert user.google_auth == True
        assert user.password is None

    # Rainy Day
    def test_login_wrong_password(self):
        user = User(1, "JohnD", "john@email.com", "pass123")
        assert user.login("john@email.com", "wrongpass") == False

    def test_login_wrong_email(self):
        user = User(1, "JohnD", "john@email.com", "pass123")
        assert user.login("wrong@email.com", "pass123") == False

    def test_google_user_cannot_use_password_login(self):
        user = User.google_login(1, "JaneD", "jane@gmail.com")
        with pytest.raises(ValueError):
            user.login("jane@gmail.com", "somepass")

    def test_register_empty_username_raises(self):
        with pytest.raises(ValueError):
            User.register(1, "", "john@email.com", "pass123")

    def test_register_invalid_email_raises(self):
        with pytest.raises(ValueError):
            User.register(1, "JohnD", "notanemail", "pass123")

    def test_register_empty_password_raises(self):
        with pytest.raises(ValueError):
            User.register(1, "JohnD", "john@email.com", "")

    def test_register_short_password_raises(self):
        """Password must be at least 6 characters."""
        with pytest.raises(ValueError):
            User.register(1, "JohnD", "john@email.com", "abc")

    # Boundary
    def test_login_empty_credentials_returns_false(self):
        user = User(1, "JohnD", "john@email.com", "pass123")
        assert user.login("", "") == False

    def test_register_minimum_valid_password(self):
        """Exactly 6 characters is the minimum valid password."""
        user = User.register(1, "JohnD", "john@email.com", "abc123")
        assert user.user_id == 1


# ─────────────────────────────────────────────
# TRANSACTION TESTS
# ─────────────────────────────────────────────

class TestTransaction:

    # Sunny Day
    def test_add_expense_transaction(self):
        """Expense added via transaction form (Expense toggle selected)."""
        tx = Transaction(1, 1, 100.0, "Food", "2026-04-01", "expense", "Grocery store")
        result = tx.add_transaction([])
        assert len(result) == 1
        assert result[0].tx_type == "expense"

    def test_add_income_transaction(self):
        """Income added via transaction form (Income toggle selected)."""
        tx = Transaction(2, 1, 3500.0, "Income", "2026-03-29", "income", "Salary deposit")
        result = tx.add_transaction([])
        assert result[0].signed_amount() == 3500.0

    def test_expense_signed_amount_is_negative(self):
        tx = Transaction(1, 1, 100.0, "Food", "2026-04-01", "expense")
        assert tx.signed_amount() == -100.0

    def test_filter_all(self):
        """'All' filter button returns every transaction."""
        tx1 = Transaction(1, 1, 100.0, "Food", "2026-04-01", "expense")
        tx2 = Transaction(2, 1, 3500.0, "Income", "2026-03-29", "income")
        result = tx1.view_transactions([tx1, tx2], "all")
        assert len(result) == 2

    def test_filter_income_only(self):
        """'Income' filter button returns only income entries."""
        tx1 = Transaction(1, 1, 100.0, "Food", "2026-04-01", "expense")
        tx2 = Transaction(2, 1, 3500.0, "Income", "2026-03-29", "income")
        result = tx1.view_transactions([tx1, tx2], "income")
        assert len(result) == 1
        assert result[0].tx_type == "income"

    def test_filter_expense_only(self):
        """'Expense' filter button returns only expense entries."""
        tx1 = Transaction(1, 1, 100.0, "Food", "2026-04-01", "expense")
        tx2 = Transaction(2, 1, 3500.0, "Income", "2026-03-29", "income")
        result = tx1.view_transactions([tx1, tx2], "expense")
        assert len(result) == 1
        assert result[0].tx_type == "expense"

    def test_monthly_income_dashboard_card(self):
        """Powers the Monthly Income card on the dashboard ($3,500 in mockup)."""
        tx = Transaction(1, 1, 3500.0, "Income", "2026-03-29", "income")
        assert tx.get_monthly_income([tx], 2026, 3) == 3500.0

    def test_monthly_expenses_dashboard_card(self):
        """Powers the Monthly Expenses card on the dashboard ($1,564 in mockup)."""
        tx1 = Transaction(1, 1, 100.0, "Food", "2026-03-30", "expense")
        tx2 = Transaction(2, 1, 65.92, "Transportation", "2026-03-20", "expense")
        total = tx1.get_monthly_expenses([tx1, tx2], 2026, 3)
        assert total == 165.92

    def test_net_savings_dashboard_card(self):
        """Powers the Net Savings card (income - expenses = net savings)."""
        tx1 = Transaction(1, 1, 3500.0, "Income", "2026-03-29", "income")
        tx2 = Transaction(2, 1, 1564.0, "Food", "2026-03-15", "expense")
        net = tx1.get_net_savings([tx1, tx2], 2026, 3)
        assert net == 1936.0

    def test_spending_by_category_pie_chart(self):
        """Powers the Spending by Category pie chart on the dashboard."""
        tx1 = Transaction(1, 1, 50.0, "Food", "2026-03-01", "expense")
        tx2 = Transaction(2, 1, 25.0, "Rent", "2026-03-01", "expense")
        breakdown = tx1.get_spending_by_category([tx1, tx2])
        assert "Food" in breakdown
        assert "Rent" in breakdown
        assert round(breakdown["Food"] + breakdown["Rent"], 1) == 100.0

    def test_generate_report_returns_all_data(self):
        """Tests the Generate Report button data structure."""
        tx = Transaction(1, 1, 3500.0, "Income", "2026-03-01", "income")
        report = tx.generate_report([tx], [], [], 2026, 3)
        assert "total_income" in report
        assert "total_expenses" in report
        assert "net_savings" in report
        assert "spending_by_category" in report

    # Rainy Day
    def test_zero_amount_raises(self):
        with pytest.raises(ValueError):
            Transaction(1, 1, 0, "Food", "2026-04-01", "expense")

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError):
            Transaction(1, 1, -50.0, "Food", "2026-04-01", "expense")

    def test_invalid_category_raises(self):
        with pytest.raises(ValueError):
            Transaction(1, 1, 50.0, "Shopping", "2026-04-01", "expense")

    def test_invalid_tx_type_raises(self):
        with pytest.raises(ValueError):
            Transaction(1, 1, 50.0, "Food", "2026-04-01", "debit")

    def test_empty_date_raises(self):
        with pytest.raises(ValueError):
            Transaction(1, 1, 50.0, "Food", "", "expense")

    def test_other_users_transactions_not_visible(self):
        """User 1 cannot see User 2's transactions."""
        tx1 = Transaction(1, 1, 50.0, "Food", "2026-04-01", "expense")
        tx2 = Transaction(2, 2, 100.0, "Income", "2026-04-01", "income")
        result = tx1.view_transactions([tx1, tx2])
        assert len(result) == 1
        assert result[0].user_id == 1

    # Boundary
    def test_very_small_amount(self):
        tx = Transaction(1, 1, 0.01, "Food", "2026-04-01", "expense")
        assert tx.amount == 0.01

    def test_view_transactions_empty_list(self):
        tx = Transaction(1, 1, 50.0, "Food", "2026-04-01", "expense")
        assert tx.view_transactions([]) == []

    def test_subscription_category_valid(self):
        """Subscription category is valid and feeds the Subscription tab."""
        tx = Transaction(1, 1, 15.99, "Subscription", "2026-04-01", "expense", "Netflix")
        assert tx.category == "Subscription"

    def test_filter_by_this_month(self):
        """'This Month' filter in Transaction History card."""
        from datetime import date
        today = date.today()
        tx = Transaction(1, 1, 50.0, "Food", str(today), "expense")
        result = tx.filter_by_date_range([tx], "this_month")
        assert len(result) == 1

    def test_custom_date_range_filter(self):
        """Custom Range filter in Transaction History card."""
        tx = Transaction(1, 1, 50.0, "Food", "2026-03-15", "expense")
        result = tx.filter_by_date_range([tx], ("2026-03-01", "2026-03-31"))
        assert len(result) == 1

    def test_custom_date_range_excludes_outside(self):
        tx = Transaction(1, 1, 50.0, "Food", "2026-01-01", "expense")
        result = tx.filter_by_date_range([tx], ("2026-03-01", "2026-03-31"))
        assert len(result) == 0


# ─────────────────────────────────────────────
# SUBSCRIPTION TESTS
# ─────────────────────────────────────────────

class TestSubscription:

    # Sunny Day
    def test_create_valid_subscription(self):
        """Netflix subscription as shown in the mockup."""
        sub = Subscription(1, 1, "Netflix", 15.99, "2026-04-01")
        assert sub.title == "Netflix"
        assert sub.cost == 15.99

    def test_view_subscriptions_returns_users_only(self):
        """Active Subscriptions list shows only the logged-in user's subs."""
        sub1 = Subscription(1, 1, "Netflix", 15.99, "2026-04-01")
        sub2 = Subscription(2, 2, "Hulu", 12.99, "2026-04-05")
        sub3 = Subscription(3, 1, "Spotify", 9.99, "2026-04-03")
        result = sub1.view_subscriptions([sub1, sub2, sub3])
        assert len(result) == 2

    def test_total_count_card(self):
        """Total Subscriptions card shows count (6 in mockup)."""
        subs = [Subscription(i, 1, f"Sub{i}", 9.99, "2026-04-01") for i in range(1, 7)]
        assert subs[0].get_total_count(subs) == 6

    def test_monthly_cost_card(self):
        """Monthly Cost card ($98.94 in mockup)."""
        sub1 = Subscription(1, 1, "Netflix", 15.99, "2026-04-01")
        sub2 = Subscription(2, 1, "Spotify", 9.99, "2026-04-03")
        total = sub1.get_monthly_cost([sub1, sub2])
        assert total == 25.98

    def test_renewal_date_display(self):
        """'Renews April 1' label in the Active Subscriptions list."""
        sub = Subscription(1, 1, "Netflix", 15.99, "2026-04-01")
        display = sub.renewal_date_display()
        assert "April" in display
        assert "1" in display

    def test_calendar_events(self):
        """Calendar tab receives subscription renewal events."""
        sub = Subscription(1, 1, "Netflix", 15.99, "2026-04-01")
        events = sub.get_calendar_events([sub])
        assert len(events) == 1
        assert events[0]["title"] == "Netflix"
        assert events[0]["date"] == "2026-04-01"
        assert events[0]["cost"] == 15.99

    # Rainy Day
    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            Subscription(1, 1, "", 15.99, "2026-04-01")

    def test_negative_cost_raises(self):
        with pytest.raises(ValueError):
            Subscription(1, 1, "Netflix", -5.0, "2026-04-01")

    def test_empty_billing_date_raises(self):
        with pytest.raises(ValueError):
            Subscription(1, 1, "Netflix", 15.99, "")

    def test_renewing_this_week_empty_list(self):
        sub = Subscription(1, 1, "Netflix", 15.99, "2026-04-01")
        assert sub.get_renewing_this_week([]) == []

    # Boundary
    def test_zero_cost_free_trial(self):
        """Free trial subscription with $0 cost."""
        sub = Subscription(1, 1, "FreeTrial", 0, "2026-05-01")
        assert sub.cost == 0

    def test_view_empty_subscription_list(self):
        sub = Subscription(1, 1, "Netflix", 15.99, "2026-04-01")
        assert sub.view_subscriptions([]) == []

    def test_subscriptions_sorted_by_billing_date(self):
        """Active subscriptions list sorted by nearest renewal date."""
        sub1 = Subscription(1, 1, "Adobe", 54.99, "2026-04-15")
        sub2 = Subscription(2, 1, "Netflix", 15.99, "2026-04-01")
        result = sub1.view_subscriptions([sub1, sub2])
        assert result[0].title == "Netflix"  # nearest date first


# ─────────────────────────────────────────────
# SAVINGS GOAL TESTS
# ─────────────────────────────────────────────

class TestSavingsGoal:

    # Sunny Day
    def test_create_valid_goal(self):
        """Emergency Fund goal as shown in mockup ($3,600 of $5,000)."""
        goal = SavingsGoal(1, 1, "Emergency Fund", 5000.0, 3600.0, "2026-06-01")
        assert goal.goal_name == "Emergency Fund"
        assert goal.target_amount == 5000.0
        assert goal.current_amount == 3600.0

    def test_view_savings_goal_card_data(self):
        """Goal card shows progress, amount left, due date."""
        goal = SavingsGoal(1, 1, "Emergency Fund", 5000.0, 3600.0, "2026-06-01")
        data = goal.view_savings_goal()
        assert data["progress_percent"] == 72.0
        assert data["amount_left"] == 1400.0
        assert "Jun" in data["due_display"]

    def test_add_funds_updates_progress(self):
        """Adding funds updates the progress bar on the goal card."""
        goal = SavingsGoal(1, 1, "Vacation", 10000.0, 800.0, "2026-08-01")
        new_total = goal.add_funds(200.0)
        assert new_total == 1000.0
        assert goal.view_savings_goal()["progress_percent"] == 10.0

    def test_total_balance_dashboard_card(self):
        """Total Balance card on the dashboard sums all goal current amounts."""
        goal1 = SavingsGoal(1, 1, "Emergency Fund", 5000.0, 3600.0)
        goal2 = SavingsGoal(2, 1, "Vacation", 10000.0, 800.0)
        total = goal1.get_total_balance([goal1, goal2])
        assert total == 4400.0

    def test_dashboard_goals_card(self):
        """Dashboard savings goals card shows name and progress for each goal."""
        goal1 = SavingsGoal(1, 1, "Emergency Fund", 5000.0, 3600.0)
        goal2 = SavingsGoal(2, 1, "Vacation", 10000.0, 4000.0)
        result = goal1.get_dashboard_goals([goal1, goal2])
        assert len(result) == 2
        assert result[0]["goal_name"] == "Emergency Fund"
        assert result[0]["progress_percent"] == 72.0

    # Rainy Day
    def test_empty_goal_name_raises(self):
        with pytest.raises(ValueError):
            SavingsGoal(1, 1, "", 5000.0, 0)

    def test_zero_target_raises(self):
        with pytest.raises(ValueError):
            SavingsGoal(1, 1, "Goal", 0, 0)

    def test_negative_target_raises(self):
        with pytest.raises(ValueError):
            SavingsGoal(1, 1, "Goal", -1000.0, 0)

    def test_negative_current_raises(self):
        with pytest.raises(ValueError):
            SavingsGoal(1, 1, "Goal", 5000.0, -100.0)

    def test_current_exceeds_target_raises(self):
        with pytest.raises(ValueError):
            SavingsGoal(1, 1, "Goal", 1000.0, 2000.0)

    def test_add_zero_funds_raises(self):
        goal = SavingsGoal(1, 1, "Goal", 1000.0, 0)
        with pytest.raises(ValueError):
            goal.add_funds(0)

    def test_add_negative_funds_raises(self):
        goal = SavingsGoal(1, 1, "Goal", 1000.0, 0)
        with pytest.raises(ValueError):
            goal.add_funds(-100)

    # Boundary
    def test_progress_caps_at_100(self):
        """Progress bar never exceeds 100%."""
        goal = SavingsGoal(1, 1, "Goal", 1000.0, 1000.0)
        data = goal.view_savings_goal()
        assert data["progress_percent"] == 100.0
        assert data["amount_left"] == 0.0

    def test_default_current_amount_is_zero(self):
        """New goal with no current savings defaults to $0."""
        goal = SavingsGoal(1, 1, "New Laptop", 1200.0)
        assert goal.current_amount == 0

    def test_no_deadline(self):
        """Goal without deadline shows 'no deadline'."""
        goal = SavingsGoal(1, 1, "General Savings", 500.0)
        data = goal.view_savings_goal()
        assert data["due_display"] == "no deadline"

    def test_add_funds_capped_at_target(self):
        """Adding more than needed caps at target amount, not over."""
        goal = SavingsGoal(1, 1, "Goal", 1000.0, 900.0)
        result = goal.add_funds(500.0)
        assert result == 1000.0


# ─────────────────────────────────────────────
# ADMIN TESTS
# ─────────────────────────────────────────────

class TestAdmin:

    # Sunny Day
    def test_view_existing_user(self):
        admin = Admin(1)
        user = User(10, "JohnD", "john@email.com", "pass123")
        result = admin.manage_user_accounts([user], "view", 10)
        assert result.user_id == 10

    def test_delete_existing_user(self):
        admin = Admin(1)
        user1 = User(10, "JohnD", "john@email.com", "pass123")
        user2 = User(11, "JaneD", "jane@email.com", "pass456")
        result = admin.manage_user_accounts([user1, user2], "delete", 10)
        assert len(result) == 1
        assert result[0].user_id == 11

    # Rainy Day
    def test_view_nonexistent_user_raises(self):
        admin = Admin(1)
        with pytest.raises(ValueError):
            admin.manage_user_accounts([], "view", 99)

    def test_delete_nonexistent_user_raises(self):
        admin = Admin(1)
        user = User(10, "JohnD", "john@email.com", "pass123")
        with pytest.raises(ValueError):
            admin.manage_user_accounts([user], "delete", 99)

    def test_unknown_action_raises(self):
        admin = Admin(1)
        user = User(10, "JohnD", "john@email.com", "pass123")
        with pytest.raises(ValueError):
            admin.manage_user_accounts([user], "ban", 10)

    # Boundary
    def test_delete_last_user_leaves_empty_list(self):
        admin = Admin(1)
        user = User(10, "JohnD", "john@email.com", "pass123")
        result = admin.manage_user_accounts([user], "delete", 10)
        assert result == []


# ─────────────────────────────────────────────
# SYSTEM MAINTAINER TESTS
# ─────────────────────────────────────────────

class TestSystemMaintainer:

    # Sunny Day
    def test_update_system_valid(self):
        sm = SystemMaintainer(1)
        result = sm.update_system("Fixed login bug")
        assert "Fixed login bug" in result

    def test_resolve_issue_valid(self):
        sm = SystemMaintainer(1)
        result = sm.resolve_issues("Dashboard not loading")
        assert "resolved" in result.lower()

    def test_view_system_status_online(self):
        sm = SystemMaintainer(1)
        status = sm.view_system_status()
        assert status["system_status"] == "online"
        assert status["open_issues"] == 0

    # Rainy Day
    def test_update_empty_notes_raises(self):
        sm = SystemMaintainer(1)
        with pytest.raises(ValueError):
            sm.update_system("")

    def test_resolve_empty_issue_raises(self):
        sm = SystemMaintainer(1)
        with pytest.raises(ValueError):
            sm.resolve_issues("")

    # Boundary
    def test_resolve_multiple_issues_all_logged(self):
        sm = SystemMaintainer(1)
        sm.resolve_issues("Issue 1")
        sm.resolve_issues("Issue 2")
        sm.resolve_issues("Issue 3")
        assert len(sm.issues_log) == 3