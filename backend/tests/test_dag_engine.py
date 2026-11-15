import pytest
from app.orchestrator.dag_engine import (
    DAGEngine,
    CycleDetectedError,
    MissingDependencyError,
)


def test_empty_dag():
    ordered, batches = DAGEngine.validate_and_order([])
    assert ordered == []
    assert batches == []


def test_linear_dag():
    tasks = [
        {"task_key": "T1", "title": "Database Schema", "assigned_agent": "database_engineer", "dependencies": []},
        {"task_key": "T2", "title": "Auth API", "assigned_agent": "backend_developer", "dependencies": ["T1"]},
        {"task_key": "T3", "title": "Login UI", "assigned_agent": "frontend_developer", "dependencies": ["T2"]},
    ]
    ordered, batches = DAGEngine.validate_and_order(tasks)
    assert len(ordered) == 3
    assert [t["task_key"] for t in ordered] == ["T1", "T2", "T3"]
    assert batches == [["T1"], ["T2"], ["T3"]]
    assert ordered[0]["tier"] == 0
    assert ordered[1]["tier"] == 1
    assert ordered[2]["tier"] == 2


def test_branch_and_merge_dag():
    r"""
    Diamond DAG:
          T1 (tier 0)
         /  \
        T2   T3 (tier 1: parallel)
         \  /
          T4 (tier 2)
    """
    tasks = [
        {"task_key": "T1", "title": "DB Models", "assigned_agent": "database_engineer", "dependencies": []},
        {"task_key": "T2", "title": "Auth API", "assigned_agent": "backend_developer", "dependencies": ["T1"]},
        {"task_key": "T3", "title": "Student API", "assigned_agent": "backend_developer", "dependencies": ["T1"]},
        {"task_key": "T4", "title": "Integration Tests", "assigned_agent": "tester", "dependencies": ["T2", "T3"]},
    ]
    ordered, batches = DAGEngine.validate_and_order(tasks)
    assert len(ordered) == 4
    assert batches[0] == ["T1"]
    assert set(batches[1]) == {"T2", "T3"}
    assert batches[2] == ["T4"]

    # Verify orders
    keys = [t["task_key"] for t in ordered]
    assert keys.index("T1") < keys.index("T2")
    assert keys.index("T1") < keys.index("T3")
    assert keys.index("T2") < keys.index("T4")
    assert keys.index("T3") < keys.index("T4")


def test_cycle_detection():
    tasks = [
        {"task_key": "T1", "title": "Task 1", "assigned_agent": "backend_developer", "dependencies": ["T2"]},
        {"task_key": "T2", "title": "Task 2", "assigned_agent": "backend_developer", "dependencies": ["T1"]},
    ]
    with pytest.raises(CycleDetectedError) as exc_info:
        DAGEngine.validate_and_order(tasks)
    assert "Circular dependency detected" in str(exc_info.value)


def test_self_cycle_detection():
    tasks = [
        {"task_key": "T1", "title": "Self Looping", "assigned_agent": "backend_developer", "dependencies": ["T1"]},
    ]
    with pytest.raises(CycleDetectedError) as exc_info:
        DAGEngine.validate_and_order(tasks)
    assert "cannot depend on itself" in str(exc_info.value)


def test_missing_dependency():
    tasks = [
        {"task_key": "T1", "title": "Task 1", "assigned_agent": "backend_developer", "dependencies": ["NON_EXISTENT"]},
    ]
    with pytest.raises(MissingDependencyError) as exc_info:
        DAGEngine.validate_and_order(tasks)
    assert "depends on non-existent task 'NON_EXISTENT'" in str(exc_info.value)
