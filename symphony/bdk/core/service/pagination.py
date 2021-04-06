"""This module takes care of creating generators from paginated endpoints, so that user do not have to care about
making several calls to the same endpoint with the correct pagination values.
"""
from typing import AsyncGenerator, TypeVar, Callable, Awaitable, Tuple

T = TypeVar('T')


async def offset_based_pagination(func: Callable[[int, int], Awaitable[T]],
                                  chunk_size=50, max_number=None) -> AsyncGenerator[T, None]:
    """Creates an asynchronous generator from a paginated endpoint. The generator makes the call to the underlying
    endpoint `func` until the `max_number` of items is reached or results are exhausted (i.e. `func` is None or empty).

    :param func: a coroutine taking two int parameters: `skip` (a.k.a offset) and `limit` (max number for items to
      retrieve in one call) and returning a list.
    :param chunk_size: the maximum number of elements to retrieve in one call.
    :param max_number: the maximum total number of items to retrieve. If not specified or set to None, it will fetch all
      items until we retrieved all elements.
    :return: an asynchronous generator of elements which makes the calls to `func` with the correct parameters.
    """
    if max_number is not None and max_number <= 0:
        return

    skip = 0
    item_count = 0

    chunk = await func(skip, chunk_size)
    while chunk:
        for item in chunk:
            yield item

            item_count += 1
            if max_number is not None and item_count == max_number:
                # max_number items already retrieved
                return

        if len(chunk) < chunk_size:
            # received chunk has less elements than the sent chunk size: we are already at the end
            return

        skip += chunk_size
        chunk = await func(skip, chunk_size)


async def cursor_based_pagination(func: Callable[[int, str], Awaitable[Tuple[T, str]]],
                                  chunk_size=100, max_number=None) -> AsyncGenerator[T, None]:
    """Creates an asynchronous generator from a cursor based endpoint. The generator makes the call to the underlying
    endpoint `func` until the `max_number` of items is reached or results are exhausted (i.e. cursor returned by `func`
    is None).

    :param func: a coroutine taking two int parameters: limit (max number for items to retrieve
      in one call) and after (for cursor based pagination).
      It must return a tuple `(result, after)` where `result` is a list containing the actual results in the chunk and
      `after` is the new cursor which will be passed to the next call to `func`.
    :param chunk_size: the maximum number of elements to retrieve in one call.
    :param max_number: the maximum total number of items to retrieve. If not specified or set to None, it will fetch all
      items until we retrieved all elements.
    :return: an asynchronous generator of elements which makes the calls to `func` with the correct parameters.
    """
    if max_number is not None and max_number <= 0:
        return

    after = None
    item_count = 0

    while True:
        (result, after) = await func(chunk_size, after)
        if result is None:
            result = []

        for item in result:
            yield item

            item_count += 1
            if max_number is not None and item_count == max_number:
                # max_number items already retrieved
                return

        if after is None:
            # we exhausted the results
            break
