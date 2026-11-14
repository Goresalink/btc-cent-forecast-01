# btc-cent-forecast-01

Forecast Bitcoin's US-dollar price 4 hours after each checkpoint, for the
[make.fun bounty btc-cent-forecast-01](https://make.fun/bounty/btc-cent-forecast-01)
($250, 100 places paid).

## What it does

`main.py` (Python 3.13, standard library only) reads one case at a time —
4,320 one-minute BTC/USDC closes for the 72 hours up to a checkpoint — and
writes a single forecast of the close 240 minutes later.

The forecaster works in log-price space and nudges the checkpoint close with
two small, opposite-signed signals, both backtested on the kit's practice
recording:

- **short-horizon momentum**: the log-return over the last 1 hour, damped
  by +0.20;
- **long-horizon mean reversion**: the log-return over the last 24 hours,
  damped by −0.20.

`forecast = last_price * exp(0.20 * ret_1h − 0.20 * ret_24h)`

Backtest results: sliding 15-minute checkpoints over the practice recording
gave MAE 47,881 cents vs 51,573 for persistence (−7.2%, win rate 0.55);
the 5 backtestable practice cases gave MAE 43,310 vs 47,055 (−8.0%).
Adjustments stay small (at most ~0.5% of price), so a wrong signal costs
little; the program is deterministic and always outputs a valid price.

## Run it locally

```sh
MAKEFUN_INPUT_DIR=<kit>/input MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

It reads every `*.in` file in the input directory (in name order) and writes
`<id>.out` for each, shaped `{"forecasts":[{"case":"<id>","price":<number>}]}`.

## License

MIT. Owner: Goresalink. Repository: btc-cent-forecast-01.
