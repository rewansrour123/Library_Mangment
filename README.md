# 📚 Lab 4: Advanced SQL Queries & Library Management System

A web application developed using **Python, Flask, MySQL, HTML, CSS, and JavaScript** as an extension of the previous Lab 3 project.

The project extends the existing Login & To-Do application and Library Management System by introducing a complete relational library database with six interconnected tables, foreign key constraints, SQL queries, and new search and reporting pages.

---

## 👥 1. Team Members

| Name | Student ID | Responsibilities |
|---|---|---|
| Rewan Mahmoud Mohamed | 2304098 | Database Design, Flask Backend, Authentication, To-Do List, and Library Management |

---

## 🛠️ 2. Technologies & Tools

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL
- **Database Connector:** PyMySQL
- **Password Security:** bcrypt
- **Session Management:** Flask Sessions
- **Environment Variables:** python-dotenv
- **Database Management:** MySQL / DBeaver

---

## ✨ 3. Website Features

### A. Existing Login & To-Do Management System

The project maintains the existing functionality from previous labs:

- User registration and login.
- Duplicate email handling.
- Secure password hashing using bcrypt.
- Session-based authentication.
- Private task lists for each user.
- Add, edit, complete, and delete tasks.
- Client-side and server-side input validation.
- Parameterized SQL queries.
- Responsive user interface.
- Dark Mode and Light Mode.

### B. Library Management System

The library system is extended to support six related database tables:

- Authors management.
- Publishers management.
- Categories management.
- Books management.
- Library members management.
- Book loans management.
- Foreign key relationships between related tables.
- Referential integrity using database constraints.
- Automatic deletion of dependent records using ON DELETE CASCADE where required.
- Storage and management of library records using MySQL.

### C. New Lab 4 Website Pages

The following pages implement the required SQL operations:

**F2.1 — Search Books (WHERE)**

- Search books using a title keyword with LIKE.
- Filter books using minimum and maximum prices with BETWEEN.
- Filter books by selected categories.
- Display matching books ordered by price, cheapest first.
- Use parameterized SQL queries to prevent SQL injection.

**F2.2 — Book Catalogue (JOIN)**

- Display books with their related author, publisher, and category information.
- Use SQL JOIN operations to retrieve related records.

**F2.3 — Library Reports**

- Display library statistics using SQL aggregate functions.
- Retrieve the required summary information from the database.

**F2.4 — Book Loans**

- Display loan records with their related book and member information.
- Retrieve loan details using relational queries.

**F2.5 — Most Borrowed Books**

- Identify the most frequently borrowed books.
- Use GROUP BY, aggregate functions, and ORDER BY.

**F2.6 — Authors**

- Display author information and related book information.
- Retrieve the required author-related results using SQL queries.

---

## 🗄️ 4. Database Design

The Lab 4 library database contains six relational tables.

### 1. AUTHOR

Stores information about book authors.

- `author_id` — Primary Key.
- `name` — Author name.
- `country` — Author's country.

### 2. PUBLISHER

Stores information about book publishers.

- `publisher_id` — Primary Key.
- `name` — Publisher name.
- `country` — Publisher's country.

### 3. CATEGORY

Stores book categories.

- `category_id` — Primary Key.
- `name` — Category name.

### 4. BOOK

Stores information about library books.

- `book_id` — Primary Key.
- `title` — Book title.
- `price` — Book price.
- `publish_year` — Publication year.
- `author_id` — Foreign Key referencing AUTHOR.
- `publisher_id` — Foreign Key referencing PUBLISHER.
- `category_id` — Foreign Key referencing CATEGORY.

### 5. MEMBER

Stores information about library members.

- `member_id` — Primary Key.
- Member information as defined in the database schema.

### 6. LOAN

Stores book borrowing transactions.

- `loan_id` — Primary Key.
- `book_id` — Foreign Key referencing BOOK.
- `member_id` — Foreign Key referencing MEMBER.
- Loan date.
- Return date, which can be NULL for books that have not yet been returned.

### Database Relationships

- `BOOK.author_id` references `AUTHOR.author_id`.
- `BOOK.publisher_id` references `PUBLISHER.publisher_id`.
- `BOOK.category_id` references `CATEGORY.category_id`.
- `LOAN.book_id` references `BOOK.book_id`.
- `LOAN.member_id` references `MEMBER.member_id`.

The database uses primary keys and foreign keys to maintain relational integrity.

It also uses `ON DELETE CASCADE` for the required dependent relationships, including author-to-books and book-to-loans.

---

## 📁 5. Project Files

The project contains the following main SQL and website files:

### Database Scripts

- `problem2_DDL.sql` — Creates the library database tables and their relationships.
- `problem2_DML.sql` — Inserts sample data into the database.
- `problem2_Queries.sql` — Contains the SQL queries required for Lab 4 (F2.1–F2.6).

### Website Files

- `app.py` — Flask application and backend routes.
- `templates/` — HTML pages for the website.
- `static/` — CSS, JavaScript, and static assets.
- `.env.example` — Example environment configuration.
- `requirements.txt` — Python dependencies.

---

## 🚀 6. Installation & Setup

### Step 1 — Install Requirements

Make sure Python and MySQL are installed.

Navigate to the project directory and run:

```bash
pip install -r requirements.txt
```

### Step 2 — Set Up the Database

Execute the SQL scripts in the following order:

```bash
mysql -u root -p < problem2_DDL.sql
mysql -u root -p < problem2_DML.sql
```

Enter your MySQL password when prompted.

### Step 3 — Configure Environment Variables

Copy `.env.example` to `.env` and configure the required database credentials and Flask secret key.

Do not upload `.env` or expose sensitive credentials on GitHub.

### Step 4 — Run the Website

Navigate to the website directory:

```bash
cd website
python app.py
```

### Step 5 — Open the Website

Open the application in your browser:

http://127.0.0.1:5000/

Log in to access the website and navigate through the library search, catalogue, and reporting pages.

**Note:** The database scripts and Flask database configuration must use the same database name and credentials.

---

## 📸 7. Screenshots

Add screenshots of the actual implemented pages.

### Existing Application

- Registration page.
- Login page.
- To-Do list management.

### Library Management

- Books table.
- Authors table.
- Publishers and Categories tables.
- Members and Loans tables.

### Lab 4 SQL Pages

- F2.1 — Search Books.
- F2.2 — Book Catalogue.
- F2.3 — Library Reports.
- F2.4 — Book Loans.
- F2.5 — Most Borrowed Books.
- F2.6 — Authors.

---

## 🔐 8. Security and Database Integrity

- Primary keys to uniquely identify database records.
- Foreign keys to establish relationships between tables.
- Referential integrity constraints.
- Parameterized SQL queries to help prevent SQL injection.
- Input validation for database operations.
- Secure password hashing using bcrypt.
- Session-based user authentication.

---

## ✅ 9. Conclusion

This project extends the previous Login & To-Do and Library Management application by implementing the Lab 4 requirements.

It demonstrates relational database design, six interconnected database tables, primary and foreign keys, SQL queries, JOIN operations, filtering, aggregate functions, GROUP BY, HAVING, ORDER BY, and LIMIT.

The project also integrates these database operations into a Flask-based web application, providing practical search, catalogue, and reporting functionality using MySQL.

---

## 📚 10. Course Information

- **University:** Alexandria National University
- **Faculty:** Faculty of Engineering
- **Course:** Introduction to Database Systems
- **Lab:** Lab 4 — SQL Queries
- **Semester:** Fall 2026
- **Submission Deadline:** November 16, 2026, at 11:59 PM
