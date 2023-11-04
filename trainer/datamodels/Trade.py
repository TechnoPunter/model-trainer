from sqlalchemy import Column, Integer, String, Numeric

from trainer.dataprovider.database import Base


class Trade(Base):
    __tablename__ = 'trade'

    trade_id = Column(Integer, primary_key=True)
    stat = Column(String)
    norenordno = Column(Integer)
    uid = Column(String)
    actid = Column(String)
    exch = Column(String)
    prctyp = Column(String)
    ret = Column(String)
    s_prdt_ali = Column(String)
    prd = Column(String)
    flid = Column(String)
    fltm = Column(String)
    trantype = Column(String)
    tsym = Column(String)
    qty = Column(String)
    token = Column(String)
    fillshares = Column(Integer)
    flqty = Column(Integer)
    pp = Column(Integer)
    ls = Column(Integer)
    ti = Column(Numeric)
    prc = Column(Numeric)
    prcftr = Column(Numeric)
    flprc = Column(Numeric)
    norentm = Column(String)
    exch_tm = Column(String)
    exchordid = Column(Integer)
    remarks = Column(String)
