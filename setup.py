from setuptools import setup, Extension
import os




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
      test_suite='nose.collector',
      tests_require=['nose'],
)
