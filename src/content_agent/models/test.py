"""Test job data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TestJobStatus(str, Enum):
    """Test job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


class TestScenarioStatus(str, Enum):
    """Individual test scenario status."""

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIP = "skip"


class TestJobId(BaseModel):
    """Test job identifier returned when starting tests."""

    job_id: str = Field(..., description="Unique job identifier")
    product: str = Field(..., description="Product being tested")
    rule_id: Optional[str] = Field(None, description="Rule ID if testing single rule")
    profile_id: Optional[str] = Field(None, description="Profile ID if testing profile")
    message: str = Field(..., description="Informational message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "job_id": "test_1234567890",
                "product": "rhel9",
                "rule_id": "sshd_set_idle_timeout",
                "profile_id": None,
                "message": "Test job submitted successfully",
            }
        }


class TestScenarioResult(BaseModel):
    """Result of a single test scenario."""

    scenario: str = Field(..., description="Test scenario name")
    status: TestScenarioStatus = Field(..., description="Scenario status")
    remediation: Optional[str] = Field(
        None, description="Remediation type tested (bash, ansible, etc.)"
    )
    duration_seconds: Optional[float] = Field(None, description="Scenario duration in seconds")
    output: str = Field(default="", description="Test output")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "scenario": "correct_value.pass.sh",
                "status": "pass",
                "remediation": "bash",
                "duration_seconds": 5.2,
                "output": "Test passed: SSH timeout is set correctly",
            }
        }


class TestResults(BaseModel):
    """Results of test execution."""

    job_id: str = Field(..., description="Job identifier")
    status: TestJobStatus = Field(..., description="Overall job status")
    product: str = Field(..., description="Product tested")
    rule_id: Optional[str] = Field(None, description="Rule ID if testing single rule")
    profile_id: Optional[str] = Field(None, description="Profile ID if testing profile")
    started_at: datetime = Field(..., description="When tests started")
    completed_at: Optional[datetime] = Field(None, description="When tests completed")
    duration_seconds: Optional[float] = Field(None, description="Total duration in seconds")
    total: int = Field(..., description="Total number of test scenarios")
    passed: int = Field(default=0, description="Number of passed scenarios")
    failed: int = Field(default=0, description="Number of failed scenarios")
    error: int = Field(default=0, description="Number of errored scenarios")
    skip: int = Field(default=0, description="Number of skipped scenarios")
    scenarios: List[TestScenarioResult] = Field(
        default_factory=list, description="Individual scenario results"
    )
    logs: str = Field(default="", description="Full test logs")
    error_message: Optional[str] = Field(None, description="Error message if job failed")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "job_id": "test_1234567890",
                "status": "completed",
                "product": "rhel9",
                "rule_id": "sshd_set_idle_timeout",
                "profile_id": None,
                "started_at": "2026-01-28T10:35:00Z",
                "completed_at": "2026-01-28T10:40:30Z",
                "duration_seconds": 330.0,
                "total": 6,
                "passed": 5,
                "failed": 1,
                "error": 0,
                "skip": 0,
                "scenarios": [
                    {
                        "scenario": "correct_value.pass.sh",
                        "status": "pass",
                        "remediation": "bash",
                        "duration_seconds": 5.2,
                        "output": "Test passed",
                    }
                ],
                "logs": "Starting tests...\nTest 1/6: correct_value.pass.sh...",
            }
        }
