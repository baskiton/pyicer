#ifndef _GNU_SOURCE
# define _GNU_SOURCE
#endif  // _GNU_SOURCE

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

#include <stdint.h>
#include <stddef.h>

#include "icer.h"


PyDoc_STRVAR(decompress__doc__,
"decompress(data: bytes[, stages: int = 4, segments: int = 6, filter: Literal['A', 'B', 'C', 'D', 'E', 'F', 'Q'] = 'A', color=1]) -> tuple\n"
"\n"
"Args:\n"
"    data (bytes): compressed data\n"
"    stages (int): 1 - 6\n"
"    segments (int): 1 - 32\n"
"    filter (str): A, B, C, D, E, F, Q\n"
"    color (int|bool): color or bw image\n"
"\n"
"Returns:\n"
"    tuple: (y-channel, u-channel, v-channel, actual width, actual height) when color\n"
"    tuple: (bw-channel, actual width, actual height) when bw\n"
"\n"
"Raises:\n"
"    ValueError: Some errors\n");

static PyObject *
pyicer_decompress(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *kwlist[] = {"data", "stages", "segments", "filter", "color", NULL};
    const char *filter_ch = "A";

    const uint8_t *data;
    Py_ssize_t dlen;
    int stages = 4, segments = 6, is_color = 1;
    enum icer_filter_types filter;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y#|iisi:decompress", kwlist,
                                     &data, &dlen, &stages, &segments, &filter_ch, &is_color))
        return NULL;

    if (dlen < (Py_ssize_t)sizeof(icer_image_segment_typedef)) {
        PyErr_SetString(PyExc_ValueError, "data is too short");
        return NULL;
    }
    if (stages < 1 || stages > ICER_MAX_DECOMP_STAGES) {
        PyErr_SetString(PyExc_ValueError, "`stages` must be between 1 and 6");
        return NULL;
    }
    if (segments < 1 || segments > ICER_MAX_SEGMENTS) {
        PyErr_SetString(PyExc_ValueError, "`segments` must be between 1 and 32");
        return NULL;
    }
    switch (*filter_ch) {
        case 'A':
            filter = ICER_FILTER_A;
            break;
        case 'B':
            filter = ICER_FILTER_B;
            break;
        case 'C':
            filter = ICER_FILTER_C;
            break;
        case 'D':
            filter = ICER_FILTER_D;
            break;
        case 'E':
            filter = ICER_FILTER_E;
            break;
        case 'F':
            filter = ICER_FILTER_F;
            break;
        case 'Q':
            filter = ICER_FILTER_Q;
            break;
        default:
            PyErr_SetString(PyExc_ValueError, "Invalid filter");
            return NULL;
    }

    size_t image_w, image_h, actual_w, actual_h;
    if (icer_get_image_dimensions(data, dlen, &image_w, &image_h) != ICER_RESULT_OK) {
        PyErr_SetString(PyExc_ValueError, "Can't determine data dimensions");
        return NULL;
    }

    uint16_t *yuv[3];
    size_t ch_len = image_w * image_h * sizeof(**yuv);
    for (int i = 0; i < 3; i++)
        yuv[i] = PyMem_Malloc(ch_len);

    // XXX: protect for data corruption https://github.com/TheRealOrange/icer_compression/issues/9
# define SAFETY_BUF_SZ 256
    uint8_t *cp_data = PyMem_Malloc(dlen + SAFETY_BUF_SZ * 2);
    memcpy(cp_data + SAFETY_BUF_SZ, data, dlen);

    int res;
    if (is_color)
        res = icer_decompress_image_yuv_uint16(yuv[0], yuv[1], yuv[2], &actual_w, &actual_h, image_w * image_h,
                                               cp_data + SAFETY_BUF_SZ, dlen, stages, filter, segments);
    else
        res = icer_decompress_image_uint16(yuv[0], &actual_w, &actual_h, image_w * image_h,
                                           cp_data + SAFETY_BUF_SZ, dlen, stages, filter, segments);

    PyMem_Free(cp_data);
# undef SAFETY_BUF_SZ

    if (res != ICER_RESULT_OK) {
        for (int i = 0; i < 3; i++) {
            if (yuv[i])
                free(yuv[i]);
        }
        PyErr_SetString(PyExc_ValueError, "Something wrong");
        return NULL;
    }

    PyObject *ret;
    if (is_color)
        ret = Py_BuildValue("((y# y# y#) n n)", yuv[0], ch_len, yuv[1], ch_len, yuv[2], ch_len, actual_w, actual_h);
    else
        ret = Py_BuildValue("(y# n n)", yuv[0], ch_len, actual_w, actual_h);

    for (int i = 0; i < 3; i++) {
        if (yuv[i])
            free(yuv[i]);
    }

    return ret;
}


static PyMethodDef pyicer_methods[] = {
        {"decompress", (PyCFunction)pyicer_decompress, METH_VARARGS | METH_KEYWORDS, decompress__doc__},
        {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
PyInit__pyicer(void)
{
    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_pyicer",
        .m_methods = pyicer_methods,
    };

    icer_init();

    return PyModuleDef_Init(&module_def);
}
