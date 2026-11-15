from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)
import pymysql
import os
import re
import uuid
import bcrypt
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# =========================================================
# CONFIGURATION
# =========================================================

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing from the .env file")

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_image(image):
    """Save an uploaded image and return its path relative to static/."""
    if not image or not image.filename:
        return None

    if not allowed_file(image.filename):
        raise ValueError("Only PNG, JPG, JPEG and WEBP images are allowed")

    extension = image.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"{uuid.uuid4()}.{extension}")
    image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return f"uploads/{filename}"


def delete_image(image_path):
    """Delete only a file located inside static/uploads."""
    if not image_path:
        return

    filename = os.path.basename(image_path)
    full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.isfile(full_path):
        os.remove(full_path)


# =========================================================
# DATABASE CONNECTIONS
# =========================================================

def get_db_connection():
    """Connection to the database used by login and the to-do application."""
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        autocommit=False
    )


def get_library_connection():
    
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("LIBRARY_DB_NAME", "librarryy"),
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        autocommit=False
    )


# =========================================================
# COMMON HELPERS
# =========================================================

def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or ""))


def login_required():
    return "user_id" in session


def library_redirect():
    return redirect(url_for("library"))


def get_user_todos(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT todo_id, title, is_done, created_at
                FROM todos
                WHERE user_id = %s
                ORDER BY todo_id DESC
                """,
                (user_id,)
            )
            return cursor.fetchall()
    finally:
        connection.close()


def parse_book_form():
    """Read and validate all fields required by the BOOK table."""
    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    year_text = request.form.get("publish_year", "").strip()
    author_text = request.form.get("author_id", "").strip()
    publisher_text = request.form.get("publisher_id", "").strip()
    category_text = request.form.get("category_id", "").strip()

    if not title:
        raise ValueError("Book title is required")
    if len(title) > 150:
        raise ValueError("Book title must be 150 characters or less")
    if not price_text:
        raise ValueError("Book price is required")
    if not author_text or not publisher_text or not category_text:
        raise ValueError("Please select an author, publisher and category")

    try:
        price = Decimal(price_text)
        author_id = int(author_text)
        publisher_id = int(publisher_text)
        category_id = int(category_text)
        publish_year = int(year_text) if year_text else None
    except (InvalidOperation, ValueError):
        raise ValueError("Please enter valid book information")

    if price < 0:
        raise ValueError("Price cannot be negative")
    if publish_year is not None and not (0 < publish_year <= 2100):
        raise ValueError("Please enter a valid publication year")

    return {
        "title": title,
        "price": price,
        "publish_year": publish_year,
        "author_id": author_id,
        "publisher_id": publisher_id,
        "category_id": category_id
    }


def get_library_dropdown_data(cursor):
    cursor.execute(
        "SELECT author_id, name, country, photo FROM AUTHOR ORDER BY name"
    )
    authors = cursor.fetchall()

    cursor.execute(
        "SELECT publisher_id, name, country FROM PUBLISHER ORDER BY name"
    )
    publishers = cursor.fetchall()

    cursor.execute(
        "SELECT category_id, name FROM CATEGORY ORDER BY name"
    )
    categories = cursor.fetchall()

    return authors, publishers, categories


# =========================================================
# HOME / TO-DO LIST
# =========================================================

@app.route("/")
def home():
    if not login_required():
        return redirect(url_for("login"))

    todos = get_user_todos(session["user_id"])
    return render_template(
        "todos.html",
        todos=todos,
        user_name=session.get("user_name")
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name:
        flash("Name is required", "error")
        return redirect(url_for("register"))
    if len(name) > 100:
        flash("Name is too long", "error")
        return redirect(url_for("register"))
    if not email:
        flash("Email is required", "error")
        return redirect(url_for("register"))
    if not valid_email(email):
        flash("Please enter a valid email", "error")
        return redirect(url_for("register"))
    if not password.strip():
        flash("Password is required", "error")
        return redirect(url_for("register"))
    if not confirm_password.strip():
        flash("Confirm password is required", "error")
        return redirect(url_for("register"))
    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect(url_for("register"))

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, name, password_hash)
                VALUES (%s, %s, %s)
                """,
                (email, name, password_hash)
            )
            connection.commit()
            user_id = cursor.lastrowid
    except pymysql.err.IntegrityError:
        connection.rollback()
        flash("Email Already Exists", "error")
        return redirect(url_for("register"))
    finally:
        connection.close()

    session.clear()
    session["user_id"] = user_id
    session["user_name"] = name
    return redirect(url_for("home"))


