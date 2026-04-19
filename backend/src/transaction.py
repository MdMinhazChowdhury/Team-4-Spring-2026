from datetime import date, datetime, timedelta

VALID_CATEGORIES = ["Food", "Income", "Subscription", "Transportation", "Rent", "Entertainment", "Other"]
VALID_TYPES = ["expense", "income"]

class Transaction:
    def __init__(self, transaction_id, user_id, amount, category, date, tx_type, description=""):
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {VALID_CATEGORIES}")
        if tx_type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{tx_type}'. Must be 'expense' or 'income'.")
        if not date:
            raise ValueError("Date cannot be empty.")
        
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.amount = round(amount, 2)
        self.category = category
        self.date = date 
        self.tx_type = tx_type 
        self.description = description


    def signed_amount(self):
        return self.amount if self.tx_type == "income" else -self.amount
 
    def add_transaction(self, transactions_list):
        transactions_list.append(self)
        return transactions_list
    def view_transactions(self, transactions_list, filter_type="all"):
        user_txs = [t for t in transactions_list if t.user_id == self.user_id]
        if filter_type == "income":
            return [t for t in user_txs if t.tx_type == "income"]
        elif filter_type == "expense":
            return [t for t in user_txs if t.tx_type == "expense"]
        return user_txs
 
    def filter_by_date_range(self, transactions_list, filter_range):
        user_txs = self.view_transactions(transactions_list)
        today = date.today()
 
        if filter_range == "this_month":
            return [t for t in user_txs
                    if str(t.date).startswith(f"{today.year}-{str(today.month).zfill(2)}")]
        elif filter_range == "last_7_days":
            cutoff = today - timedelta(days=7)
            return [t for t in user_txs
                    if datetime.strptime(str(t.date), "%Y-%m-%d").date() >= cutoff]
        elif isinstance(filter_range, tuple) and len(filter_range) == 2:
            start = datetime.strptime(filter_range[0], "%Y-%m-%d").date()
            end = datetime.strptime(filter_range[1], "%Y-%m-%d").date()
            return [t for t in user_txs
                    if start <= datetime.strptime(str(t.date), "%Y-%m-%d").date() <= end]
        return user_txs
    
    def get_monthly_income(self, transactions_list, year, month):
        user_txs = self.view_transactions(transactions_list, "income")
        monthly = [t for t in user_txs
                   if str(t.date).startswith(f"{year}-{str(month).zfill(2)}")]
        return round(sum(t.amount for t in monthly), 2)
 
    def get_monthly_expenses(self, transactions_list, year, month):
        user_txs = self.view_transactions(transactions_list, "expense")
        monthly = [t for t in user_txs
                   if str(t.date).startswith(f"{year}-{str(month).zfill(2)}")]
        return round(sum(t.amount for t in monthly), 2)
    
    def get_net_savings(self, transactions_list, year, month):
        income = self.get_monthly_income(transactions_list, year, month)
        expenses = self.get_monthly_expenses(transactions_list, year, month)
        return round(income - expenses, 2)
    
    def get_spending_by_category(self, transactions_list):
        user_txs = self.view_transactions(transactions_list, "expense")
        breakdown = {}
        for t in user_txs:
            breakdown[t.category] = breakdown.get(t.category, 0) + t.amount
        total = sum(breakdown.values())
        if total == 0:
            return {}
        return {k: round((v / total) * 100, 1) for k, v in breakdown.items()}
 
    def generate_report(self, transactions_list, goals_list, subscriptions_list, year, month):
        return {
            "report_month": f"{year}-{str(month).zfill(2)}",
            "total_income": self.get_monthly_income(transactions_list, year, month),
            "total_expenses": self.get_monthly_expenses(transactions_list, year, month),
            "net_savings": self.get_net_savings(transactions_list, year, month),
            "spending_by_category": self.get_spending_by_category(transactions_list),
            "transactions": [str(t) for t in self.view_transactions(transactions_list)],
            "savings_goals": [str(g) for g in goals_list if g.user_id == self.user_id],
            "subscriptions": [str(s) for s in subscriptions_list if s.user_id == self.user_id],
        }
 
    def __repr__(self):
        sign = "-" if self.tx_type == "expense" else "+"
        return f"Transaction(id={self.transaction_id}, {sign}${self.amount}, {self.category}, {self.date})"
 