# Type 1 Fixed-Horizon Outcome Results

This document records descriptive historical outcome measurements from the Type 1 research variants.

Dataset: current NIFTY 500 constituent universe, daily history through 2026-09-16. These results are subject to survivorship bias and are not historical index-membership results.

## Results

| Variant | Setups | 5-day triggers | 5-day rate | 20-day triggers | 20-day rate |
|---|---:|---:|---:|---:|---:|
| `ma_touch_reclaim` | 20,485 | 17,157 | 83.75% | 18,816 | 91.85% |
| `local_low_reclaim` (`N=5`) | 18,717 | 15,730 | 84.04% | 17,263 | 92.23% |

## Interpretation discipline

The local-low research parameter produces fewer setups than the MA-touch baseline and slightly higher trigger-rate measurements at both tested horizons in this dataset.

These figures are descriptive only. They do not establish profitability, risk-adjusted performance, or superiority of one setup definition. The experiment does not model fills, slippage, gaps, stops, targets, position sizing, or transaction costs.

A later trigger means a later daily bar whose high is strictly above the setup candle high. The setup candle cannot trigger itself.

The next research stage is to examine trigger timing and setup overlap before introducing an execution model.