from typing import Any

from pydantic import BaseModel, Field


class ChartDataItem(BaseModel):
    label: str = Field(..., description="The label for the data point (e.g. date, category)")
    value: float = Field(..., description="The numeric value for the data point")
    extra: dict[str, Any] | None = Field(
        default=None, description="Optional extra metadata for the point"
    )


class ChartData(BaseModel):
    chart_type: str = Field(..., description="Type of chart (e.g. line, bar, pie, area)")
    title: str = Field(..., description="Title of the chart")
    data: list[ChartDataItem] = Field(..., description="List of data points")
    x_axis_label: str | None = Field(None, description="Label for the X-axis")
    y_axis_label: str | None = Field(None, description="Label for the Y-axis")
