# Pine Script platform: live official verification

Verified by HTTPS GET against official TradingView pages on 2026-10-17. Every URL below returned HTTP 200. HTML was read locally; these are documentation checks, **not compilation or TradingView execution tests**.

## Version and new capabilities

- Official migration guide: https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
- Current release notes: https://www.tradingview.com/pine-script-docs/release-notes/
- The current manual and examples use `//@version=6`. Release notes contain September 2026 updates, so older statements that footprint data is unavailable in Pine are now obsolete.
- Release notes, January 2026: “We’ve added a new request.footprint() function and two new data types, footprint and volume_row.”
- Important v6 syntax rule: “The history-referencing operator [] can no longer be used directly on fields of user-defined types.” Use `(myObject[1]).field`, or assign the field to a scalar variable and then use `scalar[1]`.

## Requests, common 1-minute clock, and limitations

Official chapter: https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/

Verified statements:

1. Every unique `request.*()` request evaluates an expression over the requested symbol/timeframe dataset.
2. Signature:
   ```pine
   request.security_lower_tf(symbol, timeframe, expression, ignore_invalid_symbol, currency, ignore_invalid_timeframe, calc_bars_count) → array<type>
   ```
3. Exact passage: “This function requests data only from timeframes that are lower than or equal to the chart’s timeframe (timeframe.period).” Therefore, a request for `"1"` is documented as supported on each of 1m, 5m, 10m, 15m, 1h, and 4h. A separate security request for the equal-1m case is not required by this documentation. **Its actual equal-timeframe realtime behavior still needs a TradingView test.**
4. The arrays contain values “sorted in ascending order based on each intrabar’s timestamp.”
5. A tuple expression, including a function returning a tuple, produces a tuple of arrays. Example: `[open, high, low, close]` produces four arrays.
6. `request.security()` on a lower timeframe retrieves only a single intrabar per chart bar. It is unsuitable for preserving every minute’s sequential event history on a 4h chart.
7. `request.security_lower_tf()` accepts most requestable expression types, excluding **direct references to collections and mutable variables**. A user function with internal state and a scalar/tuple/UDT result is the appropriate expression form; actual syntax must still be compiled.
8. `request.security()` can return UDT IDs with fundamental fields, chart points, eligible collections, or eligible nested UDTs. The lower-timeframe chapter also demonstrates UDT results (`array<Prices>`); UDT wrappers permit collections to be returned, but the documentation calls the collection technique advanced and recommends simpler alternatives where possible.
9. A scalar-only snapshot UDT is a useful alternative to a very large tuple. Return a **new snapshot object** each source bar; do not return and repeatedly mutate the same object as historical records. Keep growing profile arrays internal to the source engine rather than returning a fresh large collection at every minute.
10. Empty arrays are possible outside the retrieved source coverage. Always guard `array.get`, `first`, and `last` with a size test. Missing minutes and source gaps are possible, so do not assume `chart_minutes` equals array size.
11. Minor retrospective changes remain possible even with `request.security_lower_tf()`: exact excerpt, “it’s still possible in some cases for minor repainting to occur due to data differences from the provider”. Documentation explains that historical and realtime feeds can differ, providers can revise data, and races can occur between feeds.
12. `barmerge.lookahead_on` with an unoffset lower-timeframe `request.security` expression does not solve this. On history it can select a first intrabar, while realtime selection differs.

### Recommended architecture (engineering inference, not a tested TradingView result)

- One source engine operates entirely in a fixed 1-minute context; use the same exchange symbol/session settings and timezone inputs on every chart.
- Within that engine, update session VWAP, profile histograms, minute-based ranges, proxy volume flow, readiness, and event state. Derive time periods from source timestamps, **never from the display chart bar count**. Source readiness must be based on complete source sessions and coverage checks.
- Request a scalar-only snapshot UDT or modest tuple using one `request.security_lower_tf` call with `"1"` and an explicit conservative `calc_bars_count = 100000`.
- Include each minute’s source-open timestamp, source-close timestamp, sequence/session identifier, readiness flags, and event timestamp in its snapshot.
- On every chart execution, inspect the returned snapshots in chronological order. Only consume a source snapshot whose source close is no later than the actual execution clock. Preserve the last known completed snapshot if the current array contains no completed minute. Do not use `barstate.isconfirmed` inside `request.security` to establish source confirmation (see below).
- Display the latest completed snapshot; record all relevant events, not only the last array element. Historical 4h bars contain many source observations; attach event drawings to **source timestamps** with `xloc.bar_time`.
- Reset bounded state on source session boundaries, reject the first incomplete source session, and flag unavailable prior profiles. Across charts, equality can only be promised for the same completed source timestamp after the **same complete warmup and available underlying data**. Different plan/history coverage can affect initial conditions.
- Display-chart plots have one value per display bar. Identical source-clock values do not imply identical-looking line sampling across chart timeframes, nor that a complete historical 4h bar’s contents were all known at its opening.
- Do not claim absolute freedom from provider revisions or exchange data corrections.

## Footprints, volume delta, and unsupported data assumptions

