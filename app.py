from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "veda_secret_key"
DATABASE = "veda.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS service_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            request_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(service_id) REFERENCES services(id)
        )
    """)

    if conn.execute("SELECT * FROM users WHERE username = ?", ("admin",)).fetchone() is None:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "admin123")
        )

    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

def login_required():
    return "username" in session

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    customer_count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    service_count = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    request_count = conn.execute("SELECT COUNT(*) FROM service_requests").fetchone()[0]
    pending_count = conn.execute(
        "SELECT COUNT(*) FROM service_requests WHERE status = 'Pending'"
    ).fetchone()[0]
    conn.close()

    return render_template(
        "dashboard.html",
        customer_count=customer_count,
        service_count=service_count,
        request_count=request_count,
        pending_count=pending_count
    )

@app.route("/customers")
def customers():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("customers.html", customers=rows)

@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()
        address = request.form["address"].strip()

        if not name or not email or not phone:
            flash("Please fill all required customer fields.", "error")
            return render_template("add_customer.html")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)",
            (name, email, phone, address)
        )
        conn.commit()
        conn.close()

        flash("Customer added successfully!", "success")
        return redirect(url_for("customers"))

    return render_template("add_customer.html")

@app.route("/delete_customer/<int:id>")
def delete_customer(id):
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM service_requests WHERE customer_id = ?", (id,))
    conn.execute("DELETE FROM customers WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Customer deleted successfully!", "success")
    return redirect(url_for("customers"))

@app.route("/services")
def services():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM services ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("services.html", services=rows)

@app.route("/add_service", methods=["GET", "POST"])
def add_service():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        service_name = request.form["service_name"].strip()
        description = request.form["description"].strip()
        price = request.form["price"].strip()

        try:
            price_value = float(price)
        except ValueError:
            flash("Price must be a valid number.", "error")
            return render_template("add_service.html")

        if not service_name:
            flash("Service name is required.", "error")
            return render_template("add_service.html")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO services (service_name, description, price) VALUES (?, ?, ?)",
            (service_name, description, price_value)
        )
        conn.commit()
        conn.close()

        flash("Service added successfully!", "success")
        return redirect(url_for("services"))

    return render_template("add_service.html")

@app.route("/delete_service/<int:id>")
def delete_service(id):
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM service_requests WHERE service_id = ?", (id,))
    conn.execute("DELETE FROM services WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Service deleted successfully!", "success")
    return redirect(url_for("services"))

@app.route("/requests")
def service_requests():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            service_requests.id,
            customers.name AS customer_name,
            services.service_name,
            service_requests.request_date,
            service_requests.status
        FROM service_requests
        JOIN customers ON service_requests.customer_id = customers.id
        JOIN services ON service_requests.service_id = services.id
        ORDER BY service_requests.id DESC
    """).fetchall()
    conn.close()

    return render_template("requests.html", requests=rows)

@app.route("/add_request", methods=["GET", "POST"])
def add_request():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    services = conn.execute("SELECT * FROM services ORDER BY service_name").fetchall()

    if request.method == "POST":
        customer_id = request.form["customer_id"]
        service_id = request.form["service_id"]
        request_date = request.form["request_date"]
        status = request.form["status"]

        conn.execute("""
            INSERT INTO service_requests
            (customer_id, service_id, request_date, status)
            VALUES (?, ?, ?, ?)
        """, (customer_id, service_id, request_date, status))
        conn.commit()
        conn.close()

        flash("Service request added successfully!", "success")
        return redirect(url_for("service_requests"))

    conn.close()
    return render_template(
        "add_request.html",
        customers=customers,
        services=services
    )

@app.route("/update_request/<int:id>/<status>")
def update_request(id, status):
    if not login_required():
        return redirect(url_for("login"))

    allowed = ["Pending", "In Progress", "Completed", "Cancelled"]
    if status not in allowed:
        flash("Invalid status.", "error")
        return redirect(url_for("service_requests"))

    conn = get_db_connection()
    conn.execute(
        "UPDATE service_requests SET status = ? WHERE id = ?",
        (status, id)
    )
    conn.commit()
    conn.close()

    flash("Request status updated!", "success")
    return redirect(url_for("service_requests"))

@app.route("/delete_request/<int:id>")
def delete_request(id):
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM service_requests WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Service request deleted!", "success")
    return redirect(url_for("service_requests"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
