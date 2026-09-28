"""Reject false candles and retain corrected sessions without duplication."""

import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from oversold.data import DataError, load_candles, parse_candles, save_candles
from oversold.models import Candle


class MarketDataTests(unittest.TestCase):
    def test_rejects_wrong_symbol_invalid_ohlc_nonfinite_and_weekend(self):
        base = {"indexCode": "931743", "tradeDate": "20230719", "open": 3450.10, "high": 3475.77, "low": 3402.53, "close": 3416.96, "tradingVol": 536439769, "tradingValue": 151.33}
        for change in ({"indexCode": "000300"}, {"high": 3000}, {"close": float("nan")}, {"tradeDate": "20230722"}, {"open": None}):
            with self.subTest(change=change), self.assertRaises(DataError):
                parse_candles({"code": "200", "data": [base | change]}, date(2023, 7, 19), date(2023, 7, 24))

    def test_duplicate_or_truncated_history_cannot_be_silently_analyzed(self):
        row = {"indexCode": "931743", "tradeDate": "20230720", "open": 100, "high": 101, "low": 98, "close": 99, "tradingVol": 1, "tradingValue": 1}
        with self.assertRaises(DataError):
            parse_candles({"code": "200", "data": [row, row]}, date(2023, 7, 20), date(2023, 7, 21))
        with self.assertRaises(DataError):
            parse_candles({"code": "200", "data": [row]}, date(2023, 7, 19), date(2023, 7, 21))
        with self.assertRaises(DataError):
            parse_candles({"code": "200", "data": []}, date(2023, 7, 19), date(2023, 7, 21))

    def test_overlapping_updates_replace_revised_day_and_keep_history(self):
        now = datetime(2026, 9, 28, tzinfo=timezone.utc)
        first = Candle(date(2026, 9, 23), 100, 102, 98, 99, 10, 1000)
        revised = Candle(date(2026, 9, 23), 100, 102, 98, 101, 11, 1100)
        next_day = Candle(date(2026, 9, 24), 101, 104, 100, 103, 12, 1200)
        with TemporaryDirectory() as directory:
            path = Path(directory) / "history.sqlite3"
            save_candles(path, [first], now)
            save_candles(path, [revised, next_day], now)
            self.assertEqual([(row.date, row.close) for row in load_candles(path, date(2026, 9, 24))], [(date(2026, 9, 23), 101), (date(2026, 9, 24), 103)])
            self.assertEqual([row.close for row in load_candles(path, date(2026, 9, 23))], [101])


if __name__ == "__main__":
    unittest.main()
