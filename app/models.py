from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    margin_capital: float = Field(..., gt=0, description="Margin capital in INR")
    category: str = Field(..., min_length=1, description="Business category")
    location: str = Field(default="default", description="District ID")


class CalculatorOutput(BaseModel):
    margin_capital: float
    project_cost: float
    loan_amount: float
    scheme_name: str | None = None
    error: str | None = None
    interest_rate: float | None = None
    tenure_years: int | None = None
    moratorium_months: int | None = None
    emi_amount: float | None = None
    emi_schedule: list[dict] | None = None


class CashFlowOutput(BaseModel):
    monthly: list[dict]
    negative_month: int | None = None
    negative_gap: float = 0.0


class ReportResponse(BaseModel):
    calculator: CalculatorOutput
    cashflow: CashFlowOutput
