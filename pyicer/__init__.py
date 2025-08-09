import ctypes
import enum

import numpy as np


__version__ = '0.0.1'
__all__ = '__version__', 'IcerStatus', 'IcerFilter', 'decompress'


libicer = ctypes.CDLL('libicer.so')

_icer_init = libicer.icer_init
_icer_init.restype = ctypes.c_int

if _icer_init():
    raise RuntimeError('libicer can\'t initialize')


class IcerStatus(enum.IntEnum):
    RESULT_OK = 0,
    INTEGER_OVERFLOW = -1,
    OUTPUT_BUF_TOO_SMALL = -2,
    TOO_MANY_SEGMENTS = -3,
    TOO_MANY_STAGES = -4,
    BYTE_QUOTA_EXCEEDED = -5,
    BITPLANE_OUT_OF_RANGE = -6,
    DECODER_OUT_OF_DATA = -7,
    DECODED_INVALID_DATA = -8,
    PACKET_COUNT_EXCEEDED = -9,
    FATAL_ERROR = -10,
    INVALID_INPUT = -11,


class IcerFilter(enum.IntEnum):
    A = 0
    B = enum.auto()
    C = enum.auto()
    D = enum.auto()
    E = enum.auto()
    F = enum.auto()
    Q = enum.auto()


_c_icer_get_image_dimensions = libicer.icer_get_image_dimensions
_c_icer_get_image_dimensions.argtypes = (
    ctypes.c_char_p,                    # datastream
    ctypes.c_size_t,                    # data_length
    ctypes.POINTER(ctypes.c_size_t),    # image_w
    ctypes.POINTER(ctypes.c_size_t),    # image_h
)
_c_icer_get_image_dimensions.restype = ctypes.c_int
def _icer_get_image_dimensions(data):
    w = ctypes.c_size_t()
    h = ctypes.c_size_t()

    res = _c_icer_get_image_dimensions(data, len(data), w, h)
    res = IcerStatus(res)
    if res != IcerStatus.RESULT_OK:
        raise ValueError(f'Image Dimensions failed: {res.name}')
    return w.value, h.value

_c_icer_decompress_image_yuv_uint16 = libicer.icer_decompress_image_yuv_uint16
_c_icer_decompress_image_yuv_uint16.argtypes = (
    ctypes.POINTER(ctypes.c_int16),     # y_channel
    ctypes.POINTER(ctypes.c_int16),     # u_channel
    ctypes.POINTER(ctypes.c_int16),     # v_channel
    ctypes.POINTER(ctypes.c_size_t),    # image_w
    ctypes.POINTER(ctypes.c_size_t),    # image_h
    ctypes.c_size_t,                    # image_bufsize
    ctypes.c_char_p,                    # datastream
    ctypes.c_size_t,                    # data_length
    ctypes.c_uint8,                     # stages
    ctypes.c_int,                       # filter
    ctypes.c_uint8,                     # segments
)
_c_icer_decompress_image_yuv_uint16.restype = ctypes.c_int
def _icer_decompress_image_yuv_uint16(data, w, h, stages, filter, segments):
    ch_arr = ctypes.c_int16 * (w * h)
    y = ch_arr()
    u = ch_arr()
    v = ch_arr()
    act_w = ctypes.c_size_t()
    act_h = ctypes.c_size_t()

    res = _c_icer_decompress_image_yuv_uint16(y, u, v, act_w, act_h, w * h, data, len(data), stages, filter, segments)
    res = IcerStatus(res)
    if res != IcerStatus.RESULT_OK:
        raise ValueError(f'Decompression failed: {res.name}')
    return y, u, v, act_w, act_h


_c_icer_decompress_image_uint16 = libicer.icer_decompress_image_uint16
_c_icer_decompress_image_uint16.argtypes = (
    ctypes.POINTER(ctypes.c_int16),     # image
    ctypes.POINTER(ctypes.c_size_t),    # image_w
    ctypes.POINTER(ctypes.c_size_t),    # image_h
    ctypes.c_size_t,                    # image_bufsize
    ctypes.c_char_p,                    # datastream
    ctypes.c_size_t,                    # data_length
    ctypes.c_uint8,                     # stages
    ctypes.c_int,                       # filter
    ctypes.c_uint8,                     # segments
)
_c_icer_decompress_image_uint16.restype = ctypes.c_int
def _icer_decompress_image_uint16(data, w, h, stages, filter, segments):
    v = (ctypes.c_int16 * (w * h))()
    act_w = ctypes.c_size_t()
    act_h = ctypes.c_size_t()

    res = _c_icer_decompress_image_uint16(v, act_w, act_h, w * h, data, len(data), stages, filter, segments)
    if res != IcerStatus.RESULT_OK:
        raise ValueError(f'Decompression failed: {res.name}')
    return v, act_w, act_h

###############################################################################

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


def compress(data, stages=4, segments=6, filter=IcerFilter.A, color=1):
    raise NotImplementedError


def decompress(data, stages=4, segments=6, filter=IcerFilter.A, color=1):
    w, h = _icer_get_image_dimensions(data)

    if color:
        y, u, v, w, h = _icer_decompress_image_yuv_uint16(data, w, h, stages, filter.value, segments)
        rgb = _yuv_to_rgb(
            np.frombuffer(y, np.int16),
            np.frombuffer(u, np.int16),
            np.frombuffer(v, np.int16),
        )
        return rgb.reshape((h.value, w.value, 3))

    else:
        v, w, h = _icer_decompress_image_uint16(data, w, h, stages, filter.value, segments)
        v = np.clip(np.frombuffer(v, np.int16), 0, 255).astype(np.uint8)
        return v.reshape((h.value, w.value))
