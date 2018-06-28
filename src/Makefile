
os:=$(shell uname -s | tr -s '[A-Z]' '[a-z]')

.PHONY: all build

all: build install

build:
	@echo "Build is done"

install:
ifeq ($(os),linux)
	(cd ../install && rm -f linux.tgz && tar zcpf linux.tgz ./linux)
else ifeq ($(os),darwin)
	(cd ../install && rm -f darwin.tgz && tar zcpf darwin.tgz ./darwin)
endif

