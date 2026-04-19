from datetime import date, datetime


class Subscription:
    def __init__(self, subscription_id, user_id, title, cost, billing_date):
        if not title:
            raise ValueError("Subscription title cannot be empty.")
        if not isinstance(cost, (int, float)):
            raise TypeError("Cost must be a number.")
        if cost < 0:
            raise ValueError("Subscription cost cannot be negative.")
        if not billing_date:
            raise ValueError("Billing date cannot be empty.")

        self.subscription_id = subscription_id
        self.user_id = user_id
        self.title = title
        self.cost = round(cost, 2)
        self.billing_date = billing_date

    def days_until_renewal(self):
        today = date.today()
        billing = datetime.strptime(str(self.billing_date), "%Y-%m-%d").date()
        delta = (billing - today).days
        return max(delta, 0)

    def renewal_date_display(self):
        billing = datetime.strptime(str(self.billing_date), "%Y-%m-%d").date()
        return billing.strftime("Renews %B %-d")

    def view_subscriptions(self, subscriptions_list):
        user_subs = [s for s in subscriptions_list if s.user_id == self.user_id]
        return sorted(user_subs, key=lambda s: s.billing_date)

    def get_total_count(self, subscriptions_list):
        return len(self.view_subscriptions(subscriptions_list))

    def get_monthly_cost(self, subscriptions_list):
        user_subs = self.view_subscriptions(subscriptions_list)
        return round(sum(s.cost for s in user_subs), 2)

    def get_renewing_this_week(self, subscriptions_list):
        user_subs = self.view_subscriptions(subscriptions_list)
        return [s for s in user_subs if 0 <= s.days_until_renewal() <= 7]

    def get_calendar_events(self, subscriptions_list):
        user_subs = self.view_subscriptions(subscriptions_list)
        return [
            {"title": s.title, "date": str(s.billing_date), "cost": s.cost}
            for s in user_subs
        ]

    def __repr__(self):
        return f"Subscription(id={self.subscription_id}, title={self.title}, cost=${self.cost}, billing={self.billing_date}, days_left={self.days_until_renewal()})"