import datetime
import time

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from .backtester import run
from .utils import TF_EQUIV
from .data_collector import collect_all
from .cexchanges.binance import BinanceClient
from .cexchanges.ftx import FtxClient

from widgets.box import BackBox

Builder.load_file('views/strategies/strategies.kv')
class Strategy(BoxLayout):
    def __init__(self, **kw) -> None:
        super().__init__(**kw)

    def onclick_mode(self):
        mode = self.ids.mode.text.strip()
        if (mode == "Backtest data"):
            self.ids.backbox_strategy.opacity = 1
            self.ids.strategy.disabled = False

            self.ids.backbox_timeframe.opacity = 1
            self.ids.timeframe.disabled = False

            self.ids.backbox_from_time.opacity = 1
            self.ids.from_time.disabled = False

            self.ids.backbox_to_time.opacity = 1
            self.ids.to_time.disabled = False
        else:
            self.ids.backbox_strategy.opacity = 0
            self.ids.strategy.disabled = True

            self.ids.backbox_timeframe.opacity = 0
            self.ids.timeframe.disabled = True

            self.ids.backbox_from_time.opacity = 0
            self.ids.from_time.disabled = True

            self.ids.backbox_to_time.opacity = 0
            self.ids.to_time.disabled = True
    
    def onclick_strategy(self):
        _strategy = self.ids.strategy.text.strip()
        if _strategy == "On-balance volume":
            self.ids.backbox_ma_period.opacity = 1
            self.ids.ma_period.disabled = False

            self.ids.backbox_kijun.opacity = 0
            self.ids.kijun.disabled = True
            self.ids.backbox_tenkan.opacity = 0
            self.ids.tenkan.disabled = True


        elif _strategy == "Ichimoku Kinko Hyo":
            self.ids.backbox_kijun.opacity = 1
            self.ids.kijun.disabled = False
            self.ids.backbox_tenkan.opacity = 1
            self.ids.tenkan.disabled = False

            self.ids.backbox_ma_period.opacity = 0
            self.ids.ma_period.disabled = True
    def render(self):
        mode = self.ids.mode.text.strip()
        # mode = input("Choose the program mode (data / backtest): ").lower()
        while True:
            exchange = self.ids.cex.text.strip()
            # exchange = input("Choose an exchange: ").lower()
            if exchange in [".", "Binance"]:
                break

        if exchange == "Binance":
            client = BinanceClient(True)
        elif exchange == ".":
            client = FtxClient()

        while True:
            symbol = self.ids.symbol.text.strip()
            # symbol = input("Choose a symbol: ").upper()
            if symbol in client.symbols:
                break

        if mode == "Get data from CEX":
            collect_all(self, client, exchange, symbol)

        elif mode == "Backtest data":

            # Strategy

            available_strategies = ["obv", "ichimoku"]
            
            while True:
                _strategy = self.ids.strategy.text.strip()
                if _strategy == "On-balance volume":
                    strategy = "obv"
                elif _strategy == "Ichimoku Kinko Hyo":
                    strategy = "ichimoku"

                # strategy = input(f"Choose a strategy ({', '.join(available_strategies)}): ").lower()
                if strategy in available_strategies:
                    break

            # Timeframe

            while True:
                tf = self.ids.timeframe.text.strip()
                # tf = input(f"Choose a timeframe ({', '.join(TF_EQUIV.keys())}): ").lower()
                if tf in TF_EQUIV.keys():
                    break

            # From

            while True:
                from_time = self.ids.from_time.text.strip()
                # from_time = input("Backtest from (yyyy-mm-dd or Press Enter): ")
                if from_time == "":
                    from_time = 0
                    break

                try:
                    from_time = int(datetime.datetime.strptime(from_time, "%Y-%m-%d").timestamp() * 1000)
                    break
                except ValueError:
                    continue

            # To

            while True:
                to_time = self.ids.to_time.text.strip()
                # to_time = input("Backtest to (yyyy-mm-dd or Press Enter): ")
                if to_time == "":
                    to_time = int(datetime.datetime.now().timestamp() * 1000)
                    break

                try:
                    to_time = int(datetime.datetime.strptime(to_time, "%Y-%m-%d").timestamp() * 1000)
                    break
                except ValueError:
                    continue

            # print("(Profit & Loss, Maximum DrawDown): ", run(self, exchange, symbol, strategy, tf, from_time, to_time))

            # open a popup
            popup_pnl, popup_drawdown = run(self, exchange, symbol, strategy, tf, from_time, to_time)

            popup_content = BackBox(orientation="vertical")
            popup_content.add_widget(Label(text="Profit & Loss: " + str(round(popup_pnl * 100, 2)) + "%"))
            popup_content.add_widget(Label(text="Maximum Drawdown: " + str(round(popup_drawdown * 100, 2)) + "%"))

            popup = Popup(title="Results", content=popup_content, size_hint=(0.9, 0.3))
            popup.open()

        

        

