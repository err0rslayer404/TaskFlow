import heapq
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Any

class TaskPriorityQueue:
    """
    Min-Heap Priority Queue implementation for Smart Task Scheduling.
    
    Order of precedence:
    1. Priority value (1 = High, 2 = Medium, 3 = Low) -> Lower integer has higher urgency
    2. Deadline timestamp (earlier deadline timestamp has higher urgency)
    3. Task ID (lower task ID acts as deterministic tie-breaker)
    
    Time Complexities:
    - Push: O(log n)
    - Pop:  O(log n)
    - Peek: O(1)
    - Size: O(1)
    - Build from list: O(n) via heapify or O(n log n) sequential pushes
    """
    
    def __init__(self):
        # The internal list used as the min-heap
        self._heap: List[Tuple[int, float, int, Any]] = []

    def _get_deadline_timestamp(self, deadline: Any) -> float:
        """Helper to convert task deadline datetime to a unix timestamp."""
        if isinstance(deadline, datetime):
            if deadline.tzinfo is None:
                # If naive, assume UTC
                deadline = deadline.replace(tzinfo=timezone.utc)
            return deadline.timestamp()
        elif isinstance(deadline, (int, float)):
            return float(deadline)
        return float('inf')

    def push(self, task: Any) -> None:
        """
        Push a task into the priority queue.
        Heap key: (priority, deadline_timestamp, task_id, task)
        Time complexity: O(log n)
        """
        deadline_ts = self._get_deadline_timestamp(task.deadline)
        # Priority mapping fallback: default to 2 (Medium) if missing
        priority = getattr(task, 'priority', 2)
        task_id = getattr(task, 'id', 0)

        # Store tuple in min-heap: (priority, deadline_timestamp, task_id, task)
        heapq.heappush(self._heap, (priority, deadline_ts, task_id, task))

    def pop(self) -> Optional[Any]:
        """
        Pop and return the highest-urgency task from the priority queue.
        Time complexity: O(log n)
        """
        if not self._heap:
            return None
        _, _, _, task = heapq.heappop(self._heap)
        return task

    def peek(self) -> Optional[Any]:
        """
        Return the highest-urgency task without removing it from the queue.
        Time complexity: O(1)
        """
        if not self._heap:
            return None
        return self._heap[0][3]

    def is_empty(self) -> bool:
        """Check if the priority queue is empty. Time complexity: O(1)"""
        return len(self._heap) == 0

    def size(self) -> int:
        """Return the count of elements in the priority queue. Time complexity: O(1)"""
        return len(self._heap)

    def to_sorted_list(self) -> List[Any]:
        """
        Return all tasks in priority order by popping until empty.
        Note: Consumes the internal heap or operates on a clone.
        Time complexity: O(n log n)
        """
        temp_heap = list(self._heap)
        sorted_tasks = []
        while temp_heap:
            _, _, _, task = heapq.heappop(temp_heap)
            sorted_tasks.append(task)
        return sorted_tasks

    @classmethod
    def from_tasks(cls, tasks: List[Any]) -> 'TaskPriorityQueue':
        """
        Factory method to construct and populate a TaskPriorityQueue from a collection of tasks.
        """
        pq = cls()
        for task in tasks:
            pq.push(task)
        return pq
