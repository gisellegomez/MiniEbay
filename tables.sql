CREATE TABLE Time(
    current_time DEFAULT (datetime('now', 'localtime')),
    forever_time DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE Users(
	user_id varchar(16) primary key,
    password varchar(30)
);

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

CREATE TABLE Categories(
	name varchar(20)
);

CREATE TABLE Bids(
    b_id integer primary key autoincrement,
    items_id int NOT NULL,
	item_buyer varchar(50) NOT NULL, 
	new_price float NOT NULL,
	b_time datetime NOT NULL
);


INSERT INTO Time DEFAULT VALUES;

INSERT INTO Users(user_id, password) VALUES
	('KellyK38', 'mistyismycat'),
	('Ramborg', 'nanamigurl'),
	('GGomez', 'hedgehogs4lyfe'),
    ('Jazafras', 'artho'),
    ('PriKuv', 'b4ym4x');

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
     0, 60.00, '2016-03-14 04:22:19', 'PriKuv'),
    ('Donkey Kong 64', 'Video Games', 'D! K! DONKEY! KONG!',
     1, 25.00, '2016-08-15 08:00:00', NULL),
    ('Dark Blue Wig', 'Cosplay', 'For your blue-haired characters.',
     1, 35.00, '2016-05-18 13:00:00', NULL),
    ('Honda Fit', 'Vehicles', 'Has embarrassing anime stickers on the back.',
     0, 12000.00, '2015-07-18 15:41:07', 'KellyK38')
;

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

INSERT INTO Bids (items_id, item_buyer, new_price, b_time) VALUES
	(1, 'KellyK38', 20, '2016-03-13 15:22:02'),
    (2, 'KellyK38', 15, '2016-03-20 16:35:42'),
	(2, 'Ramborg', 20, '2016-03-20 19:15:02'),
    (2, 'KellyK38', 25, '2016-03-23 07:12:33'),
    (2, 'Ramborg', 30, '2016-03-24 06:59:36'),
	(3, 'GGomez', 11,  '2016-04-22 14:00:01');


CREATE TRIGGER UpdateItemStatus
AFTER UPDATE OF current_time ON Time
	BEGIN
		UPDATE Items SET open = 0 WHERE end_date <= new.current_time;
        UPDATE Items SET open = 1 WHERE new.current_time < end_date AND Items.winner = NULL;
		UPDATE Items SET winner = (SELECT item_buyer from Bids 
            WHERE Bids.items_id = Items.id ORDER BY Bids.new_price DESC LIMIT 1) 
            WHERE open = 0 AND winner IS NULL;
	END;


CREATE TRIGGER UpdateBids
AFTER INSERT ON Bids
    BEGIN
        UPDATE Items SET winner = (SELECT item_buyer from Bids 
            WHERE Bids.items_id = Items.id AND Bids.new_price >= Items.price LIMIT 1) 
            WHERE open = 1;
    END;


CREATE TRIGGER UpdateItemsWin
AFTER UPDATE OF winner ON Items
    BEGIN
        UPDATE Items SET open = 0 WHERE winner IS NOT NULL;
        SELECT * FROM Items;
    END;

UPDATE Time SET current_time=(datetime('now', 'localtime'));
