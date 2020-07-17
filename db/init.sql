CREATE DATABASE TradingSystem;
use TradingSystem;
-- -----------------------------------------------------
-- Table TradingSystem.crypto
-- -----------------------------------------------------
CREATE TABLE crypto (
  crypto_id INT(11) AUTO_INCREMENT,
  crypto_name VARCHAR(255),
  24_hour_quantity INT(11),
  market_cap DECIMAL(12,2),
  PRIMARY KEY (crypto_id)
);

-- -----------------------------------------------------
-- Table TradingSystem.PnL
-- -----------------------------------------------------
CREATE TABLE PnL (
  user_id INT(11),
  pnl_id INT(11) AUTO_INCREMENT,
  crypto_id INT(11),
  UPL DECIMAL(30,2) DEFAULT '0.00',
  RPL DECIMAL(30,2) DEFAULT '0.00',
  VWAP DECIMAL(30,2) DEFAULT '0.00',
  last_updated DATETIME,
  PRIMARY KEY (pnl_id)
);

-- -----------------------------------------------------
-- Table TradingSystem.user
-- -----------------------------------------------------
CREATE TABLE user (
  user_id INT(11) AUTO_INCREMENT,
  email VARCHAR(100),
  user_name VARCHAR(255),
  PASSWORD VARCHAR(255),
  PRIMARY KEY (user_id)
);

-- -----------------------------------------------------
-- Table TradingSystem.bank_info
-- -----------------------------------------------------
CREATE TABLE bank_info (
  user_id INT(11),
  name VARCHAR(255),
  bank_acc_number VARCHAR(255),
  zip_code INT(11),
  country VARCHAR(255),
  cash DECIMAL(10,2) DEFAULT '0.00',
  PRIMARY KEY (user_id)
);


-- -----------------------------------------------------
-- Table TradingSystem.blotter
-- -----------------------------------------------------
CREATE TABLE blotter (
  blotter_id INT(11)AUTO_INCREMENT,
  user_id INT(11),
  crypto_id INT(11),
  quantity DECIMAL(10,5),
  price DECIMAL(10,0),
  trading_date DATETIME,
  side VARCHAR(50),
  PRIMARY KEY (blotter_id)
);


-- -----------------------------------------------------
-- Table TradingSystem.crypto_bank
-- -----------------------------------------------------
CREATE TABLE crypto_bank (
  bank_id INT(11) AUTO_INCREMENT,
  user_id INT(11),
  crypto_id INT(11),
  amount DECIMAL(10,5) DEFAULT 0.00,
  PRIMARY KEY (bank_id)
);


-- -----------------------------------------------------
-- Table TradingSystem.price
-- -----------------------------------------------------
CREATE TABLE price (
  price_id INT(11) AUTO_INCREMENT,
  time TIMESTAMP,
  crypto_id INT(11),
  price DECIMAL(10,5),
  PRIMARY KEY (price_id)
);


-- ###Register a user
INSERT INTO user (user_id, email , user_name, PASSWORD)
VALUES (1, "qwerjkl112@gmail.com", "qwerjkl112", MD5('abc123'));
INSERT INTO user (user_id, email , user_name, PASSWORD)
VALUES (2, "lm3744@nyu.edu", "rachel", MD5('456'));
INSERT INTO user (user_id, email , user_name, PASSWORD)
VALUES (3, "rachel@gmail.com", "rra", MD5('789'));
INSERT INTO user (user_id, email , user_name, PASSWORD)
VALUES (4, "janet@gmail.com", "janet", MD5('aaaaaa'));

-- ####Store user_name in the session of what user just entered
-- ####Look up the id the database with below
-- SELECT user_id FROM user where user_name = 'qwerjkl112';


-- ###Prompt user to set up bank info (store user_id, user_name in the session) cash will default to $0.00
INSERT INTO bank_info (user_id, name, bank_acc_number, zip_code, country)
VALUES (1, "Frank's BankAccnt", "1234567890123456", "10019", "USA");

INSERT INTO crypto (crypto_id, crypto_name) VALUES (1, 'BTC');
INSERT INTO crypto (crypto_id, crypto_name) VALUES (2, 'ETH');
INSERT INTO crypto (crypto_id, crypto_name) VALUES (3, 'LTC');
INSERT INTO crypto (crypto_id, crypto_name) VALUES (4, 'Cash');

-- ###update timestamp for prices
INSERT INTO price (crypto_id, price)
VALUES (1, 7000);
INSERT INTO price (crypto_id, price)
VALUES (2, 1000);
INSERT INTO price (crypto_id, price)
VALUES (3, 500);

-- ###Create another user to sell Coins
INSERT INTO user (email , user_name, PASSWORD)
VALUES ("master@gmail.com", "master", MD5('abc123'));

INSERT INTO crypto_bank VALUES (1, 2, 1, 200);
INSERT INTO crypto_bank VALUES (2, 2, 2, 10);
INSERT INTO crypto_bank VALUES (3, 2, 3, 2);
INSERT INTO crypto_bank VALUES (4, 2, 4, 20000);

INSERT INTO PnL VALUES (1, 1, NULL, 20000.00, 2000.00, NULL, NOW());
INSERT INTO PnL VALUES (2, 2, NULL, 10000.00, 100.00, NULL, NOW());
INSERT INTO PnL VALUES (3, 3, NULL, 400.00, 20.00, NULL, NOW());
INSERT INTO PnL VALUES (4, 4, NULL, 0.00, 0.00, NULL, NOW());

INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (1, 0.00, 20000.00, 2000.00, 2);
INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (2, 0.00, 10000.00, 100.00, 2);
INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (3, 0.00, 400.00, 20.00, 2);
INSERT INTO PnL (crypto_id, UPL, RPL, VWAP, user_id) VALUES (4, 0.00, 0.00, 0.00, 2);