# =========================================================
# LOGIN / LOGOUT
# =========================================================

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email:
        flash("Email is required", "error")
        return redirect(url_for("login"))
    if not valid_email(email):
        flash("Please enter a valid email", "error")
        return redirect(url_for("login"))
    if not password.strip():
        flash("Password is required", "error")
        return redirect(url_for("login"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, name, password_hash
                FROM users
                WHERE email = %s
                """,
                (email,)
            )
            user = cursor.fetchone()
    finally:
        connection.close()

    if user is None:
        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )
    if not password_correct:
        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    session.clear()
    session["user_id"] = user["user_id"]
    session["user_name"] = user["name"]
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# =========================================================
# TO-DO CRUD
# =========================================================

@app.route("/todo/add", methods=["POST"])
def add_todo():
    if not login_required():
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    if not title:
        flash("Title is required", "error")
        return redirect(url_for("home"))
    if len(title) > 200:
        flash("Title is too long", "error")
        return redirect(url_for("home"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO todos (user_id, title) VALUES (%s, %s)",
                (session["user_id"], title)
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return redirect(url_for("home"))


@app.route("/todo/edit/<int:todo_id>", methods=["POST"])
def edit_todo(todo_id):
    if not login_required():
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    if not title:
        flash("Title is required", "error")
        return redirect(url_for("home"))
    if len(title) > 200:
        flash("Title is too long", "error")
        return redirect(url_for("home"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE todos SET title = %s
                WHERE todo_id = %s AND user_id = %s
                """,
                (title, todo_id, session["user_id"])
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return redirect(url_for("home"))


@app.route("/todo/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    if not login_required():
        return redirect(url_for("login"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT is_done FROM todos
                WHERE todo_id = %s AND user_id = %s
                """,
                (todo_id, session["user_id"])
            )
            todo = cursor.fetchone()

            if todo is None:
                return redirect(url_for("home"))

            new_status = 0 if todo["is_done"] else 1
            cursor.execute(
                """
                UPDATE todos SET is_done = %s
                WHERE todo_id = %s AND user_id = %s
                """,
                (new_status, todo_id, session["user_id"])
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return redirect(url_for("home"))


@app.route("/todo/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    if not login_required():
        return redirect(url_for("login"))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM todos
                WHERE todo_id = %s AND user_id = %s
                """,
                (todo_id, session["user_id"])
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    return redirect(url_for("home"))


# =========================================================
# LIBRARY: CATALOGUE + SEARCH (F2.1 and F2.2)
# =========================================================


@app.route("/library")
def library():
    if not login_required():
        return redirect(url_for("login"))

    title_keyword = request.args.get("title", "").strip()
    min_price_text = request.args.get("min_price", "").strip()
    max_price_text = request.args.get("max_price", "").strip()

    selected_categories = request.args.getlist("category_id")
    selected_categories = [
        value for value in selected_categories if value.isdigit()
    ]

    where_parts = []
    params = []

    if title_keyword:
        where_parts.append("b.title LIKE %s")
        params.append(f"%{title_keyword}%")

    if min_price_text:
        try:
            min_price = Decimal(min_price_text)
            if min_price < 0:
                raise ValueError
            where_parts.append("b.price >= %s")
            params.append(min_price)
        except (InvalidOperation, ValueError):
            flash("Minimum price must be a valid non-negative number", "error")
            min_price_text = ""

    if max_price_text:
        try:
            max_price = Decimal(max_price_text)
            if max_price < 0:
                raise ValueError
            where_parts.append("b.price <= %s")
            params.append(max_price)
        except (InvalidOperation, ValueError):
            flash("Maximum price must be a valid non-negative number", "error")
            max_price_text = ""

    if min_price_text and max_price_text:
        try:
            if Decimal(min_price_text) > Decimal(max_price_text):
                flash("Minimum price cannot be greater than maximum price", "error")
                where_parts = [
                    part for part in where_parts
                    if part not in ("b.price >= %s", "b.price <= %s")
                ]
                params = [
                    value for value in params
                    if value not in (Decimal(min_price_text), Decimal(max_price_text))
                ]
                min_price_text = ""
                max_price_text = ""
        except InvalidOperation:
            pass

    if selected_categories:
        placeholders = ", ".join(["%s"] * len(selected_categories))
        where_parts.append(f"b.category_id IN ({placeholders})")
        params.extend(int(value) for value in selected_categories)

    sql = """
        SELECT
            b.book_id,
            b.title,
            b.price,
            b.publish_year,
            b.author_id,
            b.publisher_id,
            b.category_id,
            b.cover_image,
            a.name AS author_name,
            p.name AS publisher_name,
            c.name AS category_name
        FROM BOOK b
        INNER JOIN AUTHOR a ON b.author_id = a.author_id
        INNER JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
        INNER JOIN CATEGORY c ON b.category_id = c.category_id
    """

    if where_parts:
        sql += " WHERE " + " AND ".join(where_parts)

    sql += " ORDER BY b.price ASC, b.title ASC"

    connection = get_library_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            all_books = cursor.fetchall()

            # All books are kept separately for the loan dropdown,
            # so search filters do not hide books from this form.
            cursor.execute(
                "SELECT book_id, title FROM BOOK ORDER BY title"
            )
            loan_books = cursor.fetchall()

            authors, publishers, categories = get_library_dropdown_data(cursor)

            # Dashboard counts
            cursor.execute("SELECT COUNT(*) AS total FROM BOOK")
            total_books = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM AUTHOR")
            total_authors = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM PUBLISHER")
            total_publishers = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM CATEGORY")
            total_categories = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM MEMBER")
            total_members = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM LOAN")
            total_loans = cursor.fetchone()["total"]

            # F2.3(a): category report
            cursor.execute(
                """
                SELECT c.category_id, c.name AS category_name,
                       COUNT(b.book_id) AS total_books,
                       AVG(b.price) AS average_price
                FROM CATEGORY c
                LEFT JOIN BOOK b ON c.category_id = b.category_id
                GROUP BY c.category_id, c.name
                ORDER BY c.name
                """
            )
            category_report = cursor.fetchall()

            # F2.3(b) / F2.6(b): author report
            cursor.execute(
                """
                SELECT a.author_id, a.name AS author_name,
                       COUNT(b.book_id) AS total_books
                FROM AUTHOR a
                INNER JOIN BOOK b ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name
                HAVING COUNT(b.book_id) >= 2
                ORDER BY total_books DESC
                """
            )
            authors_with_two_books = cursor.fetchall()

            # F2.3(c): library price report
            cursor.execute(
                """
                SELECT SUM(price) AS total_price,
                       MIN(price) AS smallest_price,
                       MAX(price) AS largest_price
                FROM BOOK
                """
            )
            price_report = cursor.fetchone()

            # F2.4(a): loans not returned
            cursor.execute(
                """
                SELECT l.loan_id, b.title AS book_title,
                       m.name AS member_name, l.loan_date
                FROM LOAN l
                INNER JOIN BOOK b ON l.book_id = b.book_id
                INNER JOIN MEMBER m ON l.member_id = m.member_id
                WHERE l.return_date IS NULL
                ORDER BY l.loan_date
                """
            )
            unreturned_loans = cursor.fetchall()

            # F2.4(b): members who never borrowed
            cursor.execute(
                """
                SELECT m.member_id, m.name, m.email
                FROM MEMBER m
                LEFT JOIN LOAN l ON m.member_id = l.member_id
                WHERE l.loan_id IS NULL
                ORDER BY m.name
                """
            )
            members_never_borrowed = cursor.fetchall()

            # F2.4(c): books never borrowed
            cursor.execute(
                """
                SELECT b.book_id, b.title, b.price
                FROM BOOK b
                LEFT JOIN LOAN l ON b.book_id = l.book_id
                WHERE l.loan_id IS NULL
                ORDER BY b.title
                """
            )
            books_never_borrowed = cursor.fetchall()

            # F2.5(a): top 3 most borrowed books
            cursor.execute(
                """
                SELECT b.book_id, b.title,
                       COUNT(l.loan_id) AS total_loans
                FROM BOOK b
                INNER JOIN LOAN l ON b.book_id = l.book_id
                GROUP BY b.book_id, b.title
                ORDER BY total_loans DESC, b.title ASC
                LIMIT 3
                """
            )
            top_books = cursor.fetchall()

            # F2.5(b): member with most loans
            cursor.execute(
                """
                SELECT m.member_id, m.name AS member_name,
                       COUNT(l.loan_id) AS total_loans
                FROM MEMBER m
                INNER JOIN LOAN l ON m.member_id = l.member_id
                GROUP BY m.member_id, m.name
                ORDER BY total_loans DESC, m.name ASC
                LIMIT 1
                """
            )
            top_member = cursor.fetchone()

            # F2.6(a): all authors and book counts
            cursor.execute(
                """
                SELECT a.author_id, a.name AS author_name,
                       COUNT(b.book_id) AS total_books
                FROM AUTHOR a
                LEFT JOIN BOOK b ON a.author_id = b.author_id
                GROUP BY a.author_id, a.name
                ORDER BY total_books DESC, a.name ASC
                """
            )
            author_book_counts = cursor.fetchall()

            # F2.6(b): authors and publishers from same country
            cursor.execute(
                """
                SELECT b.book_id, b.title,
                       a.name AS author_name, a.country AS author_country,
                       p.name AS publisher_name, p.country AS publisher_country
                FROM BOOK b
                INNER JOIN AUTHOR a ON b.author_id = a.author_id
                INNER JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
                WHERE a.country = p.country
                ORDER BY b.title
                """
            )
            same_country_books = cursor.fetchall()

            # Full members table for the members section
            cursor.execute(
                """
                SELECT member_id, name, email, join_date
                FROM MEMBER
                ORDER BY name
                """
            )
            members = cursor.fetchall()

            # Full loans table
            cursor.execute(
                """
                SELECT l.loan_id, b.title AS book_title,
                       m.name AS member_name, l.loan_date, l.return_date
                FROM LOAN l
                INNER JOIN BOOK b ON l.book_id = b.book_id
                INNER JOIN MEMBER m ON l.member_id = m.member_id
                ORDER BY l.loan_date DESC
                """
            )
            loans = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "library.html",
        all_books=all_books,
        loan_books=loan_books,
        authors=authors,
        publishers=publishers,
        categories=categories,
        title_keyword=title_keyword,
        min_price=min_price_text,
        max_price=max_price_text,
        selected_categories=selected_categories,
        total_books=total_books,
        total_authors=total_authors,
        total_publishers=total_publishers,
        total_categories=total_categories,
        total_members=total_members,
        total_loans=total_loans,
        category_report=category_report,
        authors_with_two_books=authors_with_two_books,
        price_report=price_report,
        unreturned_loans=unreturned_loans,
        members_never_borrowed=members_never_borrowed,
        books_never_borrowed=books_never_borrowed,
        top_books=top_books,
        top_member=top_member,
        author_book_counts=author_book_counts,
        same_country_books=same_country_books,
        members=members,
        loans=loans,
        user_name=session.get("user_name")
    )


# =========================================================
# ADD BOOK
# =========================================================

@app.route("/library/book/add", methods=["POST"])
def add_book():
    if not login_required():
        return redirect(url_for("login"))

    connection = None
    image_path = None

    try:
        data = parse_book_form()
        image_path = save_image(request.files.get("cover_image") or request.files.get("image"))

        connection = get_library_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO BOOK
                    (title, price, publish_year, author_id,
                     publisher_id, category_id, cover_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data["title"], data["price"], data["publish_year"],
                    data["author_id"], data["publisher_id"],
                    data["category_id"], image_path
                )
            )
        connection.commit()

    except (ValueError, TypeError) as error:
        if image_path:
            delete_image(image_path)
        flash(str(error), "error")
        return library_redirect()
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        if image_path:
            delete_image(image_path)
        print("ADD BOOK DATABASE ERROR:", error)
        flash("Could not add book. Check the selected author, publisher and category.", "error")
        return library_redirect()
    finally:
        if connection:
            connection.close()

    flash("Book added successfully", "success")
    return library_redirect()


# =========================================================
# EDIT BOOK
# =========================================================

@app.route("/library/book/edit/<int:book_id>", methods=["POST"])
def edit_book(book_id):
    if not login_required():
        return redirect(url_for("login"))

    connection = None
    new_image_path = None
    old_image_path = None

    try:
        data = parse_book_form()
        connection = get_library_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cover_image FROM BOOK WHERE book_id = %s",
                (book_id,)
            )
            book = cursor.fetchone()

            if book is None:
                flash("Book not found", "error")
                return library_redirect()

            old_image_path = book["cover_image"]
            uploaded_image = request.files.get("cover_image") or request.files.get("image")

            if uploaded_image and uploaded_image.filename:
                new_image_path = save_image(uploaded_image)
                image_path = new_image_path
            else:
                image_path = old_image_path

            cursor.execute(
                """
                UPDATE BOOK
                SET title = %s, price = %s, publish_year = %s,
                    author_id = %s, publisher_id = %s,
                    category_id = %s, cover_image = %s
                WHERE book_id = %s
                """,
                (
                    data["title"], data["price"], data["publish_year"],
                    data["author_id"], data["publisher_id"],
                    data["category_id"], image_path, book_id
                )
            )
        connection.commit()

    except (ValueError, TypeError) as error:
        if new_image_path:
            delete_image(new_image_path)
        flash(str(error), "error")
        return library_redirect()
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        if new_image_path:
            delete_image(new_image_path)
        print("EDIT BOOK DATABASE ERROR:", error)
        flash("Could not update book. Check the database values.", "error")
        return library_redirect()
    finally:
        if connection:
            connection.close()

    if new_image_path and old_image_path:
        delete_image(old_image_path)

    flash("Book updated successfully", "success")
    return library_redirect()


# =========================================================
# DELETE BOOK
# =========================================================

@app.route("/library/book/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if not login_required():
        return redirect(url_for("login"))

    connection = get_library_connection()
    image_path = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cover_image FROM BOOK WHERE book_id = %s",
                (book_id,)
            )
            book = cursor.fetchone()
            if book is None:
                flash("Book not found", "error")
                return library_redirect()

            image_path = book["cover_image"]
            cursor.execute("DELETE FROM BOOK WHERE book_id = %s", (book_id,))
        connection.commit()
    except pymysql.MySQLError as error:
        connection.rollback()
        print("DELETE BOOK DATABASE ERROR:", error)
        flash("Could not delete book", "error")
        return library_redirect()
    finally:
        connection.close()

    if image_path:
        delete_image(image_path)

    flash("Book deleted successfully", "success")
    return library_redirect()


# =========================================================
# ADD / EDIT / DELETE AUTHOR
# =========================================================

@app.route("/library/author/add", methods=["POST"])
def add_author():
    if not login_required():
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image_path = None
    connection = None

    if not name:
        flash("Author name is required", "error")
        return library_redirect()

    try:
        image_path = save_image(request.files.get("photo") or request.files.get("image"))
        connection = get_library_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO AUTHOR (name, country, photo) VALUES (%s, %s, %s)",
                (name, country or None, image_path)
            )
        connection.commit()
    except (ValueError, pymysql.MySQLError) as error:
        if connection:
            connection.rollback()
        if image_path:
            delete_image(image_path)
        print("ADD AUTHOR ERROR:", error)
        flash(str(error) if isinstance(error, ValueError) else "Could not add author", "error")
        return library_redirect()
    finally:
        if connection:
            connection.close()

    flash("Author added successfully", "success")
    return library_redirect()


@app.route("/library/author/edit/<int:author_id>", methods=["POST"])
def edit_author(author_id):
    if not login_required():
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    if not name:
        flash("Author name is required", "error")
        return library_redirect()

    connection = get_library_connection()
    new_image_path = None
    old_image_path = None
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT photo FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )
            author = cursor.fetchone()
            if author is None:
                flash("Author not found", "error")
                return library_redirect()

            old_image_path = author["photo"]
            uploaded_image = request.files.get("photo") or request.files.get("image")
            if uploaded_image and uploaded_image.filename:
                new_image_path = save_image(uploaded_image)
                image_path = new_image_path
            else:
                image_path = old_image_path

            cursor.execute(
                """
                UPDATE AUTHOR
                SET name = %s, country = %s, photo = %s
                WHERE author_id = %s
                """,
                (name, country or None, image_path, author_id)
            )
        connection.commit()
    except (ValueError, pymysql.MySQLError) as error:
        connection.rollback()
        if new_image_path:
            delete_image(new_image_path)
        print("EDIT AUTHOR ERROR:", error)
        flash(str(error) if isinstance(error, ValueError) else "Could not update author", "error")
        return library_redirect()
    finally:
        connection.close()

    if new_image_path and old_image_path:
        delete_image(old_image_path)

    flash("Author updated successfully", "success")
    return library_redirect()


