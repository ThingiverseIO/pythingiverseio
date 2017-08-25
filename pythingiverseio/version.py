from .libthingiverseio import tvio_version
from ctypes import c_int, byref


def version():
    pmaj = c_int()
    pmin = c_int()
    pfix = c_int()

    tvio_version(byref(pmaj), byref(pmin), byref(pfix))

    maj = pmaj.value
    min = pmin.value
    fix = pfix.value

    return maj, min, fix
