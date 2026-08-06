CREATE DATABASE IF NOT EXISTS comp440;

USE comp440;

CREATE TABLE IF NOT EXISTS user (
  username   VARCHAR(50)  PRIMARY KEY,
  password   VARCHAR(255) NOT NULL,
  firstName  VARCHAR(50)  NOT NULL,
  lastName   VARCHAR(50)  NOT NULL,
  email      VARCHAR(100) NOT NULL,
  phone      VARCHAR(20)  NOT NULL,
  PRIMARY KEY (username),
  UNIQUE (email),
  UNIQUE (phone)
);

CREATE TABLE IF NOT EXISTS item (
  Item_ID INT PRIMARY KEY,
  Title VARCHAR(50) NOT NULL,
  Descript VARCHAR(255),
  Price INT NOT NULL,
  Date_Posted DATE NOT NULL,
  Seller VARCHAR(50) NOT NULL,
  Clothing BOOLEAN NOT NULL, -- For the Categories I am making a few generic ones and making them bools
  Electronic BOOLEAN NOT NULL,
  Toy BOOLEAN NOT NULL,
  Kitchen BOOLEAN NOT NULL,
  Available_in_store BOOLEAN NOT NULL,
  FOREIGN KEY (Seller) 
  REFERENCES user(username)
);

/*
SELECT DATABASE();
USE comp440;
Uncomment out whichever ones of these you want to test 
-- Code to show the tables SHOW TABLES;
-- Code to see the item table and stuff in it  SELECT * FROM item;
-- Code to see the user table and stuff in it  SELECT * FROM user;
*/




)