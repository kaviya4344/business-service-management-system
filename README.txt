VEDA - Technology of Business and Service Management System
============================================================

TECHNOLOGY
-----------
Python
Flask
HTML
CSS
SQLite

PROJECT STRUCTURE
-----------------
VEDA_Service_Management/
    app.py
    requirements.txt
    README.txt
    templates/
        base.html
        index.html
        login.html
        dashboard.html
        customers.html
        add_customer.html
        services.html
        add_service.html
        requests.html
        add_request.html
    static/
        style.css

HOW TO RUN
----------
1. Install Python 3.
2. Open Command Prompt/Terminal inside this project folder.
3. Install Flask:

       pip install -r requirements.txt

4. Start the application:

       python app.py

5. Open your browser:

       http://127.0.0.1:5000

LOGIN
-----
Username: admin
Password: admin123

DATABASE
--------
The SQLite database file "veda.db" is created automatically when
the application is started for the first time.

MAIN MODULES
------------
1. Admin Login
2. Dashboard
3. Customer Management
4. Service Management
5. Service Request Management
6. Request Status Tracking

NOTE
----
This is an educational/demo project. For a production application,
use secure password hashing, CSRF protection, stronger secret
management, authorization controls, validation and HTTPS.
