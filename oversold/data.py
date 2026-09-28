"""Official CSI daily OHLC with a persistent, overlapping SQLite cache."""

from __future__ import annotations

import json
import math
import sqlite3
from datetime import date, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Candle, INDEX_CODE

SOURCE_NAME = "中证指数官网公开行情接口"
SOURCE_URL = "https://www.csindex.com.cn/csindex-home/perf/index-perf"
# First complete OHLC date verified against Eastmoney's 2.931743 history.
# The CSI chart API can synthesize a leading point for a non-trading startDate.
# Always start on this verified session, or an actual cached trading session.
HISTORY_START = date(2023, 7, 19)


class DataError(ValueError):
    """Missing or invalid market data; never interpreted as a negative signal."""


def parse_candles(payload: dict, start: date, end: date) -> list[Candle]:
    if not isinstance(payload, dict) or str(payload.get("code")) != "200":
        raise DataError("中证接口未返回成功状态。")
    raw_rows = payload.get("data")
    if not isinstance(raw_rows, list) or not raw_rows:
        raise DataError("中证接口没有返回日线；不会以旧数据替代本次实时检查。")
    candles = []
    seen = set()
    try:
        for row in raw_rows:
            if str(row["indexCode"]) != INDEX_CODE:
                raise DataError("行情指数代码不匹配，拒绝写入缓存。")
            day = datetime.strptime(row["tradeDate"], "%Y%m%d").date()
            if day in seen or day.weekday() >= 5 or not start <= day <= end:
                raise DataError(f"行情日期重复、非工作日或越界：{day}")
            seen.add(day)
            values = [float(row[key]) for key in ("open", "high", "low", "close", "tradingVol", "tradingValue")]
            if not all(math.isfinite(value) for value in values):
                raise DataError(f"行情含非有限数值：{day}")
            opening, high, low, close, volume, amount_yi = values
            if not (0 < low <= min(opening, close) <= max(opening, close) <= high):
                raise DataError(f"OHLC 高低价关系异常：{day}")
            if volume < 0 or amount_yi < 0:
                raise DataError(f"成交量或成交额为负：{day}")
            candles.append(Candle(day, opening, high, low, close, volume, amount_yi * 100_000_000))
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, DataError):
            raise
        raise DataError(f"无法解析中证日线字段：{error}") from error
    candles.sort(key=lambda candle: candle.date)
    if candles[0].date != start:
        raise DataError(f"行情未覆盖请求起点 {start}，可能被接口截断；拒绝生成不完整报告。")
    return candles


def fetch_candles(start: date, end: date) -> list[Candle]:
    query = urlencode({"indexCode": INDEX_CODE, "startDate": start.strftime("%Y%m%d"), "endDate": end.strftime("%Y%m%d")})
    request = Request(
        f"{SOURCE_URL}?{query}",
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.csindex.com.cn/", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (URLError, OSError, ValueError) as error:
        raise DataError(f"获取中证日线失败：{error}。可显式使用 --offline 查看缓存，但不能当作今日检查。") from error
    return parse_candles(payload, start, end)


def load_candles(path: Path, end: date) -> list[Candle]:
    if not path.exists():
        return []
    with sqlite3.connect(path) as connection:
        rows = connection.execute(
            "SELECT date, open, high, low, close, volume, amount FROM candles WHERE date <= ? ORDER BY date",
            (end.isoformat(),),
        ).fetchall()
    return [Candle(date.fromisoformat(row[0]), *row[1:]) for row in rows]


def save_candles(path: Path, candles: list[Candle], fetched_at: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS candles (
            date TEXT PRIMARY KEY, open REAL NOT NULL, high REAL NOT NULL,
            low REAL NOT NULL, close REAL NOT NULL, volume REAL NOT NULL, amount REAL NOT NULL
        )""")
        connection.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.executemany(
            """INSERT INTO candles VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET open=excluded.open, high=excluded.high,
            low=excluded.low, close=excluded.close, volume=excluded.volume, amount=excluded.amount""",
            [(c.date.isoformat(), c.open, c.high, c.low, c.close, c.volume, c.amount) for c in candles],
        )
        connection.executemany(
            "INSERT INTO metadata VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            [("index_code", INDEX_CODE), ("source", SOURCE_URL), ("fetched_at", fetched_at.isoformat())],
        )


def history(path: Path, end: date, now: datetime, *, offline: bool = False) -> list[Candle]:
    if end < HISTORY_START:
        raise DataError(f"本项目完整 OHLC 历史起点为 {HISTORY_START}，请求日期过早。")
    cached = load_candles(path, end)
    if offline:
        if not cached:
            raise DataError("没有可用缓存；请先联网运行一次。")
        return cached
    start = cached[max(0, len(cached) - 20)].date if cached else HISTORY_START
    fetched = fetch_candles(start, end)
    save_candles(path, fetched, now)
    return load_candles(path, end)
