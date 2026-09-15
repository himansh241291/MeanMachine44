# MA44 Strategy Specification v1

**Status:** Draft — implementation contract for research only  
**Scope:** BUY/LONG only  
**Source basis:** MA44 source material supplied in the MeanMachine44 project conversation

## 1. Source-control rule

This specification is intentionally limited to rules that are explicitly supported by the supplied MA44 source or explicitly agreed in this project conversation.

- No short/sell-entry logic.
- No rules imported from DoorDieAgent or any other project.
- No rules imported from other conversations.
- No discretionary concept is silently converted into a numeric rule.
- Anything not defined below remains `UNDEFINED` and must be researched/approved before it becomes a strategy rule.

## 2. Core indicator

The source explicitly uses a **44-period Simple Moving Average (SMA44)** based on closing price.

The source scanner setting is described as:

- Moving average: SMA
- Period: 44
- Source: Closing
- Direction: Rising
- Minimum: 3 periods

For implementation, `SMA44` means the arithmetic mean of the current close and the preceding 43 closes once 44 observations are available.

## 3. Universe / timeframe filtering

The source demonstrates this workflow:

1. Start with the NIFTY 500 universe.
2. Scan the **weekly** chart for SMA44 rising for at least 3 periods.
3. Save the resulting symbols.
4. Filter that saved list using the **daily** chart for SMA44 rising.
5. Inspect the remaining symbols for BUY setups.

The NIFTY 500 universe is the source example. A production universe is `UNDEFINED` unless explicitly approved.

## 4. Common BUY mechanism

The source repeatedly describes the following execution mechanism:

- A bullish/green trigger candle qualifies as part of a BUY setup.
- The BUY is placed **above the high of the trigger candle**.
- The initial stop reference is **below the low of the trigger candle** for the common setup examples.

For the first software implementation, we will represent this as a pending BUY trigger rather than immediately creating a trade when the setup candle closes.

Exact order semantics when price gaps above the trigger high are `UNDEFINED`.

## 5. BUY setup families in source

### 5.1 Type 1 BUY

Source classification: **rising moving average + support**.

This is the preferred/dominant setup family for the initial deterministic research implementation.

The exact mathematical definitions of `rising` and `support` are `UNDEFINED`.

### 5.2 Type 2 BUY

Source classification: **sideways moving average + support**.

The source treats sideways MA classification as chart-reading/discretionary judgment. No numeric sideways threshold is established in the source.

**Implementation status:** excluded from deterministic V1 until an explicit operational definition is researched and approved.

### 5.3 Type 3 BUY

Source classification: **falling moving average + support**.

The source describes this as relatively rare and indicates a preference for rising-MA setups.

**Implementation status:** a falling-MA direction primitive may label research context only. No Type 3 setup detector or trade rule is enabled because support remains undefined.

## 6. Rising SMA44 + support / bullish price action

The source presents setups where price action interacts with a rising MA44 and a bullish candle provides the trigger.

For the first research engine, the intended sequence is:

```text
Daily OHLC
   -> SMA44
   -> rising MA44 condition
   -> qualifying support/bullish setup
   -> trigger candle HIGH becomes pending entry
   -> later price crosses trigger HIGH
   -> BUY
   -> trigger candle LOW is initial stop reference
```

The following are deliberately **UNDEFINED**:

- numerical definition of rising SMA44;
- numerical definition of support;
- maximum distance from SMA44;
- definition of qualifying bullish/green candle;
- whether the candle must touch, overlap, or merely be near SMA44;
- whether the setup candle must close above/at/below SMA44;
- whether the setup must be a single candle or can be a multi-candle structure.

## 7. Double-bottom + MA44 support

The source describes a BUY setup involving a double-bottom/support structure in the vicinity of MA44, followed by bullish confirmation and entry above the trigger candle high.

The following remain `UNDEFINED` for automation:

- lookback window;
- minimum/maximum separation of the two lows;
- acceptable difference between the two lows;
- neckline definition;
- exact relationship of MA44 to each low;
- confirmation-candle definition;
- invalidation conditions.

Therefore no double-bottom detector will be enabled in V1 until those definitions are explicitly researched and approved.

## 8. Bullish MA44 crossover

The source describes a bullish crossover setup where:

- MA44 is rising;
- price is in an upward/rising structure;
- price moves below MA44;
- price crosses back above MA44;
- MA44 has not turned down;
- a bullish/green candle provides confirmation;
- BUY is taken above the confirmation candle high;
- stop reference is below the confirmation candle low.

Exact crossover and uptrend definitions are `UNDEFINED`.

No crossover detector will be enabled in V1 until these are formalized.

## 9. ATR exhaustion + MA44 support

The source describes an advanced setup using:

- ATR period 14;
- ATR smoothing changed from RMA to SMA;
- an ATR-based expected daily move/exhaustion area;
- MA44 support;
- bullish confirmation;
- lower-timeframe confirmation/entry;
- BUY above the bullish trigger high and stop below its low.

The source shows ATR exhaustion by subtracting the ATR from a demonstration reference price: the concrete example uses the next day's open, while an earlier illustration uses the prior close. The unique reference-price rule, synchronization between daily and lower timeframe data, and entry timing are `UNDEFINED`.

V1 includes only reusable ATR(14)-SMA, lower-boundary, and boundary-reached primitives. It does not select the reference price or create an ATR-based trade signal.

## 10. Historical MA44 behaviour

The source recommends checking how well MA44 has historically worked for an individual stock.

For research this is a candidate feature, **not a hard filter in V1**. Any future implementation must avoid look-ahead bias by calculating historical behaviour only from information available before each candidate trade.

The exact measurement methodology is `UNDEFINED`.

## 11. Fundamental quality filters

The source discusses high-quality/fundamentally strong stocks and demonstrates example filters. The demonstrated thresholds are explicitly examples rather than a canonical MA44 rule.

Therefore V1 will **not hard-code** debt, ROIC, earnings-yield, market-cap, profitability, or similar fundamental thresholds.

## 12. Risk, target and portfolio rules

The source references risk/reward examples including 1:2 and 1:3, but V1 does not yet assign a universal target policy.

The following are `UNDEFINED`:

- target selection by setup;
- fixed R multiple vs structural target;
- trailing stop;
- partial exits;
- risk per trade;
- position sizing;
- maximum concurrent trades;
- sector concentration;
- re-entry rules.

## 13. V1 implementation boundary

V1 should implement only the following reusable primitives:

1. OHLC data validation.
2. SMA44 calculation.
3. Pending BUY trigger representation using setup high.
4. Trigger event representation when later price crosses the setup high.
5. Initial stop reference using setup low.
6. Deterministic tests for the above primitives.

A complete automated setup detector is **not yet authorized** because the source has not supplied machine-definitions for the discretionary concepts listed above.

## 14. Research status labels

Every future strategy rule must be labelled internally as one of:

- `SOURCE_RULE` — explicitly supported by the supplied source.
- `PROJECT_DECISION` — explicitly approved in the MeanMachine44 conversation.
- `RESEARCH_PARAMETER` — proposed for experimentation and not yet accepted as source truth.
- `UNDEFINED` — insufficient source information; requires research/approval.

## 15. No profitability claim

This specification defines a research hypothesis. It does not establish that MA44 has predictive power or positive expectancy.
