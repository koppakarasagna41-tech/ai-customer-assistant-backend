from pydantic import BaseModel, Field
from typing import Optional

class KPIDetail(BaseModel):
    name: str = Field(..., description="Name of the key performance indicator")
    value: float = Field(..., description="Current value of the KPI")
    target: float = Field(..., description="Target value for the KPI")
    unit: str = Field(..., description="Unit of measurement (e.g. %, hours, count, USD)")
    status: str = Field(..., description="Status of the KPI (ON_TRACK, AT_RISK, BEHIND)")
    trend: str = Field(..., description="Trend direction (UP, DOWN, STABLE)")
    change_percentage: float = Field(..., description="Percentage change from the previous period")

class KPIOverview(BaseModel):
    ticket_resolution_rate: KPIDetail = Field(..., description="KPI for ticket resolution rate")
    avg_response_time: KPIDetail = Field(..., description="KPI for average response time")
    customer_satisfaction: KPIDetail = Field(..., description="KPI for customer satisfaction score")
    ai_handling_rate: KPIDetail = Field(..., description="KPI for AI handling rate")
    cost_efficiency: KPIDetail = Field(..., description="KPI for cost efficiency of AI assistance")
