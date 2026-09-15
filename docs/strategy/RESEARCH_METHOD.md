# MeanMachine44 Research Method

**Status:** Project decision — v1 research method

## 1. Purpose

The purpose of MeanMachine44 is to determine whether the BUY-side MA44 price-action concepts from the supplied source contain a measurable, repeatable edge.

This project will not begin by optimizing parameters until the source-derived concept has been represented and tested without look-ahead bias.

## 2. Source discipline

The only strategy authority for this project is:

1. MA44 source material supplied in this MeanMachine44 conversation.
2. Explicit decisions made in this MeanMachine44 conversation.
3. External research only when explicitly introduced and labelled.

Other chats, other trading systems, and prior project logic must not be used to define MeanMachine44.

## 3. Rule classification

Every rule in code/config/documentation must be traceable to one of:

- `SOURCE_RULE`
- `PROJECT_DECISION`
- `RESEARCH_PARAMETER`
- `UNDEFINED`

A research parameter must never be represented as though it came from the source.

## 4. Research stages

### Stage A — Source formalization

Convert the supplied MA44 material into an explicit rule inventory. Preserve ambiguity rather than guessing.

### Stage B — Deterministic primitives

Implement only unambiguous mechanics first:

- OHLC validation;
- SMA44 calculation;
- trigger-high representation;
- trigger crossing;
- stop-reference representation.

### Stage C — Setup formalization

For concepts such as support, rising MA, bullish candle, double bottom and crossover, propose candidate machine definitions as research parameters. Do not call them source rules.

### Stage D — Historical testing

Run reproducible tests over historical data with timestamps and data provenance recorded.

### Stage E — Robustness

Test sensitivity to reasonable parameter changes. Avoid selecting a single parameter set solely because it produces the best historical result.

### Stage F — Out-of-sample validation

Freeze a strategy version and evaluate it on data that was not used to select its parameters.

### Stage G — Paper trading

Only after deterministic behaviour and out-of-sample testing are satisfactory should the system generate live-market paper signals.

## 5. Look-ahead prevention

A signal at time `t` may use only information that would have been available at or before the decision point at `t`.

Future candles must not influence:

- setup classification;
- indicator values;
- parameter selection for the evaluated trade;
- historical MA44 behaviour features;
- universe membership at the decision point.

## 6. Reproducibility

Each backtest result must record at minimum:

- strategy version;
- configuration/parameter version;
- market universe/version;
- data source;
- data time range;
- timeframe;
- timezone assumptions;
- execution model;
- transaction-cost assumptions;
- generated signals;
- resulting trades;
- summary metrics.

## 7. Execution-model boundary

The first research engine will model a pending BUY above a qualifying trigger candle high and an initial stop reference below its low.

Gap-through behaviour, intrabar ordering, slippage, transaction costs, and other execution details are `UNDEFINED` until explicitly specified.

## 8. Success criteria

The project must not promote a strategy because of a single attractive backtest.

Promotion requires evidence of:

- deterministic implementation;
- passing unit/replay tests;
- no known look-ahead leakage;
- robustness to reasonable parameter changes;
- out-of-sample evaluation;
- paper-trading validation.

No fixed profitability threshold is defined yet; that is a future project decision.
