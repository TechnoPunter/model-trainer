"""
Order:
    ID
    Scrip
    Dir
    Qty
    Time
    Entry Price (if Limit)
    SL Price
    SL Step
    Target Price
    Target Range
    Movement Step Trailing SL
    Entry Open?
    SL Open?
    Target Open?
    Validity (Day, GTC)
    Order Status - Open, Filled, SL Hit, Target Hit, COB Hit
"""
from typing import Literal, Dict
import logging

logger = logging.getLogger(__name__)

Order_Direction = Literal["Long", "Short"]
Order_Type = Literal["Market", "Limit", "CO", "BO"]
Order_Status = Literal["Created", "Entered", "Closed"]


class Order:
    id: int
    scrip: str
    direction: Order_Direction
    quantity: float
    time: int
    type: Order_Type
    entry_limit: float
    sl_range: float
    sl: float
    sl_step: float
    target: float
    target_range: float
    movement_step_trail_sl: float
    entry_open: bool
    sl_open: bool
    target_open: bool
    status: Order_Status
    anchor_price: float

    def __init__(self, o: Dict):
        for key, value in o.items():
            setattr(self, key, value)

        self.status = "Created"
        self.entry_open = True
        if self.type in ['CO', 'BO']:
            self.sl_open = True
        else:
            self.sl_open = False

        if self.type in ['BO']:
            self.target_open = True
        else:
            self.target_open = False

        self.__post_init__()

    def __post_init__(self):
        """
        Validations here

        Returns: None (Raises ValueError)

        """
        pass

    def __repr__(self):
        members = vars(self)
        members_string = ', '.join(f'{key}={value}' for key, value in members.items())
        return f'{self.__class__.__name__}({members_string})'

    def order_entered(self):
        self.status = "Entered"
        self.entry_open = False
        return self

    def sl_hit(self):
        self.status = "Closed"
        self.sl_open = False
        self.target_open = False
        return self

    def target_hit(self):
        self.status = "Closed"
        self.target_open = False
        self.sl_open = False
        return self

    def update_sl(self, new_sl=None, row=None):
        old_sl = self.sl
        if new_sl is not None:
            self.sl = new_sl
        else:
            if self.direction == "BUY":
                self.sl = row['close'] - self.sl_range
            else:
                self.sl = row['close'] + self.sl_range
        self.anchor_price = row['close']
        logger.debug(f"SL updated: @ {row['date']}, old SL: {old_sl} new SL : {self.sl}")
        return self

    def cob_hit(self):
        self.status = "Closed"
        self.sl_open = False
        self.target_open = False
        return self


class OrderBook:
    orders: [Order]

    def __init__(self, o: Dict):
        self.orders = []
        self.__post_init__()

    def __post_init__(self):
        """
        Validations here

        Returns: None (Raises ValueError)

        """
        pass

    def enter_order(self, o: dict):
        order = Order(o)
        self.orders.append(order)

    def update_order(self, order_id: int, updates: [str], row=None) -> Order:
        """

        Args:
            order_id: The order ID that will be updated
            row: The current OHLC
            updates: List of strings containing updates to Order
                Entered --> Entry Leg created
                SL Hit --> SL Leg Hit (now close order)
                Target Hit --> Target Hit (now close order)

        Returns: Updated order

        """
        o = self.get_open_orders(order_id)
        assert len(o) == 1, "Order Id is invalid"
        for upd in updates:
            if upd == "Entered":
                return o[0].order_entered()
            elif upd == "exit-sl":
                return o[0].sl_hit()
            elif upd == "exit-target":
                return o[0].target_hit()
            elif upd == "update-sl":
                return o[0].update_sl(row=row)
            elif upd == "exit-cob":
                return o[0].cob_hit()

    def get_open_orders(self, order_id: int = None) -> [Order]:
        res = []
        for o in self.orders:
            if order_id is not None and o.id != order_id:
                continue

            if o.status not in ["Closed"]:
                res.append(o)

        return res


if __name__ == "__main__":
    o = {
        "id": 1,
        "scrip": "ABC",
        "direction": "Long",
        "quantity": 10,
        "time": 1000,
        "type": "BO",
        "entry_limit": None,
        "sl": "95",
        "sl_range": None,
        "target": 105,
        "target_range": None,
        "trailing_sl_range": 3
    }

    om = OrderBook({})
    om.enter_order(o)

    x = om.get_open_orders()
    print(x)

    x = om.get_open_orders(1)
    print(x)

    x = om.update_order(1, ["Entered"])
    print(x)

    x = om.update_order(1, ["SL Hit"])
    print(x)
