from datetime import date

import pandas as pd
import pytest

from meanmachine44.universe import HistoricalUniverse, MembershipInterval
from scripts.audit_pit_price_coverage import yearly_coverage


def test_yearly_coverage_reports_missing_historical_prices():
    universe = HistoricalUniverse(
        (
            MembershipInterval("AAA", date(2018, 1, 1), date(2020, 1, 1)),
            MembershipInterval("BBB", date(2018, 1, 1), date(2020, 1, 1)),
            MembershipInterval("CCC", date(2019, 1, 1), None),
        )
    )
    market = pd.DataFrame(
        {
            "timestamp": [
                "2018-06-01T00:00:00Z",
                "2019-06-01T00:00:00Z",
            ],
            "symbol": ["AAA", "CCC"],
        }
    )
    result = yearly_coverage(market, universe, "2018-01-01", "2019-12-31")
    first, second = result.to_dict("records")
    assert first["active_members_in_history"] == 2
    assert first["active_members_with_prices_in_period"] == 1
    assert first["active_members_without_any_price_history"] == 1
    assert first["period_member_coverage_pct"] == pytest.approx(50.0)
    assert second["active_members_in_history"] == 1
    assert second["active_members_with_prices_in_period"] == 1
