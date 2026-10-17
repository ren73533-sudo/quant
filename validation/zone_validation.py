#!/usr/bin/env python3
"""Offline, stdlib-only first-touch study. Does not simulate a trading strategy."""

from __future__ import annotations

import argparse
import bisect
import csv
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys
from typing import Iterable


MINUTE = timedelta(minutes=1)
SCORED = {"success", "adverse", "ambiguous", "timeout"}


def instant(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("timestamps must include a UTC offset or Z")
    return result.astimezone(timezone.utc)


def finite(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("numeric fields must be finite")
    return result


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    contract: str


@dataclass(frozen=True)
class Zone:
    zone_id: str
    created_at: datetime
    valid_until: datetime
    session: str
    family: str
    center: float
    half_width: float
    scale: float
    reference_price: float
    contract: str

    @property
    def side(self) -> int:
        return 1 if self.center > self.reference_price else -1


@dataclass(frozen=True)
class Config:
    controls: int = 5
    distance_bin: float = 1.0
    attempts: int = 1000
    horizon: int = 15
    favorable: float = 0.5
    adverse: float = 0.5
    spread_points: float = 0.25
    slippage_points: float = 0.25
    bootstrap: int = 2000
    seed: int = 20261017

    @property
    def round_trip_cost(self) -> float:
        return self.spread_points + 2 * self.slippage_points

    def validate(self) -> None:
        if self.controls < 1 or self.attempts < 1 or self.horizon < 1:
            raise ValueError("controls, attempts and horizon must be positive integers")
        if self.bootstrap < 1:
            raise ValueError("bootstrap replicates must be positive")
        for field in ("distance_bin", "favorable", "adverse"):
            if not math.isfinite(getattr(self, field)) or getattr(self, field) <= 0:
                raise ValueError(f"{field} must be finite and positive")
        for field in ("spread_points", "slippage_points"):
            if not math.isfinite(getattr(self, field)) or getattr(self, field) < 0:
                raise ValueError(f"{field} must be finite and nonnegative")


def read_bars(path: Path) -> list[Bar]:
    result = []
    seen = set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        require_columns(reader, {"timestamp", "open", "high", "low", "close", "volume", "contract"})
        for line, row in enumerate(reader, 2):
            try:
                bar = Bar(instant(row["timestamp"]), *(finite(row[k]) for k in
                          ("open", "high", "low", "close", "volume")), row["contract"].strip())
                if bar.timestamp.second or bar.timestamp.microsecond:
                    raise ValueError("bar timestamps must be minute opens, aligned to a full minute")
                if not bar.contract or bar.volume < 0 or not (
                    bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high
                ):
                    raise ValueError("invalid contract, volume or OHLC ordering")
                key = (bar.contract, bar.timestamp)
                if key in seen:
                    raise ValueError("duplicate contract and minute")
                seen.add(key)
                result.append(bar)
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                raise ValueError(f"{path}:{line}: {exc}") from exc
    return sorted(result, key=lambda b: (b.contract, b.timestamp))


def require_columns(reader: csv.DictReader, columns: set[str]) -> None:
    missing = columns - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")


def read_zones(path: Path) -> list[Zone]:
    result = []
    seen = set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        require_columns(reader, {"created_at", "valid_until", "session", "family", "center",
                                 "half_width", "scale", "reference_price", "contract"})
        for line, row in enumerate(reader, 2):
            try:
                zone = Zone(row.get("zone_id", "").strip() or f"row-{line}",
                            instant(row["created_at"]), instant(row["valid_until"]),
                            row["session"].strip(), row["family"].strip(),
                            *(finite(row[k]) for k in
                              ("center", "half_width", "scale", "reference_price")),
                            row["contract"].strip())
                validate_zone(zone)
                if zone.zone_id in seen:
                    raise ValueError("duplicate zone_id")
                seen.add(zone.zone_id)
                result.append(zone)
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                raise ValueError(f"{path}:{line}: {exc}") from exc
    return result


def validate_zone(zone: Zone) -> None:
    if not zone.zone_id or not zone.session or not zone.family or not zone.contract:
        raise ValueError("zone_id, session, family and contract must be nonempty")
    if zone.valid_until <= zone.created_at:
        raise ValueError("valid_until must be later than created_at")
    if zone.half_width <= 0 or zone.scale <= 0:
        raise ValueError("half_width and scale must be positive")
    if abs(zone.center - zone.reference_price) <= zone.half_width:
        raise ValueError("reference_price must be strictly outside the zone at creation")


def seeded(seed: int, label: str) -> random.Random:
    digest = hashlib.sha256(f"{seed}|{label}".encode()).digest()
    return random.Random(int.from_bytes(digest, "big"))


def match_controls(zone: Zone, config: Config) -> tuple[list[Zone], int]:
    """Use creation-time geometry only; never inspect bars or reaction outcomes."""
    rng = seeded(config.seed, json.dumps(asdict(zone), default=str, sort_keys=True))
    distance = abs(zone.center - zone.reference_price)
    radius = 0.5 * config.distance_bin * zone.scale
    controls = []
    used = set()
    for attempt in range(1, config.attempts + 1):
        candidate_distance = distance + rng.uniform(-radius, radius)
        if candidate_distance <= zone.half_width:
            continue
        center = zone.reference_price + zone.side * candidate_distance
        # Reject boundary overlap too: touching intervals are not independent levels.
        if abs(center - zone.center) <= 2 * zone.half_width or center in used:
            continue
        used.add(center)
        controls.append(replace(zone, zone_id=f"{zone.zone_id}/control-{len(controls) + 1}",
                                center=center))
        if len(controls) == config.controls:
            return controls, attempt
    return controls, config.attempts


class Market:
    def __init__(self, bars: Iterable[Bar]):
        self.bars: dict[str, list[Bar]] = {}
        for bar in bars:
            self.bars.setdefault(bar.contract, []).append(bar)
        for contract in self.bars:
            self.bars[contract].sort(key=lambda bar: bar.timestamp)
            timestamps = [bar.timestamp for bar in self.bars[contract]]
            if len(set(timestamps)) != len(timestamps):
                raise ValueError("duplicate contract and minute")
        self.times = {key: [b.timestamp for b in value] for key, value in self.bars.items()}

    def evaluate(self, zone: Zone, config: Config) -> dict:
        # Creation belongs to its current candle even when it is exactly minute-aligned.
        start = zone.created_at.replace(second=0, microsecond=0) + MINUTE
        count = int((zone.valid_until - start).total_seconds() // 60)
        result = {"zone_id": zone.zone_id, "session": zone.session, "family": zone.family,
                  "contract": zone.contract, "center": zone.center,
                  "created_at": zone.created_at.isoformat(),
                  "valid_until": zone.valid_until.isoformat(),
                  "reference_price": zone.reference_price, "half_width": zone.half_width,
                  "scale": zone.scale, "side_at_creation": "above" if zone.side > 0 else "below",
                  "touched": None, "touch_time": None, "entry_time": None,
                  "entry_open": None, "favorable_barrier": None, "adverse_barrier": None,
                  "result": "empty_window"}
        if count <= 0:
            return result
        times = self.times.get(zone.contract, [])
        lo = bisect.bisect_left(times, start)
        hi = bisect.bisect_left(times, start + count * MINUTE)
        window = self.bars.get(zone.contract, [])[lo:hi]
        if len(window) != count:
            result["result"] = "missing_window_data"
            return result
        # Minute alignment plus uniqueness and count prove the entire window is present.
        touch = next((i for i, b in enumerate(window) if
                      b.low <= zone.center + zone.half_width and
                      b.high >= zone.center - zone.half_width), None)
        result["touched"] = touch is not None
        if touch is None:
            result["result"] = "no_touch"
            return result
        result["touch_time"] = window[touch].timestamp.isoformat()
        entry = touch + 1  # Touch-bar sequencing is unknown; enter at the next minute open.
        if entry + config.horizon > len(window):
            result["result"] = "censored_expiry"
            return result
        direction = -zone.side  # Fixed at creation; never choose direction after the event.
        entry_open = window[entry].open
        cost = config.round_trip_cost
        if config.adverse * zone.scale <= cost:
            result["result"] = "invalid_cost_scale"
            return result
        favorable = entry_open + direction * (config.favorable * zone.scale + cost)
        adverse = entry_open + direction * (cost - config.adverse * zone.scale)
        result.update(entry_time=window[entry].timestamp.isoformat(), entry_open=entry_open,
                      favorable_barrier=favorable, adverse_barrier=adverse, result="timeout")
        # All H full candles must exist before any outcome is scored. Expiry never extends.
        for bar in window[entry:entry + config.horizon]:
            favorable_at_open = bar.open >= favorable if direction > 0 else bar.open <= favorable
            adverse_at_open = bar.open <= adverse if direction > 0 else bar.open >= adverse
            favorable_hit = bar.high >= favorable if direction > 0 else bar.low <= favorable
            adverse_hit = bar.low <= adverse if direction > 0 else bar.high >= adverse
            # A gap can establish the first observed crossing before later intrabar movement.
            if favorable_at_open:
                result["result"] = "success"
            elif adverse_at_open:
                result["result"] = "adverse"
            elif favorable_hit and adverse_hit:
                result["result"] = "ambiguous"
            elif adverse_hit:
                result["result"] = "adverse"
            elif favorable_hit:
                result["result"] = "success"
            else:
                continue
            break
        return result


def describe(events: list[dict]) -> dict:
    known = [e for e in events if e["touched"] is not None]
    scored = [e for e in events if e["result"] in SCORED]
    counts = {key: sum(e["result"] == key for e in events)
              for key in sorted({e["result"] for e in events})}
    touches = sum(e["touched"] is True for e in known)
    successes = sum(e["result"] == "success" for e in scored)
    return {"zones": len(events), "touch_denominator": len(known), "touches": touches,
            "touch_rate": touches / len(known) if known else None,
            "reaction_denominator": len(scored), "successes": successes,
            "conditional_reaction_rate": successes / len(scored) if scored else None,
            "outcome_counts": counts}


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lo = math.floor(position)
    hi = math.ceil(position)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


def bootstrap_difference(values: list[float], config: Config, label: str) -> dict:
    result = {"sessions": len(values), "mean_session_difference":
              statistics.fmean(values) if values else None, "percentile_95_interval": None}
    if len(values) >= 2:
        rng = seeded(config.seed, label)
        means = [statistics.fmean(rng.choices(values, k=len(values)))
                 for _ in range(config.bootstrap)]
        result["percentile_95_interval"] = [percentile(means, .025), percentile(means, .975)]
    return result


def analyze(bars: list[Bar], zones: list[Zone], config: Config) -> dict:
    config.validate()
    market = Market(bars)
    events = []
    matches = []
    groups: dict[tuple[str, str], dict[str, list[dict]]] = {}
    for zone in zones:
        validate_zone(zone)
        target = market.evaluate(zone, config)
        target.update(kind="target", target_id=zone.zone_id)
        events.append(target)
        candidates, attempts = match_controls(zone, config)
        complete = len(candidates) == config.controls
        matches.append({"zone_id": zone.zone_id, "complete": complete,
                        "controls_found": len(candidates), "attempts": attempts})
        # Incomplete sets are reported but excluded from paired comparison, without relaxing bins.
        if not complete:
            continue
        controls = []
        for candidate in candidates:
            event = market.evaluate(candidate, config)
            event.update(kind="control", target_id=zone.zone_id)
            controls.append(event)
            events.append(event)
        group = groups.setdefault((zone.family, zone.session), {"targets": [], "controls": []})
        group["targets"].append(target)
        group["controls"].extend(controls)
    session_results = []
    for (family, session), group in sorted(groups.items()):
        target = describe(group["targets"])
        control = describe(group["controls"])
        row = {"family": family, "session": session, "targets": target, "controls": control}
        for name, field in (("touch_difference", "touch_rate"),
                            ("conditional_reaction_difference", "conditional_reaction_rate")):
            row[name] = (target[field] - control[field]
                         if target[field] is not None and control[field] is not None else None)
        session_results.append(row)
    families = {}
    for family in sorted({zone.family for zone in zones}):
        rows = [row for row in session_results if row["family"] == family]
        families[family] = {
            field: bootstrap_difference([row[field] for row in rows if row[field] is not None],
                                        config, f"{family}|{field}")
            for field in ("touch_difference", "conditional_reaction_difference")}
    return {"schema_version": 1, "config": asdict(config),
            "interpretation": "Exploratory first-touch geometry study; no trading P&L or significance claim.",
            "all_targets": describe([e for e in events if e["kind"] == "target"]),
            "matched_controls": describe([e for e in events if e["kind"] == "control"]),
            "matches": matches, "session_results": session_results,
            "family_bootstrap": families, "events": events}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bars", type=Path, required=True)
    parser.add_argument("--zones", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--controls", type=int, default=5)
    parser.add_argument("--distance-bin", type=float, default=1.0)
    parser.add_argument("--attempts", type=int, default=1000)
    parser.add_argument("--horizon", type=int, default=15)
    parser.add_argument("--favorable", type=float, default=0.5)
    parser.add_argument("--adverse", type=float, default=0.5)
    parser.add_argument("--spread-points", type=float, required=True,
                        help="full bid/ask spread in index points; choose explicitly")
    parser.add_argument("--slippage-points", type=float, required=True,
                        help="slippage per side in index points; choose explicitly")
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261017)
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.resolve() in {args.bars.resolve(), args.zones.resolve()}:
            raise ValueError("output must not overwrite either input CSV")
        config = Config(**{key: getattr(args, key) for key in Config.__dataclass_fields__})
        report = analyze(read_bars(args.bars), read_zones(args.zones), config)
        report["input_sha256"] = {"bars": hashlib.sha256(args.bars.read_bytes()).hexdigest(),
                                  "zones": hashlib.sha256(args.zones.read_bytes()).hexdigest()}
        payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
