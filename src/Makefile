
os:=$(shell uname -s | tr -s '[A-Z]' '[a-z]')

# .PHONY: build install

tstamp:=$(shell date "+%Y-%m-%d_%H.%M.%S")

all: build install

FORCE:

build: FORCE
	@echo "Build is done"

install: FORCE
	(cd ../install && rm -f tstamp.txt && echo $(tstamp) > tstamp.txt)
	rm -f ../install/*.tgz
ifeq ($(os),linux)
	# mkdir -p ../install
	# (cd ../install && rm -f linux.tgz && tar zcpf linux_$(tstamp).tgz ./linux tstamp.txt)
	(cd ../install && rm -f linux.tgz && tar zcpf linux.tgz ./linux tstamp.txt)
	ls -l ../install/linux*.tgz
else ifeq ($(os),darwin)
	# mkdir -p ../install
	# (cd ../install && rm -f darwin.tgz && tar zcpf darwin_$(tstamp).tgz ./darwin tstamp.txt)
	(cd ../install && rm -f darwin.tgz && tar zcpf darwin.tgz ./darwin tstamp.txt)
	ls -l ../install/darwin*.tgz
endif
	@cat ../install/tstamp.txt

# end
# comment

