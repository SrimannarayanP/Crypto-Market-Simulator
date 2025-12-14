# fetch_real_time_data.py


from sqlalchemy import create_engine
from datetime import datetime
from models import RealTimeData, Cryptocurrency, SessionLocal
from decimal import Decimal

import websockets, json, asyncio



db_url = "mysql://Sriman:SpitterDune#891*@localhost/crypto_market_sim"
engine = create_engine(db_url)
connection = engine.connect()


def get_symbol_to_id_mapping():
    session = SessionLocal()

    try:
        mapping = {crypto.symbol: crypto.id for crypto in session.query(Cryptocurrency).all()}

        # session.query constructs a query to select all columns from the cryptocurrencies table and .all() returns all rows of the cryptocurrency as a list.
        # for loop iterates through the list returned by the list & crypto represents each object in the list
        # mapping is a dictionary that has keys as crypto.symbol and crypto.id as values

        # print(mapping)
        return mapping

    finally:
        session.close()


async def fetch_crypto_data(session):

    # async func used because of the way the data is fetched. In an async func., when it reaches an await keyword it pauses the execution of that func. freeing up the event loop to handle other tasks. Async is particularly useful here as the data is being fetched in real-time continously, so this loop will keep executing. Using a normal func. here would mean that the rest of the functionalities would never execute as the loop of fetching data would never stop
    # A normal func. will block execution until each task completes. If a func. has a time-consuming task, then it prevents the other code from running until that task is done

    url = 'wss://stream.binance.com:9443/ws/!ticker@arr'

    async with websockets.connect(url) as ws:

    # Instead of trying to fetch all the data at once & slowing down the entire process, async helps to fetch some amt of data, process it & then fetch the next set of data & so on
    # Websockets have been used here instead of a normal API call as it is more efficient. Websockets allow you to request data over an active connection to the server (pings the server once & keeps it active until you close the connection) whereas an API continuously pings the server everytime you request for data making it less efficient

        while True:
            try:
                response = await ws.recv() # Receiving response from the websocket connection (Receives the data, waits until the rest part of the code is executed & then fetches the next batch of data)

                data = json.loads(response)

                for ticker in data:
                    symbol = ticker['s'] # Mapping to each symbol (asset) from data received from the websocket connection

                    if symbol in symbol_to_id:
                        price = Decimal(ticker['c']) # For every asset, this gets their current price
                        volume = Decimal(ticker['v']) # For every asset, this gets their volume traded

                        crypto = session.query(Cryptocurrency).filter_by(symbol = symbol).first()

                        # session.query creates a database query for the cryptocurrency table using the Cryptocurrency ORM (Object Relation Mapping - Basically a concept used in converting the SQL tables into a form that can be edited using Python instead of SQL queries) from models.py
                        # .filter_by is used to filter the results of the query where the symbol column matches the symbol variable
                        # .first() is used to fetch the 1st record found that matches these conditions

                        if crypto:
                            new_data = RealTimeData(cryptocurrency_id = crypto.id, price = price, volume = volume, timestamp = datetime.utcnow()) # Stores all the related data that was fetched that has to be appended to the real_time_data table using RealTimeData ORM

                            session.add(new_data) # Adds the data to the table
                            # print(f"Added data for {symbol}: price = {price}, volume = {volume}")

                        else:
                            print(f"Cryptocurrency {symbol} not found in the database")

                session.commit() # Saves the changes made to tables (Python equivalent to SQL's commit)

            except Exception as e:
                session.rollback() # In case of any error / any exception, this will undo all the changes made after the last commit (Python's equivalent to SQL's rollback)

                print(f"Error : {e}")

            await asyncio.sleep(1)


# __main__
async def main():
    session = SessionLocal() # Creates a local session (Stays until the user / application explicitly clears it)

    try:
        await fetch_crypto_data(session)

    except:
        session.close()

symbol_to_id = get_symbol_to_id_mapping()

asyncio.run(main())
