MICRO_FINANCE_THRESHOLD = 140_000
TERM_LOAN_MAX = 5_000_000

MICRO_FINANCE = {
    "scheme_name": "Micro Finance Scheme",
    "interest_rate": 6.5,
    "tenure_years": 3,
    "moratorium_months": 3,
    "loan_cap": 125_000,
}

TERM_LOAN = {
    "scheme_name": "Term Loan Scheme",
    "interest_rate": 8.0,
    "tenure_years": 7,
    "moratorium_months": 6,
    "loan_cap": 4_500_000,
}


def calculate_project_cost(margin_capital: float) -> float:
    return margin_capital / 0.10


def calculate_loan_amount(project_cost: float) -> float:
    return project_cost * 0.90


def route_scheme(project_cost: float) -> dict:
    if project_cost <= MICRO_FINANCE_THRESHOLD:
        return dict(MICRO_FINANCE)
    elif project_cost <= TERM_LOAN_MAX:
        return dict(TERM_LOAN)
    else:
        return {
            "scheme_name": None,
            "error": "Project cost exceeds Term Loan Scheme ceiling of ₹50L",
        }


def calculate_emi(
    principal: float,
    annual_rate: float,
    tenure_years: int,
    moratorium_months: int,
) -> dict:
    monthly_rate = annual_rate / 12 / 100
    total_months = tenure_years * 12
    repayment_months = total_months - moratorium_months

    # Interest capitalizes into the balance during moratorium, so EMI must be
    # sized against the post-capitalization balance — not the original
    # principal — or the loan will never fully amortize by the end of tenure.
    balance_at_repayment_start = principal * (1 + monthly_rate) ** moratorium_months

    if monthly_rate == 0:
        emi = balance_at_repayment_start / repayment_months
    else:
        emi = (
            balance_at_repayment_start
            * monthly_rate
            * (1 + monthly_rate) ** repayment_months
            / ((1 + monthly_rate) ** repayment_months - 1)
        )

    schedule = []
    balance = principal
    for month in range(1, total_months + 1):
        if month <= moratorium_months:
            interest_accrued = balance * monthly_rate
            balance += interest_accrued
            schedule.append(
                {
                    "month": month,
                    "emi": 0,
                    "principal_component": 0,
                    "interest_component": round(interest_accrued, 2),
                    "balance": round(balance, 2),
                }
            )
        else:
            interest_component = balance * monthly_rate
            principal_component = emi - interest_component
            balance -= principal_component
            schedule.append(
                {
                    "month": month,
                    "emi": round(emi, 2),
                    "principal_component": round(principal_component, 2),
                    "interest_component": round(interest_component, 2),
                    "balance": round(max(balance, 0), 2),
                }
            )

    return {"emi_amount": round(emi, 2), "schedule": schedule}


def get_full_calculation(margin_capital: float) -> dict:
    project_cost = calculate_project_cost(margin_capital)
    scheme = route_scheme(project_cost)

    if scheme.get("error"):
        return {
            "margin_capital": margin_capital,
            "project_cost": project_cost,
            "loan_amount": None,
            "scheme_name": None,
            "error": scheme["error"],
        }

    loan_amount = calculate_loan_amount(project_cost)
    loan_amount = min(loan_amount, scheme["loan_cap"])

    emi_result = calculate_emi(
        principal=loan_amount,
        annual_rate=scheme["interest_rate"],
        tenure_years=scheme["tenure_years"],
        moratorium_months=scheme["moratorium_months"],
    )

    return {
        "margin_capital": margin_capital,
        "project_cost": project_cost,
        "loan_amount": loan_amount,
        "scheme_name": scheme["scheme_name"],
        "interest_rate": scheme["interest_rate"],
        "tenure_years": scheme["tenure_years"],
        "moratorium_months": scheme["moratorium_months"],
        "emi_amount": emi_result["emi_amount"],
        "emi_schedule": emi_result["schedule"],
    }