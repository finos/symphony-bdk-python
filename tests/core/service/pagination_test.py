from unittest.mock import AsyncMock, call

import pytest

from symphony.bdk.core.service.pagination import generator

CHUNK_SIZE = 2


async def assert_generator_produces(func_responses, max_number, expected_output, expected_calls):
    mock_func = AsyncMock()
    mock_func.side_effect = func_responses

    assert [x async for x in generator(mock_func, CHUNK_SIZE, max_number)] == expected_output
    mock_func.assert_has_awaits(expected_calls)


@pytest.mark.asyncio
async def test_empty_answer():
    await assert_generator_produces(func_responses=[[]], max_number=None,
                                    expected_output=[],
                                    expected_calls=[call(0, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_answer_less_than_one_chunk():
    await assert_generator_produces(func_responses=[["one"]], max_number=None,
                                    expected_output=["one"],
                                    expected_calls=[call(0, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_answer_same_length_than_one_chunk():
    await assert_generator_produces(func_responses=[["one", "two"], []], max_number=None,
                                    expected_output=["one", "two"],
                                    expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_answer_more_than_one_chunk_less_than_two_chunks():
    await assert_generator_produces(func_responses=[["one", "two"], ["three"]], max_number=None,
                                    expected_output=["one", "two", "three"],
                                    expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_answer_two_chunks():
    await assert_generator_produces(func_responses=[["one", "two"], ["three", "four"], []], max_number=None,
                                    expected_output=["one", "two", "three", "four"],
                                    expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE),
                                                    call(2 * CHUNK_SIZE, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_negative_max_number():
    await assert_generator_produces(func_responses=[[]], max_number=-1,
                                    expected_output=[],
                                    expected_calls=[])


@pytest.mark.asyncio
async def test_zero_max_number():
    await assert_generator_produces(func_responses=[[]], max_number=0,
                                    expected_output=[],
                                    expected_calls=[])


@pytest.mark.asyncio
async def test_max_number_less_than_one_chunk():
    await assert_generator_produces(func_responses=[["one", "two"]], max_number=1,
                                    expected_output=["one"],
                                    expected_calls=[call(0, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_max_number_equals_one_chunk():
    await assert_generator_produces(func_responses=[["one", "two"]], max_number=CHUNK_SIZE,
                                    expected_output=["one", "two"],
                                    expected_calls=[call(0, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_max_number_equals_more_than_one_chunk():
    await assert_generator_produces(func_responses=[["one", "two"], ["three", "four"]], max_number=3,
                                    expected_output=["one", "two", "three"],
                                    expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_func_returns_none():
    await assert_generator_produces(func_responses=[None], max_number=None,
                                    expected_output=[],
                                    expected_calls=[call(0, CHUNK_SIZE)])


@pytest.mark.asyncio
async def test_func_second_chunk_returns_none():
    await assert_generator_produces(func_responses=[["one", "two"], None], max_number=None,
                                    expected_output=["one", "two"],
                                    expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)])
