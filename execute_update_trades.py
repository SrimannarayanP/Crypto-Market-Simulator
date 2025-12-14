# execute_update_trades.py


from sqlalchemy import desc
from models import RealTimeData, Cryptocurrency, Order, Portfolio, db
from flask import Flask

import csv


class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Sriman:SpitterDune#891*@localhost/crypto_market_sim'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


def get_real_time_data(cryptocurrency_symbol):
    cryptocurrency = Cryptocurrency.query.filter_by(symbol = cryptocurrency_symbol).first() # Fetches the 1st cryptocurrency specified by the user from the cryptocurrency table
    latest_data = RealTimeData.query.filter_by(cryptocurrency_id = cryptocurrency.id)\
                                    .order_by(desc(RealTimeData.timestamp))\
                                    .first()

    # Fetches the latest data from the real_time_data table for the asset specified by the user, arranges in the decreasing order of the timestamp column & stores the 1st value of it
    return latest_data


# func. used to update the portfolio of the users
def update_portfolio(user_id, asset, quantity, order_type):
    existing_asset = Portfolio.query.filter_by(user_id = user_id, asset = asset).first() # Gets the 1st asset requested by the user that is in their portfolio

    try:
        if existing_asset:
            if order_type.lower() == 'buy':
                existing_asset.quantity = float(existing_asset.quantity) + float(quantity) # If the user wants to buy an asset, then it adds the amt they need to buy to the existing amt they have

            elif order_type.lower() == 'sell':
            # Similar func. as that of buy, with conditions to check the quantity of the asset the user has before they sell
                if float(existing_asset.quantity) >= float(quantity):
                    existing_asset.quantity = float(existing_asset.quantity) - float(quantity)

                elif existing_asset.quantity == 0:
                    db.session.delete(existing_asset)

                else:
                    
                    raise Exception(f"Insufficient {asset} balance. Current balance : {existing_asset.quantity}")

            db.session.commit()

            print(f"Portfolio updated successfully for {asset}")

        else:

            if order_type.lower() == 'buy':
                new_asset = Portfolio(user_id = user_id, asset = asset, quantity = quantity) # Query to add asset to portfolio if the user wants to buy an asset he/she already doesn't own

                db.session.add(new_asset) # Executing the query
                db.session.commit()

                print(f"New asset {asset} added to portfolio")
            else:

                raise Exception(f"Cannot sell {asset}: Asset not found in portfolio")

    except Exception as e:
        db.session.rollback()

        raise Exception(f"Error updating portfolio: {str(e)}")


# func. that is used to replicate the feature of placing orders for assets
def place_order(user_id, order_type, asset, quantity):
    try:
        file = open('orders.csv', 'a', newline = '')

        writer = csv.writer(file)
        latest_data = get_real_time_data(asset)

        if not latest_data:

            raise Exception(f"No price data found for {asset}")

        price = latest_data.price
        cryptocurrency = Cryptocurrency.query.filter_by(symbol = asset).first() # Fetch the cryptocurrency ID for the order

        if not cryptocurrency:

            raise Exception(f"{asset} not found")

        # print(cryptocurrency)

        new_order = Order(user_id = user_id, order_type = order_type, asset = asset, quantity = quantity, price = price) # Executes a query to update the orders table for placing orders via the order ORM
        new_order_list = [user_id, order_type.title(), asset, quantity, price]

        writer.writerow(new_order_list)

        db.session.add(new_order)
        db.session.commit()

        update_portfolio(user_id, asset, quantity, order_type) # Calling the update_portfolio func. here to update the portfolio values accordingly

        return new_order

    except Exception as e:
        db.session.rollback()

        raise Exception(f"Error placing order: {str(e)}")

    finally:
        file.close()


# func. used the complete pending orders here in case the orders table had any pending orders left (Noticeable when many transactions are happening)
def complete_pending_orders():
    db.session.query(Order).filter_by(status = 'pending').update({'status' : 'completed'})
    db.session.commit()

    print("Pending orders successfully updated to 'completed' status")

def check_asset_exists(asset):
    try:
        asset_exists = db.session.query(Cryptocurrency).filter_by(symbol = asset).first()

        if not asset_exists:
            supported_assets = db.session.query(Cryptocurrency.symbol).all()
            supported_assets_list = [a[0] for a in supported_assets]

            print(f"Asset {asset} not found")
            print("Here's a list of supported assets : ", ",".join(supported_assets_list))

            return False

    except Exception as e:
        print(f"Database error check asset: {e}")

        return False



# __main__
with app.app_context():
    try:
        while True:
            try:
                order_type = input("Enter buy/sell (To exit, type 'exit'): ").lower().strip()

                if order_type not in ['buy', 'sell', 'exit']:

                    raise ValueError("Invalid order type. Please enter 'buy' / 'sell' / 'exit'")

                else:
                    if order_type == 'exit':
                        print("Exiting trading system...")

                        break
                    asset = input("Enter asset : ").upper()

                    if not asset:
                        print("Asset cannot be empty")

                        continue

                    if not check_asset_exists(asset):
                        print(f"Asset {asset} isn't supported")

                        continue

                    try:
                        quantity = float(input("Enter quantity : "))

                        if quantity <= 0:
                            print("Quantity must be greater than 0")

                            continue
                    except ValueError:
                        print("invalid quantity format. Please enter a number")

                        continue

                    # Add balance checking thing here, update in other parts of code also wherever this is being used (modify update_portfolio func. when implementing this)

                    order = place_order(user_id = 1, order_type = order_type, asset = asset, quantity = quantity)

                    complete_pending_orders()

                    print(f"Order placed successfully : {order}")

                    portfolio = Portfolio.query.filter_by(user_id = 1).all() # Finds the portfolio corresponding to the user_id entered & gets all the data related to it

                    if portfolio:
                        print("\nCurrent portfolio : ")

                        for asset in portfolio:
                            print(f"{asset.asset} : {asset.quantity}")

                    else:
                        print("\nPortfolio is empty")

            except ValueError as ve:
                print(f"Error: {ve}")

                continue

            except Exception as e:
                print(f"Unexpected error: {e}")

                continue

    except KeyboardInterrupt:
        print("\nTrading system interrrupted by user")

    except Exception as e:
        print(f"Critical error in trading system : {e}")

    finally:
        print("Trading system shutdown complete")
