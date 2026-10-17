"""Synthetic sanity tests only: these fixtures contain no NQ market observations."""

from dataclasses import replace
from datetime import timedelta
from pathlib import Path
import json
import tempfile
import unittest

from zone_validation import (Bar, Config, Market, Zone, analyze, bootstrap_difference,
                             instant, main, match_controls, read_bars, read_zones)


T0 = instant("2026-01-05T14:30:00Z")
BASE = Config(controls=2, horizon=2, spread_points=0, slippage_points=0, bootstrap=100)


def zone(**kwargs):
    return replace(Zone("z", T0, T0 + timedelta(minutes=7), "2026-01-05", "synthetic",
                        110, 1, 10, 100, "NQH26"), **kwargs)


def bar(minute, low=99, high=101, opening=100, close=100, contract="NQH26"):
    return Bar(T0 + timedelta(minutes=minute), opening, high, low, close, 1, contract)


class EventTests(unittest.TestCase):
    def test_creation_candle_ignored_and_first_future_touch_only(self):
        bars = [bar(i) for i in range(7)]
        bars[0] = bar(0, high=111)
        bars[2] = bar(2, high=110)
        bars[3] = bar(3, low=99, high=110, opening=109, close=105)
        event = Market(bars).evaluate(zone(), BASE)
        self.assertEqual(event["touch_time"], bars[2].timestamp.isoformat())
        self.assertEqual(event["entry_time"], bars[3].timestamp.isoformat())
        self.assertEqual(event["result"], "success")
        self.assertEqual(event["favorable_barrier"], 104)

    def test_fractional_creation_skips_partial_candle(self):
        bars = [bar(i) for i in range(7)]
        bars[0] = bar(0, high=111)
        event = Market(bars).evaluate(zone(created_at=T0 + timedelta(seconds=30)), BASE)
        self.assertFalse(event["touched"])

    def test_two_barriers_on_same_bar_is_distinct_and_pessimistic(self):
        bars = [bar(i) for i in range(7)]
        bars[1] = bar(1, high=110)
        bars[2] = bar(2, low=103, high=115, opening=109, close=109)
        report = analyze(bars, [zone()], BASE)
        event = report["events"][0]
        self.assertEqual(event["result"], "ambiguous")
        self.assertEqual(report["all_targets"]["conditional_reaction_rate"], 0)

    def test_expiry_is_exclusive_and_does_not_extend_horizon(self):
        bars = [bar(i) for i in range(8)]
        bars[4] = bar(4, high=110)
        bars[5] = bar(5, low=90, high=110, opening=109, close=100)
        event = Market(bars).evaluate(zone(valid_until=T0 + timedelta(minutes=6)), BASE)
        self.assertEqual(event["result"], "censored_expiry")
        self.assertTrue(event["touched"])
        bars[4] = bar(4)
        bars[5] = bar(5)
        bars[6] = bar(6, high=110)
        event = Market(bars).evaluate(zone(valid_until=T0 + timedelta(minutes=6)), BASE)
        self.assertFalse(event["touched"])

    def test_missing_minutes_and_other_contracts_are_not_no_touch(self):
        bars = [bar(i) for i in range(7) if i != 3]
        bars.append(bar(3, high=110, contract="NQM26"))
        event = Market(bars).evaluate(zone(), BASE)
        self.assertIsNone(event["touched"])
        self.assertEqual(event["result"], "missing_window_data")

    def test_costs_shift_both_barriers_and_can_change_outcome(self):
        bars = [bar(i) for i in range(7)]
        bars[1] = bar(1, high=110)
        bars[2] = bar(2, low=104, high=110, opening=109, close=109)
        bars[3] = bar(3, low=108, high=110, opening=109, close=109)
        free = Market(bars).evaluate(zone(), BASE)
        paid = Market(bars).evaluate(zone(), replace(BASE, spread_points=1, slippage_points=.5))
        self.assertEqual(free["result"], "success")
        self.assertEqual(paid["result"], "timeout")
        self.assertEqual(paid["favorable_barrier"], 102)
        self.assertEqual(paid["adverse_barrier"], 112)

    def test_opening_gap_establishes_order_before_dual_barrier_range(self):
        bars = [bar(i) for i in range(7)]
        bars[1] = bar(1, high=110)
        bars[2] = bar(2, low=108, high=110, opening=109, close=109)
        bars[3] = bar(3, low=100, high=115, opening=103, close=110)
        self.assertEqual(Market(bars).evaluate(zone(), BASE)["result"], "success")
        bars[3] = bar(3, low=103, high=116, opening=115, close=110)
        self.assertEqual(Market(bars).evaluate(zone(), BASE)["result"], "adverse")

    def test_adverse_move_is_checked_and_direction_fixed_at_creation(self):
        bars = [bar(i) for i in range(7)]
        bars[1] = bar(1, high=110)
        bars[2] = bar(2, low=108, high=115, opening=109, close=109)
        event = Market(bars).evaluate(zone(), BASE)
        self.assertEqual(event["result"], "adverse")
        # Lower zones prescribe the opposite direction without looking at future returns.
        lower = zone(center=90)
        bars[1] = bar(1, low=90)
        bars[2] = bar(2, low=89, high=96, opening=91, close=91)
        event = Market(bars).evaluate(lower, BASE)
        self.assertEqual(event["result"], "success")

    def test_no_touch_and_censoring_denominators_are_separate(self):
        bars = [bar(i) for i in range(7)]
        report = analyze(bars, [zone()], BASE)
        self.assertEqual(report["all_targets"]["touch_rate"], 0)
        self.assertIsNone(report["all_targets"]["conditional_reaction_rate"])

    def test_future_bars_outside_zone_cannot_change_results(self):
        bars = [bar(i) for i in range(7)]
        before = analyze(bars, [zone()], BASE)
        after = analyze(bars + [bar(7, low=1, high=500)], [zone()], BASE)
        self.assertEqual(before, after)


