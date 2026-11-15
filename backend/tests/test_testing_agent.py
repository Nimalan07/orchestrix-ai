"""
Unit tests for the Testing Agent and Pytest log parsing.
"""

import pytest
from app.agents.testing_agent import testing_agent


def test_generate_default_tests():
    tests = testing_agent.generate_default_tests("Demo App", ["backend/app/main.py"])
    assert len(tests) >= 1
    assert tests[0]["file_path"] == "backend/tests/test_api.py"
    assert "test_root_endpoint" in tests[0]["content"]
    assert "test_health_endpoint" in tests[0]["content"]


def test_parse_pytest_output_all_passed():
    stdout = """
============================= test session starts =============================
backend/tests/test_api.py::test_root_endpoint PASSED                    [ 50%]
backend/tests/test_api.py::test_health_endpoint PASSED                  [100%]
============================== 2 passed in 0.15s ==============================
"""
    report = testing_agent.parse_pytest_output(
        stdout=stdout,
        stderr="",
        duration=0.15,
        exit_code=0,
        sandbox_mode="local_process",
    )

    assert report.total == 2
    assert report.passed == 2
    assert report.failed == 0
    assert report.all_passed is True
    assert len(report.failures) == 0


def test_parse_pytest_output_with_failures():
    stdout = """
============================= test session starts =============================
backend/tests/test_api.py::test_root_endpoint PASSED                    [ 50%]
backend/tests/test_api.py::test_items_endpoint FAILED                   [100%]
=================================== FAILURES ===================================
_____________________________ test_items_endpoint _____________________________
    def test_items_endpoint():
>       assert response.status_code == 200
E       assert 404 == 200
=========================== 1 failed, 1 passed in 0.22s ===========================
"""
    report = testing_agent.parse_pytest_output(
        stdout=stdout,
        stderr="",
        duration=0.22,
        exit_code=1,
        sandbox_mode="local_process",
    )

    assert report.total == 2
    assert report.passed == 1
    assert report.failed == 1
    assert report.all_passed is False
    assert len(report.failures) == 1
    assert report.failures[0].test_name == "test_items_endpoint"
    assert report.failures[0].status == "failed"


def test_parse_pytest_output_collection_error():
    stderr = "ModuleNotFoundError: No module named 'invalid_module'"
    report = testing_agent.parse_pytest_output(
        stdout="",
        stderr=stderr,
        duration=0.05,
        exit_code=2,
        sandbox_mode="docker",
    )

    assert report.all_passed is False
    assert report.errors >= 1
    assert len(report.failures) >= 1
    assert "invalid_module" in report.failures[0].error_message
