from .libthingiverseio import *


def version():
    pmaj = new_intp()
    pmin = new_intp()
    pfix = new_intp()

    _check_error(tvio_version(pmaj, pmin, pfix))

    maj = intp_value(pmaj)
    delete_intp(pmaj)

    min = intp_value(pmin)
    delete_intp(pmin)

    fix = intp_value(pfix)
    delete_intp(pfix)

    return maj, min, fix
