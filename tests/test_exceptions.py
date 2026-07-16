import pytest
from pydantic import ValidationError
from app.schemas.error import ErrorDetail, ErrorResponse

def test_error_detail_model():
    error = ErrorDetail(code="VALIDATION_ERROR", message="Field is required", field="username")
    assert error.code == "VALIDATION_ERROR"
    assert error.message == "Field is required"
    assert error.field == "username"

def test_error_response_model():
    detail = ErrorDetail(code="NOT_FOUND", message="Resource could not be found")
    res = ErrorResponse(success=False, error=detail)
    assert res.success is False
    assert res.error.code == "NOT_FOUND"
    assert res.error.message == "Resource could not be found"

def test_pydantic_error_creation():
    with pytest.raises(ValidationError):
        # Missing required 'code' field should raise validation error
        ErrorDetail(message="Missing code")
