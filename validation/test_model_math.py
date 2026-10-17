"""Independent numerical checks; no Pine execution or market backtest."""

import math
import random
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo


class ModelMathTests(unittest.TestCase):
    def test_range_estimators_on_valid_ohlc(self):
        rng = random.Random(20261017)
        for _ in range(10000):
            opening = rng.uniform(100, 30000)
            closing = opening * math.exp(rng.uniform(-0.1, 0.1))
            high = max(opening, closing) * math.exp(rng.uniform(0, 0.1))
            low = min(opening, closing) * math.exp(-rng.uniform(0, 0.1))
            h, l, c = (math.log(p / opening) for p in (high, low, closing))
            rs = h * (h - c) + l * (l - c)
            rs_ratios = math.log(high / opening) * math.log(high / closing)
            rs_ratios += math.log(low / opening) * math.log(low / closing)
            self.assertGreaterEqual(rs, -1e-14)
            self.assertAlmostEqual(rs, rs_ratios, places=13)
            self.assertAlmostEqual(
                (h - l) ** 2 / (4 * math.log(2)),
                math.log(high / low) ** 2 / (4 * math.log(2)),
                places=13,
            )

    def test_finite_variance_window_forgets_initial_history(self):
        rng = random.Random(32)
        observations = [rng.random() / 1000 for _ in range(120)]
        window = 20
        values = []
        for start in (0, 10, 65, 100):
            retained = observations[start:][-window:]
            values.append(math.sqrt(sum(retained) / len(retained)))
        self.assertTrue(all(value == values[0] for value in values))

    def test_efficiency_is_bounded_including_first_minute(self):
        rng = random.Random(128)
        for _ in range(200):
            opening = 20000
            closes = [opening]
            for _ in range(390):
                closes.append(closes[-1] + rng.uniform(-20, 20))
            path = sum(abs(b - a) for a, b in zip(closes, closes[1:]))
            efficiency = abs(closes[-1] - opening) / path
            self.assertGreaterEqual(efficiency, 0)
            self.assertLessEqual(efficiency, 1)

    def test_new_york_paris_dst_mismatch(self):
        ny, paris = ZoneInfo("America/New_York"), ZoneInfo("Europe/Paris")
        cases = [
            ((2026, 3, 13, 9, 30), "14:30"),
            ((2026, 3, 30, 9, 30), "15:30"),
            ((2026, 10, 23, 9, 30), "15:30"),
            ((2026, 10, 29, 8, 30), "13:30"),
            ((2026, 11, 6, 8, 30), "14:30"),
        ]
        for components, expected in cases:
            self.assertEqual(datetime(*components, tzinfo=ny).astimezone(paris).strftime("%H:%M"), expected)

    def test_tick_envelope_contains_original_reference(self):
        rng = random.Random(16)
        tick = 0.25
        for _ in range(10000):
            price, sigma = rng.uniform(10000, 30000), rng.uniform(2, 700)
            center = math.floor(price / tick + 0.5) * tick
            width = max(tick, 0.015 * sigma)
            lower = math.floor((center - width) / tick) * tick
            upper = math.ceil((center + width) / tick) * tick
            self.assertLessEqual(lower, price)
            self.assertGreaterEqual(upper, price)
            self.assertEqual(lower % tick, 0)
            self.assertEqual(upper % tick, 0)

    def test_synchronized_cross_product_mapping(self):
        nq, ndx, qqq = 25010, 25000, 610
        ratio, basis = ndx / qqq, nq - ndx
        self.assertAlmostEqual(qqq * ratio + basis, nq)
        self.assertAlmostEqual(ndx + basis, nq)


if __name__ == "__main__":
    unittest.main()
