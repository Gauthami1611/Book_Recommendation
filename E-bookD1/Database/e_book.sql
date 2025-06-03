drop database e_book;
create database e_book;
use e_book;

create table readers(
	reader_id int primary key auto_increment,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    email varchar(255) not null unique,
    phone varchar(255) not null unique,
    password varchar(255) not null,
    address varchar(255) not null
);

create table genres(
	genre_id int primary key auto_increment,
    genre_name varchar(255) not null
);

create table reader_genres(
	reader_genre_id int primary key auto_increment,
	genre_id int,
    reader_id int,
    foreign key (genre_id) references genres(genre_id),
    foreign key (reader_id) references readers(reader_id) 
);

create table books(
	book_id int primary key auto_increment,
    title varchar(255) not null,
    author varchar(255) not null,
    book_link varchar(255) not null,
    genre varchar(255) not null,
    date_published varchar(255) not null,
    publisher varchar(255) not null,
    num_of_page int,
    lang varchar(255) not null,
    rate varchar(255),
    image_url varchar(255) not null,
    primary_genre varchar(255) not null,
    sub_genre varchar(255) not null
);

create table reader_books(
	reader_book_id int primary key auto_increment,
    book_id int,
    reader_id int,
    status varchar(255) not null,
    foreign key (book_id) references books(book_id), 
    foreign key (reader_id) references readers(reader_id) 
);

create table new_arrivals(
	arrival_id int primary key auto_increment,
    title varchar(255) not null,
    author varchar(255) not null,
    rating varchar(255) not null,
	reviewer varchar(255) not null,
    review_text text not null,
    positive_score varchar(255) not null,
    negative_score varchar(255) not null,
    positive_words varchar(255) not null,
    negative_words varchar(255) not null,
    book_url varchar(255) not null,
    image_url varchar(255) not null
);

CREATE TABLE not_rated (
    not_rated_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    publisher VARCHAR(255),
    published_date VARCHAR(50),
    description TEXT,
    cover_url TEXT,
    categories VARCHAR(255),
    rating FLOAT DEFAULT 0
);


create table rating(
  rating_id INT AUTO_INCREMENT PRIMARY KEY,
  rating VARCHAR(255) not null,
  not_rated_id int,
  reader_id int,
  foreign key(not_rated_id)references not_rated(not_rated_id),
  foreign key (reader_id) references readers(reader_id) 
);

CREATE TABLE reader_goal (
  reader_goal_id INT AUTO_INCREMENT PRIMARY KEY,
  no_of_books_goal INT NOT NULL,
  reader_id INT NOT NULL,
  goal_month INT NOT NULL,
  goal_year INT NOT NULL,
  goal_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (reader_id, goal_month, goal_year),
  FOREIGN KEY (reader_id) REFERENCES readers(reader_id)
);





