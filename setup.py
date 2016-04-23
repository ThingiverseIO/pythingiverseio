from setuptools import setup, Extension
import os

swigfile = os.environ['GOPATH']+'/src/github.com/joernweissenborn/thingiverseio/shared_library/libthingiverse.i'

include = os.environ['GOPATH']+'/src/github.com/joernweissenborn/thingiverseio/shared_library/include/'

_libthingiverseio = Extension('_libthingiverseio',
                           sources=[swigfile],
                           swig_opts=['-I'+include]
                           )


setup(name='pythingiverseio',
      version="0.0.1",
      description='Thingiverse.io for python.',
      url='http://github.com/joernweissenborn/pythingiverseio',
      author='Joern Weissenborn',
      author_email='joern.weissenborn@gmail.com',
      license='lGPLv3',
      packages=['pythingiverseio'],
      install_requires=[
        'msgpack-python',
      ],
      ext_modules = [_libthingiverseio],
      test_suite='nose.collector',
      tests_require=['nose'],
)
