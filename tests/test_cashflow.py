from app.data.categories import get_category_data
from app.services.calculator import get_full_calculation
from app.services.cashflow import project_cash_flow


def _make_calc_output(capital: float) -> dict:
    return get_full_calculation(capital)


def test_comfortable_category():
    """Dairy with ₹1,00,000 capital — net_this_month should be positive every month
    (revenue exceeds operating costs), even though cumulative stays negative
    from the large initial setup cost."""
    calc = _make_calc_output(100_000)
    cat = get_category_data("Dairy")
    result = project_cash_flow(calc, cat, months=12)

    for m in result["monthly"]:
        assert m["net_this_month"] > 0, f"Month {m['month']} net is negative"


def test_high_setup_cost():
    """Kirana Store has high setup_cost_ratio (0.65) — should trigger negative early."""
    calc = _make_calc_output(14_000)
    cat = get_category_data("Kirana Store")
    result = project_cash_flow(calc, cat, months=12)

    assert result["negative_month"] is not None
    assert result["negative_month"] >= 2
    assert result["negative_gap"] > 0


def test_emi_pushes_negative():
    """Tailoring with small capital — EMI kicks in after moratorium.
    Verify EMI is 0 during moratorium and > 0 after."""
    calc = _make_calc_output(50_000)
    cat = get_category_data("Tailoring")
    result = project_cash_flow(calc, cat, months=12)

    assert len(result["monthly"]) == 12

    moratorium = calc["moratorium_months"]

    # EMI is 0 during moratorium
    for i in range(moratorium):
        assert result["monthly"][i]["emi"] == 0

    # EMI kicks in after moratorium
    emi_month = result["monthly"][moratorium]
    assert emi_month["emi"] > 0


def test_cash_flow_output_structure():
    """Verify output matches the expected contract."""
    calc = _make_calc_output(100_000)
    cat = get_category_data("Dairy")
    result = project_cash_flow(calc, cat, months=12)

    assert "monthly" in result
    assert "negative_month" in result
    assert "negative_gap" in result

    for m in result["monthly"]:
        assert "month" in m
        assert "revenue" in m
        assert "operating_cost" in m
        assert "emi" in m
        assert "net_this_month" in m
        assert "cumulative_balance" in m