Official request documentation:
https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/

Official type documentation:
https://www.tradingview.com/pine-script-docs/language/type-system/

Verified `request.footprint()` capabilities:

- Signature: `request.footprint(ticks_per_row, va_percent, imbalance_percent) → series footprint`.
- Provides footprint rows, total/buy/sell volume, delta, POC, VAH, VAL, and diagonal imbalance checks.
- “Volume footprints are available exclusively to users who have a Premium or Ultimate plan.” Lower-tier accounts cannot use scripts that request them.
- At most one unique footprint request. A `request.security()`/`lower_tf` expression dependent on footprint data counts toward the unique-footprint limit. Adding a chart-local footprint call and a separately requested footprint context can raise a runtime error.
- Data can be `na` even with a permitted subscription.
- Crucial meaning: the official description says footprints categorize lower-timeframe volume as buy/upward or sell/downward **based on intrabar price action**. These labels must not be represented as authenticated exchange aggressor-side trades or a complete Level 2 order book.
- For a broadly compatible deliverable, use an explicitly labelled 1m price-direction volume proxy by default. A separate footprint edition is possible for eligible users; do not include an unsupported hidden footprint request in a general-plan script.

Official Volume Delta description (canonical article ID; the arbitrary slug does not select its identity):
https://www.tradingview.com/support/solutions/43000725057/

Exact important description: “The Volume Delta indicator uses intrabar volume and price fluctuations to estimate the difference (delta) between buying and selling pressure within each chart bar”. It classifies close > open as positive, close < open as negative; for a doji it compares with the prior intrabar close; when both are equal it preserves the prior sign. A 1m implementation of this rule is a **directional-volume proxy**, not an exact replica of native subminute delta.

No documented `request.*()` API in the current manual provides a full options chain, dealer positioning inventory, or account-level gamma exposure. Option symbols, manually supplied levels, externally calculated reference values, and futures-derived proxies are different data products. Do not imply an automatically fetched full options chain, measured dealer gamma/GEX, true bid/ask aggressor delta, or Level 2 DOM without an actual supported data source.

## Confirmation, rollback, and alerts

Official bar states:
https://www.tradingview.com/pine-script-docs/concepts/bar-states/

- `barstate.isconfirmed` is true on every historical bar and on the final closing update of a realtime chart bar.
- Exact warning: “barstate.isconfirmed will not work when used in a request.security() call.” Do not confuse parent-chart confirmation with confirmation of a requested 1m source.

Official execution model:
https://www.tradingview.com/pine-script-docs/language/execution-model/

- Indicators recalculate with realtime updates; rollback resets ordinary state to its previous committed bar state before each new update.
- `varip` can retain state between realtime ticks; that also means intrabar behavior is not historically reconstructible after reload unless restricted to deduplicating already closed source timestamps.
- A realtime parent-bar scan can be redone from the parent bar’s committed initial state using the ordered completed-minute array. For event alerts, a small `varip` last-alert source timestamp can suppress duplicate alerts within the open parent bar, but should never be used to manufacture unreplayable signal calculations.

Official alerts:
https://www.tradingview.com/pine-script-docs/concepts/alerts/

- “Alerts only trigger in the realtime bar.” No historical backfill of alert notifications.
- A script supplies alert events; the user must create the running alert in the TradingView UI.
- The alert server stores a snapshot of the script, inputs, symbol, and chart timeframe. Changes require recreating the alert.
- `alert.freq_once_per_bar_close` means the **chart bar** closing update. It would delay a minute-source alert until the display bar’s close, potentially 4h. That should not be marketed as timeframe-independent realtime timing.
- For minute-close source events on a higher chart timeframe: inspect closed source snapshots, use `alert.freq_all` and source-timestamp deduplication, and explicitly test availability/timing in TradingView. TradingView cannot emit anything without a market update; exact wall-clock delivery is not guaranteed.
- If loading a script halfway through a 4h bar, choose and document a freshness rule so it does not alert for every older event inside that open bar. Alert notification traffic is not the signal history.

## Budgets to respect

Official limitations:
https://www.tradingview.com/pine-script-docs/writing/limitations/

- 40 unique `request.*()` calls ordinarily; 64 for Ultimate. Identical repeated requests normally reuse an existing request.
- All non-professional plans (Basic, Essential, Plus, Premium): up to 100,000 LTF bars; Expert: 125,000; Ultimate: 200,000. Explicit `calc_bars_count` controls requested history, within plan/dataset limits. It does not make inaccessible history available.
- Lower timeframe chart coverage depends on actual minute counts. A 100,000-minute budget covers approximately 416 full 4h bars in a nonstop market, and more parent bars when source minutes are missing.
- All tuple results across all `request.*()` calls together: at most 127 elements. UDT fields provide the documented alternative when larger structured snapshots are necessary.
- Up to 64 plot counts. `alertcondition`, series colors and some multi-series plots can consume extra counts.
- Maximum IDs: 500 lines, 500 boxes, 500 labels, 100 polylines. Existing IDs count even if coordinates are `na`. Reuse/delete objects instead of creating unbounded objects.
- Each loop is capped at 500 ms per bar; total script execution is capped at 20 s for Basic and 40 s for other plans.
- Each collection has a maximum of 100,000 elements.
- Use fixed-size histograms, bounded event history, bounded object pools, and avoid scanning thousands of bins every source minute. Performance and object budgets must be tested in TradingView on the longest target timeframe.

