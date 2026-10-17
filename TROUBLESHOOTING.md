# Replay and price-scale troubleshooting

## Zones appear to float when zooming

The zones use numerical price coordinates. Boxes and lines use timestamp coordinates horizontally (`xloc.bar_time`). Only the information table is attached to a screen corner.

If a zone's printed price remains the same but its position moves away from that price on the candle scale:

1. Open the indicator title's **⋯** menu.
2. Choose **Pin to scale** and select the **existing scale used by the NQ candles**, usually the right-hand price scale. Do not create a new scale for this indicator.
3. Add a normal TradingView horizontal line at the zone's printed center. Zoom vertically. Their center prices should remain aligned. This is a display check, not a trading test.
4. If the indicator instance still uses an old scale assignment, remove it and add it again from the updated Pine script. Do not just add a duplicate instance.

The declaration explicitly uses `overlay = true, scale = scale.none`, which uses the chart scale. TradingView already documents this as the default for overlays, so the explicit argument is a safeguard and **not proof of a repaired calculation bug**. User interface scale assignments and actual behavior must be checked on the chart. Setting `scale.right` or `scale.left` in this overlay would create a separate scale.

If only the horizontal length changes when zooming, that is expected: the default drawing span is **120 minutes**, not a fixed number of pixels. The right label offset is also measured in minutes. The current script displays the latest map, not a permanent historical archive. Changing Extension to Both extends a center line/zone in both time directions, but does not make the latest geometry a historical signal.

If the number on the label itself changes while the Replay cursor and source minute stay unchanged, that is a different issue from scale pinning. Record the before/after label, Source NY, Contract, State, timeframe and Replay date. In a fully warmed calculation with identical source data/settings, viewport zoom should not change source reference prices. A source-data reload or insufficient history needs separate diagnosis.

## No zones in Bar Replay on NQ1!

For historical replay, use the **dated NQ contract covering the Replay date as the chart symbol**. Leave Source contract blank, or select that same dated contract explicitly. This also avoids comparing unadjusted dated-contract levels with differently backadjusted continuous-chart history.

On a continuous chart the automatic source uses `syminfo.current_contract`; this is not a historical per-bar rollover map. Check the actual **Contract** row. A contract without history at the selected Replay date cannot supply valid zones. The exact dated contract depends on your Replay date; the script must not guess it from today's expiry.

Read the State row:

| State | Meaning and next step |
|---|---|
| No minute coverage | The requested source has no available minute snapshots there. Check dated contract, Replay date and plan/feed history limits. |
| Warmup n/20 | All zone widths require the historical volatility scale. Load enough source history before the cursor for 20 complete cash-session observations. You do not have to manually play through 20 days if they are already loaded. Close-return variance needs 21 complete sessions for 20 observations after initialization. |
| Incomplete session / no scale | The latest required session/reference is incomplete. Check data gaps and cash/futures calendar overrides. |
| Confirmed 1m map | A source snapshot is available. Compare its timestamp with the Replay cursor and check display filters if there are no eligible zones. |

The script requests up to 100,000 source minutes, subject to TradingView plan and feed availability. It cannot recover data outside that coverage. Do not lower the volatility lookback merely to make lines appear; that changes the model being tested.

The built-in default cash holiday calendar covers 2026 only. Update calendar overrides when replaying another year. Normal indicators and drawings work in Bar Replay. This script's alert branch intentionally requires realtime data, so it does not simulate historical alert notifications.

## Verified documentation

- TradingView, Pine Script visuals: scale and initial instance settings: https://www.tradingview.com/pine-script-docs/visuals/overview/#scale and https://www.tradingview.com/pine-script-docs/visuals/overview/#changing-settings
- TradingView, line and box coordinates: https://www.tradingview.com/pine-script-docs/visuals/lines-and-boxes/
- TradingView, lower-timeframe availability: https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/
- TradingView, historical/last/realtime bars: https://www.tradingview.com/pine-script-docs/concepts/bar-states/
- TradingView, Bar Replay and alert limitations: https://www.tradingview.com/support/solutions/43000474024-how-do-i-turn-bar-replay-on/

These sources were opened for the diagnosis. No TradingView runtime session or Pine compilation was available here, so the user-visible symptom has not been reproduced in this environment.
