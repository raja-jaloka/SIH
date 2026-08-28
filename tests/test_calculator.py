import math

from app.services.calculator import (
    calculate_emi,
    calculate_loan_amount,
    calculate_project_cost,
    get_full_calculation,
    route_scheme,
)


def test_project_cost_basic():
    assert calculate_project_cost(100_000) == 1_000_000


def test_loan_amount_basic():
    assert calculate_loan_amount(1_000_000) == 900_000


# --- Scheme routing tests (spec 1.6) ---


def test_boundary_micro_finance():
    """₹14,000 capital → project_cost ₹1,40,000 → Micro Finance (exactly at threshold)."""
    project_cost = calculate_project_cost(14_000)
    assert project_cost == 140_000
    scheme = route_scheme(project_cost)
    assert scheme["scheme_name"] == "Micro Finance Scheme"
    assert scheme["interest_rate"] == 6.5
    assert scheme["tenure_years"] == 3


def test_term_loan_standard():
    """₹1,00,000 capital → project_cost ₹10,00,000 → Term Loan."""
    project_cost = calculate_project_cost(100_000)
    assert project_cost == 1_000_000
    scheme = route_scheme(project_cost)
    assert scheme["scheme_name"] == "Term Loan Scheme"
    assert scheme["interest_rate"] == 8.0
    assert scheme["tenure_years"] == 7


def test_boundary_term_loan():
    """₹5,00,000 capital → project_cost ₹50,00,000 → Term Loan (exactly at ceiling)."""
    project_cost = calculate_project_cost(500_000)
    assert project_cost == 5_000_000
    scheme = route_scheme(project_cost)
    assert scheme["scheme_name"] == "Term Loan Scheme"


def test_exceeds_ceiling():
    """₹5,00,001 capital → project_cost > ₹50,00,000 → Error."""
    project_cost = calculate_project_cost(500_001)
    assert project_cost > 5_000_000
    scheme = route_scheme(project_cost)
    assert scheme["scheme_name"] is None
    assert "error" in scheme


# --- EMI hand-calculation verification ---


def test_emi_hand_calculation():
    """Hand-verify EMI for ₹9,00,000 loan at 8% for 7 years, 6 months moratorium.

    Note: EMI is calculated on the original principal (per spec).
    Interest accrues during moratorium and is added to balance,
    but EMI stays based on original principal.
    """
    loan = 900_000
    rate = 8.0
    tenure = 7
    moratorium = 6

    result = calculate_emi(loan, rate, tenure, moratorium)

    monthly_rate = rate / 12 / 100
    repayment_months = (tenure * 12) - moratorium  # 78 months

    # EMI calculated on original principal (not accrued balance)
    expected_emi = (
        loan
        * monthly_rate
        * (1 + monthly_rate) ** repayment_months
        / ((1 + monthly_rate) ** repayment_months - 1)
    )

    assert result["emi_amount"] == round(expected_emi, 2)
    assert len(result["schedule"]) == tenure * 12

    # Moratorium months should have emi=0
    for i in range(moratorium):
        assert result["schedule"][i]["emi"] == 0

    # Post-moratorium months should have emi > 0
    for i in range(moratorium, len(result["schedule"])):
        assert result["schedule"][i]["emi"] > 0


# --- Full calculation integration ---


def test_full_calculation_micro():
    result = get_full_calculation(14_000)
    assert result["project_cost"] == 140_000
    assert result["scheme_name"] == "Micro Finance Scheme"
    assert result["loan_amount"] == min(140_000 * 0.90, 125_000)
    assert result["emi_schedule"] is not None
    assert len(result["emi_schedule"]) == 36  # 3 years * 12


def test_full_calculation_term():
    result = get_full_calculation(100_000)
    assert result["project_cost"] == 1_000_000
    assert result["scheme_name"] == "Term Loan Scheme"
    assert result["loan_amount"] == min(1_000_000 * 0.90, 4_500_000)
    assert result["emi_schedule"] is not None
    assert len(result["emi_schedule"]) == 84  # 7 years * 12


def test_full_calculation_error():
    result = get_full_calculation(500_001)
    assert result["error"] is not None
    assert result["scheme_name"] is None
