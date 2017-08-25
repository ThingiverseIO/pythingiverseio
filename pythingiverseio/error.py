from .libthingiverseio import tvio_error_message


def _check_error(code):
    if code is not 0:
        raise Exception(tvio_error_message(code))
