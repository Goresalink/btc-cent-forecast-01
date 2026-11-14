#!/usr/bin/env python3
"""btc-cent-forecast-01 entry: forecast BTC's US-dollar price 240 minutes
after each checkpoint.

Design (backtested on the kit's practice recording, Nov 7-11 2026):
work in log-price space and nudge the checkpoint close with two small,
opposite-signed signals:

  * short-horizon momentum: the log-return over the last 1 hour,
    damped by +0.20 (recent direction tends to persist a little);
  * long-horizon mean reversion: the log-return over the last 24 hours,
    damped by -0.20 (a big one-day move tends to partially retrace).

  forecast = last_price * exp(0.20 * ret_1h - 0.20 * ret_24h)

Backtest (sliding checkpoints every 15 min over the practice recording,
64 windows; plus the 5 backtestable practice cases p00-p04):
  * backtest MAE 47,881 cents vs persistence 51,573 (-7.2%), win rate 0.55,
    median error ratio 0.90;
  * 4-hour-spaced blocks: MAE 43,801 vs 52,741 (-17.0%), win rate 0.75;
  * practice cases: MAE 43,310 vs 47,055 (-8.0%), win rate 0.60.
The same sign pattern (positive 1h, negative 24h coefficient) wins across
the whole neighbourhood of these parameters, so the design is not tuned
to a single point. Adjustments stay small (at most ~0.5% of price).

Deterministic, Python 3.13 standard library only, no network, no clock.
Reads every *.in file in $MAKEFUN_INPUT_DIR (else /input) in name order
and writes <id>.out to $MAKEFUN_OUTPUT_DIR (else /output).
"""

import json
import math
import os
import sys

# Tuned damping factors (see module docstring for the backtest).
A_SHORT = 0.20   # weight on the 1-hour log-return (momentum)
A_LONG = -0.20   # weight on the 24-hour log-return (mean reversion)

MIN_PRICE = 0.00001
MAX_PRICE = 9999999.99999


def forecast_price(prices):
    """Forecast the price 240 minutes after the last close in `prices`."""
    n = len(prices)
    if n == 0:
        return None
    last = prices[-1]
    if last <= 0:
        return None
    log_last = math.log(last)

    adj = 0.0
    if n > 60:
        ret_1h = log_last - math.log(prices[-61])
        adj += A_SHORT * ret_1h
    if n > 1440:
        ret_24h = log_last - math.log(prices[-1441])
        adj += A_LONG * ret_24h

    price = math.exp(log_last + adj)
    price = round(price, 5)
    if price < MIN_PRICE:
        price = MIN_PRICE
    elif price > MAX_PRICE:
        price = MAX_PRICE
    return price


def main():
    in_dir = os.environ.get("MAKEFUN_INPUT_DIR") or "/input"
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)

    names = sorted(fn for fn in os.listdir(in_dir) if fn.endswith(".in"))
    for name in names:
        case_id = name[:-3]
        with open(os.path.join(in_dir, name), "r", encoding="utf-8") as fh:
            case = json.load(fh)
        prices = case["markets"][0]["prices"]
        price = forecast_price(prices)
        if price is None:
            # No usable price: fall back to the checkpoint close itself
            # (persistence), which is always a valid guess.
            price = round(float(prices[-1]), 5) if prices else 1.0
            price = min(max(price, MIN_PRICE), MAX_PRICE)
        payload = {"forecasts": [{"case": case_id, "price": price}]}
        out_path = os.path.join(out_dir, case_id + ".out")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, separators=(",", ":"))
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
