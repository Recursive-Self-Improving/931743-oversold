"""Consumer-visible cutoffs, stale-data states, and signal-window boundaries."""

import unittest
from datetime import date, datetime, timedelta, timezone

from oversold.app import SHANGHAI, build_report, closed_through
from oversold.data import DataError
from oversold.models import Candle


def bars_ending(end, closes):
    days = []
    current = end
    while len(days) < len(closes):
        if current.weekday() < 5:
            days.append(current)
        current -= timedelta(days=1)
    return [Candle(day, close, close, close, close, 0, 0) for day, close in zip(reversed(days), closes)]


class ClosePolicyTests(unittest.TestCase):
    def test_cutoff_uses_shanghai_not_machine_timezone(self):
        before = datetime(2026, 9, 28, 7, 29, 59, tzinfo=timezone.utc)
        after = datetime(2026, 9, 28, 7, 30, tzinfo=timezone.utc)
        self.assertEqual(closed_through(before), date(2026, 9, 27))
        self.assertEqual(closed_through(after), date(2026, 9, 28))

    def test_intraday_crash_cannot_trigger_final_signal(self):
        day = date(2026, 9, 28)
        candles = bars_ending(day, [100] * 30 + [1])
        before = build_report(candles, day, datetime(2026, 9, 28, 14, tzinfo=SHANGHAI))
        after = build_report(candles, day, datetime(2026, 9, 28, 18, tzinfo=SHANGHAI))
        self.assertEqual(before["status"], "awaiting_close")
        self.assertEqual(before["latest"]["date"], "2026-09-25")
        self.assertFalse(before["latest"]["oversold"])
        self.assertEqual(after["status"], "current")
        self.assertTrue(after["latest"]["oversold"])
        self.assertTrue(after["latest"]["entry"])

    def test_missing_current_bar_keeps_requested_calendar_window(self):
        candles = bars_ending(date(2026, 9, 24), [100] * 30)
        report = build_report(candles, date(2026, 9, 28), datetime(2026, 9, 28, 18, tzinfo=SHANGHAI))
        self.assertEqual(report["status"], "no_current_bar")
        self.assertEqual(report["data_end"], "2026-09-24")
        self.assertEqual(report["window_start"], "2024-09-28")

    def test_cache_on_current_date_remains_explicitly_offline(self):
        report = build_report(bars_ending(date(2026, 9, 28), [100] * 30), date(2026, 9, 28), datetime(2026, 9, 28, 18, tzinfo=SHANGHAI), offline=True)
        self.assertEqual(report["status"], "offline")

    def test_history_does_not_use_future_crash(self):
        candles = bars_ending(date(2026, 9, 28), [100] * 30 + [1])
        report = build_report(candles, date(2026, 9, 25), datetime(2026, 9, 28, 18, tzinfo=SHANGHAI))
        self.assertEqual(report["latest"]["rsi"], 50)
        self.assertEqual(report["latest"]["date"], "2026-09-25")
        self.assertFalse(report["latest"]["oversold"])

    def test_window_start_inside_oversold_run_is_not_a_new_entry(self):
        candles = bars_ending(date(2024, 9, 30), [200] * 16 + [150] * 4 + [100])
        report = build_report(candles, date(2026, 9, 30), datetime(2026, 9, 30, 18, tzinfo=SHANGHAI))
        self.assertEqual([row["date"] for row in report["signals"]], ["2024-09-30"])
        self.assertFalse(report["signals"][0]["entry"])
        self.assertEqual(report["entries"], [])

    def test_rejects_future_or_unwarmed_analysis(self):
        now = datetime(2026, 9, 28, 18, tzinfo=SHANGHAI)
        with self.assertRaises(DataError):
            build_report(bars_ending(date(2026, 9, 28), [100] * 30), date(2026, 9, 29), now)
        with self.assertRaises(DataError):
            build_report(bars_ending(date(2026, 9, 28), [100] * 19), date(2026, 9, 28), now)


if __name__ == "__main__":
    unittest.main()
