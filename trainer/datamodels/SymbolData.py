from sqlalchemy import Column, Integer, String

from trainer.dataprovider.database import Base


class SymbolData(Base):
    __tablename__ = 'symbol_data'

    ts = Column(Integer, primary_key=True)
    symbol = Column(String)
    timeframe = Column(Integer)
    indicator_data = Column(String)
