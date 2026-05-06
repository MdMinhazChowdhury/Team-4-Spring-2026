import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from factory import FinancialEntityFactory


# ─────────────────────────────────────────────
# INTEGRATION: LOGIN PAGE
# ─────────────────────────────────────────────

class TestLoginIntegration:

    # Sunny Day
    def test_email_password_registration_and_login(self):
        """User signs up then logs in with email and password."""
        user = FinancialEntityFactory.create("user", user_id=1, username="JohnD",
                                              email="john@email.com", password="pass123")
        assert user.login("john@email.com", "pass123") == True

    def test_google_login_flow(self):
        """User clicks 'Continue with Google'."""
        user = FinancialEntityFactory.create("google_user", user_id=2,
                                              username="JaneD", email="jane@gmail.com")
        assert user.google_auth == True
        assert user.password is None

    # Rainy Day
    def test_wrong_password_login_fails(self):
        user = FinancialEntityFactory.create("user", user_id=1, username="JohnD",
                                              email="john@email.com", password="pass123")
        assert user.login("john@email.com", "wrongpass") == False

    # Boundary
    def test_minimum_password_length(self):
        """Password must be at least 6 characters for sign up."""
        with pytest.raises(ValueError):
            FinancialEntityFactory.create("user", user_id=1, username="JohnD",
                                          email="john@email.com", password="abc")


# ─────────────────────────────────────────────
# INTEGRATION: DASHBOARD
# ─────────────────────────────────────────────

class TestDashboardIntegration:

    # Sunny Day
    def test_all_four_dashboard_cards(self):
        """
        Simulates the 4 dashboard cards from the mockup:
        Total Balance=$4,852 | Monthly Income=$3,500 | Monthly Expenses=$1,564 | Net Savings=$1,555
        (values approximate based on mockup)
        """
        tx_income = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                                   amount=3500.0, category="Income",
                                                   date="2026-03-29", tx_type="income",
                                                   description="Salary deposit")
        tx_food = FinancialEntityFactory.create("transaction", transaction_id=2, user_id=1,
                                                 amount=100.0, category="Food",
                                                 date="2026-03-30", tx_type="expense",
                                                 description="Grocery store")
        tx_netflix = FinancialEntityFactory.create("transaction", transaction_id=3, user_id=1,
                                                    amount=15.99, category="Subscription",
                                                    date="2026-03-25", tx_type="expense",
                                                    description="Netflix")
        tx_gas = FinancialEntityFactory.create("transaction", transaction_id=4, user_id=1,
                                               amount=65.92, category="Transportation",
                                               date="2026-03-20", tx_type="expense",
                                               description="Gas station")
        tx_list = [tx_income, tx_food, tx_netflix, tx_gas]

        income = tx_income.get_monthly_income(tx_list, 2026, 3)
        expenses = tx_income.get_monthly_expenses(tx_list, 2026, 3)
        net = tx_income.get_net_savings(tx_list, 2026, 3)

        assert income == 3500.0
        assert expenses == round(100.0 + 15.99 + 65.92, 2)
        assert net == round(income - expenses, 2)

    def test_spending_by_category_pie_chart(self):
        """Pie chart shows Food 50%, Rent 25%, Trans 16%, Subs 9% (approx mockup values)."""
        tx1 = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                             amount=500.0, category="Food", date="2026-03-01", tx_type="expense")
        tx2 = FinancialEntityFactory.create("transaction", transaction_id=2, user_id=1,
                                             amount=250.0, category="Rent", date="2026-03-01", tx_type="expense")
        tx3 = FinancialEntityFactory.create("transaction", transaction_id=3, user_id=1,
                                             amount=160.0, category="Transportation", date="2026-03-01", tx_type="expense")
        tx4 = FinancialEntityFactory.create("transaction", transaction_id=4, user_id=1,
                                             amount=90.0, category="Subscription", date="2026-03-01", tx_type="expense")
        breakdown = tx1.get_spending_by_category([tx1, tx2, tx3, tx4])
        assert breakdown["Food"] == 50.0
        assert breakdown["Rent"] == 25.0

    def test_generate_report_button(self):
        """Generate Report button produces a complete summary dict."""
        tx = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                            amount=3500.0, category="Income",
                                            date="2026-03-01", tx_type="income")
        goal = FinancialEntityFactory.create("savings_goal", goal_id=1, user_id=1,
                                              goal_name="Emergency Fund", target_amount=5000.0,
                                              current_amount=3600.0, deadline="2026-06-01")
        sub = FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                             title="Netflix", cost=15.99, billing_date="2026-04-01")
        report = tx.generate_report([tx], [goal], [sub], 2026, 3)
        assert report["total_income"] == 3500.0
        assert "spending_by_category" in report
        assert len(report["savings_goals"]) == 1
        assert len(report["subscriptions"]) == 1

    # Rainy Day
    def test_dashboard_shows_zero_when_no_transactions(self):
        tx = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                            amount=100.0, category="Food",
                                            date="2026-03-01", tx_type="expense")
        assert tx.get_monthly_income([], 2026, 3) == 0
        assert tx.get_monthly_expenses([], 2026, 3) == 0

    # Boundary
    def test_total_balance_from_savings_goals(self):
        """Total Balance card sums current_amount across all savings goals."""
        goal1 = FinancialEntityFactory.create("savings_goal", goal_id=1, user_id=1,
                                               goal_name="Emergency Fund", target_amount=5000.0,
                                               current_amount=3600.0)
        goal2 = FinancialEntityFactory.create("savings_goal", goal_id=2, user_id=1,
                                               goal_name="Vacation", target_amount=10000.0,
                                               current_amount=800.0)
        total = goal1.get_total_balance([goal1, goal2])
        assert total == 4400.0


