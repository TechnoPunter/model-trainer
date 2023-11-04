from sqlalchemy import Column, Integer, String, Numeric

from trainer.dataprovider.database import Base


class SlThresholds(Base):
    __tablename__ = 'sl_thresholds'

    scrip = Column(String, primary_key=True)
    direction = Column(Integer, primary_key=True)
    strategy = Column(String, primary_key=True)
    sl = Column(Numeric)
    trail_sl = Column(Numeric)
    tick = Column(Numeric)
    target = Column(Numeric)
