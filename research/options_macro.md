# Options, contract conventions and macro: verified research inputs

Verified online in this execution on 2026-10-17 (Europe/Paris client date; Saturday). This note distinguishes published mechanisms, demonstrated sample-specific effects, and untested NQ trading rules. Official source content was opened and read, not inferred from URL titles. Primary-source numbers below are exactly the releases returned by those official endpoints. All source data refer to their indicated observation dates, not Saturday trading.

## Evidence scale

An exchange specification is authoritative for a contract convention, but is not evidence of a profitable reaction rule. A mathematical identity is strong as an identity, but does not identify dealer inventories. Single peer-reviewed empirical studies are moderate evidence under the user's definition. Related results on stocks and S&P futures support expiration pinning as a real phenomenon across samples; they do not establish NQ 1-minute reversal probabilities. No NQ tick-level effect or reaction rate has been estimated here.

## Dealer gamma, flips and walls

Let signed dealer option inventory be q_i (positive long), multiplier M_i, underlying S, option delta Δ_i and gamma Γ_i. The inventory hedge in underlying units is H = -Σ q_i M_i Δ_i. To first order, holding positions and volatility fixed:

    dH = -Σ q_i M_i Γ_i dS.
    dollar GEX per 1% move = 0.01 S² Σ q_i M_i Γ_i.

For futures hedges, divide underlying-equivalent exposure by the futures multiplier, with the appropriate cross-product sensitivity. A positive gamma dealer hedges by selling an increase and buying a decrease; negative gamma reverses the flow. This is a conditional flow mechanism, not an unconditional prediction: hedging time, netting across products, competing informed flow, liquidity and discrete execution matter.

Open interest OI_i is not signed dealer q_i. Every open contract has a long and a short. Assigning dealers long calls/short puts or the reverse from OI alone is an assumption, not observed positioning. Black-Scholes long call and long put gammas are both positive:

    Γ = exp(-q τ) φ(d1) / (S σ sqrt(τ)).

A gamma flip solves G(S*) = Σ q_i M_i Γ_i(S*, σ_i(S*), τ_i) = 0 under an explicitly specified inventory and volatility-surface model. There can be no root, more than one root, or an unstable root. Moving the spot through a provider's quoted flip does not mechanically cause all dealers to change sign. A call/put wall is not standardized: it might maximize call/put OI, gamma-weighted OI, modeled signed gamma or another measure. Store the definition, provider, underlying, timestamp and expiry universe with every manually supplied level.

**Evidence:** moderate for a gamma–intraday momentum/reversal association in a broad stock-options panel (Barbon and Buraschi working-paper abstract verified); weak for a fixed NQ flip/wall being a reversal zone. Cboe's primary SPX evidence explicitly contradicts equating huge 0DTE gross volume with huge net hedging. Thus include manual contextual levels only with separate attribution; do not derive or fabricate GEX from futures OHLCV. No causal grade upgrades from multi-family confluence.

## Vanna, charm, 0DTE and expiration pinning

With calendar-time charm C_i = ∂Δ_i/∂t and vanna V_i = ∂Δ_i/∂σ:

    dH ≈ -Σ q_i M_i [Γ_i dS + V_i dσ + C_i dt].

If charm is instead defined as ∂Δ/∂τ for remaining time τ, its calendar-time term has the opposite sign. Positions, implied-volatility changes and the hedge convention are all required. Vanna/charm are exposures/flow channels, not unique price coordinates. Exclude computed vanna/charm levels from OHLCV-only v1; externally researched levels can be pasted as explicitly manual context. As τ→0, near-ATM gamma may become large, but far-from-ATM gamma collapses, and same-day trading changes inventory. A morning OI snapshot is particularly weak for 0DTE intraday net positioning.

**Verified expiration evidence:** Ni, Pearson and Poteshman find expiration-date stock-price clustering at strikes and evidence consistent with market-maker hedge rebalancing and proprietary trading. Golez and Jackwerth find S&P500 futures pulled toward the ATM futures-option strike on serial-option expiry, but **pushed away** from the carry-adjusted ATM index-option strike before index-option expiry (anti-cross-pinning). Avellaneda and Lipkin provide a price-impact/delta-hedging model with a finite pinning probability. These are specific expiry/instrument/settlement mechanisms. A generic 'largest OI strike attracts price every day' rule is unsupported. Options on NDX, QQQ and NQ have different settlement and exercise conventions; do not treat their expirations as interchangeable or apply stock-pin empirical magnitudes to NQ.

