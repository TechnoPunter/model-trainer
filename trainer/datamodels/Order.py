from sqlalchemy import Column, Integer, String, Numeric

from trainer.dataprovider.database import Base


class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    order_ref = Column(String)
    model = Column(String)
    scrip = Column(String)
    symbol = Column(String)
    exchange = Column(String)
    ts = Column(Integer)
    order_date = Column(String)
    o = Column(Numeric)
    h = Column(Numeric)
    l = Column(Numeric)
    c = Column(Numeric)
    signal = Column(Integer)
    sl = Column(Numeric)
    t1 = Column(Numeric)
    t2 = Column(Numeric)
    qty = Column(Numeric)
    indicators = Column(String)
