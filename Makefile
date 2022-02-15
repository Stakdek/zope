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
	bash $(INSTALL)
start:
	bash $(START) 1
service:
	bash install_service.sh
