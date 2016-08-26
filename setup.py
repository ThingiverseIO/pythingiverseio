from setuptools import setup, Extension

setup(name='pythingiverseio',
      version="0.1.0",
      description='Thingiverse.io for python.',
      url='http://github.com/ThingiverseIO/pythingiverseio',
      author='Joern Weissenborn',
      author_email='joern.weissenborn@gmail.com',
      license='lGPLv3',
      packages=['pythingiverseio'],
      install_requires=[
        'msgpack-python',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      py_modules=['libthingiverseio']
      )
