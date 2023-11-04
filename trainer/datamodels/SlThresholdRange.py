from sqlalchemy import Column, Integer, String, Numeric

from trainer.dataprovider.database import Base


class SlThresholdRange(Base):
    __tablename__ = 'sl_threshold_range'

    scrip = Column(String, primary_key=True)
    min_target = Column(Numeric)
    max_target = Column(Numeric)
    target_step = Column(Numeric)
    min_sl = Column(Numeric)
    max_sl = Column(Numeric)
    sl_step = Column(Numeric)
    min_trail_sl = Column(Numeric)
    max_trail_sl = Column(Numeric)
    trail_sl_step = Column(Numeric)
    tick = Column(Numeric)