**Verified Cboe counterevidence:** Mandy Xu's 2023 exchange study sees customer/market-maker, buy/sell, open/close flags for SPX transactions, unlike OI-based outside estimates. It reports balanced net flow and no discernible rise in SPX intraday/gap volatility in its studied period. The study expressly notes potential offsets in other expiries/products and hedging with other options. Its conclusion is historical SPX evidence, not a claim that 0DTE can never matter, and not evidence about today's NQ inventory.

**Grades:** moderate for the individual pinning/anti-pinning empirical studies; mathematical mechanism/model only for Avellaneda–Lipkin; moderate exchange evidence for the Cboe sample; weak for an unconditional NQ wall/flip/pinning trading rule. No current dealer sign, gamma-flip, wall, vanna or charm figure has been verified. Current positioning is **unknown**.

## Mapping QQQ / NDX option levels into NQ

At a synchronized observation t with cash prices observed, define:

    r_t = NDX_t / QQQ_t,
    b_t = NQ_t - NDX_t,
    mapped(QQQ strike K) = K r_t + b_t,
    mapped(NDX strike K) = K + b_t,
    mapped(NQ strike K) = K.

Round final chart prices to syminfo.mintick. This is a local mapping of equivalent index exposures, not an options-arbitrage identity across ETF and index. QQQ fees, tracking, cash distributions, cash-market price differences and basis all affect r_t; the same r_t is only a local scale approximation for nearby strikes. CME fair-value documentation confirms basis reflects financing, dividends and time to expiry; actual futures also differ from theoretical fair value because of supply/demand. Its published illustrative formula is F = Cash[1+r(days/360)] − dividends; its settlement fallback uses a different day-count convention. Do not hardcode a QQQ multiplier or assume zero basis.

Use request.security for each explicitly selected source and a synchronized confirmed timestamp. A requirement to convert using the *live* ratio/basis means mapped levels move as those inputs move. It conflicts with treating mapped manual zones as immutable session references. Resolve explicitly: freeze the conversion at a confirmed cash-session observation and label its timestamp, while permitting a clearly labeled live mode if implemented. At 09:30 before a minute closes no synchronized confirmed current-day conversion exists. Outside the cash session, a held-last NDX value combined with live NQ makes b_t absorb essentially the entire NQ price move, spuriously dragging every manual zone alongside the market; do not call that a live verified basis. Freeze the last synchronized conversion and show staleness, or suppress converted levels until cash data return. A newly entered Sunday level therefore uses stale Friday conversion until Monday cash opens unless the user supplies actual NQ coordinates. Do not silently use stale cash prints as fresh observations.

Near expiry fair-value basis tends toward its final-settlement linkage, but SOQ constituents do not necessarily open simultaneously and NDX AM/PM options settle differently. The next quarterly futures contract can have a nonzero financing/dividend calendar spread; continuous-futures rolls change the coordinate system. An explicit current contract is safest. Do not shift inherited levels by an inferred gap or claim a heuristic gap detector identifies all rolls. Back-adjusted continuous history can itself be rewritten after a roll. A manual roll/reset date and resetting accumulated session state avoids carrying old-contract levels, but cannot reverse every vendor historical adjustment; disclose this limitation.

For ES/MES the relevant index/ETF defaults are SPX/SPY, not NDX/QQQ. All such source symbols must be configurable or detected per root; an NQ-specific source must never quietly map to ES.

## Verified contract, session, roll and settlement conventions

The current CME product page is JavaScript rendered. Its own client script exposes the actual official specification API, which was opened successfully:

- NQ: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/146
- MNQ: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/8668
- ES: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/133

| Contract | Multiplier | Outright tick | Dollar tick |
|---|---:|---:|---:|
| NQ | $20/index point | 0.25 | $5.00 |
| MNQ | $2/index point | 0.25 | $0.50 |
| ES | $50/index point | 0.25 | $12.50 |

All three specifications say Globex Sunday 18:00 through Friday 17:00 Eastern, with daily maintenance 17:00–18:00 Eastern. The current specifications do **not** give the historical additional 16:15–16:30 halt. CME ClearPort reporting hours differ and must not be mistaken for Globex trading hours. Nasdaq official equity cash hours are weekdays 09:30–16:00 ET. Encode these with America/New_York IANA timezone and explicit session inputs, never fixed Paris UTC offsets. Cash weekdays differ from Globex trade dates that begin the preceding evening.

