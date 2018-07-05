
os:=$(shell uname -s | tr -s '[A-Z]' '[a-z]')

# .PHONY: build install

all: build install

FORCE:

build: FORCE
	@echo "Build is done"

install: FORCE
ifeq ($(os),linux)
	# mkdir -p ../install
	(cd ../install && rm -f linux.tgz && tar zcpf linux.tgz ./linux)
	(ls -l ../install/linux.tgz)
else ifeq ($(os),darwin)
	# mkdir -p ../install
	(cd ../install && rm -f darwin.tgz && tar zcpf darwin.tgz ./darwin)
	(ls -l ../install/darwin.tgz)
endif

# end
# comment

