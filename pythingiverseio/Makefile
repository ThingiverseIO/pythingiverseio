all: libthingiverse_wrap.c libthingiverse_wrap.o _libthingiverseio.so clean-intermediates

libthingiverse_wrap.c:
	swig -I/usr/include -python -o libthingiverse_wrap.c $(GOPATH)/src/github.com/joernweissenborn/thingiverseio/shared_library/libthingiverse.i

libthingiverse_wrap.o:
	gcc -O2 -fPIC -c libthingiverse_wrap.c -I/usr/include/python2.7

_libthingiverseio.so:
	gcc -shared -lthingiverseio libthingiverse_wrap.o -o _libthingiverseio.so

clean-intermediates:
	rm -f libthingiverse_wrap.*

clean: clean-intermediates
	rm -f _libthingiverseio.so
	rm -f libthingiverseio.py
	rm -f *.pyc