NQ final expiry is ordinarily 09:30 ET on the third Friday of the quarterly month. Rule35903 states final settlement is the special opening quotation based on Nasdaq Official Opening Prices of index components; holiday and missing-stock rules apply. Current official CME roll guidance says the customary lead-month roll is the **Monday before** the third Friday (not the older Thursday convention). It explicitly allows participants to roll at any time; TradingView's continuous roll choice need not be the same. The verified table lists Dec2026 roll December14, expiration December18. June2026 expiry is June18 because of the holiday exception; don't derive every expiry with an unconditional third-Friday function.

**Daily settlement is not a session close.** CME's settlement page says lead-month NQ daily settlement Tier1 is trade VWAP in **14:59:30–15:00:00 CT = 15:59:30–16:00:00 ET**. Tier2 is bid/ask midpoint when no trade; Tier3 uses an index/carry fallback. Other months use calendar-spread rules. A 1-minute cash close, a 17:00 ET Globex close, or request.security daily close is not independently verified as this settlement. With only minute OHLCV a script cannot reconstruct the 30-second trade VWAP or fallback order book. Use manually verified official settlement if desired, or label prior cash/futures close accurately and omit settlement. Never call an approximation 'SET'.

Holidays require exchange calendars, not just absence of 09:30 bars (futures can trade on a cash holiday). Official Nasdaq2026 table has full closures Jan1, Jan19, Feb16, Apr3, May25, Jun19, Jul3, Sep7, Nov26, Dec25; cash early closes Nov27 and Dec24 at13:00ET. CME holiday hours are separate, product-specific and subject to change. A reusable script needs configurable early-close/skip-date overrides and must disclose any finite calendar coverage. No trading bars during maintenance should enter overnight or cash accumulations.

## Current verified context, as of 17 October 2026, Europe/Paris

It is Saturday. Latest exchange volatility observations returned are Friday16October, and the latest rates observations below are Thursday15October. These dates must appear with the numbers.

| Measure | Verified latest observation | Source and interpretation |
|---|---|---|
| VXN | 2026-10-16: O22.54, H28.17, L22.41, **C27.13** | Official Cboe historical CSV; prior10/15 close22.89, one-day change18.5234%, calculated from those two observed closes. NDX 30-day option-implied volatility, not today's NQ reaction rate. |
| VIX | 2026-10-16 C19.99 | Cboe official CSV; S&P500 implied volatility, different underlying. |
| VIX3M | 2026-10-16 C20.50 | Cboe official CSV; VIX/VIX3M=0.97512, calculated. This pair is consistent with slightly higher 3-month than 30-day S&P implied vol; it does not establish NDX term structure. |
| 10-year real Treasury yield DFII10 | **2.78% on2026-10-15** | FRED official series page, updated10/16 15:16CDT. Level only; a direction or intraday change was not verified. |
| Effective fed funds DFF | **3.88% on2026-10-15** | FRED official page, updated10/16. It is an effective overnight rate, not a verified current target range. |
| September CPI | Release2026-10-14: headline +0.6%m/m,+3.7%y/y; core +0.3%m/m,+2.6%y/y | BLS actual release. Inflation surprise versus consensus was not verified, so do not call this a surprise. |
| August PCE prices | Release2026-09-30: headline +0.3%m/m,+3.4%y/y; core +0.2%m/m,+3.0%y/y | BEA actual release. These are August data, not September CPI-comparable same-month data. |
| September payrolls | Release2026-10-02: +29,000; unemployment4.2%; AHE +0.1%m/m,+3.0%y/y | BLS actual release; says payrolls/unemployment changed little. No consensus or market reaction verified. |

VXN's27.13 annualized reading yields a **heuristic trading-day** standard-deviation scale27.13/sqrt252=1.70903% and a **calendar-day** scale27.13/sqrt365=1.42005%. These are computed mathematical conversions under explicitly chosen square-root-time assumptions, not measured next-day prediction intervals, not an expected high-low range and not automatically68% physical coverage. Cboe's official VXN methodology targets30-day implied NDX volatility using NDX/NDXP options; the annual calendar convention and risk-neutral/physical distinction must be respected. A static30-day reading cannot allocate a specific fraction to cash hours, overnight or an announcement minute without additional assumptions. If code uses252 it must label this a trading-day scaling convention and validate empirical coverage separately.

