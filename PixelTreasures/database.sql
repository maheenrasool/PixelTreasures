Create Database PixelTreasures;
use PixelTreasures;
Create Table sellers
(
	username VARCHAR(64) PRIMARY KEY,
    userpassword VARCHAR(128),
    email VARCHAR(300)
);

CREATE TABLE artpieces
( 
	item_num INT PRIMARY KEY auto_increment,
    owner_username VARCHAR(64),
    item_status INT CONSTRAINT CHECK (item_status IN (0,1)),
    item_price DECIMAL(10, 2),
    FOREIGN KEY (owner_username)  REFERENCES sellers(username)
);
CREATE TABLE seller_bank_account
(
	username VARCHAR(64),
    account_number VARCHAR(17),
     FOREIGN KEY (username)  REFERENCES sellers(username)
);
SELECT * FROM sellers;
SELECT * FROM artpieces;
DROP TABLE artpieces;