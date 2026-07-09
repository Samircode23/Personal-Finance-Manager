from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database location
DATABASE = "database/finance.db"


# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/")
def dashboard():

    conn = get_db_connection()

    # Total Income
    income = conn.execute("""
        SELECT IFNULL(SUM(amount),0) AS total
        FROM income
    """).fetchone()

    # Total Expenses
    expenses_total = conn.execute("""
        SELECT IFNULL(SUM(amount),0) AS total
        FROM expenses
    """).fetchone()

    total_income = income["total"]
    total_expenses = expenses_total["total"]
    savings = total_income - total_expenses

    # Categories
    categories = conn.execute(
        "SELECT * FROM categories"
    ).fetchall()

    # Load recent expenses 
    recent_expenses = conn.execute("""
        SELECT
            expenses.*,
            categories.name AS category_name,
            categories.icon AS category_icon
        FROM expenses
        JOIN categories
            ON expenses.category_id = categories.id
        ORDER BY expenses.date DESC, expenses.id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        total_income=total_income,
        total_expenses=total_expenses,
        savings=savings,
        recent_expenses=recent_expenses
    )


# -----------------------------
# Expenses
# -----------------------------
@app.route("/expenses", methods=["GET", "POST"])
def expenses():

    conn = get_db_connection()

    # Load categories
    categories = conn.execute(
        "SELECT * FROM categories"
    ).fetchall()

    # Save expense
    if request.method == "POST":

        date = request.form["date"]
        category_id = request.form["category_id"]
        description = request.form["description"]
        payment_method = request.form["payment_method"]
        note = request.form["note"]
        amount = request.form["amount"]

        conn.execute("""
            INSERT INTO expenses
            (
                date,
                category_id,
                description,
                payment_method,
                note,
                amount,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            date,
            category_id,
            description,
            payment_method,
            note,
            amount
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("expenses"))

    # Load all expenses
    expenses = conn.execute("""
        SELECT
            expenses.*,
            categories.name AS category_name
        FROM expenses
        JOIN categories
            ON expenses.category_id = categories.id
        ORDER BY date DESC
    """).fetchall()

    

    conn.close()

    return render_template(
        "expenses.html",
        categories=categories,
        expenses=expenses
    )


@app.route("/income")
def income():
    return render_template("income.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/savings")
def savings():
    return "<h2>💰 Savings (Coming Soon)</h2>"


@app.route("/settings")
def settings():
    return "<h2>⚙ Settings (Coming Soon)</h2>"

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)