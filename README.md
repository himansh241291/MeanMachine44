# MeanMachine44

**MA44 buy-only swing trading research and paper-trading system.**

MeanMachine44 is a standalone research project for converting the MA44 swing-trading methodology from the supplied source material into deterministic, testable rules.

## Project principles

- **BUY/LONG only.** No short-selling logic is part of this project.
- **GitHub is the source of truth.** Strategy rules, decisions, configuration, research methodology, code, tests, and project state belong in this repository so the project can be recovered on any laptop/WSL environment.
- **Source fidelity first.** Rules explicitly supported by the source are separated from rules that still require formalization or research.
- **No silent assumptions.** Ambiguous discretionary concepts are recorded as `UNDEFINED` until we choose and test an operational definition.
- **Research before automation.** Backtesting and validation precede live-market paper trading.
- **Paper trading only initially.** No real-money broker execution is implemented in this project phase.
- **Reproducibility matters.** Data provenance, strategy versions, parameters, signals, fills, and research results must be traceable.

## Current strategy scope

The source material establishes these BUY-side concepts for investigation:

1. Rising SMA44 + support / bullish price action.
2. Double-bottom + MA44 support.
3. Bullish MA44 crossover.
4. Weekly SMA44 rising followed by daily SMA44 rising filtering.
5. Type 1 / Type 2 / Type 3 BUY classification based on MA slope.
6. ATR exhaustion + MA44 support as an advanced setup.
7. Historical MA44 behavior as a research feature.

The first implementation will start with the most deterministic common mechanism:

```text
Daily data
  -> SMA44
  -> rising-MA44 filter
  -> qualifying bullish setup candle near MA44
  -> pending BUY at setup-candle HIGH
  -> trigger when a later market price crosses that HIGH
  -> initial stop reference at setup-candle LOW
```

The exact definitions of `rising`, `near MA44`, `qualifying bullish candle`, execution semantics, targets, position sizing, and several pattern-specific rules remain versioned research parameters until formally validated.

## Repository layout

```text
MeanMachine44/
├── config/                 # Versioned research/paper configuration
├── data/                   # Metadata only; raw market data is not committed by default
├── docs/
│   ├── decisions/          # Architecture and strategy decisions
│   └── strategy/           # Source-derived rules and formal specification
├── src/
│   └── meanmachine44/      # Application and strategy code
├── tests/                  # Deterministic unit/replay tests
├── scripts/                # Reproducible local commands
├── .github/workflows/      # CI
├── pyproject.toml
└── README.md
```

## Source of truth workflow

The repository is the durable project state. WSL is an execution environment, not the authoritative copy.

```bash
git clone https://github.com/himansh241291/MeanMachine44.git
cd MeanMachine44
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

Before changing strategy logic:

```bash
git pull --ff-only
```

After a meaningful change:

```bash
git status
git add .
git commit -m "<meaningful change>"
git push
```

Use feature branches for substantial changes and merge reviewed work into `main`.

## Research lifecycle

```text
Source extraction
      ↓
Strategy specification
      ↓
Deterministic implementation
      ↓
Unit tests + replay fixtures
      ↓
Historical backtest
      ↓
Parameter sensitivity / robustness
      ↓
Out-of-sample validation
      ↓
Live-market paper trading
      ↓
Review / promotion decision
```

## Safety boundary

MeanMachine44 is a research and paper-trading system. It must not contain broker credentials or a real-money order endpoint. Any future live execution would be a separately reviewed project boundary rather than a switch in this repository.

## Current status

**Phase 0 — repository foundation and MA44 rule formalization.**

No profitability claim is made. The strategy is an empirical hypothesis to be tested.