@app.route("/library/author/delete/<int:author_id>", methods=["POST"])
def delete_author(author_id):
    if not login_required():
        return redirect(url_for("login"))

    connection = get_library_connection()
    author_photo = None
    book_images = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT photo FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )
            author = cursor.fetchone()
            if author is None:
                flash("Author not found", "error")
                return library_redirect()

            author_photo = author["photo"]

            cursor.execute(
                "SELECT cover_image FROM BOOK WHERE author_id = %s",
                (author_id,)
            )
            book_images = [
                row["cover_image"] for row in cursor.fetchall()
                if row["cover_image"]
            ]

            # BOOK.author_id has ON DELETE CASCADE in the supplied schema.
            cursor.execute("DELETE FROM AUTHOR WHERE author_id = %s", (author_id,))
        connection.commit()
    except pymysql.MySQLError as error:
        connection.rollback()
        print("DELETE AUTHOR ERROR:", error)
        flash("Could not delete author. Check related records.", "error")
        return library_redirect()
    finally:
        connection.close()

    delete_image(author_photo)
    for path in book_images:
        delete_image(path)

    flash("Author and related books deleted successfully", "success")
    return library_redirect()


# =========================================================
# ADD PUBLISHER / CATEGORY
# =========================================================

@app.route("/library/publisher/add", methods=["POST"])
def add_publisher():
    if not login_required():
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    if not name:
        flash("Publisher name is required", "error")
        return library_redirect()

    connection = get_library_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO PUBLISHER (name, country) VALUES (%s, %s)",
                (name, country or None)
            )
        connection.commit()
    except pymysql.MySQLError as error:
        connection.rollback()
        print("ADD PUBLISHER ERROR:", error)
        flash("Could not add publisher", "error")
        return library_redirect()
    finally:
        connection.close()

    flash("Publisher added successfully", "success")
    return library_redirect()


