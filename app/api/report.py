from fastapi import APIRouter, HTTPException

from app.data.categories import get_category_data
from app.models import CashFlowOutput, CalculatorOutput, ReportRequest, ReportResponse
from app.services.calculator import get_full_calculation
from app.services.cashflow import project_cash_flow

router = APIRouter()


@router.post("/api/report", response_model=ReportResponse)
def generate_report(req: ReportRequest):
    calc = get_full_calculation(req.margin_capital)

    if calc.get("error"):
        raise HTTPException(status_code=400, detail=calc["error"])

    try:
        cat = get_category_data(req.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cashflow = project_cash_flow(calc, cat)

    return ReportResponse(
        calculator=CalculatorOutput(**calc),
        cashflow=CashFlowOutput(**cashflow),
    )
