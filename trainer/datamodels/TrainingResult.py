from sqlalchemy import Column, String, Numeric, Integer

from trainer.dataprovider.database import Base


class TrainingResult(Base):
    __tablename__ = 'training_result'
    id = Column(Integer, primary_key=True)

    # Business Key Columns
    model = Column(String)
    training_date = Column(String)
    scrip = Column(String)

    # PNL Column
    ref = Column(String)
    dir = Column(String)
    size = Column(Integer)
    datein = Column(String)
    pricein = Column(Numeric)
    eventin = Column(String)
    dateout = Column(String)
    priceout = Column(Numeric)
    eventout = Column(String)
    pnl = Column(Numeric)
    cumpnl = Column(Numeric)
    result = Column(String)
    sl = Column(Numeric)
    target = Column(Numeric)

    # Prediction Columns
    time = Column(Integer)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    signal = Column(Integer)
    t1 = Column(Numeric)
    t2 = Column(Numeric)
    date = Column(String)
    day_row_number = Column(Integer)
    next_close = Column(Numeric)
    mean = Column(Numeric)
    mean_se = Column(Numeric)
    mean_ci_lower = Column(Numeric)
    mean_ci_upper = Column(Numeric)
    datetime = Column(String)
    slupdcnt = Column(Integer)
    maxprofit = Column(Numeric)
    maxloss = Column(Numeric)