**Practical interpretation supported by these observations:** the VXN increase justifies checking updated volatility-scaled distances and avoiding stale fixed-point widths. It does not tell us to widen every stop or trade larger zones: a zone beyond the prop-risk budget should be excluded. Rates and inflation are macro state information, not NQ support prices. Without announcement surprises, actual dealer inventory, current strike distributions, synchronized NQ/NDX/QQQ prices, positioning or earnings filings, there is no verified current directional bias, wall, flip or numerical NQ support/resistance level. Do not invent any.

Next releases explicitly announced in the opened official releases:

- BEA September personal income/outlays:2026-10-29 at08:30EDT =13:30 Europe/Paris, because Europe has switched to winter time and the US has not yet.
- BLS October employment situation:2026-11-06 at08:30ET =14:30 Europe/Paris.
- BLS October CPI:2026-11-10 at08:30ET =14:30 Europe/Paris.

The Fed calendar, latest policy statement and open-market pages still returned HTTP403. Do not claim a current FOMC target band or next meeting date from memory. Nasdaq methodology PDF also returned403, so no verified current rebalance or component-weight claim is used. Current mega-cap earnings dates, dollar/liquidity trend, intraday rates moves, NDX IV term structure, and dealer positioning remain unverified. Their role is scheduled risk/volatility or bias, generally not a precise horizontal level. Manual event dates should change a risk indicator, alert policy or level eligibility; they should not manufacture prices. This partial source failure does not block using verified primary and academic sources elsewhere.

## Full verified bibliography and verification scope

