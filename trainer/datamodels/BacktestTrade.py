from sqlalchemy import Column, Integer, String, Numeric

from trainer.dataprovider.database import Base


class BacktestTrade(Base):
    __tablename__ = 'bt_trade'

    trade_id = Column(Integer, primary_key=True)
    order_ref = Column(String)
    trade_date = Column(String)
    price = Column(Numeric)
    direction = Column(Integer)
    qty = Column(Numeric)
