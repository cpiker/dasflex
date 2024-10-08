# Just pushes commands down to setup.py

ifeq ($(PREFIX),)
	PREFIX:=/var/www/dasflex
endif

ifeq ($(INST_ETC),)
	INST_ETC:=$(PREFIX)/etc
endif

# Default to no sub-dir for architecture dependent files
ifeq ($(N_ARCH),)
	N_ARCH:=/   
endif

ifeq ($(PYVER),)
	PYVER=$(shell python3 -c "import sys; print('.'.join( sys.version.split()[0].split('.')[:2] ))")
endif

export PREFIX
export INST_ETC
export N_ARCH
export PYVER

build:
	python${PYVER} setup.py build

install_noex:
	python${PYVER} setup.py install --prefix=${PREFIX} \
	   --install-lib=${PREFIX}/lib/python${PYVER} \
	   --install-scripts=${PREFIX}/bin/${N_ARCH} --no-examples
	@echo "-------------------------------------------------------------------"
	@echo "Scripts installed, but you probably need to symlink dasflex_cgimain"
	@echo "and dasflex_logmain from your designated CGI bin directory."
	@echo "-------------------------------------------------------------------"

install:
	python${PYVER} setup.py install --prefix=${PREFIX} \
	   --install-lib=${PREFIX}/lib/python${PYVER} \
	   --install-scripts=${PREFIX}/bin/${N_ARCH}
	@echo "-------------------------------------------------------------------"
	@echo "Scripts installed, but you probably need to symlink dasflex_cgimain"
	@echo "and dasflex_logmain from your designated CGI bin directory."
	@echo "-------------------------------------------------------------------"

#python${PYVER} setup.py install --prefix=${PREFIX} \
#   --install-lib=${PREFIX}/lib/python${PYVER} --no-examples


distclean:
	rm -r build
