"""Daily RSI and Bollinger analysis over the complete available trading history."""

from collections import deque
from collections.abc import Sequence
from datetime import date
from math import fsum, sqrt

from .models import Candle, Signal


def two_year_start(end: date) -> date:
    """Return the same calendar date two years earlier (Feb 29 becomes Feb 28)."""
    try:
        return end.replace(year=end.year - 2)
    except ValueError:
        return end.replace(year=end.year - 2, day=28)


def _rsi(average_gain: float, average_loss: float) -> float:
    if average_loss == 0:
        return 50.0 if average_gain == 0 else 100.0
    if average_gain == 0:
        return 0.0
    return 100.0 * average_gain / (average_gain + average_loss)


def analyze(candles: Sequence[Candle]) -> list[Signal]:
    """Analyze every bar in order, without filtering history or looking ahead.

    RSI(14) uses the mean of the first 14 close-to-close gains/losses,
    followed by Wilder smoothing. The Bollinger band is the mean of the
    current and preceding 19 closes, plus/minus two population deviations.
    After both indicators warm up, either RSI < 30 or a close strictly below
    the lower band triggers oversold. Equality alone is not a band breakout,
    so a flat, zero-width band cannot trigger. Entry starts each oversold run.
    """
    results: list[Signal] = []
    closes: deque[float] = deque(maxlen=20)
    seed_gains: list[float] = []
    seed_losses: list[float] = []
    average_gain = average_loss = 0.0
    previous: Candle | None = None
    previous_oversold = False

    for index, candle in enumerate(candles):
        if previous is not None and candle.date <= previous.date:
            raise ValueError("candle dates must be strictly increasing")

        rsi: float | None = None
        if previous is not None:
            change = candle.close - previous.close
            gain = max(change, 0.0)
            loss = max(-change, 0.0)
            if index <= 14:
                seed_gains.append(gain)
                seed_losses.append(loss)
                if index == 14:
                    average_gain = fsum(seed_gains) / 14
                    average_loss = fsum(seed_losses) / 14
                    seed_gains.clear()
                    seed_losses.clear()
            else:
                average_gain = (average_gain * 13 + gain) / 14
                average_loss = (average_loss * 13 + loss) / 14
            if index >= 14:
                rsi = _rsi(average_gain, average_loss)

        closes.append(candle.close)
        middle: float | None = None
        upper: float | None = None
        lower: float | None = None
        if len(closes) == 20:
            middle = fsum(closes) / 20
            deviation = sqrt(fsum((close - middle) ** 2 for close in closes) / 20)
            upper = middle + 2 * deviation
            lower = middle - 2 * deviation

        reasons = []
        if rsi is not None and lower is not None:
            if rsi < 30:
                reasons.append("RSI < 30")
            if candle.close < lower:
                reasons.append("跌破布林下轨")
        oversold = bool(reasons)
        results.append(Signal(candle, rsi, middle, upper, lower, oversold,
                              oversold and not previous_oversold, " + ".join(reasons)))
        previous_oversold = oversold
        previous = candle

    return results
