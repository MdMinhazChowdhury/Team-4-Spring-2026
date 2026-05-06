import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from factory import FinancialEntityFactory

app = Flask(__name__)
CORS(app)

users = []
transactions = []
subscriptions = []
savings_goals = []

def next_id(lst):
    return len(lst) + 1


@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_response_time(response):
    duration = round((time.time() - request.start_time) * 1000, 2)
    print(f"[PERFORMANCE] {request.method} {request.path} — {duration}ms")
    response.headers['X-Response-Time'] = f"{duration}ms"
    return response



@app.before_request
def security_check():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        if request.content_length and request.content_length > 10000:
            return jsonify({"error": "Request too large"}), 413



@app.route('/')
def home():
    return jsonify({"message": "FinTrac API is running", "status": "online"}), 200


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Username, email, and password are required"}), 400
        existing = next((u for u in users if u.email == data['email']), None)
        if existing:
            return jsonify({"error": "Email already registered"}), 409
        user = FinancialEntityFactory.create("user",
            user_id=next_id(users),
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        users.append(user)
        return jsonify({"message": "User registered", "user_id": user.user_id, "username": user.username}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        user = next((u for u in users if u.email == data['email']), None)
        if not user:
            return jsonify({"error": "User not found"}), 404
        if user.login(data['email'], data['password']):
            return jsonify({"message": "Login successful", "user_id": user.user_id, "username": user.username}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/google-login', methods=['POST'])
def google_login():
    data = request.json
    try:
        if not data.get('email') or not data.get('username'):
            return jsonify({"error": "Email and username are required"}), 400
        existing = next((u for u in users if u.email == data['email']), None)
        if existing:
            return jsonify({"message": "Login successful", "user_id": existing.user_id, "username": existing.username}), 200
        user = FinancialEntityFactory.create("google_user",
            user_id=next_id(users),
            username=data['username'],
            email=data['email']
        )
        users.append(user)
        return jsonify({"message": "Google login successful", "user_id": user.user_id, "username": user.username}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route('/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    try:
        required = ['user_id', 'amount', 'category', 'date', 'tx_type']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        tx = FinancialEntityFactory.create("transaction",
            transaction_id=next_id(transactions),
            user_id=data['user_id'],
            amount=float(data['amount']),
            category=data['category'],
            date=data['date'],
            tx_type=data['tx_type'],
            description=data.get('description', '')
        )
        tx.add_transaction(transactions)
        if data['category'] == 'Subscription' and data['tx_type'] == 'expense':
            try:
                sub = FinancialEntityFactory.create("subscription",
                    subscription_id=next_id(subscriptions),
                    user_id=data['user_id'],
                    title=data.get('description', 'Subscription'),
                    cost=float(data['amount']),
                    billing_date=data['date']
                )
                subscriptions.append(sub)
            except Exception:
                pass
        return jsonify({"message": "Transaction added", "transaction_id": tx.transaction_id}), 201
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route('/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    filter_type = request.args.get('filter', 'all')
    user_txs = [t for t in transactions if t.user_id == user_id]
    if not user_txs:
        return jsonify([]), 200
    if filter_type == 'income':
        user_txs = [t for t in user_txs if t.tx_type == 'income']
    elif filter_type == 'expense':
        user_txs = [t for t in user_txs if t.tx_type == 'expense']
    elif filter_type == 'this_month':
        user_txs = user_txs[0].filter_by_date_range(user_txs, 'this_month')
    elif filter_type == 'last_7_days':
        user_txs = user_txs[0].filter_by_date_range(user_txs, 'last_7_days')
    return jsonify([{
        "transaction_id": t.transaction_id,
        "amount": t.amount,
        "category": t.category,
        "date": str(t.date),
        "tx_type": t.tx_type,
        "description": t.description
    } for t in user_txs]), 200


@app.route('/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard(user_id):
    from datetime import date
    today = date.today()
    year, month = today.year, today.month

    user_txs   = [t for t in transactions if t.user_id == user_id]
    user_goals = [g for g in savings_goals if g.user_id == user_id]

    if not user_txs:
        income, expenses, net, breakdown = 0, 0, 0, {}
    else:
        dummy    = user_txs[0]
        income   = dummy.get_monthly_income(user_txs, year, month)
        expenses = dummy.get_monthly_expenses(user_txs, year, month)
        net      = dummy.get_net_savings(user_txs, year, month)
        breakdown = dummy.get_spending_by_category(user_txs)

    total_balance = user_goals[0].get_total_balance(user_goals) if user_goals else 0
    recent = sorted(user_txs, key=lambda t: str(t.date), reverse=True)[:5]

    return jsonify({
        "total_balance": total_balance,
        "monthly_income": income,
        "monthly_expenses": expenses,
        "net_savings": net,
        "spending_by_category": breakdown,
        "recent_transactions": [{
            "transaction_id": t.transaction_id,
            "amount": t.amount,
            "category": t.category,
            "date": str(t.date),
            "tx_type": t.tx_type,
            "description": t.description
        } for t in recent]
    }), 200


@app.route('/report/<int:user_id>', methods=['GET'])
def generate_report(user_id):
    from datetime import date
    today = date.today()
    user_txs   = [t for t in transactions if t.user_id == user_id]
    user_goals = [g for g in savings_goals if g.user_id == user_id]
    user_subs  = [s for s in subscriptions if s.user_id == user_id]
    if not user_txs:
        return jsonify({"error": "No transactions found for this user"}), 404
    report = user_txs[0].generate_report(user_txs, user_goals, user_subs, today.year, today.month)
    return jsonify(report), 200


@app.route('/subscriptions', methods=['POST'])
def add_subscription():
    data = request.json
    try:
        required = ['user_id', 'title', 'cost', 'billing_date']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        sub = FinancialEntityFactory.create("subscription",
            subscription_id=next_id(subscriptions),
            user_id=data['user_id'],
            title=data['title'],
            cost=float(data['cost']),
            billing_date=data['billing_date']
        )
        subscriptions.append(sub)
        return jsonify({"message": "Subscription added", "subscription_id": sub.subscription_id}), 201
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route('/subscriptions/<int:user_id>', methods=['GET'])
def get_subscriptions(user_id):
    user_subs = [s for s in subscriptions if s.user_id == user_id]
    if not user_subs:
        return jsonify({
            "total_count": 0,
            "monthly_cost": 0,
            "renewing_this_week": [],
            "subscriptions": []
        }), 200
    dummy = user_subs[0]
    renewing = dummy.get_renewing_this_week(user_subs)
    return jsonify({
        "total_count": dummy.get_total_count(user_subs),
        "monthly_cost": dummy.get_monthly_cost(user_subs),
        "renewing_this_week": [s.title for s in renewing],
        "subscriptions": [{
            "subscription_id": s.subscription_id,
            "title": s.title,
            "cost": s.cost,
            "billing_date": str(s.billing_date),
            "days_until_renewal": s.days_until_renewal(),
            "renewal_display": s.renewal_date_display()
        } for s in dummy.view_subscriptions(user_subs)]
    }), 200


@app.route('/calendar/<int:user_id>', methods=['GET'])
def get_calendar(user_id):
    user_subs = [s for s in subscriptions if s.user_id == user_id]
    if not user_subs:
        return jsonify({"events": []}), 200
    events = user_subs[0].get_calendar_events(user_subs)
    return jsonify({"events": events}), 200


@app.route('/savings-goals', methods=['POST'])
def add_savings_goal():
    data = request.json
    try:
        required = ['user_id', 'goal_name', 'target_amount']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        goal = FinancialEntityFactory.create("savings_goal",
            goal_id=next_id(savings_goals),
            user_id=data['user_id'],
            goal_name=data['goal_name'],
            target_amount=float(data['target_amount']),
            current_amount=float(data.get('current_amount', 0)),
            deadline=data.get('deadline', None)
        )
        savings_goals.append(goal)
        return jsonify({"message": "Goal added", "goal_id": goal.goal_id}), 201
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route('/savings-goals/<int:user_id>', methods=['GET'])
def get_savings_goals(user_id):
    user_goals = [g for g in savings_goals if g.user_id == user_id]
    return jsonify([g.view_savings_goal() for g in user_goals]), 200


@app.route('/savings-goals/<int:goal_id>/add-funds', methods=['POST'])
def add_funds(goal_id):
    data = request.json
    goal = next((g for g in savings_goals if g.goal_id == goal_id), None)
    if not goal:
        return jsonify({"error": "Goal not found"}), 404
    try:
        if 'amount' not in data:
            return jsonify({"error": "Amount is required"}), 400
        new_total = goal.add_funds(float(data['amount']))
        return jsonify({"message": "Funds added", "new_total": new_total}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)