## Validation boundaries

This environment has no TradingView Pine compiler or live paid TradingView feed. Official-document checks and local mirror tests can validate definitions, boundedness, chronological replay, and deterministic aggregation. They cannot prove that the Pine file compiles, fits TradingView runtime limits, has equal 1m request realtime behavior, or emits alerts at the intended time. Keep compilation, runtime, data entitlement, and six-timeframe timestamp comparisons as explicit remaining acceptance checks in TradingView.

## Continuous futures: adjustment and rollover (additional official reference check)

Official reference URLs:

- https://www.tradingview.com/pine-script-reference/v6/#fun_ticker.modify
- https://www.tradingview.com/pine-script-reference/v6/#fun_ticker.new
- https://www.tradingview.com/pine-script-reference/v6/#var_syminfo.current_contract

The reference page is dynamically rendered. Its current official reference payload was fetched successfully from the TradingView static origin, as loaded by that page:
https://static.tradingview.com/static/bundles/11967.3c92723cdb229aeaa95a.js

The payload declares exactly:
```text
name:"syminfo.current_contract",type:"simple string"
```
Its official English definition is: “The ticker identifier of the underlying contract, if the current symbol is a continuous futures contract; na otherwise.”

**Critical implication:** `syminfo.current_contract` is a **simple** value, not a historical `series string`. It is not a documented source of per-bar historical contract identifiers. Comparing this value to its history in a continuous NQ1! source engine does not reliably detect historical rollover. It can identify/display the current underlying contract. Do not claim automatic exact historical rollover detection from this variable.

Supported named options:
```pine
sourceTicker = ticker.modify(syminfo.tickerid,
     backadjustment = backadjustment.off,
     settlement_as_close = settlement_as_close.off)
```

- `backadjustment`: `.on`, `.off`, `.inherit`; controls backadjustment of past contract data for eligible continuous futures.
- `settlement_as_close`: `.on`, `.off`, `.inherit`; actual close versus settlement **only on 1D and higher** data. It has no minute-close settlement effect.
- Explicit `.off` fixes a reproducible source policy but does not remove contract rollover gaps.
- With unadjusted NQ1!, prior-session price references can straddle different contracts. Recommended exact handling is dated contract symbols plus an explicit roll/reset policy, or user-provided historical roll/reset timestamps. Gap-based detection may be a conservative heuristic; ordinary overnight gaps and roll gaps are not uniquely distinguishable from OHLCV alone. Mark such a detector and its false-positive/false-negative limitations explicitly.
- Continuous-series backadjustment can change historical price levels after rollover; values previously displayed can therefore change after reload even when signal code itself is causal.

### Returning an offset source snapshot

The current official `request.security_lower_tf` reference explicitly accepts “a function call that does not use Pine Script® drawings, an object, or a tuple of expressions.” Collections are permitted only inside object fields. The manual gives an `array<Prices>` result example, so returning `array<SourceSnapshot>` with fundamental scalar fields is a documented pattern.

A one-minute causal lag can be constructed by first calculating every scalar series in the source engine and constructing `SourceSnapshot.new(sourceTime[1], sourceCloseTime[1], scalar1[1], ...)`. A prior snapshot object may alternatively be referenced as `snapshot[1]`, guarding `na` before reading its fields. Do **not** write `snapshot.field[1]` in v6. If deliberate offsetting is used, carry the lagged source timestamp with all the lagged values and document actual delivery latency. Whether the equal-timeframe lower_tf call provides the forming 1m object or only a closed one in realtime remains a specific runtime acceptance test, so do not promise tick-exact arrival from documentation alone.

### Selected safe policy for present-day continuous-chart use

If the chart is continuous and `syminfo.current_contract` is available, using that **simple ticker identifier as a fixed requested source symbol** is consistent with the documented `request.*` symbol contract. It requests the current dated contract's own price/volume history rather than concatenating old front contracts. `ticker.modify` can apply an explicit source session and adjustment policy. Keep a user override for an explicit dated contract identifier, and fall back conservatively if metadata is unavailable.

This solves a present-day reference-mixing problem, with these boundaries:

- It intentionally does **not** recreate the then-front contract across old continuous-chart history. In historical replay crossing an old roll, the user must supply the dated contract appropriate to that replay interval.
- Latest-zone display avoids plotting current-contract historical prices as though they were the continuous chart's then-front historical levels.
- A fixed current dated contract can have sparse volume earlier in its life. Twenty session boundaries are not alone proof of twenty liquid, complete source sessions. Validate minute coverage and positive volume; report missing/thin source history.
- Source contract or input changes require TradingView alert recreation. Automatic exact live alert rollover handling must not be claimed without runtime testing.
