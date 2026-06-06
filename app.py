from flask import Flask, request, jsonify
from flask_cors import CORS
from db_config import run_query, run_insert, run_insert_and_get_id
from datetime import datetime, timedelta
import statistics

app = Flask(__name__)
CORS(app)

def get_user_id():
    user_id = request.args.get('user_id')
    if user_id is not None:
        return int(user_id)
    if request.is_json:
        data = request.get_json(silent=True)
        if data and 'user_id' in data:
            return int(data['user_id'])
    return 1

# ==================== AUTH - REGISTER (plain text) ====================
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    required = ['username', 'email', 'password', 'monthly_income']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400
    if len(data['email']) < 5 or '@' not in data['email']:
        return jsonify({'error': 'Invalid email address'}), 400
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    existing = run_query("SELECT UserID FROM Users WHERE Email = ?", (data['email'],))
    if existing:
        return jsonify({'error': 'Email already registered. Please sign in.'}), 409
    # Store password as plain text (INSECURE – for development only)
    plain_password = data['password']
    sql = """
        INSERT INTO Users (Username, Email, PasswordHash, MonthlyIncome, CurrencyPreference)
        VALUES (?, ?, ?, ?, 'PKR')
    """
    params = (data['username'].strip(), data['email'].strip().lower(), plain_password, float(data['monthly_income']))
    new_id = run_insert_and_get_id(sql, params)
    return jsonify({'success': True, 'user_id': new_id, 'username': data['username'].strip(), 'message': 'Account created successfully'})

# ==================== AUTH - LOGIN (plain text comparison) ====================
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    user = run_query(
        "SELECT UserID, Username, Email, PasswordHash, MonthlyIncome FROM Users WHERE LOWER(Email) = LOWER(?)",
        (data['email'].strip(),)
    )
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    stored_password = user[0]['PasswordHash']
    # Plain text comparison
    if stored_password != data['password']:
        return jsonify({'error': 'Invalid email or password'}), 401
    return jsonify({
        'success': True,
        'user_id': user[0]['UserID'],
        'username': user[0]['Username'],
        'email': user[0]['Email'],
        'monthly_income': float(user[0]['MonthlyIncome'])
    })

# ==================== CREATE NEW USER (legacy, stores 'temp_hash') ====================
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    required = ['username', 'email', 'monthly_income']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400
    sql = """
        INSERT INTO Users (Username, Email, PasswordHash, MonthlyIncome, CurrencyPreference)
        VALUES (?, ?, 'temp_hash', ?, 'PKR')
    """
    params = (data['username'], data['email'], data['monthly_income'])
    new_id = run_insert_and_get_id(sql, params)
    return jsonify({'success': True, 'user_id': new_id})

# ==================== GET ALL USERS ====================
@app.route('/api/users', methods=['GET'])
def get_users():
    users = run_query("SELECT UserID, Username, MonthlyIncome FROM Users ORDER BY UserID")
    return jsonify(users)

# ==================== DASHBOARD SUMMARY ====================
@app.route('/api/summary', methods=['GET'])
def get_summary():
    user_id = get_user_id()
    spent = run_query("""
        SELECT ISNULL(SUM(Amount), 0) as TotalSpent
        FROM Expenses
        WHERE UserID = ? AND YEAR(ExpenseDate) = YEAR(GETDATE())
          AND MONTH(ExpenseDate) = MONTH(GETDATE())
    """, (user_id,))[0]['TotalSpent']
    income = run_query("SELECT MonthlyIncome FROM Users WHERE UserID = ?", (user_id,))
    monthly_income = income[0]['MonthlyIncome'] if income else 100000
    savings = run_query("""
        SELECT ISNULL(SUM(CurrentAmount), 0) as Saved,
               ISNULL(SUM(TargetAmount), 0) as Target
        FROM Savings_Goal WHERE UserID = ? AND Status = 'Active'
    """, (user_id,))
    saved  = savings[0]['Saved']  if savings else 0
    target = savings[0]['Target'] if savings else 1
    savings_progress = (saved / target) * 100 if target > 0 else 0
    budget_remaining = monthly_income - spent - saved
    return jsonify({
        'total_spent': spent,
        'monthly_income': monthly_income,
        'budget_remaining': budget_remaining,
        'savings_progress': round(savings_progress, 1),
        'saved_amount': saved,
        'target_amount': target
    })