# ─────────────────────────────────────────────
# INTEGRATION: TRANSACTION TAB
# ─────────────────────────────────────────────

class TestTransactionTabIntegration:

    # Sunny Day
    def test_transaction_form_submit_appears_in_history(self):
        """
        Submitting the transaction form adds it to the Transaction History card
        and to the Recent Transactions on the dashboard.
        """
        tx = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                            amount=100.0, category="Food",
                                            date="2026-03-30", tx_type="expense",
                                            description="Grocery store")
        tx_list = []
        tx.add_transaction(tx_list)
        assert len(tx_list) == 1
        assert tx_list[0].description == "Grocery store"

    def test_this_month_filter(self):
        """'This Month' filter in Transaction History returns current month only."""
        from datetime import date
        today = str(date.today())
        tx_now = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                                amount=50.0, category="Food",
                                                date=today, tx_type="expense")
        tx_old = FinancialEntityFactory.create("transaction", transaction_id=2, user_id=1,
                                                amount=50.0, category="Food",
                                                date="2025-01-01", tx_type="expense")
        result = tx_now.filter_by_date_range([tx_now, tx_old], "this_month")
        assert len(result) == 1

    def test_custom_range_filter(self):
        """Custom Range filter returns only transactions within specified dates."""
        tx = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                            amount=65.92, category="Transportation",
                                            date="2026-03-20", tx_type="expense",
                                            description="Gas station")
        result = tx.filter_by_date_range([tx], ("2026-03-01", "2026-03-31"))
        assert len(result) == 1

    # Rainy Day
    def test_invalid_category_blocked(self):
        """Category must be from the valid list in the dropdown."""
        with pytest.raises(ValueError):
            FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                          amount=50.0, category="Shopping",
                                          date="2026-03-01", tx_type="expense")

    # Boundary
    def test_two_users_history_is_isolated(self):
        tx1 = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                             amount=100.0, category="Food",
                                             date="2026-03-01", tx_type="expense")
        tx2 = FinancialEntityFactory.create("transaction", transaction_id=2, user_id=2,
                                             amount=200.0, category="Rent",
                                             date="2026-03-01", tx_type="expense")
        result = tx1.view_transactions([tx1, tx2])
        assert len(result) == 1
        assert result[0].user_id == 1


# ─────────────────────────────────────────────
# INTEGRATION: SUBSCRIPTION TAB
# ─────────────────────────────────────────────

