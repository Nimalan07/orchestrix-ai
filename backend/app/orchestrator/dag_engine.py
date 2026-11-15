from collections import defaultdict, deque
from typing import Dict, List, Set, Any, Tuple


class CycleDetectedError(ValueError):
    """Raised when a circular dependency is detected in the task graph."""
    pass


class MissingDependencyError(ValueError):
    """Raised when a task depends on an unknown task key."""
    pass


class DAGEngine:
    """
    Deterministic Directed Acyclic Graph (DAG) Engine.
    Handles dependency validation, cycle detection, topological sorting,
    and concurrent execution tier (batch) scheduling.
    """

    @staticmethod
    def validate_and_order(tasks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[List[str]]]:
        """
        Validates the task graph, checks for missing dependencies, detects cycles,
        and returns:
          1. The topologically ordered list of tasks (with 'execution_order' and 'tier' populated)
          2. The parallel execution batches (list of task key lists by tier)
        """
        if not tasks:
            return [], []

        task_map = {t["task_key"]: t for t in tasks}
        task_keys = set(task_map.keys())

        # 1. Validate dependencies exist
        adj: Dict[str, List[str]] = defaultdict(list)  # dependency -> dependents
        in_degree: Dict[str, int] = {k: 0 for k in task_keys}

        for t in tasks:
            key = t["task_key"]
            deps = t.get("dependencies", []) or []
            for dep in deps:
                if dep == key:
                    raise CycleDetectedError(f"Task '{key}' cannot depend on itself.")
                if dep not in task_keys:
                    raise MissingDependencyError(
                        f"Task '{key}' depends on non-existent task '{dep}'."
                    )
                adj[dep].append(key)
                in_degree[key] += 1

        # 2. Kahn's Algorithm for Topological Sort & Layer/Tier assignment
        queue = deque([k for k, deg in in_degree.items() if deg == 0])
        topological_keys: List[str] = []
        task_tiers: Dict[str, int] = {}

        # Initialize tier 0 for roots
        for k in queue:
            task_tiers[k] = 0

        while queue:
            curr = queue.popleft()
            topological_keys.append(curr)
            curr_tier = task_tiers[curr]

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                # The neighbor's tier must be at least curr_tier + 1
                task_tiers[neighbor] = max(task_tiers.get(neighbor, 0), curr_tier + 1)
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 3. Check for cycles
        if len(topological_keys) != len(task_keys):
            unresolved = [k for k, deg in in_degree.items() if deg > 0]
            cycle_path = DAGEngine._find_cycle_path(adj, unresolved)
            raise CycleDetectedError(
                f"Circular dependency detected among tasks: {' -> '.join(cycle_path) if cycle_path else unresolved}"
            )

        # 4. Group into parallel execution batches
        batches_dict: Dict[int, List[str]] = defaultdict(list)
        for k in topological_keys:
            tier = task_tiers[k]
            batches_dict[tier].append(k)

        sorted_tiers = sorted(batches_dict.keys())
        parallel_batches = [batches_dict[tier] for tier in sorted_tiers]

        # 5. Build enriched ordered tasks
        ordered_tasks: List[Dict[str, Any]] = []
        for order_idx, k in enumerate(topological_keys):
            task_copy = dict(task_map[k])
            task_copy["execution_order"] = order_idx
            task_copy["tier"] = task_tiers[k]
            ordered_tasks.append(task_copy)

        return ordered_tasks, parallel_batches

    @staticmethod
    def _find_cycle_path(adj: Dict[str, List[str]], nodes: List[str]) -> List[str]:
        """Find an explicit cycle path for human-readable error reporting."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    path.append(neighbor)
                    return True

            rec_stack.remove(node)
            path.pop()
            return False

        for node in nodes:
            if node not in visited:
                if dfs(node):
                    # Trim path to only the cycle
                    cycle_start = path[-1]
                    start_idx = path.index(cycle_start)
                    return path[start_idx:]
        return []
