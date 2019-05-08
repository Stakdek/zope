SHELL := /bin/bash

INSTALL = install.sh
START = startup.sh

.PHONY: bin
clean:
	rm -rf *.pyc
	rm -rf *~*
	rm -f *.jpeg*
	rm -rf app
install:
	source settings.sh
	bash $(INSTALL)
start:
	bash $(START)