class TestSubscriptionTabIntegration:

    # Sunny Day
    def test_subscription_tab_three_cards(self):
        """
        Subscription tab shows 3 summary cards from the mockup:
        Total Subscriptions=6, Monthly Cost=$98.94, Renewing This Week=2
        """
        subs = [
            FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                          title="Netflix", cost=15.99, billing_date="2026-04-01"),
            FinancialEntityFactory.create("subscription", subscription_id=2, user_id=1,
                                          title="Spotify", cost=9.99, billing_date="2026-04-03"),
            FinancialEntityFactory.create("subscription", subscription_id=3, user_id=1,
                                          title="Adobe", cost=54.99, billing_date="2026-04-15"),
            FinancialEntityFactory.create("subscription", subscription_id=4, user_id=1,
                                          title="Gym Membership", cost=12.99, billing_date="2026-04-12"),
            FinancialEntityFactory.create("subscription", subscription_id=5, user_id=1,
                                          title="Youtube Premium", cost=13.99, billing_date="2026-04-22"),
        ]
        count = subs[0].get_total_count(subs)
        monthly = subs[0].get_monthly_cost(subs)
        assert count == 5
        assert monthly == round(15.99 + 9.99 + 54.99 + 12.99 + 13.99, 2)

    def test_active_subscriptions_sorted_by_renewal(self):
        """Active list sorted nearest renewal first (Netflix 2 days, Spotify 4 days)."""
        sub1 = FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                              title="Spotify", cost=9.99, billing_date="2026-04-10")
        sub2 = FinancialEntityFactory.create("subscription", subscription_id=2, user_id=1,
                                              title="Netflix", cost=15.99, billing_date="2026-04-05")
        result = sub1.view_subscriptions([sub1, sub2])
        assert result[0].title == "Netflix"  # earlier date first

    # Rainy Day
    def test_invalid_subscription_blocked(self):
        with pytest.raises(ValueError):
            FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                          title="", cost=9.99, billing_date="2026-04-01")

    # Boundary
    def test_no_subscriptions_returns_zero_cost(self):
        sub = FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                             title="Netflix", cost=15.99, billing_date="2026-04-01")
        assert sub.get_monthly_cost([]) == 0


# ─────────────────────────────────────────────
# INTEGRATION: SAVINGS GOAL TAB
# ─────────────────────────────────────────────

class TestSavingsGoalTabIntegration:

    # Sunny Day
    def test_three_goal_cards_from_mockup(self):
        """
        Savings Goals page shows 3 cards from the mockup:
        Emergency Fund $3,600/$5,000 (72%), Vacation $800/$10,000 (40%), New Laptop $350/$1,200 (28%)
        """
        goal1 = FinancialEntityFactory.create("savings_goal", goal_id=1, user_id=1,
                                               goal_name="Emergency Fund", target_amount=5000.0,
                                               current_amount=3600.0, deadline="2026-06-01")
        goal2 = FinancialEntityFactory.create("savings_goal", goal_id=2, user_id=1,
                                               goal_name="Vacation", target_amount=10000.0,
                                               current_amount=800.0, deadline="2026-08-01")
        goal3 = FinancialEntityFactory.create("savings_goal", goal_id=3, user_id=1,
                                               goal_name="New Laptop", target_amount=1200.0,
                                               current_amount=350.0, deadline="2026-12-01")

        data1 = goal1.view_savings_goal()
        data2 = goal2.view_savings_goal()
        data3 = goal3.view_savings_goal()

        assert data1["progress_percent"] == 72.0
        assert data1["amount_left"] == 1400.0
        assert data2["progress_percent"] == 8.0   # $800/$10,000
        assert data3["progress_percent"] == 29.2  # $350/$1,200

    def test_new_goal_form_submit_creates_card(self):
        """Submitting the savings goal form creates a new goal card."""
        goal = FinancialEntityFactory.create("savings_goal", goal_id=4, user_id=1,
                                              goal_name="Car", target_amount=8000.0,
                                              current_amount=0.0, deadline="2027-01-01")
        data = goal.view_savings_goal()
        assert data["goal_name"] == "Car"
        assert data["progress_percent"] == 0.0
        assert data["amount_left"] == 8000.0

    # Rainy Day
    def test_goal_missing_name_blocked(self):
        with pytest.raises(ValueError):
            FinancialEntityFactory.create("savings_goal", goal_id=1, user_id=1,
                                          goal_name="", target_amount=1000.0)

    # Boundary
    def test_goal_reaches_100_percent(self):
        goal = FinancialEntityFactory.create("savings_goal", goal_id=1, user_id=1,
                                              goal_name="Goal", target_amount=1000.0,
                                              current_amount=900.0)
        goal.add_funds(100.0)
        data = goal.view_savings_goal()
        assert data["progress_percent"] == 100.0
        assert data["amount_left"] == 0.0


