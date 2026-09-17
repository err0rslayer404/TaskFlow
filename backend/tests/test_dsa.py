import pytest
from datetime import datetime, timezone, timedelta
from backend.dsa.priority_queue import TaskPriorityQueue

class MockTask:
    def __init__(self, id, title, priority, deadline, category='Study'):
        self.id = id
        self.title = title
        self.priority = priority
        self.deadline = deadline
        self.category = category

def test_priority_queue_empty():
    pq = TaskPriorityQueue()
    assert pq.is_empty() is True
    assert pq.size() == 0
    assert pq.pop() is None
    assert pq.peek() is None

def test_priority_ordering():
    pq = TaskPriorityQueue()
    now = datetime.now(timezone.utc)
    
    t_low = MockTask(1, "Low Priority Task", priority=3, deadline=now + timedelta(hours=1))
    t_high = MockTask(2, "High Priority Task", priority=1, deadline=now + timedelta(hours=5))
    t_med = MockTask(3, "Medium Priority Task", priority=2, deadline=now + timedelta(hours=2))

    pq.push(t_low)
    pq.push(t_high)
    pq.push(t_med)

    assert pq.size() == 3
    assert pq.is_empty() is False

    # Highest priority should be popped first (priority 1)
    first = pq.pop()
    assert first.id == 2
    assert first.priority == 1

    # Next is medium priority (priority 2)
    second = pq.pop()
    assert second.id == 3
    assert second.priority == 2

    # Next is low priority (priority 3)
    third = pq.pop()
    assert third.id == 1
    assert third.priority == 3

    assert pq.is_empty() is True

def test_deadline_tiebreaker():
    """When priorities are identical, earlier deadline should come first."""
    pq = TaskPriorityQueue()
    now = datetime.now(timezone.utc)

    t_later = MockTask(10, "Later High Task", priority=1, deadline=now + timedelta(hours=10))
    t_earlier = MockTask(20, "Earlier High Task", priority=1, deadline=now + timedelta(hours=2))
    t_tomorrow = MockTask(30, "Tomorrow High Task", priority=1, deadline=now + timedelta(days=1))

    pq.push(t_later)
    pq.push(t_tomorrow)
    pq.push(t_earlier)

    # First popped should be t_earlier (2 hours)
    first = pq.pop()
    assert first.id == 20

    # Second popped should be t_later (10 hours)
    second = pq.pop()
    assert second.id == 10

    # Third popped should be t_tomorrow (24 hours)
    third = pq.pop()
    assert third.id == 30

def test_id_tiebreaker():
    """When priorities and deadlines are identical, lower ID comes first."""
    pq = TaskPriorityQueue()
    fixed_time = datetime(2026, 9, 20, 12, 0, 0, tzinfo=timezone.utc)

    t_id_50 = MockTask(50, "Task 50", priority=1, deadline=fixed_time)
    t_id_10 = MockTask(10, "Task 10", priority=1, deadline=fixed_time)
    t_id_25 = MockTask(25, "Task 25", priority=1, deadline=fixed_time)

    pq.push(t_id_50)
    pq.push(t_id_10)
    pq.push(t_id_25)

    assert pq.peek().id == 10
    assert pq.pop().id == 10
    assert pq.pop().id == 25
    assert pq.pop().id == 50

def test_from_tasks_factory():
    now = datetime.now(timezone.utc)
    tasks = [
        MockTask(1, "Task 1", priority=2, deadline=now + timedelta(hours=3)),
        MockTask(2, "Task 2", priority=1, deadline=now + timedelta(hours=1)),
        MockTask(3, "Task 3", priority=3, deadline=now + timedelta(hours=5)),
    ]

    pq = TaskPriorityQueue.from_tasks(tasks)
    assert pq.size() == 3
    assert pq.pop().id == 2
    assert pq.pop().id == 1
    assert pq.pop().id == 3
