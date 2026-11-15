
CREATE DATABASE IF NOT EXISTS library;

USE library;

CREATE TABLE IF NOT EXISTS AUTHOR (
    author_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    photo VARCHAR(255) NULL,
    PRIMARY KEY (author_id)
);


CREATE TABLE IF NOT EXISTS PUBLISHER (
    publisher_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    PRIMARY KEY (publisher_id)
);

CREATE TABLE IF NOT EXISTS CATEGORY (
    category_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    PRIMARY KEY (category_id)
);

CREATE TABLE IF NOT EXISTS BOOK (
    book_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    publish_year INT,
    author_id INT NOT NULL,
    publisher_id INT NOT NULL,
    category_id INT NOT NULL,
    cover_image VARCHAR(255) NULL,

    PRIMARY KEY (book_id),

    FOREIGN KEY (author_id)
        REFERENCES AUTHOR(author_id)
        ON DELETE CASCADE,

    FOREIGN KEY (publisher_id)
        REFERENCES PUBLISHER(publisher_id),

    FOREIGN KEY (category_id)
        REFERENCES CATEGORY(category_id)
);

CREATE TABLE IF NOT EXISTS MEMBER (
    member_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    join_date DATE NOT NULL,

    PRIMARY KEY (member_id)
);

CREATE TABLE IF NOT EXISTS LOAN (
    loan_id INT NOT NULL AUTO_INCREMENT,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NULL,

    PRIMARY KEY (loan_id),

    FOREIGN KEY (book_id)
        REFERENCES BOOK(book_id)
        ON DELETE CASCADE,

    FOREIGN KEY (member_id)
        REFERENCES MEMBER(member_id)
);

