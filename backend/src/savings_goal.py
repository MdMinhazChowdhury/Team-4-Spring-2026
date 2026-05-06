from datetime import datetime


class SavingsGoal:
    def __init__(self, goal_id, user_id, goal_name, target_amount, current_amount=0, deadline=None):
        if not goal_name:
            raise ValueError("Goal name cannot be empty.")
        if not isinstance(target_amount, (int, float)) or target_amount <= 0:
            raise ValueError("Target amount must be a positive number.")
        if not isinstance(current_amount, (int, float)) or current_amount < 0:
            raise ValueError("Current savings cannot be negative.")
        if current_amount > target_amount:
            raise ValueError("Current savings cannot exceed target amount.")

        self.goal_id = goal_id
        self.user_id = user_id
        self.goal_name = goal_name
        self.target_amount = round(target_amount, 2)
        self.current_amount = round(current_amount, 2)
        self.deadline = deadline

    def view_savings_goal(self):
        progress = (self.current_amount / self.target_amount) * 100
        amount_left = self.target_amount - self.current_amount
        return {
            "goal_id": self.goal_id,
            "goal_name": self.goal_name,
            "current_amount": self.current_amount,
            "target_amount": self.target_amount,
            "deadline": self.deadline,
            "due_display": self._format_deadline(),
            "progress_percent": round(min(progress, 100.0), 1),
            "amount_left": round(max(amount_left, 0), 2),
        }

    def _format_deadline(self):
        if not self.deadline:
            return "no deadline"
        d = datetime.strptime(str(self.deadline), "%Y-%m-%d").date()
        return d.strftime("due %b %Y")

    def add_funds(self, amount):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount to add must be a positive number.")
        self.current_amount = round(min(self.current_amount + amount, self.target_amount), 2)
        return self.current_amount

    def get_total_balance(self, goals_list):
        user_goals = [g for g in goals_list if g.user_id == self.user_id]
        return round(sum(g.current_amount for g in user_goals), 2)

    def get_dashboard_goals(self, goals_list):
        user_goals = [g for g in goals_list if g.user_id == self.user_id]
        return [
            {
                "goal_name": g.goal_name,
                "progress_percent": round(min((g.current_amount / g.target_amount) * 100, 100.0), 1)
            }
            for g in user_goals
        ]

    def __repr__(self):
        pct = round((self.current_amount / self.target_amount) * 100, 1)
        return f"SavingsGoal(id={self.goal_id}, name={self.goal_name}, ${self.current_amount}/${self.target_amount}, {pct}%, deadline={self.deadline})"