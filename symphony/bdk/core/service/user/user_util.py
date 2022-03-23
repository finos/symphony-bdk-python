"""Module containing utility function to extract the tenant ID from a user ID.
The user ID is a combination of a unique tenant ID, and a unique sub-tenant ID, combined into a number.
The tenant ID is stored in the 27 highest bits (minus the sign bit which is unused so that all IDs remain a
positive value) which allows for 134 million pods.
This leaves 36 lowest bits for the user ID, which allows 68.7 billion users per tenant.
"""
TENANT_ID_BIT_LENGTH = 27
SUBTENANT_ID_BIT_LENGTH = 36
TENANT_ID_INDEX = 1


def extract_tenant_id(user_id: int):
    """Extracts the tenant ID from a user ID.

    :param user_id: the user ID.
    :return: the tenant ID.
    """
    number_util = NumberUtil(sizes=[SUBTENANT_ID_BIT_LENGTH, TENANT_ID_BIT_LENGTH])
    return number_util.extract(user_id, TENANT_ID_INDEX)


class NumberUtil:
    """Used to compute the segments bases in the input sizes
    """

    def __init__(self, sizes: []):
        self._segments = []
        self._total_size = 0
        self._shift = 0

        for size in sizes:
            segment = Segment(size, self._shift)
            self._shift += size
            self._segments.append(segment)
            self._total_size += size

        if self._total_size > 64:
            raise ValueError("total size is larger than the bit-count of 64")

    def extract(self, value: int, index: int):
        """Extract the tenant_id given the user_id and the index
        """
        segment = self._segments[index]
        return value >> segment._shift & segment._mask


class Segment:
    """Helper class to initialize a Segment
    """

    def __init__(self, size: int, shift: int):
        mask = 0
        for _ in range(size):
            mask |= 1
            mask <<= 1

        mask >>= 1
        self._mask = mask
        self._shift = shift
