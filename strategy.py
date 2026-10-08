
from dataclasses import dataclass


@dataclass
class Signal:
    side: str
    score: int
    reasons: list[str]


def ema(values: list[float], period: int) -> float:
    if len(values) < period:
        raise ValueError("Candles insuficientes para EMA")

    multiplier = 2 / (period + 1)
    result = sum(values[:period]) / period

    for value in values[period:]:
        result = value * multiplier + result * (1 - multiplier)

    return result


def rsi(values: list[float], period: int = 14) -> float:
    if len(values) <= period:
        raise ValueError("Candles insuficientes para RSI")

    changes = [
        values[i] - values[i - 1]
        for i in range(len(values) - period, len(values))
    ]

    gains = [max(change, 0) for change in changes]
    losses = [max(-change, 0) for change in changes]

    average_gain = sum(gains) / period
    average_loss = sum(losses) / period

    if average_loss == 0:
        return 100.0

    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def generate_signal(
    candles: list[dict],
    min_score: int = 70,
) -> Signal | None:
    # São necessárias velas suficientes para os indicadores.
    if len(candles) < 25:
        return None

    candles = sorted(candles, key=lambda candle: int(candle["time"]))

    # Usa as 20 velas fechadas anteriores como referência.
    reference = candles[-21:-1]
    current = candles[-1]

    closes = [float(candle["close"]) for candle in candles]
    ema9 = ema(closes, 9)
    ema20 = ema(closes, 20)
    rsi14 = rsi(closes, 14)

    high20 = max(float(candle["high"]) for candle in reference)
    low20 = min(float(candle["low"]) for candle in reference)

    open_price = float(current["open"])
    close_price = float(current["close"])
    high = float(current["high"])
    low = float(current["low"])

    candle_range = max(high - low, 1e-12)
    body_ratio = abs(close_price - open_price) / candle_range
    upper_wick = high - max(open_price, close_price)
    lower_wick = min(open_price, close_price) - low

    buy_score = 0
    sell_score = 0
    buy_reasons = []
    sell_reasons = []

    if close_price > high20:
        buy_score += 25
        buy_reasons.append("Rompimento da máxima de referência")

    if close_price < low20:
        sell_score += 25
        sell_reasons.append("Rompimento da mínima de referência")

    if ema9 > ema20:
        buy_score += 20
        buy_reasons.append("EMA 9 acima da EMA 20")
    elif ema9 < ema20:
        sell_score += 20
        sell_reasons.append("EMA 9 abaixo da EMA 20")

    if 50 <= rsi14 <= 70:
        buy_score += 15
        buy_reasons.append("RSI favorável à compra")
    elif 30 <= rsi14 < 50:
        sell_score += 15
        sell_reasons.append("RSI favorável à venda")

    if close_price > open_price and body_ratio >= 0.55:
        buy_score += 15
        buy_reasons.append("Candle com força compradora")
    elif close_price < open_price and body_ratio >= 0.55:
        sell_score += 15
        sell_reasons.append("Candle com força vendedora")

    if lower_wick > upper_wick * 1.5 and close_price > open_price:
        buy_score += 15
        buy_reasons.append("Rejeição de preço inferior")

    if upper_wick > lower_wick * 1.5 and close_price < open_price:
        sell_score += 15
        sell_reasons.append("Rejeição de preço superior")

    if buy_score >= min_score and buy_score > sell_score:
        return Signal("BUY", min(99, buy_score), buy_reasons)

    if sell_score >= min_score and sell_score > buy_score:
        return Signal("SELL", min(99, sell_score), sell_reasons)

    return None