# ─────────────────────────────────────────────
# INTEGRATION: CALENDAR TAB
# ─────────────────────────────────────────────

class TestCalendarTabIntegration:

    # Sunny Day
    def test_calendar_events_for_all_subscriptions(self):
        """
        Calendar tab marks subscription renewal dates.
        Upcoming Renewals panel shows Netflix, Spotify, Gym, Adobe, YouTube.
        """
        subs = [
            FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                          title="Netflix", cost=15.99, billing_date="2026-04-01"),
            FinancialEntityFactory.create("subscription", subscription_id=2, user_id=1,
                                          title="Spotify", cost=9.99, billing_date="2026-04-03"),
        ]
        events = subs[0].get_calendar_events(subs)
        assert len(events) == 2
        titles = [e["title"] for e in events]
        assert "Netflix" in titles
        assert "Spotify" in titles

    def test_upcoming_renewals_panel(self):
        """Upcoming Renewals card shows subscriptions sorted by billing date."""
        sub1 = FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                              title="Spotify", cost=9.99, billing_date="2026-04-10")
        sub2 = FinancialEntityFactory.create("subscription", subscription_id=2, user_id=1,
                                              title="Netflix", cost=15.99, billing_date="2026-04-05")
        sorted_subs = sub1.view_subscriptions([sub1, sub2])
        assert sorted_subs[0].title == "Netflix"

    # Rainy Day
    def test_calendar_empty_when_no_subscriptions(self):
        sub = FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                             title="Netflix", cost=15.99, billing_date="2026-04-01")
        events = sub.get_calendar_events([])
        assert events == []

    # Boundary
    def test_calendar_event_has_correct_fields(self):
        """Each calendar event must have title, date, and cost for the calendar widget."""
        sub = FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                             title="Adobe", cost=54.99, billing_date="2026-04-15")
        event = sub.get_calendar_events([sub])[0]
        assert "title" in event
        assert "date" in event
        assert "cost" in event


# ─────────────────────────────────────────────
# INTEGRATION: FACTORY
# ─────────────────────────────────────────────

class TestFactoryIntegration:

    def test_factory_creates_all_entity_types(self):
        user  = FinancialEntityFactory.create("user", user_id=1, username="JohnD",
                                               email="john@email.com", password="pass123")
        guser = FinancialEntityFactory.create("google_user", user_id=2, username="JaneD",
                                               email="jane@gmail.com")
        tx    = FinancialEntityFactory.create("transaction", transaction_id=1, user_id=1,
                                               amount=100.0, category="Food",
                                               date="2026-04-01", tx_type="expense")
        sub   = FinancialEntityFactory.create("subscription", subscription_id=1, user_id=1,
                                               title="Netflix", cost=15.99, billing_date="2026-04-01")
        goal  = FinancialEntityFactory.create("savings_goal", goal_id=1, user_id=1,
                                               goal_name="Emergency Fund", target_amount=5000.0,
                                               current_amount=3600.0, deadline="2026-06-01")
        admin = FinancialEntityFactory.create("admin", admin_id=1)
        sm    = FinancialEntityFactory.create("system_maintainer", maintainer_id=1)

        assert user.username == "JohnD"
        assert guser.google_auth == True
        assert tx.category == "Food"
        assert sub.title == "Netflix"
        assert goal.goal_name == "Emergency Fund"
        assert admin.admin_id == 1
        assert sm.system_status == "online"

    def test_factory_unknown_type_raises(self):
        with pytest.raises(ValueError):
            FinancialEntityFactory.create("banana")