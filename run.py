from flask import Flask, request, jsonify, session
import MySQLdb.cursors
from flask_mysqldb  import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['MYSQL_HOST'] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "lmsystem"

mysql = MySQL(app)

#_______Register API____________
@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            return jsonify({'message': "Email is already registered"}), 400

        cursor.execute("INSERT INTO user (email, password, role) VALUES (%s, %s, %s)", (email, password, role))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': "Registration successful"}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------ LOGIN ------------------
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[2] == password:  # Assuming user[2] = password
            session['user'] = {'email': user[1], 'role': user[3]}  # user[1]=email, user[3]=role
            return jsonify({'message': 'Login successful', 'role': user[3]}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
            
#-------------------Book Management(CRUD)--------------------------
@app.route("/api/book_manage", methods=['POST'])
def book_manage():
    try:
        data = request.get_json()

        title = data.get("title")
        author = data.get("author")
        isbn = data.get("isbn")
        category_name = data.get("category")
        quantity = data.get("quantity")

        cursor = mysql.connection.cursor()

        #  Get or create category
        cursor.execute("SELECT id FROM Category WHERE name = %s", (category_name,))
        category = cursor.fetchone()

        if category:
            category_id = category[0]
        else:
            cursor.execute("INSERT INTO Category (name) VALUES (%s)", (category_name,))
            mysql.connection.commit()
            category_id = cursor.lastrowid

        # Insert book
        insert_query = """
            INSERT INTO Book (title, author, isbn, category_id, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (title, author, isbn, category_id, quantity))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': "Book added successfully"}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
#--------------------------------Update Book -----------------------
@app.route("/api/update_book/<int:id>", methods=["PUT"])
def update_book(id):
    try:
        data = request.get_json()

        title = data.get("title")
        author = data.get("author")
        isbn = data.get("isbn")
        quantity = data.get("quantity")
        category_name = data.get("category")

        cursor = mysql.connection.cursor()

        # Get or insert category_id
        cursor.execute("SELECT id FROM Category WHERE name = %s", (category_name,))
        category = cursor.fetchone()

        if category:
            category_id = category[0]
        else:
            cursor.execute("INSERT INTO Category (name) VALUES (%s)", (category_name,))
            mysql.connection.commit()
            category_id = cursor.lastrowid

        # Update book
        update_query = """
            UPDATE Book 
            SET title = %s, author = %s, isbn = %s, quantity = %s, category_id = %s
            WHERE id = %s
        """
        cursor.execute(update_query, (title, author, isbn, quantity, category_id, id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Book updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#--------------------------------DELETE Book -----------------------
@app.route("/api/delete_book/<int:id>", methods=["DELETE"])
def delete_book(id):
    try:
        cursor = mysql.connection.cursor()
        
        query = "DELETE FROM Book WHERE id = %s"
        cursor.execute(query, (id,))
        mysql.connection.commit()
        
        cursor.close()
        return jsonify({"message": "Book ID deleted successfully"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#--------------------------------View Book -----------------------
@app.route("/api/views_book", methods=["GET"])
def views_book():
    try:
        cursor = mysql.connection.cursor()
        query  = "SELECT * FROM book "
        book = cursor.execute(query)
        book = cursor.fetchall()
        mysql.connection.commit()
        return jsonify({"result": book})
    except Exception as e:
        return jsonify({ "error": str(e)})
#-------------------Search Book-----------------------------
@app.route("/api/search_books", methods=["GET"])
def search_books():
    try:
        title = request.args.get("title")
        author = request.args.get("author")
        isbn = request.args.get("isbn")
        category = request.args.get("category")

        cursor = mysql.connection.cursor()

        query = """
            SELECT 
                b.id, b.title, b.author, b.isbn, b.quantity,
                c.name AS category
            FROM Book b
            LEFT JOIN Category c ON b.category_id = c.id
            WHERE 1=1
        """
        params = []

        if title:
            query += " AND b.title LIKE %s"
            params.append(f"%{title}%")
        if author:
            query += " AND b.author LIKE %s"
            params.append(f"%{author}%")
        if isbn:
            query += " AND b.isbn = %s"
            params.append(isbn)
        if category:
            query += " AND c.name LIKE %s"
            params.append(f"%{category}%")

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        # Convert result to list of dictionaries manually
        column_names = [desc[0] for desc in cursor.description]
        books = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        return jsonify(books), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
#--------------------------Issue Book_--------------------------
@app.route("/api/issue_book", methods=["POST"])
def issue_book():
    try:
        data = request.get_json()
        student_id = data.get("student_id")
        book_id = data.get("book_id")

        issue_date = datetime.today().date()
        due_date = issue_date + timedelta(days=14)  # 2 weeks due date

        cursor = mysql.connection.cursor()

        query = """
            INSERT INTO IssuedBooks (student_id, book_id, issue_date, due_date)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (student_id, book_id, issue_date, due_date))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Book issued successfully"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
