-- F2.1 - SEARCH BOOKS

SELECT
    b.book_id,
    b.title,
    b.price,
    b.publish_year,
    c.name AS category_name
FROM BOOK b
JOIN CATEGORY c
    ON b.category_id = c.category_id
WHERE b.title LIKE '%Python%'
  AND b.price BETWEEN 15 AND 40
  AND c.category_id IN (1, 2, 3)
ORDER BY b.price ASC;


-- F2.2 - CATALOGUE
SELECT
    b.book_id,
    b.title,
    b.price,
    b.publish_year,
    a.name AS author_name,
    p.name AS publisher_name,
    c.name AS category_name
FROM BOOK b
JOIN AUTHOR a
    ON b.author_id = a.author_id
JOIN PUBLISHER p
    ON b.publisher_id = p.publisher_id
JOIN CATEGORY c
    ON b.category_id = c.category_id
ORDER BY b.title ASC;

-- F2.3 (a) - CATEGORY REPORT

SELECT
    c.name AS category_name,
    COUNT(b.book_id) AS total_books,
    AVG(b.price) AS average_price
FROM CATEGORY c
LEFT JOIN BOOK b
    ON c.category_id = b.category_id
GROUP BY c.category_id, c.name
ORDER BY c.name;


-- F2.3 (b) - AUTHORS WITH AT LEAST 2 BOOKS

SELECT
    a.author_id,
    a.name AS author_name,
    COUNT(b.book_id) AS total_books
FROM AUTHOR a
JOIN BOOK b
    ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(b.book_id) >= 2
ORDER BY total_books DESC;

-- F2.3 (c) - LIBRARY PRICE REPORT


SELECT
    SUM(price) AS total_price,
    MIN(price) AS smallest_price,
    MAX(price) AS largest_price
FROM BOOK;

-- F2.4 (a) - NOT RETURNED LOANS

SELECT
    l.loan_id,
    b.title AS book_title,
    m.name AS member_name,
    l.loan_date
FROM LOAN l
JOIN BOOK b
    ON l.book_id = b.book_id
JOIN MEMBER m
    ON l.member_id = m.member_id
WHERE l.return_date IS NULL
ORDER BY l.loan_date;


-- F2.4 (b) - MEMBERS WHO NEVER BORROWED

SELECT
    m.member_id,
    m.name,
    m.email
FROM MEMBER m
LEFT JOIN LOAN l
    ON m.member_id = l.member_id
WHERE l.loan_id IS NULL;

-- F2.4 (c) - BOOKS NEVER BORROWED

SELECT
    b.book_id,
    b.title,
    b.price
FROM BOOK b
LEFT JOIN LOAN l
    ON b.book_id = l.book_id
WHERE l.loan_id IS NULL;


-- F2.5 (a) - TOP 3 MOST BORROWED BOOKS

SELECT
    b.book_id,
    b.title,
    COUNT(l.loan_id) AS total_loans
FROM BOOK b
JOIN LOAN l
    ON b.book_id = l.book_id
GROUP BY b.book_id, b.title
ORDER BY total_loans DESC, b.title ASC
LIMIT 3;

-- F2.5 (b) - MEMBER WITH MOST LOANS

SELECT
    m.member_id,
    m.name AS member_name,
    COUNT(l.loan_id) AS total_loans
FROM MEMBER m
JOIN LOAN l
    ON m.member_id = l.member_id
GROUP BY m.member_id, m.name
ORDER BY total_loans DESC, m.name ASC
LIMIT 1;


-- F2.6 (a) - AUTHORS AND BOOK COUNTS

SELECT
    a.author_id,
    a.name AS author_name,
    COUNT(b.book_id) AS total_books
FROM AUTHOR a
LEFT JOIN BOOK b
    ON a.author_id = b.author_id
GROUP BY a.author_id, a.name
ORDER BY total_books DESC, a.name ASC;


-- F2.6 (b) - AUTHOR AND PUBLISHER SAME COUNTRY

SELECT
    b.book_id,
    b.title,
    a.name AS author_name,
    a.country AS author_country,
    p.name AS publisher_name,
    p.country AS publisher_country
FROM BOOK b
JOIN AUTHOR a
    ON b.author_id = a.author_id
JOIN PUBLISHER p
    ON b.publisher_id = p.publisher_id
WHERE a.country = p.country;








