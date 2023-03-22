
from locale import currency
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.metrics import dp, sp
from kivy.utils import rgba, QueryDict
from kivy.properties import ColorProperty, ObjectProperty, BooleanProperty, ListProperty, StringProperty, NumericProperty

from kivy.garden.graph import LinePlot
from kivy.garden.iconfonts import icon
from kivy.clock import Clock

Builder.load_file('views/assetview/assetview.kv')
class AssetView(ModalView):
    currency = StringProperty("BTC")
    asset_value = NumericProperty(42342.62)
    source = StringProperty("")
    chart_data = ListProperty([0,1])
    day_data = ListProperty([0,1])
    weekly_data = ListProperty([0,1])
    # monthly_data = ListProperty([0,1])
    # yearly_data = ListProperty([0,1])
    data = ObjectProperty(allownone=True)
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .2)

    def render(self, _):
        graph = self.ids.asset_graph
        plot = LinePlot()
        plot.line_width = dp(1.2)
        plot.color = App.get_running_app().colors.tertiary_light

        self.ids.asset_graph.add_plot(plot)

    def on_data(self, inst, data):
        """
            Expected data
            =======================
            ['id', 'symbol', 'name', 'image', 'current_price', 'market_cap', 'market_cap_rank', 'fully_diluted_valuation', 'total_volume', 'high_24h', 'low_24h', 'price_change_24h', 'price_change_percentage_24h', 'market_cap_change_24h', 'market_cap_change_percentage_24h', 'circulating_supply', 'total_supply', 'max_supply', 'ath', 'ath_change_percentage', 'ath_date', 'atl', 'atl_change_percentage', 'atl_date', 'roi', 'last_updated']
        """
        self.ids.market_cap.text = str(data['market_cap'])
        self.ids.low.text = str(data['low_24h'])
        self.ids.volume.text = str(data['total_volume'])
        self.ids.high.text = str(data['high_24h'])
        self.ids.circulating_supply.text = str(data['circulating_supply'])
        self.ids.total_supply.text = str(data['total_supply'])

        price_change = str(data['price_change_percentage_24h'])[:4] + "%"
        price_change = price_change.replace("+-", "-")
        self.ids.price_change.text = price_change
    
    def update_graph(self, data_type="day"):
        if data_type == 'hour':
            target = [x for x in self.day_data[-60:]]
        if data_type == 'day':
            target = self.day_data
        elif data_type == 'week':
            target = self.weekly_data
            # print(target)
        # elif data_type == 'month':
        #     target = self.monthly_data
        # elif data_type == 'year':
        #     target = self.yearly_data

        if len(target) > 4:
            self.chart_data = target

    def on_chart_data(self, inst, prices):
        graph = self.ids.asset_graph
        plots = graph.plots


        if len(plots) == 0:
            return

        points = []
        ymax = 0
        ymin = min(prices)

        for i, p in enumerate(prices):
            pt = (i+1, p)
            points.append(pt)

            if p > ymax:
                ymax = p

        graph.ymax = ymax
        graph.ymin = ymin
        plots[0].points = points
    
    def place_order(self, buy=True):
        ao = AssetOrder()
        ao.buy = buy
        ao.currency = self.currency
        ao.current_balance = 0.0
        ao.open()

class AssetOrder(ModalView):
    buy = BooleanProperty(True)
    currency = StringProperty("BTC")
    current_balance = NumericProperty(0.0)
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
        Clock.schedule_once(self.render, .2)

    def render(self, _):
        keys = '789456123.0-'
        numpad = self.ids.numpad
        numpad.clear_widgets()

        for k in keys:
            anchor = AnchorLayout()
            kp = KeyPad()
            if k == "-":
                k = icon("icon-delete")
                kp.filled = False
            
            if k == ".":
                kp.filled = False
            kp.text = str(k)

            anchor.add_widget(kp)
            numpad.add_widget(anchor)

class KeyPad(Button):
    filled = BooleanProperty(True)
    def __init__(self, **kw) -> None:
        super().__init__(**kw)
