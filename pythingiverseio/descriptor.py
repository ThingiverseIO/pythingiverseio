from .libthingiverseio import tvio_check_descriptor
from ctypes import c_char_p, c_int, byref


def flavour_descriptor(desc, flavour):
    return desc + '\n' + flavour


def profile_descriptor(desc, profile):
    if type(profile) is list:
        tags = "tags"
        for t in profile:
            tags = tags + " " + t
        return flavour_descriptor(desc, tags)
    return flavour_descriptor(desc, "tag " + profile)


def profile_descriptor_key_value(desc, key, value):
    return profile_descriptor(desc, key + ":" + value)


def check_descriptor(desc):
    if type(desc) is not str:
        raise ValueError('Descriptor must be a string!')
    res = c_char_p()
    res_size = c_int()
    tvio_check_descriptor(c_char_p(desc.encode("ascii")),
                          byref(res), byref(res_size))
    return res.value
