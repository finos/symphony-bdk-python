from typing import AsyncGenerator, TypeVar, Callable, Awaitable

T = TypeVar('T')


async def generator(func: Callable[[int, int], Awaitable[T]], chunk_size=50, max_number=None) \
        -> AsyncGenerator[T, None]:
    """Creates an asynchronous generator from a paginated endpoint. The generators makes the call to the underlying
    endpoint `func` until the `max_number` of items is reached or results are exhausted.

    :param func: a coroutine taking two int parameters: skip (a.k.a offset) and limit (max number for items to retrieve
      in one call) and returning a list.
    :param chunk_size: the maximum number of elements to retrieve in one call.
    :param max_number: the maximum total number of items to retrieve. If not specified or set to None, it will fetch all
      items until we retrieved all elements.
    :return: an asynchronous generator of elements which makes the calls to `func` with the correct parameters
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