@app.route("/library/category/add", methods=["POST"])
def add_category():
    if not login_required():
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    if not name:
        flash("Category name is required", "error")
        return library_redirect()

    connection = get_library_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO CATEGORY (name) VALUES (%s)", (name,))
        connection.commit()
    except pymysql.MySQLError as error:
        connection.rollback()
        print("ADD CATEGORY ERROR:", error)
        flash("Could not add category", "error")
        return library_redirect()
    finally:
        connection.close()

    flash("Category added successfully", "success")
    return library_redirect()


# =========================================================
# MEMBERS AND LOANS
# =========================================================

@app.route("/library/member/add", methods=["POST"])
def add_member():
    if not login_required():
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    join_date = request.form.get("join_date", "").strip()

    if not name or not email or not join_date:
        flash("Member name, email and join date are required", "error")
        return library_redirect()
    if not valid_email(email):
        flash("Please enter a valid member email", "error")
        return library_redirect()

    connection = get_library_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO MEMBER (name, email, join_date)
                VALUES (%s, %s, %s)
                """,
                (name, email, join_date)
            )
        connection.commit()
    except pymysql.MySQLError as error:
        connection.rollback()
        print("ADD MEMBER ERROR:", error)
        flash("Could not add member. The email may already exist.", "error")
        return library_redirect()
    finally:
        connection.close()

    flash("Member added successfully", "success")
    return library_redirect()


@app.route("/library/loan/add", methods=["POST"])
def add_loan():
    if not login_required():
        return redirect(url_for("login"))

    book_text = request.form.get("book_id", "").strip()
    member_text = request.form.get("member_id", "").strip()
    loan_date = request.form.get("loan_date", "").strip()
    return_date = request.form.get("return_date", "").strip() or None

    try:
        book_id = int(book_text)
        member_id = int(member_text)
        if book_id <= 0 or member_id <= 0:
            raise ValueError
    except (TypeError, ValueError):
        flash("Please select a valid book and member", "error")
        return library_redirect()

    if not loan_date:
        flash("Loan date is required", "error")
        return library_redirect()

    connection = get_library_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO LOAN (book_id, member_id, loan_date, return_date)
                VALUES (%s, %s, %s, %s)
                """,
                (book_id, member_id, loan_date, return_date)
            )
        connection.commit()
    except pymysql.MySQLError as error:
        connection.rollback()
        print("ADD LOAN ERROR:", error)
        flash("Could not add loan. Check the selected book and member.", "error")
        return library_redirect()
    finally:
        connection.close()

    flash("Loan added successfully", "success")
    return library_redirect()


@app.route("/library/loan/return/<int:loan_id>", methods=["POST"])
def return_loan(loan_id):
    if not login_required():
        return redirect(url_for("login"))

    connection = get_library_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE LOAN
                SET return_date = CURDATE()
                WHERE loan_id = %s AND return_date IS NULL
                """,
                (loan_id,)
            )
        connection.commit()
    except pymysql.MySQLError as error:
        connection.rollback()
        print("RETURN LOAN ERROR:", error)
        flash("Could not update loan", "error")
        return library_redirect()
    finally:
        connection.close()

    flash("Book return recorded", "success")
    return library_redirect()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
