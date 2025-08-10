import numpy as np

import _pyicer


def _yuv_to_rgb(y, u, v):
    yuv_to_rgb_matrix = np.array([
        [1, 0, 1.402],
        [1, -0.344136, -0.714136],
        [1, 1.772, 0]
    ])
    yuv_combined = np.stack([y, u - 128, v - 128], axis=-1)
    rgb_data = np.dot(yuv_combined, yuv_to_rgb_matrix.T)
    return np.clip(rgb_data, 0, 255).astype(np.uint8)

###############################################################################


def compress(data, stages=4, segments=6, filter='A', color=1):
    raise NotImplementedError


def decompress(data, stages=4, segments=6, filter='A', color=1):
    """
    Decompress ICER image

    :type data: bytes
    :param data: compressed image data
    :type stages: int
    :param stages: 1 - 6
    :type segments: int
    :param segments: 1 - 32
    :type filter: Literal['A', 'B', 'C', 'D', 'E', 'F', 'Q']
    :param filter: filter type, one of A, B, C, D, E, F, Q
    :type color: int|bool
    :param color: color image or not
    :rtype: ndarray
    :return: array of imgdata
    """

    img_data, w, h = _pyicer.decompress(data, stages, segments, filter, color)

    if color:
        rgb = _yuv_to_rgb(
            np.frombuffer(img_data[0], np.int16),
            np.frombuffer(img_data[1], np.int16),
            np.frombuffer(img_data[2], np.int16),
        )
        return rgb.reshape((h, w, 3))

    else:
        return np.frombuffer(img_data, np.int16).clip(0, 255).astype(np.uint8).reshape((h, w))
