DROP TABLE IF EXISTS Time;
CREATE TABLE Time(current_time datetime DEFAULT CURRENT_TIMESTAMP);
INSERT INTO Time DEFAULT VALUES;

DROP TABLE IF EXISTS Categories;
CREATE TABLE Categories(
	name varchar(20)
);
INSERT INTO Categories ('name') VALUES
	('Movies'),
	('Clothes'),
	('Books'),
	('Tools'),
	('Other');

DROP TABLE IF EXISTS Users;
CREATE TABLE Users(
	user_id varchar(16) primary key
);
INSERT INTO Users VALUES
	('KellyK38'),
	('Ramborg'),
	('GGomez');

DROP TABLE IF EXISTS Items;
CREATE TABLE Items(
	id integer primary key autoincrement,
	title char(50), 
	category char(50) NOT NULL, 
	description char(255), 
	open boolean, 
	price float, 
	end_date datetime,
	winner varchar(50)
);
INSERT INTO Items(title, category, description, open, price, end_date, winner) VALUES
    ('Shrek', 'movies', 'The best movie of all time.',
     1, 15, '2016-05-06 12:00:00', NULL),
    ('JJBA T-Shirt', 'clothes', 'Yare yare daze.',
     0, 30, '2016-03-24 07:00:00', 'Ramborg'),
    ('Wrench', 'tools', 'A very useful tool.',
     1, 8, '2016-05-16 03:00:00', NULL)
;

DROP TABLE IF EXISTS Bids;
CREATE TABLE Bids(
    id int NOT NULL,
	buyer varchar(50) NOT NULL, 
	price float NOT NULL,
	b_time datetime NOT NULL,
	b_id integer primary key autoincrement
);
INSERT INTO Bids (id, buyer, price, b_time) VALUES
	(1, 'KellyK38', 20, '2016-03-13 15:22:02'),
    (2, 'KellyK38', 15, '2016-03-20 16:35:42'),
	(2, 'Ramborg', 20, '2016-03-20 19:15:02'),
    (2, 'KellyK38', 25, '2016-03-23 07:12:33'),
    (2, 'Ramborg', 30, '2016-03-24 06:59:36'),
	(3, 'GGomez', 11,  '2016-04-22 14:00:01');

DROP TRIGGER IF EXISTS TimeUpdateTrigger;
CREATE TRIGGER TimeUpdateTrigger
AFTER UPDATE OF current_time ON Time
	BEGIN
		UPDATE Items SET open = 0 WHERE end_date <= new.current_time;
		UPDATE Items SET winner = (SELECT buyer from Bids WHERE Bids.id = Items.id ORDER BY Bids.price DESC LIMIT 1) WHERE open = 0 AND winner IS NULL;
	END;

DROP TRIGGER IF EXISTS BidUpdateTrigger;
CREATE TRIGGER BidUpdateTrigger
AFTER INSERT ON Bids
    BEGIN
        UPDATE Items SET winner = (SELECT buyer from Bids WHERE Bids.id = Items.id AND Bids.price >= Items.price LIMIT 1) WHERE open = 1;
    END;

DROP TRIGGER IF EXISTS ItemsUpdateTrigger;
CREATE TRIGGER ItemsUpdateTrigger
AFTER UPDATE OF winner ON Items
    BEGIN
        UPDATE Items SET open = 0 WHERE winner IS NOT NULL;
        SELECT * FROM Items;
    END;

UPDATE Time SET current_time=CURRENT_TIMESTAMP;