class MatchingAndAggregationTests(unittest.TestCase):
    def test_controls_are_immutable_deterministic_and_geometrically_matched(self):
        original = zone()
        controls, attempts = match_controls(original, BASE)
        self.assertEqual((controls, attempts), match_controls(original, BASE))
        self.assertEqual(len(controls), BASE.controls)
        for control in controls:
            self.assertEqual(control.created_at, original.created_at)
            self.assertEqual(control.valid_until, original.valid_until)
            self.assertEqual(control.contract, original.contract)
            self.assertEqual(control.side, original.side)
            self.assertEqual(control.half_width, original.half_width)
            self.assertEqual(control.scale, original.scale)
            self.assertLessEqual(abs(abs(control.center - control.reference_price) - 10), 5)
            self.assertGreater(abs(control.center - original.center), 2)
        self.assertEqual(original.center, 110)

    def test_too_narrow_bin_is_unmatched_without_relaxation(self):
        config = replace(BASE, distance_bin=.1, attempts=5)
        report = analyze([bar(i) for i in range(7)], [zone()], config)
        self.assertEqual(report["matches"], [{"zone_id": "z", "complete": False,
                                            "controls_found": 0, "attempts": 5}])
        self.assertEqual(report["session_results"], [])
        self.assertEqual(len(report["events"]), 1)

    def test_bootstrap_resamples_sessions_deterministically(self):
        values = [-.5, 0, .5]
        first = bootstrap_difference(values, BASE, "family")
        self.assertEqual(first, bootstrap_difference(values, BASE, "family"))
        self.assertEqual(first["sessions"], 3)
        self.assertEqual(first["mean_session_difference"], 0)
        self.assertLessEqual(first["percentile_95_interval"][0], 0)
        self.assertGreaterEqual(first["percentile_95_interval"][1], 0)
        self.assertIsNone(bootstrap_difference([.5], BASE, "f")["percentile_95_interval"])

    def test_each_session_contributes_one_difference(self):
        second = T0 + timedelta(days=1)
        bars = [bar(i) for i in range(7)]
        bars += [replace(bar(i), timestamp=second + timedelta(minutes=i)) for i in range(7)]
        zones = [zone(), zone(zone_id="second", created_at=second,
                              valid_until=second + timedelta(minutes=7), session="2026-01-06")]
        report = analyze(bars, zones, BASE)
        stats = report["family_bootstrap"]["synthetic"]["touch_difference"]
        self.assertEqual(stats["sessions"], 2)
        self.assertEqual(stats["mean_session_difference"], 0)
        self.assertEqual(stats["percentile_95_interval"], [0, 0])


class InputTests(unittest.TestCase):
    def test_naive_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "UTC offset"):
            instant("2026-01-05T14:30:00")

    def test_bad_ohlc_duplicate_bar_and_nonminute_open_are_rejected(self):
        header = "timestamp,open,high,low,close,volume,contract\n"
        rows = ["2026-01-05T14:30:00Z,100,101,99,100,1,NQH26\n",
                "2026-01-05T14:30:00Z,100,99,98,100,1,NQH26\n",
                "2026-01-05T14:30:30Z,100,101,99,100,1,NQH26\n"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bars.csv"
            for content in (rows[0] * 2, rows[1], rows[2]):
                path.write_text(header + content)
                with self.assertRaises(ValueError):
                    read_bars(path)

    def test_zone_parser_requires_creation_reference_outside_zone(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "zones.csv"
            path.write_text("created_at,valid_until,session,family,center,half_width,scale,reference_price,contract\n"
                            "2026-01-05T14:30:00Z,2026-01-05T14:40:00Z,s,f,100,1,10,100,NQH26\n")
            with self.assertRaisesRegex(ValueError, "outside"):
                read_zones(path)

    def test_cli_produces_auditable_json_from_synthetic_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            bars_path = Path(tmp) / "bars.csv"
            zones_path = Path(tmp) / "zones.csv"
            report_path = Path(tmp) / "report.json"
            bars_path.write_text("timestamp,open,high,low,close,volume,contract\n" + "".join(
                f"{bar(i).timestamp.isoformat()},100,101,99,100,1,NQH26\n" for i in range(7)))
            zones_path.write_text("created_at,valid_until,session,family,center,half_width,scale,reference_price,contract\n"
                                  "2026-01-05T14:30:00Z,2026-01-05T14:37:00Z,s,synthetic,110,1,10,100,NQH26\n")
            exit_code = main(["--bars", str(bars_path), "--zones", str(zones_path),
                              "--output", str(report_path), "--spread-points", "0.25",
                              "--slippage-points", "0.25", "--bootstrap", "10"])
            self.assertEqual(exit_code, 0)
            report = json.loads(report_path.read_text())
            self.assertEqual(len(report["input_sha256"]["bars"]), 64)
            self.assertEqual(report["all_targets"]["touch_rate"], 0)


if __name__ == "__main__":
    unittest.main()
