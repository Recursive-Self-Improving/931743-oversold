"""Deterministic reference and boundary tests for historical indicators."""

import unittest
from datetime import date, timedelta

from oversold.indicators import analyze, two_year_start
from oversold.models import Candle


START = date(2024, 1, 1)


def candles_from_closes(closes):
    return [
        Candle(START + timedelta(days=day), close, close, close, close, 0.0, 0.0)
        for day, close in enumerate(closes)
    ]


class IndicatorTests(unittest.TestCase):
    def test_wilder_reference_seed_and_subsequent_smoothing(self):
        # Wilder's published sample; values below are independently tabulated
        # (rounded to six decimal places), not derived from this implementation.
        closes = [
            44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
            45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00,
            46.03, 46.41, 46.22, 45.64, 46.21,
        ]
        rows = analyze(candles_from_closes(closes))
        self.assertTrue(all(row.rsi is None for row in rows[:14]))
        for index, expected in [(14, 70.464135), (15, 66.249619), (16, 66.480942)]:
            self.assertAlmostEqual(rows[index].rsi, expected, delta=0.000002)
        self.assertTrue(all(row.bb_lower is None for row in rows[:19]))

    def test_flat_all_gain_and_all_loss(self):
        for closes, expected in [([100] * 22, 50), (list(range(22)), 100),
                                 (list(range(22, 0, -1)), 0)]:
            with self.subTest(expected=expected):
                rows = analyze(candles_from_closes(closes))
                self.assertTrue(all(row.rsi == expected for row in rows[14:]))
                self.assertFalse(any(row.oversold for row in rows))

    def test_bollinger_population_band_and_equality_signal(self):
        rows = analyze(candles_from_closes([100] * 16 + [50] * 4))
        self.assertFalse(any(row.oversold for row in rows[:19]))
        last = rows[-1]
        self.assertEqual((last.bb_middle, last.bb_upper, last.bb_lower), (90, 130, 50))
        self.assertEqual(last.rsi, 0)
        self.assertTrue(last.oversold)
        self.assertTrue(last.entry)

    def test_consecutive_oversold_exit_and_reentry(self):
        closes = [100] * 16 + [50] * 4 + [0, 0, 100, -100]
        rows = analyze(candles_from_closes(closes))
        self.assertEqual([index for index, row in enumerate(rows) if row.oversold],
                         [19, 20, 21, 23])
        self.assertEqual([index for index, row in enumerate(rows) if row.entry],
                         [19, 23])

    def test_strict_rsi_threshold_when_price_is_below_lower_band(self):
        # The loss/gain path is tuned to straddle RSI 30; the last three
        # closes stay below their rolling lower band on both sides.
        a = 13 / 14
        boundary_gain = 150 / (7 * a - 3 * a * a)
        for gain, expected_oversold in [(boundary_gain * (1 - 1e-9), True),
                                        (boundary_gain * (1 + 1e-9), False)]:
            with self.subTest(gain=gain):
                closes = [100] * 15 + [100 - gain, 100, 50, 50, 50]
                last = analyze(candles_from_closes(closes))[-1]
                self.assertLess(50, last.bb_lower)
                self.assertAlmostEqual(last.rsi, 30, delta=1e-7)
                self.assertEqual(last.rsi < 30, expected_oversold)
                self.assertEqual(last.oversold, expected_oversold)

    def test_prefix_invariance_across_future_extremes(self):
        prefix = candles_from_closes([100] * 16 + [50] * 4 + [0])
        earlier = analyze(prefix)
        future = [
            Candle(prefix[-1].date + timedelta(days=1 + index), close, close,
                   close, close, 0, 0)
            for index, close in enumerate([1e10, -1e10])
        ]
        self.assertEqual(earlier, analyze(prefix + future)[:len(prefix)])

    def test_rejects_duplicate_and_out_of_order_dates(self):
        ordered = candles_from_closes([100, 90])
        for invalid in [[ordered[0], ordered[0]], list(reversed(ordered))]:
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "strictly increasing"):
                    analyze(invalid)

    def test_two_year_calendar_leap_boundary(self):
        self.assertEqual(two_year_start(date(2024, 2, 29)), date(2022, 2, 28))
        self.assertEqual(two_year_start(date(2026, 9, 28)), date(2024, 9, 28))


if __name__ == "__main__":
    unittest.main()
