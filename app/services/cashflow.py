def project_cash_flow(
    calculator_output: dict, category_data: dict, months: int = 12
) -> dict:
    emi_schedule = calculator_output["emi_schedule"]
    setup_cost = calculator_output["project_cost"] * category_data["setup_cost_ratio"]
    monthly_operating_cost = category_data["monthly_operating_cost"]

    monthly_flows = []
    cumulative_balance = -setup_cost
    negative_month = None
    negative_gap = 0.0

    for month in range(1, months + 1):
        if month <= category_data["ramp_up_months"]:
            units = category_data["avg_units_sold_month1"] + (
                category_data["steady_state_units_sold"]
                - category_data["avg_units_sold_month1"]
            ) * (month - 1) / category_data["ramp_up_months"]
        else:
            units = category_data["steady_state_units_sold"]

        revenue = units * category_data["avg_unit_price"]
        emi_this_month = emi_schedule[month - 1]["emi"]
        net_this_month = revenue - monthly_operating_cost - emi_this_month
        cumulative_balance += net_this_month

        monthly_flows.append(
            {
                "month": month,
                "revenue": round(revenue, 2),
                "operating_cost": monthly_operating_cost,
                "emi": emi_this_month,
                "net_this_month": round(net_this_month, 2),
                "cumulative_balance": round(cumulative_balance, 2),
            }
        )

        # Flags the first month (if any) where cumulative net position goes
        # negative — including month 1, since a large upfront setup cost
        # relative to capital is exactly the kind of risk this is meant to catch.
        if cumulative_balance < 0 and negative_month is None:
            negative_month = month
            negative_gap = round(abs(cumulative_balance), 2)

    return {
        "monthly": monthly_flows,
        "negative_month": negative_month,
        "negative_gap": negative_gap,
    }