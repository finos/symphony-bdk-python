from copy import deepcopy
from unittest.mock import AsyncMock

import pytest

from symphony.bdk.core.client.trace_id import (
    TRACE_ID_LENGTH,
    X_TRACE_ID,
    DistributedTracingContext,
    add_x_trace_id,
)


def setup_function():
    DistributedTracingContext.clear()


def assert_args_except_trace_id_kept_as_is(input_args, actual_args):
    assert actual_args[0:3] == input_args[0:3]

    if len(actual_args) >= 4:
        assert X_TRACE_ID in actual_args[4]
        assert {k: actual_args[4][k] for k in actual_args[4].keys() - {X_TRACE_ID}} == input_args[4]

    if len(actual_args) >= 5:
        assert actual_args[5:] == input_args[5:]


def test_empty_tracing_context():
    assert not DistributedTracingContext.has_trace_id()
    assert DistributedTracingContext.get_trace_id() == ""
    assert not DistributedTracingContext.is_trace_id_set_by_user()


def test_set_trace_id():
    trace_id = "trace-id"
    DistributedTracingContext.set_trace_id(trace_id)

    assert DistributedTracingContext.has_trace_id()
    assert DistributedTracingContext.get_trace_id() == trace_id
    assert DistributedTracingContext.is_trace_id_set_by_user()


def test_set_new_trace_id():
    DistributedTracingContext.set_new_trace_id()

    assert DistributedTracingContext.has_trace_id()
    assert len(DistributedTracingContext.get_trace_id()) == TRACE_ID_LENGTH
    assert not DistributedTracingContext.is_trace_id_set_by_user()


def test_clear_trace_id():
    DistributedTracingContext.set_trace_id("trace-id")
    DistributedTracingContext.clear()

    assert not DistributedTracingContext.has_trace_id()
    assert DistributedTracingContext.get_trace_id() == ""
    assert not DistributedTracingContext.is_trace_id_set_by_user()


@pytest.mark.asyncio
async def test_add_x_trace_id_no_trace_id_set_args_length_too_short():
    args = ["a", 2, "b", 3]
    func_return_value = "value"

    func = AsyncMock()
    func.return_value = func_return_value

    actual_return_value = await add_x_trace_id(func)(*deepcopy(args))

    assert DistributedTracingContext.has_trace_id()
    assert len(DistributedTracingContext.get_trace_id()) == TRACE_ID_LENGTH

    assert actual_return_value == func_return_value
    func.assert_awaited_once_with(*args)


@pytest.mark.asyncio
async def test_add_x_trace_id_no_trace_id_set_args_length_long_enough():
    args = ["a", 2, "b", 3, {"key": "value"}, "c", 4]
    func_return_value = "value"

    func = AsyncMock()
    func.return_value = func_return_value

    actual_return_value = await add_x_trace_id(func)(*deepcopy(args))

    assert actual_return_value == func_return_value
    func.assert_awaited_once()

    actual_args = list(func.call_args.args)

    assert_args_except_trace_id_kept_as_is(args, actual_args)
    assert len(actual_args[4][X_TRACE_ID]) == TRACE_ID_LENGTH


@pytest.mark.asyncio
async def test_add_x_trace_id_trace_id_set_args_length_too_short():
    args = ["a", 2, "b", 3]
    func_return_value = "value"
    trace_id = "trace-id"

    func = AsyncMock()
    func.return_value = func_return_value

    DistributedTracingContext.set_trace_id(trace_id)
    actual_return_value = await add_x_trace_id(func)(*deepcopy(args))

    assert DistributedTracingContext.get_trace_id() == trace_id

    assert actual_return_value == func_return_value
    func.assert_awaited_once_with(*args)


@pytest.mark.asyncio
async def test_add_x_trace_id_trace_id_set_args_length_long_enough():
    args = ["a", 2, "b", 3, {"key": "value"}, "c", 4]
    func_return_value = "value"
    trace_id = "trace-id"

    func = AsyncMock()
    func.return_value = func_return_value

    DistributedTracingContext.set_trace_id(trace_id)
    actual_return_value = await add_x_trace_id(func)(*deepcopy(args))

    assert actual_return_value == func_return_value
    func.assert_awaited_once()

    actual_args = list(func.call_args.args)

    assert_args_except_trace_id_kept_as_is(args, actual_args)
    assert actual_args[4][X_TRACE_ID] == trace_id


@pytest.mark.asyncio
async def test_add_x_trace_id_trace_id_set_several_calls():
    args = ["a", 2, "b", 3, {"key": "value"}, "c", 4]
    trace_id = "trace-id"

    func = AsyncMock()

    DistributedTracingContext.set_trace_id(trace_id)
    await add_x_trace_id(func)(*deepcopy(args))
    await add_x_trace_id(func)(*deepcopy(args))

    first_trace_id = func.call_args_list[0].args[4][X_TRACE_ID]
    second_trace_id = func.call_args_list[1].args[4][X_TRACE_ID]

    assert first_trace_id == trace_id
    assert second_trace_id == trace_id


@pytest.mark.asyncio
async def test_add_x_trace_id_trace_id_not_set_several_calls():
    args = ["a", 2, "b", 3, {"key": "value"}, "c", 4]

    func = AsyncMock()

    await add_x_trace_id(func)(*deepcopy(args))
    await add_x_trace_id(func)(*deepcopy(args))

    first_trace_id = func.call_args_list[0].args[4][X_TRACE_ID]
    second_trace_id = func.call_args_list[1].args[4][X_TRACE_ID]

    assert first_trace_id != second_trace_id
    assert len(first_trace_id) == TRACE_ID_LENGTH
    assert len(second_trace_id) == TRACE_ID_LENGTH
