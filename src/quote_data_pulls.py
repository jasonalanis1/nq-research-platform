"""
quote_data_pulls.py -- EXACT Databento quotes for the queue v2 data plan.
BUYS NOTHING. Uses metadata.get_cost only. Reads .databento_key.

Run from your own Terminal (the sandboxed shells cannot reach
hist.databento.com):

    cd ~/Documents/nq-research-platform-live && python3 src/quote_data_pulls.py

Paste the output into the chat and the cycles will buy under whatever cap
you set.
"""
import calendar
import datetime as dt
from pathlib import Path

import databento as db

ROOT = Path(__file__).resolve().parent.parent
KEY = (ROOT / ".databento_key").read_text().strip()
START, END = "2015-01-01", "2026-09-09"
DATASET, SCHEMA = "GLBX.MDP3", "ohlcv-1m"


def third_friday(y, m):
    fr = [d for d in calendar.Calendar().itermonthdates(y, m) if d.month == m and d.weekday() == 4]
    return fr[2]


def main():
    c = db.Historical(KEY)
    print("EXACT QUOTES (metadata.get_cost) -- nothing purchased\n")
    grand = 0.0
    print("Batch 1 -- index futures, 1-minute, continuous front month, 2015-01-01..2026-09-09")
    for sym, label in [("ES.c.0", "ES"), ("RTY.c.0", "RTY"), ("YM.c.0", "YM")]:
        cost = c.metadata.get_cost(dataset=DATASET, symbols=[sym], schema=SCHEMA, stype_in="continuous", start=START, end=END)
        grand += cost
        print(f"  {label:<4} ${cost:,.2f}")
    codes = {3: "H", 6: "M", 9: "U", 12: "Z"}
    total, n = 0.0, 0
    for y in range(2015, 2027):
        for m in (3, 6, 9, 12):
            f = third_friday(y, m)
            if f > dt.date(2026, 9, 9):
                continue
            s, e = (f - dt.timedelta(days=7)).isoformat(), (f + dt.timedelta(days=4)).isoformat()
            total += c.metadata.get_cost(dataset=DATASET, symbols=[f"NQ{codes[m]}{str(y)[-1]}"], schema=SCHEMA, stype_in="raw_symbol", start=s, end=e)
            n += 1
    grand += total
    print(f"  NQ outright contract months, {n} witching weeks (revives M9): ${total:,.2f}")
    print(f"  BATCH 1 TOTAL: ${grand:,.2f}\n")
    print("Batch 2 -- later")
    zt = c.metadata.get_cost(dataset=DATASET, symbols=["ZT.c.0"], schema=SCHEMA, stype_in="continuous", start=START, end=END)
    print(f"  ZT 2-year note 1-minute: ${zt:,.2f}")
    try:
        eq = c.metadata.get_cost(dataset="XNAS.ITCH", symbols=["QQQ", "SPY", "IWM", "DIA"], schema=SCHEMA, stype_in="raw_symbol", start="2018-05-01", end=END)
        print(f"  SPY/QQQ/IWM/DIA 1-minute (Nasdaq feed, from 2018-05): ${eq:,.2f}")
    except Exception as ex:
        print(f"  SPY/QQQ/IWM/DIA: could not quote on XNAS.ITCH ({type(ex).__name__}); the cycle will try another equities dataset")
    try:
        up = [u for u in c.metadata.list_unit_prices(dataset=DATASET) if u.get("mode") == "historical"][0]["unit_prices"]
        print(f"\nGLBX.MDP3 historical $/GB -- ohlcv-1m {up.get('ohlcv-1m')}, trades {up.get('trades')}, statistics {up.get('statistics')}")
    except Exception:
        pass
    print("\nCredits: new accounts carry $125; check your balance at databento.com/portal before deciding.")


if __name__ == "__main__":
    main()
