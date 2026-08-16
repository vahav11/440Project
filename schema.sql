CREATE DATABASE IF NOT EXISTS comp440;

USE comp440;

CREATE TABLE IF NOT EXISTS user (
  username   VARCHAR(50)  NOT NULL,
  password   VARCHAR(255) NOT NULL,
  firstName  VARCHAR(50)  NOT NULL,
  lastName   VARCHAR(50)  NOT NULL,
  email      VARCHAR(100) NOT NULL,
  phone      VARCHAR(20)  NOT NULL,
  PRIMARY KEY (username),
  UNIQUE (email),
  UNIQUE (phone)
);

-- one row per item for sale
CREATE TABLE IF NOT EXISTS item (
  itemID       INT           NOT NULL AUTO_INCREMENT,
  title        VARCHAR(100)  NOT NULL,
  description  TEXT,
  price        DECIMAL(10,2) NOT NULL,
  datePosted   DATE          NOT NULL,
  seller       VARCHAR(50)   NOT NULL,
  PRIMARY KEY (itemID),
  FOREIGN KEY (seller) REFERENCES user(username),
  CHECK (price >= 0)
);

-- one row per category ON an item, so 3 categories = 3 rows.
-- cant put a list in a column so it needs its own table.
CREATE TABLE IF NOT EXISTS item_category (
  itemID    INT         NOT NULL,
  category  VARCHAR(50) NOT NULL,
  -- both columns together, so an item can repeat but not the pair
  PRIMARY KEY (itemID, category),
  FOREIGN KEY (itemID) REFERENCES item(itemID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS review (
  reviewID    INT          NOT NULL AUTO_INCREMENT,
  itemID      INT          NOT NULL,
  reviewer    VARCHAR(50)  NOT NULL,
  rating      ENUM('Excellent','Good','Fair','Poor') NOT NULL,
  comment     VARCHAR(255),
  reviewDate  DATE         NOT NULL,
  PRIMARY KEY (reviewID),
  -- one review per person per item
  UNIQUE (itemID, reviewer),
  FOREIGN KEY (itemID)   REFERENCES item(itemID) ON DELETE CASCADE,
  FOREIGN KEY (reviewer) REFERENCES user(username)
);


-- the rules below cant be done with a constraint because they need to
-- count other rows or look at another table, so they are triggers.
-- DELIMITER is only there because workbench splits the file on ; and
-- the trigger has semicolons inside it.

DROP TRIGGER IF EXISTS limit_items_per_day;

DELIMITER $$

CREATE TRIGGER limit_items_per_day
BEFORE INSERT ON item
FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM item
      WHERE seller = NEW.seller AND datePosted = NEW.datePosted) >= 2 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'You may post at most 2 items per day.';
  END IF;
END$$

DELIMITER ;


DROP TRIGGER IF EXISTS limit_reviews_per_day;

DELIMITER $$

CREATE TRIGGER limit_reviews_per_day
BEFORE INSERT ON review
FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM review
      WHERE reviewer = NEW.reviewer AND reviewDate = NEW.reviewDate) >= 3 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'You may submit at most 3 reviews per day.';
  END IF;
END$$

DELIMITER ;


DROP TRIGGER IF EXISTS no_self_review;

DELIMITER $$

CREATE TRIGGER no_self_review
BEFORE INSERT ON review
FOR EACH ROW
BEGIN
  -- has to look in item to find out who owns it
  IF (SELECT seller FROM item WHERE itemID = NEW.itemID) = NEW.reviewer THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'You cannot review your own item.';
  END IF;
END$$

DELIMITER ;


DROP TRIGGER IF EXISTS no_review_edits;

DELIMITER $$

-- no IF on this one, editing a review is never allowed
CREATE TRIGGER no_review_edits
BEFORE UPDATE ON review
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Reviews cannot be modified after submission.';
END$$

DELIMITER ;
