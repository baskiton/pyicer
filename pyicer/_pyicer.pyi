from typing import Literal, Union


def decompress(
        data: bytes,
        stages: int = 4,
        segments: int = 6,
        filter: Literal['A', 'B', 'C', 'D', 'E', 'F', 'Q'] = 'A',
        color=1) -> tuple[Union[tuple, bytes], int, int]:
    pass
