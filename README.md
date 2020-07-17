# Cryptocurrency-Trading-System
3540 Cryptocurrency Trading System

### How to use Docker to run app
**Please stop existing mysql client running (use terminal ```mysqld stop``` OR MAC: System Preferences last row go into MySQL to turn off)**
#### Since the Flask depends on a Mysql server, its a big overhead for users to install their own mysql servers and populate them with their own data. We created 2 containers (1 for python code, 1 for the mysqlserver) and linked them through docker-composer to be able to communicate with each other. The setup code in db/init.sql automatically populates the database with sufficient data to test and run the Flask app
1. install Docker and docker-compose for your operation system
2. ```cd``` into TradingSystem directory (one that contains docker-compose.yml)
3. Run ```docker-compose build``` then ```docker-compose up``` to set up both python and mysql containers and connect them together
4. If you make any changes to the python code, you can use ```ctrl-c``` to stop both services, run ```docker-compose build app``` to build the latest python app image ```docker-compose up``` to deploy the latest app image into a container
5. If you want to use your own python app.py which is eaiser to debug and develop in. I recommend doing only the ```docker-compose build db``` and ```docker-compose start db```. This way you can connect to the mysql image that is in your container without having your own mysql server in your localhost. Then you can use ```python app.py``` to run your Flask app. Make sure to update your mysqlConfig.py with (host="127.0.0.1" instead)

### Steps to use the app
1. **Register Page - Register**
2. **Login Page - Login**: Please use the password you input when you register; Session lasts 10 mins;
3. **Account Page - Deposit**: to make sure you have enough money to buy crypto;
4. **Overview Page - Overview**: Check the lastest page, updated every 2 seconds;
5. **Trading Page - Buy**: Please follow the rules for trading: you have enough cash, not lower than the ask price, and not 10% higher than the ask price;
6. **Trading Page - Sell**: Please follow the rules for trading: you have enough coins, not exceeds the bid price, and not 10% lower than the bid price;
7. **Trading Page & Account Page - Blotter and P&L Reporting**: See the blotter and P&L for your account (link the db using userId);
