from enum import Enum
import json

class DatafeedVersion(str, Enum):
    V1: str = "v1"
    V2: str = "v2"

    @classmethod
    def version_of(cls, version):
        if version.lower() == cls.V2.value:
            return cls.V2
        else:
            return cls.V1


