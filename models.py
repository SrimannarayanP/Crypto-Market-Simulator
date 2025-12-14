# models.py


from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, create_engine, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Converting every SQL table into a Python obj which can then be used in various other places to edit & modify the tables
class RealTimeData(db.Model):
    __tablename__ = 'real_time_data'

    id = Column(Integer, primary_key = True, autoincrement = True)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"), nullable = False)
    timestamp = Column(DateTime, nullable = False)
    price = Column(DECIMAL(20, 8), nullable = False)
    volume = Column(DECIMAL(20, 8), nullable = False)

    cryptocurrency = relationship('Cryptocurrency', back_populates = 'real_time_data') # Defining relations b/w the tables


class Cryptocurrency(db.Model):
    __tablename__ = 'cryptocurrencies'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String)
    symbol = Column(String, unique = True, index = True)

    real_time_data = relationship('RealTimeData', back_populates = 'cryptocurrency', lazy = True)


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, autoincrement = True)
    username = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    email = Column(String, nullable = False, unique = True)
    created_at = Column(db.TIMESTAMP, server_default = db.func.now())

    orders = relationship('Order', back_populates = 'user', lazy = True)
    portfolios = relationship('Portfolio', back_populates = 'user', lazy = True)


class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    asset = Column(String, nullable = False)
    quantity = Column(DECIMAL(20, 8), nullable = False)

    user = relationship('User', back_populates = 'portfolios')


class Order(db.Model):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    order_type = Column(db.Enum('buy', 'sell'), nullable = False)
    asset = Column(String, nullable = False)
    quantity = Column(DECIMAL(20, 8), nullable = False)
    price = Column(DECIMAL(20, 8))
    status = Column(db.Enum('pending', 'completed', 'cancelled'), default = 'pending')
    created_at = Column(db.TIMESTAMP, server_default = db.func.now())

    user = relationship('User', back_populates = 'orders')


# Database connection
db_url = "mysql+pymysql://Sriman:SpitterDune#891*@localhost/crypto_market_sim"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine) # The method used to create local sessions (temporary notepad for database operations
