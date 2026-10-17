# Offline zone validation

This optional Python 3.10+ tool uses only the standard library. It compares
pre-recorded zone families against local random-level controls. No market dataset
is included. Unit-test candles are invented fixtures for software checks only;
they are not a backtest, evidence of an edge, or a profitability result.

Run from the repository root:

```sh
python3 -m unittest discover -s validation -v
python3 validation/zone_validation.py \
  --bars /path/to/nq_minutes.csv --zones /path/to/zones.csv \
  --spread-points 0.25 --slippage-points 0.25 \
  --horizon 15 --favorable 0.5 --adverse 0.5 \
  --controls 5 --distance-bin 1 --bootstrap 2000 --seed 20261017 \
  --output /tmp/zone-study.json
```

The spread and slippage values above illustrate the syntax. Choose and register
appropriate assumptions before examining outcomes. Units are NQ index points,
not ticks or dollars. No package installation is required.

## Input contract

Minute CSV columns:

```csv
timestamp,open,high,low,close,volume,contract
```

Zone CSV columns:

```csv
zone_id,created_at,valid_until,session,family,center,half_width,scale,reference_price,contract
```

`zone_id` is optional; absent IDs use CSV row numbers. Other columns are required.
Every timestamp must be ISO 8601 with an offset, for example
`2026-01-05T14:30:00Z`. A minute timestamp denotes the candle **open** and must
align to a full minute. Duplicate contract/minute pairs, invalid OHLC values,
nonfinite values and negative volume are rejected. Contract identifiers match
exactly: `NQH26` and `NQM26` never share observations. Do not supply a continuous
back-adjusted series as though it were a single unadjusted contract.

For each zone:

- `created_at` is the first instant at which **all** zone inputs were actually
  available. Completed-bar values, confirmed pivots and event releases cannot be
  backdated to an earlier plotting location.
- `valid_until` is an exclusive, predetermined expiry. The entire interval of a
  candle must precede or end at expiry; a candle straddling expiry is excluded.
- `session` identifies one independent sampling cluster, normally one CME trading
  date with an explicitly documented timezone/session calendar upstream.
- `family` is a prespecified hypothesis label. Do not relabel families after
  inspecting results.
- `center`, positive `half_width`, positive `scale` and `reference_price` are
  frozen at creation and share price-point units. `reference_price` must be
  strictly outside the zone and must have been known at creation. `scale` can be
  a lagged volatility measure; its exact definition belongs in the study protocol.
- Use genuinely recorded, causal exports. The tool cannot certify the timestamp
  provenance of pasted zones, recover unpublished Pine historical object state,
  or detect an input computed with future information. A Pine chart screenshot or
  a retrospectively recomputed zone is not a causal event log.

Preserve exchange timestamp conventions, trade breaks, early closes, DST changes
and contract rolls in the upstream export. The tool does not infer calendars or
fill missing candles. Limit each validity window to contiguous minute data that
you intend to study. If any full minute in its risk window is absent, its touch
status is unknown (`missing_window_data`), not a no-touch observation.

## Fixed experiment

The creation candle is always excluded, even when creation is exactly on a minute
boundary. The first eligible candle opens at the next full minute. A touch means
its OHLC range overlaps the closed zone interval. Only the first such candle per
zone is used. Partial creation/expiry candles and all later touches are ignored.

Controls use only creation-time geometry. For each target, sample absolute
distance from the same reference price uniformly over

`target_distance ± 0.5 × distance_bin × scale`.

Retain the same side, half-width, scale, creation, expiry, family, session and
contract. Reject candidates containing the reference price or overlapping the
target interval, including a shared boundary. Never inspect future candles to
select a control. Prices are continuous; controls are not rounded to NQ ticks.
The null therefore concerns continuous geometric zones, not executable limit
orders. The bin matches distances approximately, not exactly.

Sampling stops after `attempts` candidate draws (default 1,000). If fewer than
`controls` candidates survive, mark the target unmatched and omit its incomplete
control set from paired statistics. Keep that target in the separate descriptive
`all_targets` total. Do not widen bins after seeing outcomes. Controls can overlap
one another and other zones, so individual observations are not independent.

For the reaction proxy, direction is fixed at creation: a zone above its
reference prescribes a downward reaction, and a zone below prescribes an upward
reaction. It is **not** selected from subsequent price motion. This definition
does not require the final candle before touch to approach from that side; gaps
and direction reversals remain in the sample. Stratify such cases upstream if
that is a different prespecified hypothesis.

Entry is the **next minute open after the touch candle**. This deliberate delay
avoids assuming that a touch and a later barrier occurred in an identifiable
order inside one OHLC candle. It measures a delayed reaction proxy, not the
maximum excursion from the exact intrabar touch price. The next `H` full candles,
starting with entry, must all finish before or at expiry. Otherwise the touch is
reported as `censored_expiry` and has no reaction score, even if a barrier could
have been observed during the shorter remaining window.

Let `s` be +1 for an upward reaction and −1 for a downward reaction, `E` the next
minute open, and `C = spread_points + 2 × slippage_points`. The net point movement
at a hypothetical liquidation price `P` is `s × (P − E) − C`. The favorable
barrier is reached when this is at least `favorable × scale`; the adverse barrier
when it is at most `−adverse × scale`. Thus the raw price barriers are:

```text
favorable: E + s × (favorable × scale + C)
adverse:   E + s × (C − adverse × scale)
```

`adverse × scale` must exceed `C`; otherwise that touched event is flagged
`invalid_cost_scale` and excluded from reaction scores. Costs are constant
assumptions, not reconstructed historical spreads. Fees, queue position, fill
probability, latency, tick rounding and limit-lock conditions are not modeled.

The first barrier observed wins. A candle opening beyond a barrier establishes
that crossing before later intrabar movement. If a candle opens between barriers
and then reaches both, its result is `ambiguous` and contributes **zero** successes. Adverse hits and no
barrier within `H` candles (`timeout`) also contribute zero. Gaps beyond a barrier
are classified using the opening price without estimating an exit fill price.
This tool reports barrier outcomes; it does not estimate trade P&L.

## Outputs and inference limits

The JSON report includes configuration, SHA-256 input fingerprints, every event,
matching diagnostics, per-session/family totals and session bootstrap intervals.
Preserve this report with the raw input files and the preregistered protocol.

Touch rate and conditional reaction rate have separate denominators:

```text
touch_rate = touched / zones with a fully observed risk window
conditional_reaction_rate = success / (success + adverse + ambiguous + timeout)
```

Censored/missing events stay visible in outcome counts. Reaction rates condition
on each population's own observed touches, so target and control cohorts can
differ. They do not identify a causal effect among identical touched events.

Only targets with complete matched sets enter `session_results`. Within each
session/family, calculate target rate minus pooled control rate. Each target has
the same requested number of controls. For each family, report the **equally
weighted mean of session differences**, not a pooled bar-level estimate. Resample
whole session differences with replacement using the deterministic seed to form
the 2.5/97.5 percentile interval. At least two sessions are required for an
interval; a two-session interval is still weak evidence. Repeated controls do
not increase the number of independent sessions.

These are exploratory intervals, without a null p-value, multiple-testing
correction, power guarantee or claim of statistical significance. Neighboring
sessions can remain dependent; week-block resampling, nested contract/regime
analysis and a chronological held-out period belong in a stronger study. Bins,
families, horizons, costs and all exclusions must be frozen before that period.
The CLI cannot replace data licensing checks, provenance review or manual audit
of a random sample of events.
