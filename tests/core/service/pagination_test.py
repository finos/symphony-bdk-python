from unittest.mock import AsyncMock, call

import pytest

from symphony.bdk.core.service.pagination import cursor_based_pagination, offset_based_pagination

AFTER = "after"

CHUNK_SIZE = 2


class TestOffsetBasedPagination:
    @staticmethod
    async def assert_generator_produces(
        func_responses, max_number, expected_output, expected_calls
    ):
        mock_func = AsyncMock()
        mock_func.side_effect = func_responses

        assert [
            x async for x in offset_based_pagination(mock_func, CHUNK_SIZE, max_number)
        ] == expected_output
        mock_func.assert_has_awaits(expected_calls)

    @pytest.mark.asyncio
    async def test_empty_answer(self):
        await self.assert_generator_produces(
            func_responses=[[]],
            max_number=None,
            expected_output=[],
            expected_calls=[call(0, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_answer_less_than_one_chunk(self):
        await self.assert_generator_produces(
            func_responses=[["one"]],
            max_number=None,
            expected_output=["one"],
            expected_calls=[call(0, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_answer_same_length_than_one_chunk(self):
        await self.assert_generator_produces(
            func_responses=[["one", "two"], []],
            max_number=None,
            expected_output=["one", "two"],
            expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_answer_more_than_one_chunk_less_than_two_chunks(self):
        await self.assert_generator_produces(
            func_responses=[["one", "two"], ["three"]],
            max_number=None,
            expected_output=["one", "two", "three"],
            expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_answer_two_chunks(self):
        await self.assert_generator_produces(
            func_responses=[["one", "two"], ["three", "four"], []],
            max_number=None,
            expected_output=["one", "two", "three", "four"],
            expected_calls=[
                call(0, CHUNK_SIZE),
                call(CHUNK_SIZE, CHUNK_SIZE),
                call(2 * CHUNK_SIZE, CHUNK_SIZE),
            ],
        )

    @pytest.mark.asyncio
    async def test_negative_max_number(self):
        await self.assert_generator_produces(
            func_responses=[[]], max_number=-1, expected_output=[], expected_calls=[]
        )

    @pytest.mark.asyncio
    async def test_zero_max_number(self):
        await self.assert_generator_produces(
            func_responses=[[]], max_number=0, expected_output=[], expected_calls=[]
        )

    @pytest.mark.asyncio
    async def test_max_number_less_than_one_chunk(self):
        await self.assert_generator_produces(
            func_responses=[["one", "two"]],
            max_number=1,
            expected_output=["one"],
            expected_calls=[call(0, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_max_number_equals_one_chunk(self):
        await self.assert_generator_produces(
            func_responses=[["one", "two"]],
            max_number=CHUNK_SIZE,
            expected_output=["one", "two"],
            expected_calls=[call(0, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_max_number_equals_more_than_one_chunk(self):
        await self.assert_generator_produces(
            func_responses=[["one", "two"], ["three", "four"]],
            max_number=3,
            expected_output=["one", "two", "three"],
            expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_func_returns_none(self):
        await self.assert_generator_produces(
            func_responses=[None],
            max_number=None,
            expected_output=[],
            expected_calls=[call(0, CHUNK_SIZE)],
        )

    @pytest.mark.asyncio
    async def test_func_second_chunk_returns_none(self):
        await self.assert_generator_produces(
            func_responses=[["one", "two"], None],
            max_number=None,
            expected_output=["one", "two"],
            expected_calls=[call(0, CHUNK_SIZE), call(CHUNK_SIZE, CHUNK_SIZE)],
        )


class TestCursorBasedPagination:
    @pytest.mark.asyncio
    async def test_answer_none(self):
        mock_func = AsyncMock()
        mock_func.side_effect = [(None, None)]

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE)] == []
        mock_func.assert_has_awaits([call(CHUNK_SIZE, None)])

    @pytest.mark.asyncio
    async def test_empty_answer(self):
        mock_func = AsyncMock()
        mock_func.side_effect = [([], None)]

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE)] == []
        mock_func.assert_has_awaits([call(CHUNK_SIZE, None)])

    @pytest.mark.asyncio
    async def test_answer_only_one_chunk(self):
        mock_func = AsyncMock()
        mock_func.side_effect = [(["one"], None)]

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE)] == ["one"]
        mock_func.assert_has_awaits([call(CHUNK_SIZE, None)])

    @pytest.mark.asyncio
    async def test_answer_two_chunks(self):
        mock_func = AsyncMock()
        mock_func.side_effect = [(["one", "two"], AFTER), (["three"], None)]

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE)] == [
            "one",
            "two",
            "three",
        ]
        mock_func.assert_has_awaits([call(CHUNK_SIZE, None), call(CHUNK_SIZE, AFTER)])

    @pytest.mark.asyncio
    async def test_negative_max_number(self):
        mock_func = AsyncMock()

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE, -1)] == []
        mock_func.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_zero_max_number(self):
        mock_func = AsyncMock()

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE, 0)] == []
        mock_func.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_max_number_less_than_one_chunk(self):
        mock_func = AsyncMock()
        mock_func.side_effect = [(["one", "two"], AFTER)]

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE, 1)] == ["one"]
        mock_func.assert_has_awaits([call(CHUNK_SIZE, None)])

    @pytest.mark.asyncio
    async def test_max_number_equals_one_chunk(self):
        mock_func = AsyncMock()
        mock_func.side_effect = [(["one", "two"], AFTER)]

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE, 2)] == [
            "one",
            "two",
        ]
        mock_func.assert_has_awaits([call(CHUNK_SIZE, None)])

    @pytest.mark.asyncio
    async def test_max_number_equals_more_than_one_chunk(self):
        mock_func = AsyncMock()
        mock_func.side_effect = [(["one", "two"], AFTER), (["three", "four"], "after_two")]

        assert [x async for x in cursor_based_pagination(mock_func, CHUNK_SIZE, 3)] == [
            "one",
            "two",
            "three",
        ]
        mock_func.assert_has_awaits([call(CHUNK_SIZE, None), call(CHUNK_SIZE, AFTER)])
