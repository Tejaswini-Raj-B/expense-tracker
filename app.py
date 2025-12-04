from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from db import get_conn, init_db

# ---------- app ----------
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"  # change for production

# ensure DB exists and tables ready
init_db()

# ---------- routes ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        try:
            amount = float(request.form.get("amount", "").strip())
        except ValueError:
            flash("Amount must be a number.", "error")
            return redirect(url_for("add_expense"))

        if amount <= 0:
            flash("Amount must be positive.", "error")
            return redirect(url_for("add_expense"))

        category = request.form.get("category", "").strip()
        if not category:
            flash("Category is required.", "error")
            return redirect(url_for("add_expense"))

        note = request.form.get("note", "").strip()
        date_str = request.form.get("date", "").strip()
        if date_str:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                flash("Date must be YYYY-MM-DD or empty.", "error")
                return redirect(url_for("add_expense"))
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")

        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses(amount, category, date, note) VALUES (?,?,?,?)",
            (amount, category, date_str, note)
        )
        conn.commit()
        conn.close()

        # check alerts
        month_prefix = date_str[:7]
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE category=? AND substr(date,1,7)=?",
            (category, month_prefix)
        )
        total = cur.fetchone()[0] or 0.0

        cur.execute("SELECT monthly_budget FROM budgets WHERE category=?", (category,))
        row = cur.fetchone()
        alert_msg = None
        if row:
            budget = row["monthly_budget"]
            if total > budget:
                alert_msg = f"ALERT: Budget exceeded for {category} in {month_prefix}: spent {total:.2f} > budget {budget:.2f}"
            else:
                left = budget - total
                if left <= 0.1 * budget:
                    alert_msg = f"WARNING: Low budget for {category} in {month_prefix}: only {left:.2f} left (<=10%)"

        if alert_msg:
            flash(alert_msg, "alert")
        else:
            flash("Expense added.", "success")
        return redirect(url_for("add_expense"))

    return render_template("add_expense.html")


@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
    flash("Expense deleted successfully.", "success")
    return redirect(request.referrer or url_for("report"))


@app.route("/set-budget", methods=["GET", "POST"])
def set_budget():
    if request.method == "POST":
        category = request.form.get("category", "").strip()
        try:
            amount = float(request.form.get("amount", "").strip())
        except ValueError:
            flash("Amount must be a number.", "error")
            return redirect(url_for("set_budget"))

        if not category:
            flash("Category is required.", "error")
            return redirect(url_for("set_budget"))

        conn = get_conn()
        cur = conn.cursor()
        # upsert by category
        cur.execute(
            "INSERT INTO budgets(category, monthly_budget) VALUES(?,?) "
            "ON CONFLICT(category) DO UPDATE SET monthly_budget=excluded.monthly_budget;",
            (category, amount)
        )
        conn.commit()
        conn.close()
        flash(f"Budget set for {category}: {amount:.2f}", "success")
        return redirect(url_for("set_budget"))

    # show current budgets
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, category, monthly_budget FROM budgets ORDER BY category")
    budgets = cur.fetchall()
    conn.close()
    return render_template("set_budget.html", budgets=budgets)


@app.route("/delete-budget/<int:budget_id>", methods=["POST"])
def delete_budget(budget_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM budgets WHERE id=?", (budget_id,))
    conn.commit()
    conn.close()
    flash("Budget deleted successfully.", "success")
    return redirect(url_for("set_budget"))


@app.route("/report", methods=["GET"])
def report():
    month = request.args.get("month") or datetime.now().strftime("%Y-%m")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE substr(date,1,7)=?",
        (month,)
    )
    total_spent = cur.fetchone()["total"] or 0.0

    cur.execute(
        "SELECT id, date, category, amount, note FROM expenses WHERE substr(date,1,7)=? ORDER BY date",
        (month,)
    )
    expenses = cur.fetchall()

    cur.execute("""
        SELECT category, COALESCE(SUM(amount),0) as spent
        FROM expenses
        WHERE substr(date,1,7)=?
        GROUP BY category
        ORDER BY category
    """, (month,))
    spent_rows = cur.fetchall()

    cur.execute("SELECT category, monthly_budget FROM budgets")
    budget_rows = {r["category"]: r["monthly_budget"] for r in cur.fetchall()}

    data = []
    for r in spent_rows:
        cat = r["category"]
        spent = r["spent"]
        bud = budget_rows.get(cat)
        status = "OK"
        if bud is not None:
            if spent > bud:
                status = "Exceeded"
            else:
                left = bud - spent
                if left <= 0.1 * bud:
                    status = "Low"
        data.append({"category": cat, "spent": spent, "budget": bud, "status": status})

    for cat, bud in budget_rows.items():
        if not any(d["category"] == cat for d in data):
            data.append({"category": cat, "spent": 0.0, "budget": bud, "status": "OK"})

    conn.close()
    return render_template(
        "report.html",
        month=month,
        total_spent=total_spent,
        data=data,
        expenses=expenses
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
