******Library Management System********

A web-based Library Management System (LMS) built with Flask (Python) and MySQL. This system allows users (students) to register, login, view and issue books, return books with fine calculation, and admins to manage books, view issued books, fine records, and generate reports.

****Features****
**User (Student) Dashboard**
Register and login

View issued books and their return dates

Check pending fines

Search for books by title, author, ISBN, or category

**Admin Dashboard**
Manage books (Add, Update, Delete)

View all issued books (currently issued and returned)

View fine records for students

Generate daily, weekly, and monthly reports:

    Books issued

    Books returned

    Fines collected

**Technologies Used**
Python 3.x

Flask Web Framework

MySQL Database

flask-mysqldb for MySQL integration

flask-cors for Cross-Origin Resource Sharing

JSON for API communication

**Installation**
**Prerequisites**
Python 3.x installed

MySQL server installed and running

**Steps**
1. Clone the repository:


git clone https://github.com/Murtaza12Khosa/library-management-system.git
cd library-management-system
2. Create a virtual environment (optional but recommended):


python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
3. Install required dependencies:


pip install -r requirements.txt
4. Set up your MySQL database:

Create a database named lmsystem

Import your SQL schema or manually create tables:

User, Book, Category, IssuedBooks, etc.

5. Configure database connection in app.py (or your config file):


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lmsystem'

6. Run the Flask app:

flask run

Or if you use your main file directly:

python app.py

7. Access API endpoints at http://localhost:5000/api/...

**API Endpoints**
**User Routes**
POST /api/register - Register a new user

POST /api/login - User login

GET /api/user_dashboard/<student_id> - View user dashboard and issued books

**Book Management Routes (Admin)**
POST /api/book_manage - Add new book

PUT /api/update_book/<book_id> - Update book details

DELETE /api/delete_book/<book_id> - Delete a book

GET /api/views_book - View all books

GET /api/search_books - Search books by filters

**Issued Books Routes**
POST /api/issue_book - Issue a book to a student

POST /api/return_book/<issue_id> - Return a book and calculate fine

**Admin Dashboard**
GET /api/admin/dashboard?type=daily|weekly|monthly - View admin dashboard and reports

**Notes**
Passwords are stored in plain text for simplicity; in production, always hash passwords using secure hashing (e.g., bcrypt).

Fine calculation is Rs.10 per day after the due date.

Reports can be generated for daily, weekly, and monthly periods using query parameters.


**Contact**
Created by Ghulam Murtaza
Email: murtazakhosa069@gmail.com
GitHub: https://github.com/Murtaza12Khosa
