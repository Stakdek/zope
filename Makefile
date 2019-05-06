SHELL := /bin/bash

INSTALL = install.sh
START = startup.sh

.PHONY: bin
clean:
	rm -rf *.pyc
	rm -rf *~*
	rm -f *.jpeg*
install:
	sudo bash $(INSTALL)
start:
	sudo bash startup.sh