# ==================== EXPENSES (CRUD) ====================
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    user_id = get_user_id()
    category   = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date   = request.args.get('end_date')
    search     = request.args.get('search')
    sql = """
        SELECT e.ExpenseID, e.Amount, e.ExpenseDate, e.Description,
               e.PaymentMethod, c.CategoryID, c.CategoryName, c.Icon, c.ColorCode
        FROM Expenses e
        JOIN Categories c ON e.CategoryID = c.CategoryID
        WHERE e.UserID = ?
    """
    params = [user_id]
    if category:
        sql += " AND c.CategoryName = ?"; params.append(category)
    if start_date:
        sql += " AND e.ExpenseDate >= ?"; params.append(start_date)
    if end_date:
        sql += " AND e.ExpenseDate <= ?"; params.append(end_date)
    if search:
        sql += " AND (e.Description LIKE ? OR c.CategoryName LIKE ?)"; params.append(f"%{search}%"); params.append(f"%{search}%")
    sql += " ORDER BY e.ExpenseDate DESC"
    return jsonify(run_query(sql, params))

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    user_id = data.get('user_id', 1)
    required = ['category_id', 'amount', 'expense_date']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400
    sql = """
        INSERT INTO Expenses (UserID, CategoryID, Amount, ExpenseDate, Description, PaymentMethod)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (user_id, data['category_id'], data['amount'], data['expense_date'], data.get('description', ''), data.get('payment_method', 'Cash'))
    rows = run_insert(sql, params)
    if rows:
        return jsonify({'success': True, 'message': 'Expense added'})
    return jsonify({'error': 'Insert failed'}), 500

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.json
    user_id = data.get('user_id', 1)
    sql = """
        UPDATE Expenses
        SET CategoryID = ?, Amount = ?, ExpenseDate = ?, Description = ?, PaymentMethod = ?
        WHERE ExpenseID = ? AND UserID = ?
    """
    params = (data['category_id'], data['amount'], data['expense_date'], data.get('description', ''), data.get('payment_method', 'Cash'), expense_id, user_id)
    rows = run_insert(sql, params)
    if rows:
        return jsonify({'success': True})
    return jsonify({'error': 'Expense not found'}), 404

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    user_id = get_user_id()
    rows = run_insert("DELETE FROM Expenses WHERE ExpenseID = ? AND UserID = ?", (expense_id, user_id))
    if rows:
        return jsonify({'success': True})
    return jsonify({'error': 'Expense not found'}), 404

# ==================== CATEGORIES ====================
@app.route('/api/categories', methods=['GET'])
def get_categories():
    cats = run_query("SELECT CategoryID, CategoryName, Icon, ColorCode FROM Categories ORDER BY CategoryName")
    return jsonify(cats)

@app.route('/api/categories/spending', methods=['GET'])
def category_spending():
    user_id = get_user_id()
    total_all = run_query("SELECT ISNULL(SUM(Amount), 0) as Total FROM Expenses WHERE UserID = ?", (user_id,))[0]['Total']
    if total_all == 0:
        return jsonify([])
    results = run_query("""
        SELECT c.CategoryID, c.CategoryName, c.ColorCode, ISNULL(SUM(e.Amount), 0) as Total
        FROM Categories c
        LEFT JOIN Expenses e ON c.CategoryID = e.CategoryID AND e.UserID = ?
        GROUP BY c.CategoryID, c.CategoryName, c.ColorCode
        ORDER BY Total DESC
    """, (user_id,))
    for row in results:
        row['Percentage'] = round((row['Total'] / total_all) * 100, 1)
    return jsonify(results)

# ==================== MONTHLY TREND ====================
@app.route('/api/trend', methods=['GET'])
def monthly_trend():
    user_id = get_user_id()
    data = run_query("""
        SELECT FORMAT(ExpenseDate, 'yyyy-MM') as Month, SUM(Amount) as Total
        FROM Expenses
        WHERE UserID = ? AND ExpenseDate >= DATEADD(MONTH, -6, GETDATE())
        GROUP BY FORMAT(ExpenseDate, 'yyyy-MM')
        ORDER BY Month ASC
    """, (user_id,))
    return jsonify(data)

# ==================== AI PREDICTION ====================
@app.route('/api/predict', methods=['GET'])
def predict():
    user_id = get_user_id()
    last_3 = run_query("""
        SELECT TOP 3 YEAR(ExpenseDate) as Yr, MONTH(ExpenseDate) as Mn, SUM(Amount) as Total
        FROM Expenses WHERE UserID = ?
        GROUP BY YEAR(ExpenseDate), MONTH(ExpenseDate)
        ORDER BY Yr DESC, Mn DESC
    """, (user_id,))
    if len(last_3) == 0:
        return jsonify({'predicted_amount': 0, 'confidence': 0, 'next_month': ''})
    amounts = [row['Total'] for row in last_3]
    avg = statistics.mean(amounts)
    if len(amounts) > 1:
        stdev = statistics.stdev(amounts)
        confidence = max(50, min(95, 100 - (stdev / avg) * 50))
    else:
        confidence = 85
    next_month_date = datetime.now().replace(day=28) + timedelta(days=4)
    return jsonify({
        'predicted_amount': round(avg, 2),
        'confidence': round(confidence, 1),
        'next_month': next_month_date.strftime('%B %Y'),
        'used_months': [f"{r['Yr']}-{r['Mn']}" for r in last_3]
    })

# ==================== SAVINGS GOALS ====================
@app.route('/api/goals', methods=['GET'])
def get_goals():
    user_id = get_user_id()
    goals = run_query("""
        SELECT GoalID, GoalName, TargetAmount, CurrentAmount, TargetDate, Priority, Status,
               CreatedAt, CompletedAt,
               (CurrentAmount * 100.0 / TargetAmount) as ProgressPercent
        FROM Savings_Goal WHERE UserID = ?
        ORDER BY Priority DESC, TargetDate ASC
    """, (user_id,))
    for g in goals:
        g['ProgressPercent'] = round(g['ProgressPercent'], 1) if g['ProgressPercent'] else 0
    return jsonify(goals)

@app.route('/api/goals', methods=['POST'])
def add_goal():
    data = request.json
    user_id = data.get('user_id', 1)
    required = ['goal_name', 'target_amount', 'target_date']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400
    sql = """
        INSERT INTO Savings_Goal (UserID, GoalName, TargetAmount, TargetDate, Priority, Status)
        VALUES (?, ?, ?, ?, ?, 'Active')
    """
    new_id = run_insert_and_get_id(sql, (user_id, data['goal_name'], data['target_amount'], data['target_date'], data.get('priority', 'Medium')))
    return jsonify({'success': True, 'goal_id': new_id})

@app.route('/api/goals/<int:goal_id>/progress', methods=['PUT'])
def update_goal_progress(goal_id):
    data = request.json
    user_id = get_user_id()
    if 'current_amount' not in data:
        return jsonify({'error': 'Missing current_amount'}), 400
    run_insert("UPDATE Savings_Goal SET CurrentAmount = ? WHERE GoalID = ? AND UserID = ?", (data['current_amount'], goal_id, user_id))
    run_insert("UPDATE Savings_Goal SET Status = 'Completed', CompletedAt = GETDATE() WHERE GoalID = ? AND CurrentAmount >= TargetAmount", (goal_id,))
    return jsonify({'success': True})

# ==================== INSIGHTS ====================
@app.route('/api/insights/most-spent', methods=['GET'])
def most_spent_category():
    user_id = get_user_id()
    result = run_query("""
        SELECT TOP 1 c.CategoryName, SUM(e.Amount) as Total
        FROM Expenses e JOIN Categories c ON e.CategoryID = c.CategoryID
        WHERE e.UserID = ? GROUP BY c.CategoryName ORDER BY Total DESC
    """, (user_id,))
    return jsonify(result[0] if result else {'CategoryName': 'None', 'Total': 0})

@app.route('/api/insights/least-spent', methods=['GET'])
def least_spent_category():
    user_id = get_user_id()
    result = run_query("""
        SELECT TOP 1 c.CategoryName, SUM(e.Amount) as Total
        FROM Expenses e JOIN Categories c ON e.CategoryID = c.CategoryID
        WHERE e.UserID = ? GROUP BY c.CategoryName ORDER BY Total ASC
    """, (user_id,))
    return jsonify(result[0] if result else {'CategoryName': 'None', 'Total': 0})

@app.route('/api/insights/weekly', methods=['GET'])
def weekly_spending():
    user_id = get_user_id()
    data = run_query("""
        SELECT DATEPART(weekday, ExpenseDate) as DayNum, DATENAME(weekday, ExpenseDate) as DayName, SUM(Amount) as Total
        FROM Expenses WHERE UserID = ?
        GROUP BY DATEPART(weekday, ExpenseDate), DATENAME(weekday, ExpenseDate)
        ORDER BY DayNum
    """, (user_id,))
    return jsonify(data)

# ==================== BUDGET STATUS ====================
@app.route('/api/budget/status', methods=['GET'])
def budget_status():
    user_id = get_user_id()
    result = run_query("""
        SELECT c.CategoryName, c.BudgetLimit, ISNULL(SUM(e.Amount), 0) as Spent
        FROM Categories c
        LEFT JOIN Expenses e ON c.CategoryID = e.CategoryID AND e.UserID = ?
        GROUP BY c.CategoryName, c.BudgetLimit
    """, (user_id,))
    for row in result:
        row['Remaining']  = row['BudgetLimit'] - row['Spent']
        row['Percentage'] = round((row['Spent'] / row['BudgetLimit']) * 100, 1) if row['BudgetLimit'] > 0 else 0
    return jsonify(result)

# ==================== TEST ====================
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'status': 'Backend is running!', 'user_id': get_user_id()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)