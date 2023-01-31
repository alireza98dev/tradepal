import click
import MetaTrader5 as mt5
from datetime import datetime
import time
import pandas as pd
from constants import seconds_of_a_day, forex_sessions, forex_session_duration
import pathlib

current_dir = pathlib.Path(__file__).parent.__str__()


@click.command("manipulation", help="Counts the number of manipulations in a date range ( Separate symbols using dash, Example : USDJPY-GBPUSD-AUDUSD ).")
@click.argument("symbol")
@click.option("-d", "--days", help="Number of days", default=120, type=int)
@click.option("-n", "--n", help="The manipulation should be considered in the first n hours of any session", default=4, type=int)
@click.option("-p", "--points", help="How many points (or Pipettes) from the opening of a session should be considered as a manipulation ?", default=400, type=int)
@click.option("-t", "--target", help="How many points (or Pipettes) from the manipulation point should be considered as a target point ?", default=400, type=int)
@click.option("--dir", help="Directory path to save the csv results", default=current_dir, show_default=True)
def manipulation(symbol: str, days, n, points, target, dir):
    symbols = []
    if "-" in symbol:
        symbols = symbol.split("-")
    else:
        symbols = [symbol]

    for symbol in symbols:
        total_manipulations = 0
        print(f"Getting symbol info for {symbol}")
        info = mt5.symbol_info(symbol)
        if not info:
            print("Symbol not found")
        NOW = time.time()
        start = datetime.fromtimestamp(NOW - (days * seconds_of_a_day))
        end = datetime.fromtimestamp(NOW)
        print(f"Getting historical data for {symbol}")
        candlestick = mt5.copy_rates_range(
            symbol, mt5.TIMEFRAME_H1, start, end)
        candlestick = pd.DataFrame(candlestick, columns=[
            "time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume"])
        candlestick['time'] = pd.to_datetime(candlestick['time'], unit='s')
        session_start: dict[str, datetime] = dict()
        open: dict[str, float] = dict()
        high: dict[str, float] = dict()
        low: dict[str, float] = dict()
        day_of_manip: dict[str, int] = dict()

        # Initializing session vars
        for s in forex_sessions.keys():
            session_start[s] = datetime.fromtimestamp(
                NOW - ((days + 2) * seconds_of_a_day))
            open[s] = 0.
            high[s] = 0.
            low[s] = 0.
            day_of_manip[s] = 0

        # calculates points of a price delta
        def calc_points(price_delta: float):
            return price_delta / info.point

        columns = ["points", "target", "n_hours", "days", "start", "end"]
        m_data = [points, target, n, days, start, end]
        for s in forex_sessions.keys():
            columns.append(f"{s}_lows")
            columns.append(f"{s}_highs")
            m_data.append(0)
            m_data.append(0)

        manipulation_df = pd.DataFrame([m_data], columns=columns)
        print(f"Counting manipulations for {symbol}")
        for index, row in candlestick.iterrows():
            t: datetime = row["time"]
            for s in forex_sessions.keys():
                session = forex_sessions[s]
                if t.hour == session.hour and t.minute == session.minute:
                    session_start[s] = t
                    open[s] = row["open"]

                # The number of past from the start of current session
                hours = (t - session_start[s]).total_seconds() / 3600

                if day_of_manip[s] != t.day and hours <= n and calc_points(row["high"] - open[s]) >= points:
                    # When the manipulation conditions met (highs)
                    high[s] = max(open[s] + points * info.point, high[s])
                    if calc_points(high[s] - row["low"]) > target:
                        day_of_manip[s] = t.day
                        manipulation_df.at[0, f"{s}_highs"] += 1
                        total_manipulations += 1
                elif day_of_manip[s] != t.day and hours <= n and calc_points(open[s] - row["low"]) >= points:
                    # When the manipulation conditions met (lows)
                    low[s] = max(open[s] - points * info.point, low[s])
                    if calc_points(row["high"] - low[s]) > target:
                        day_of_manip[s] = t.day
                        manipulation_df.at[0, f"{s}_lows"] += 1
                        total_manipulations += 1
                elif hours > n:
                    high[s] = 0.
                    low[s] = 0.
                    day_of_manip[s] = 0

        manipulation_df.to_csv(
            f"{dir}/{symbol}_{end.year}-{end.month}-{end.day}_{end.hour}-{end.minute}-{end.second}(Manipulation stats).csv")
        print(
            f"Manipulation counting saved for {symbol} \nTotal manipulations  : {total_manipulations}")
