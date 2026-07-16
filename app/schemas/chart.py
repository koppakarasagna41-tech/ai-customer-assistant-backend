from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChartDataItem(BaseModel):
    label: str = Field(..., description="The label for the data point (e.g. date, category)")
    value: float = Field(..., description="The numeric value for the data point")
    extra: Optional[Dict[str, Any]] = Field(default=None, description="Optional extra metadata for the point")

class ChartData(BaseModel):
    chart_type: str = Field(..., description="Type of chart (e.g. line, bar, pie, area)")
    title: str = Field(..., description="Title of the chart")
    data: List[ChartDataItem] = Field(..., description="List of data points")
    x_axis_label: Optional[str] = Field(None, description="Label for the X-axis")
    y_axis_label: Optional[str] = Field(None, description="Label for the Y-axis")
