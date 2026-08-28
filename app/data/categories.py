CATEGORIES = {
    "Dairy": {
        "monthly_operating_cost": 8000,
        "avg_unit_price": 45,
        "avg_units_sold_month1": 300,
        "ramp_up_months": 3,
        "steady_state_units_sold": 600,
        "setup_cost_ratio": 0.6,
    },
    "Tailoring": {
        "monthly_operating_cost": 5000,
        "avg_unit_price": 300,
        "avg_units_sold_month1": 25,
        "ramp_up_months": 4,
        "steady_state_units_sold": 40,
        "setup_cost_ratio": 0.7,
    },
    "Food Stall": {
        "monthly_operating_cost": 10000,
        "avg_unit_price": 80,
        "avg_units_sold_month1": 300,
        "ramp_up_months": 2,
        "steady_state_units_sold": 500,
        "setup_cost_ratio": 0.5,
    },
    "Kirana Store": {
        "monthly_operating_cost": 12000,
        "avg_unit_price": 500,
        "avg_units_sold_month1": 50,
        "ramp_up_months": 3,
        "steady_state_units_sold": 80,
        "setup_cost_ratio": 0.65,
    },
    "Beauty Salon": {
        "monthly_operating_cost": 6000,
        "avg_unit_price": 250,
        "avg_units_sold_month1": 35,
        "ramp_up_months": 3,
        "steady_state_units_sold": 60,
        "setup_cost_ratio": 0.55,
    },
    "Mobile Repair": {
        "monthly_operating_cost": 4000,
        "avg_unit_price": 500,
        "avg_units_sold_month1": 30,
        "ramp_up_months": 2,
        "steady_state_units_sold": 50,
        "setup_cost_ratio": 0.5,
    },
}


def get_category_data(category: str) -> dict:
    if category not in CATEGORIES:
        available = ", ".join(CATEGORIES.keys())
        raise ValueError(f"Unknown category '{category}'. Available: {available}")
    return CATEGORIES[category]
