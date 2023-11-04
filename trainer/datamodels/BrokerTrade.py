from sqlalchemy import Column, Integer, String, Numeric

from trainer.dataprovider.database import Base


class BrokerTrade(Base):
    __tablename__ = 'broker_trade'

    trade_id = Column(Integer, primary_key=True)
    order_ref = Column(String)
    trade_date = Column(String)
    price = Column(Numeric)
    direction = Column(Integer)
    qty = Column(Numeric)
    remarks = Column(String)
