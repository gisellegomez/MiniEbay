drop table IF EXISTS Time;
CREATE TABLE Time(current_time datetime DEFAULT CURRENT_TIMESTAMP);
insert into Time DEFAULT VALUES;

drop table IF EXISTS categories;

CREATE TABLE categories(
	name varchar(20)
);

insert into categories values
	('electronics'),
	('toys'),
	('books'),
	('auto'),
	('computers'),
	('misc')
	;

drop table IF EXISTS Users;

Create table Users(
	userId varchar(16) primary key
);

insert into Users values
	('JohnSmith10'),
	('JamesRandy28'),
	('SaveFerris123'),
	('R2Bl3nd')
	;

drop table IF EXISTS items;
CREATE TABLE items(
	id integer primary key autoincrement,
	title char(50), 
	category char(50) NOT NULL, 
	description char(255), 
	open boolean, 
	price float, 
	end_date datetime,
	winner varchar(50)
);

insert into Items(title, category, description, open, price, end_date, winner) values
	(
		'Dell laptop computer',
		'computers',
		'Dell laptop computer, 2ghz processor, 1gb memory, 40gb hard drive, 15-inch screen',
		0,
		400,
		'2015-12-25 12:00:00.000000',
		'SaveFerris123'
	),
	(
		'Samsung DVD player',
		'electronics',
		'Samsung DVD player featuring SD card slot, support for playback MP3s and displaying of JPEG images; remote included',
		1,
		100,
		'2015-12-24 14:00:00.000000',
		NULL
	),
	(
		'2016 Ferrari',
		'auto',
		'A fast, red sports car with less than 10,000 miles',
		1,
		90000,
		'2015-12-01 16:00:00.000000',
		NULL
	)
;

drop table IF EXISTS Bids;

Create table Bids(
	id int NOT NULL,
	buyer varchar(50) NOT NULL, 
	price float NOT NULL,
	bid_time datetime NOT NULL,
	bid_id integer primary key autoincrement
);

insert into Bids (id, buyer, price, bid_time) values
	(1, 'JohnSmith10', 200, '2015-12-03 14:00:02'),
	(1, 'SaveFerris123',  400, '2015-12-04 14:00:03'),
	(2, 'R2Bl3nd',  50,  '2015-12-02 14:00:01')
	;

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