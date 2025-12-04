# Expense Tracker Application

A lightweight Python Flask web app to help users track daily expenses, manage monthly budgets, and monitor spending.



## Features

* Add daily expenses with amount, category, note, and date.
* Set monthly budgets for each category.
* Alerts if spending exceeds a budget.
* Remove individual expenses.
* View monthly reports showing:

  * Total spending for the month.
  * Summary of spending vs. budget by category.



## Tech Stack

* Python 3.11
* Flask
* Lightweight database: SQLite
* Frontend: HTML/CSS
* Docker (optional for containerized setup)


## Project Structure


expense-tracker/

├── app.py               # Main Flask application

├── db.py                # Database connection & setup

├── templates/           # HTML templates
│   ├── index.html
│   ├── add_expense.html
│   ├── set_budget.html
│   └── report.html
├── static/
│   └── style.css        # Shared CSS for all pages
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker build instructions
└── expenses.db          # SQLite database (auto-created)




## Setup & Run Locally

1. Clone the repository:

    cd expense-tracker


2. Install dependencies:


pip install -r requirements.txt


3. Run the application:


python app.py


4. Open your web browser and go to:


http://localhost:5000


## Using Docker (Optional)

1. Build the Docker image:


docker build -t expense-tracker .


2. Run the Docker container:


docker run -p 5000:5000 expense-tracker


3. Open your browser at:

http://localhost:5000




## Testing / Validation

1. Add Expense

   * Go to the **Add Expense** page.
   * Enter example values:

     * Amount: 50
     * Category: Food
     * Date: 2025-12-04
   * Click Add Expense → you should see a success message.

2. Set Budget

   * Go to the Set Budget page.
   * Enter:

     * Category: Food
     * Amount: 500
   * Click Set Budget → budget confirmation message should appear.

3. Alert Check

   * Add expenses exceeding the category budget → you should see an ALERT: Budget exceeded message.

4. View Monthly Report

   * Click Monthly Report.
   * Select the current month (or leave empty for current month).
   * You will see:

     * Total spent
     * Category summary
     * List of expenses with Delete buttons

5. Delete Expense

   * Click Delete next to an expense → confirm → the expense is removed.



## Edge Cases / Notes

* Amount must be positive.
* Category cannot be empty.
* Date format must be **YYYY-MM-DD**.
* Deleting expenses is permanent.
* Budget alerts are tracked per category per month.

---

## Database / SQL Usage

* SQLite queries are used for:

  * Adding and deleting expenses
  * Setting or updating budgets
  * Fetching totals and monthly summaries


