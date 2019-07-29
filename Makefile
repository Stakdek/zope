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
	bash $(START)
service:
	sudo rm -f /usr/bin/start_zope
	sudo chmod -x $(START)
	sudo chmod 775 $(START)
	sudo ln -s $(PWD)/$(START) /usr/bin/start_zope
	sudo cp zope.service /etc/systemd/system
	sudo systemctl daemon-reload
	sudo systemctl enable zope
	sudo systemctl restart zope
