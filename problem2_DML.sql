USE library;
INSERT INTO AUTHOR (author_id, name, country, photo)
VALUES
(1, 'John Smith', 'USA', NULL),
(2, 'Sarah Johnson', 'USA', NULL),
(3, 'Ahmed Hassan', 'Egypt', NULL),
(4, 'David Brown', 'UK', NULL);


INSERT INTO PUBLISHER (publisher_id, name, country)
VALUES
(1, 'Oxford Press', 'UK'),
(2, 'Pearson', 'USA'),
(3, 'Nile Publishing', 'Egypt');


INSERT INTO CATEGORY (category_id, name)
VALUES
(1, 'Programming'),
(2, 'Science'),
(3, 'Literature');


INSERT INTO BOOK
(book_id, title, price, publish_year, author_id,
 publisher_id, category_id, cover_image)
VALUES
(1, 'Python Programming', 25.00, 2022, 1, 1, 1, NULL),
(2, 'Learning SQL', 18.50, 2021, 1, 2, 1, NULL),
(3, 'Database Systems', 35.00, 2023, 1, 2, 1, NULL),
(4, 'Introduction to Physics', 40.00, 2020, 2, 2, 2, NULL),
(5, 'Modern Chemistry', 22.00, 2022, 2, 1, 2, NULL),
(6, 'The Science Book', 19.00, 2021, 2, 3, 2, NULL),
(7, 'Egyptian History', 30.00, 2019, 3, 3, 3, NULL),
(8, 'Arabic Literature', 28.00, 2020, 3, 1, 3, NULL),
(9, 'Artificial Intelligence', 45.00, 2024, 3, 2, 1, NULL),
(10, 'Machine Learning Basics', 32.00, 2023, 3, 2, 1, NULL);


INSERT INTO MEMBER
(member_id, name, email, join_date)
VALUES
(1, 'Rewan Mahmoud', 'rewan@gmail.com', '2025-01-10'),
(2, 'Sara Ahmed', 'sara@gmail.com', '2025-02-15'),
(3, 'Omar Khaled', 'omar@gmail.com', '2025-03-20'),
(4, 'Mariam Hassan', 'mariam@gmail.com', '2025-04-05'),
(5, 'Youssef Samir', 'youssef@gmail.com', '2025-05-12');


INSERT INTO LOAN
(loan_id, book_id, member_id, loan_date, return_date)
VALUES
(1,  1, 1, '2025-06-01', '2025-06-10'),
(2,  1, 2, '2025-06-12', '2025-06-20'),
(3,  1, 1, '2025-07-01', NULL),
(4,  2, 1, '2025-07-05', '2025-07-15'),
(5,  2, 3, '2025-07-20', NULL),
(6,  3, 2, '2025-08-01', '2025-08-10'),
(7,  3, 1, '2025-08-15', NULL),
(8,  4, 3, '2025-08-20', '2025-08-30'),
(9,  5, 4, '2025-09-01', NULL),
(10, 6, 2, '2025-09-05', '2025-09-15'),
(11, 7, 4, '2025-09-20', NULL),
(12, 8, 1, '2025-10-01', '2025-10-10');