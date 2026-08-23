import pytest
from arb_engine.distribution import Allocation, ProfitAllocator


def test_profit_is_split_by_percentage():
    allocator = ProfitAllocator([
        Allocation("a", 50, "A"),
        Allocation("b", 30, "B"),
        Allocation("reserve", 20, "R"),
    ])
    assert allocator.allocate_profit(100) == {"a": 50, "b": 30, "reserve": 20}


def test_allocations_must_total_one_hundred():
    with pytest.raises(ValueError):
        ProfitAllocator([Allocation("a", 60, "A")])
