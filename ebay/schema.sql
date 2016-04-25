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
    ('Art Supplies'),
    ('Figures'),
    ('Cosplay'),
    ('Vehicles'),
    ('Video Games'),
    ('Lights'),
	('Other');

DROP TABLE IF EXISTS Users;
CREATE TABLE Users(
	user_id varchar(16) primary key
);
INSERT INTO Users VALUES
	('KellyK38'),
	('Ramborg'),
	('GGomez'),
    ('Jazafras'),
    ('PriKuv'),
    ('JuriLover');

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
    ('Shrek', 'Movies', 'The best movie of all time.',
     1, 15.00, '2016-05-06 12:00:00', NULL),
    ('JJBA T-Shirt', 'Clothes', 'Yare yare daze.',
     0, 30.00, '2016-03-24 07:00:00', 'Ramborg'),
    ('Wrench', 'Tools', 'A very useful tool.',
     1, 8.00, '2016-05-16 03:00:00', NULL),
    ('Colored Pencils', 'Art Supplies', 'Make your drawings pretty.',
     1, 7.00, '2016-06-17 15:00:00', NULL),
    ('Utena Tenjou Figure', 'Figures', 'Your favorite rose prince.',
     0, 60.00, '2016-03-14 04:22:19', 'JuriLover'),
    ('Donkey Kong 64', 'Video Games', 'D! K! DONKEY! KONG!',
     1, 25.00, '2016-08-15 08:00:00', NULL),
    ('Dark Blue Wig', 'Cosplay', 'For your blue-haired characters.',
     1, 35.00, '2016-05-18 13:00:00', NULL),
    ('Honda Fit', 'Vehicles', 'Has embarrassing anime stickers on the back.',
     0, 12000.00, '2015-07-18 15:41:07', 'KellyK38')
;

DROP TABLE IF EXISTS Bids;
CREATE TABLE Bids(
    b_id integer primary key autoincrement,
    items_id int NOT NULL,
	item_buyer varchar(50) NOT NULL, 
	new_price float NOT NULL,
	b_time datetime NOT NULL
);
INSERT INTO Bids (items_id, item_buyer, new_price, b_time) VALUES
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
		UPDATE Items SET winner = (SELECT item_buyer from Bids WHERE Bids.items_id = Items.id ORDER BY Bids.new_price DESC LIMIT 1) WHERE open = 0 AND winner IS NULL;
	END;

DROP TRIGGER IF EXISTS BidUpdateTrigger;
CREATE TRIGGER BidUpdateTrigger
AFTER INSERT ON Bids
    BEGIN
        UPDATE Items SET winner = (SELECT item_buyer from Bids WHERE Bids.items_id = Items.id AND Bids.new_price >= Items.price LIMIT 1) WHERE open = 1;
    END;

DROP TRIGGER IF EXISTS ItemsUpdateTrigger;
CREATE TRIGGER ItemsUpdateTrigger
AFTER UPDATE OF winner ON Items
    BEGIN
        UPDATE Items SET open = 0 WHERE winner IS NOT NULL;
        SELECT * FROM Items;
    END;

UPDATE Time SET current_time=CURRENT_TIMESTAMP;
