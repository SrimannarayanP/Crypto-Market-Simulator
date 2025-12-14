This was a very crude attempt at a Crypto Market Simulator for my Grade 12 project 😅. Flask is used here only to provide an application context so that Flask-SQLAlchemy ORM queries work in a 
standalone script. I've also used a websocket to fetch data related to cryptos continuously from Binance. There were certain conditions imposed by my mentor to use text, CSV & binary files in any way
possible. That has been implemented by using CSV files for storing orders, text files for storing user-related data (Yes, I know, it isn't safe!) & so on. Frontend was made using basic HTML & CSS.

One noticeable feature that I've implemented is the use of TradingView's chart widget feature to show the real-time prices of the cryptos in a graphical format. Because it's TradingView's widget,
the user can plot points, mark some lines & analyse using the graph. Basically everything you can do with TradingView's chart in their native app can be done on the widget as well.