1. Sophie Xiaoyan Ni, Neil D. Pearson and Allen M. Poteshman(2005), **Stock price clustering on option expiration dates**, *Journal of Financial Economics*78(1),49–87. https://doi.org/10.1016/j.jfineco.2004.08.005 . Journal identity/authors/pages confirmed at https://api.crossref.org/works/10.1016/j.jfineco.2004.08.005 ; abstract of2004 author working-paper version confirmed in Crossref at DOI https://doi.org/10.2139/ssrn.519044 . Full journal paper not retrieved; use only abstract-supported qualitative findings, not remembered sample details/statistics.
2. Benjamin Golez and Jens Carsten Jackwerth(2012), **Pinning in the S&P500 futures**, *Journal of Financial Economics*106(3),566–585. https://doi.org/10.1016/j.jfineco.2012.06.010 . Journal metadata confirmed in Crossref title search;2010 author abstract confirmed at https://doi.org/10.2139/ssrn.1664261 via Crossref. The abstract explicitly states pinning *and anti-cross-pinning*. Direct SSRN page403; fulltext not retrieved. Do not cite the superficially similar DOI ending06.005, which is a different paper.
3. Marco Avellaneda and Michael D. Lipkin(2003), **A market-induced mechanism for stock pinning**, *Quantitative Finance*3(6),417–425. https://doi.org/10.1088/1469-7688/3/6/301 . Journal metadata and working-paper abstract https://doi.org/10.2139/ssrn.458020 confirmed in Crossref. Model mechanism only; not a calibrated NQ pin probability. DOI ending/305 is a different paper and must not be used.
4. Andrea Barbon and Andrea Buraschi(2020 Crossref working-paper registration), **Gamma Fragility**, SSRN working paper3725454. https://doi.org/10.2139/ssrn.3725454 . Author names and full abstract opened via Crossref search. The abstract reports negative(positive) ex-ante gamma interacting with illiquidity explains intraday momentum(reversal), stronger in less-liquid underlying stocks. This is not an NQ-specific study. Version/publication status beyond the verified working-paper record was not established; do not label it peer reviewed or cite an invented journal.
5. Mandy Xu(2023-09-08), **Much Ado About0DTEs — Evaluating the Market Impact of SPX0DTE Options**, Cboe Insights, full article opened. https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/ . Primary exchange analysis, not peer reviewed and not a current2026 positioning report.
6. CME Group(undated,current specifications), **E-mini Nasdaq-100 Futures Contract Specs**, **Micro E-mini Nasdaq-100 Futures Contract Specs**, **E-mini S&P500 Futures Contract Specs**. https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html ; https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html ; https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.contractSpecs.html . Pages plus actual specification API read; API links above.
7. CME Group(current), **Rulebook, Chapter359: E-mini Nasdaq-100 Index Futures**, especially35901,35902.G,35903. Full PDF read via pdftotext. https://www.cmegroup.com/rulebook/CME/IV/350/359/359.pdf . Final SOQ, business-day exceptions and contract multiplier are authoritative rules.
8. CME Group(current), **Nasdaq-100 settlement procedures**, full body opened from official product-spec link https://www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 which redirects to https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457222172/Nasdaq-100 . Section Normal Daily Settlement Procedure, Lead Month Tier1–3; Final Settlement.
9. CME Group(current), **Equity Index Roll Dates**, full page read. https://www.cmegroup.com/trading/equity-index/rolldates.html . Monday convention, voluntary timing and2026 table verified.
10. CME Group(current), **Calculating Fair Value**, full page read. https://www.cmegroup.com/trading/equity-index/fairvalue.html . Financing, dividends, expiry and actual supply/demand basis deviations.
11. CME Group(current), **Globex Trading Hours and Holiday Schedules**, full page read. https://www.cmegroup.com/trading-hours.html .2026 product-specific schedules subject to change; do not replace them with the cash calendar.
12. Nasdaq(current2026), **U.S. Stock Market Holiday Schedule / Trading Hours**, full page read. https://www.nasdaq.com/market-activity/stock-market-holiday-schedule . Weekday09:30–16:00ET cash hours,2026 closures and13:00ET early closes.
13. Cboe Global Indices(current, PDF contains March23,2026 amendment), **Cboe Selected Broad-Based Index, Equity and ETF Volatility Indices: Methodology**, full PDF read. Link discovered on official VXN dashboard: https://cdn-api.cboe.com/api/global/us_indices/governance/Volatility_Index_Methodology_Selected_Broad_Based_Index_Equity_and_ETF_Volatility_Indices.pdf . Sections1.1,2.1 and VXN row:30-day target from NDX/NDXP, Nasdaq PHLX options venue, VXN dissemination09:31–16:15ET. https://www.cboe.com/us/indices/dashboard/vxn/ . Does not assert futures1-day forecast accuracy.
14. Cboe Global Indices, **VXN daily historical prices**, retrieved2026-10-17. https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv redirects officially to https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv . Last observation2026-10-16. CSV was read and final observations verified.
15. Cboe Global Indices, **VIX / VIX3M daily historical prices**, retrieved2026-10-17. https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv and https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv (same official cdn-api redirects). Last observations2026-10-16.
16. U.S. Bureau of Labor Statistics(2026-10-14), **Consumer Price Index — September2026**, USDL26-1574. Full release opened. https://www.bls.gov/news.release/cpi.nr0.htm . Mutable current-release URL, observation and publication date explicitly recorded.
17. U.S. Bureau of Economic Analysis(2026-09-30), **Personal Income and Outlays, August2026**, BEA26-43. Full release opened. https://www.bea.gov/news/2026/personal-income-and-outlays-august-2026 . Includes next release date.
18. U.S. Bureau of Labor Statistics(2026-10-02), **The Employment Situation — September2026**, USDL26-1549. Full release opened. https://www.bls.gov/news.release/empsit.nr0.htm . Mutable release URL, date explicitly recorded.
19. Board of Governors, via Federal Reserve Bank of St.Louis FRED, **Market Yield on U.S. Treasury Securities at10-Year Constant Maturity, Quoted on an Investment Basis, Inflation-Indexed(DFII10)**, latest observed2026-10-15,2.78%. https://fred.stlouisfed.org/series/DFII10 . Page's actual observation date/value and updated timestamp read.
20. Board of Governors, via FRED, **Federal Funds Effective Rate(DFF)**, latest observed2026-10-15,3.88%. https://fred.stlouisfed.org/series/DFF . Actual observation/date read; not a policy-target-range source.

No forums, social media, blogs, community TradingView ideas or invented hit rates were used. Academics with only an abstract accessed are explicitly marked above. A DOI/title mismatch was resolved rather than cited from memory.

### Additional MES verification

CME Group, *Micro E-mini S&P 500 Futures Contract Specs*: https://www.cmegroup.com/markets/equities/sp/micro-e-mini-sandp-500.contractSpecs.html . Its official specification API was opened: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/8667 . Contract unit **$5 × S&P 500 index**, outright tick **0.25 points = $1.25**; calendar-spread tick differs (**0.05 points = $0.25**). Globex 18:00–17:00 ET and maintenance 17:00–18:00 ET. These support the MES risk-budget example; no trading-edge claim follows.