#---------------return Book--------------------------
@app.route("/api/return_book/<int:issue_id>", methods=["POST"])
def return_book(issue_id):
    try:
        return_date = datetime.today().date()
        cursor = mysql.connection.cursor()

        # Get issue details
        cursor.execute("SELECT due_date FROM IssuedBooks WHERE id = %s", (issue_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Issue ID not found"}), 404

        due_date = row[0]
        fine = 0
        if return_date > due_date:
            delta = (return_date - due_date).days
            fine = delta * 10  # fine Rs.10 per day

        # Update return info
        cursor.execute("""
            UPDATE IssuedBooks
            SET return_date = %s, fine = %s
            WHERE id = %s
        """, (return_date, fine, issue_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "message": "Book returned successfully",
            "return_date": str(return_date),
            "fine": fine
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#---------------------------User Dashboard-----------------------
@app.route("/api/user_dashboard/<int:student_id>", methods=["GET"])
def user_dashboard(student_id):
    try:
        cursor = mysql.connection.cursor()

        query = """
            SELECT 
                b.title,
                i.issue_date,
                i.due_date,
                i.return_date,
                i.fine
            FROM IssuedBooks i
            JOIN Book b ON i.book_id = b.id
            WHERE i.student_id = %s
        """
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()

        books = []
        for row in rows:
            books.append({
                "title": row[0],
                "issue_date": str(row[1]),
                "due_date": str(row[2]),
                "return_date": str(row[3]) if row[3] else None,
                "fine": row[4]
            })

        return jsonify({
            "student_id": student_id,
            "issued_books": books
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#----------------------Admin Dashboard---------------------------
@app.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():
    try:
        cursor = mysql.connection.cursor()

        # 1. Total Books
        cursor.execute("SELECT COUNT(*) FROM Book")
        total_books = cursor.fetchone()[0]

        # 2. All Issued Books (not returned yet)
        cursor.execute("""
            SELECT i.id, b.title, i.student_id, i.issue_date, i.due_date
            FROM IssuedBooks i
            JOIN Book b ON i.book_id = b.id
            WHERE i.return_date IS NULL
        """)
        issued_books = cursor.fetchall()
        issued_books_list = [
            {"issue_id": r[0], "title": r[1], "student_id": r[2], "issue_date": str(r[3]), "due_date": str(r[4])}
            for r in issued_books
        ]

        # 3. Fine Records (all fines > 0)
        cursor.execute("SELECT student_id, fine FROM IssuedBooks WHERE fine > 0")
        fines = cursor.fetchall()
        fine_records = [{"student_id": r[0], "fine": r[1]} for r in fines]

        # 4. Reports based on query param: type=daily|weekly|monthly
        report_type = request.args.get("type", "daily").lower()

        if report_type == "daily":
            time_filter = "DATE(issue_date) = CURDATE()"
        elif report_type == "weekly":
            time_filter = "YEARWEEK(issue_date, 1) = YEARWEEK(CURDATE(), 1)"
        elif report_type == "monthly":
            time_filter = "YEAR(issue_date) = YEAR(CURDATE()) AND MONTH(issue_date) = MONTH(CURDATE())"
        else:
            return jsonify({"error": "Invalid report type"}), 400

        # Books issued in timeframe
        cursor.execute(f"SELECT COUNT(*) FROM IssuedBooks WHERE {time_filter}")
        books_issued = cursor.fetchone()[0]

        # Books returned in timeframe
        cursor.execute(f"SELECT COUNT(*) FROM IssuedBooks WHERE return_date IS NOT NULL AND {time_filter.replace('issue_date', 'return_date')}")
        books_returned = cursor.fetchone()[0]

        # Fine collected in timeframe
        cursor.execute(f"SELECT SUM(fine) FROM IssuedBooks WHERE return_date IS NOT NULL AND {time_filter.replace('issue_date', 'return_date')}")
        fine_collected = cursor.fetchone()[0] or 0

        return jsonify({
            "total_books": total_books,
            "issued_books": issued_books_list,
            "fine_records": fine_records,
            "reports": {
                "type": report_type,
                "books_issued": books_issued,
                "books_returned": books_returned,
                "fine_collected": fine_collected
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

        
    




if __name__ == '__main__':
    app.run(debug=True)
    