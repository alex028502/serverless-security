TEST_DIR=./tests
CONF_DIR=$(TEST_DIR)/config
KEYS_DIR=$(TEST_DIR)/keys
IMGS=red blue
COV_DIR=coverage
BASH_COV_DIR=$(COV_DIR)/sh
BASH_COV_FILE=$(BASH_COV_DIR)/index.html
PY_COV_FILE=coverage.json
ADDRESSES=tools/addresses.py $(CONF_DIR)/settings.json
ADDITIONAL=$(TEST_DIR)/additional.txt
PY=venv/bin/python
PUB=public-key-1.asc
PRI=private-key-1.asc

.PHONY: install $(COV_DIR)/index.html test e2e
install:
	./sysreq.sh
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	./check-install.sh
	npm ci
	cp coverage.pth venv/lib/python*/site-packages
	$(MAKE) $(CONF_DIR)/keys
	$(MAKE) $(TEST_DIR)/images
	bundle install
test:
	$(MAKE) -f test.mk
e2e:
	$(MAKE) -f test.mk e2e
check-coverage:
	$(MAKE) -f test.mk check-coverage
$(CONF_DIR)/keys: $(TEST_DIR)/keys
	rm -rf $@ $@.tmp
	mkdir $@.tmp
	$(PY) $(ADDRESSES) | xargs -I {} mkdir $@.tmp/{}
	$(PY) $(ADDRESSES) | xargs -I {} cp $</{}/$(PUB) $@.tmp/{}
	$(PY) $(ADDRESSES) | head -n1 | xargs -I {} cp $</{}/$(PRI) $@.tmp/{}
	mv $@.tmp $@
$(TEST_DIR)/keys: tools/new-account.js makefile $(ADDITIONAL) $(ADDRESSES)
	rm -rf $@ $@.tmp
	mkdir $@.tmp
	$(PY) $(ADDRESSES) | cat - $(ADDITIONAL) | xargs -I {} node $< $@.tmp/{} {} $(PRI) $(PUB)
	mv $@.tmp $@
$(TEST_DIR)/images: makefile
	rm -rf $@ $@.tmp
	mkdir $@.tmp
	echo $(IMGS) | xargs -n1 echo | xargs -I {} convert -size 1000x1000 xc:{} $@.tmp/{}.jpg
	mv $@.tmp $@
deploy:
	[ "${SECURITY_LIVE_TARGET}" != *:* ]
	[ "${SECURITY_CAMERA_TUNING}" != *:*:* ]
	venv/bin/ansible-playbook playbook.yml --limit prod -v
	echo ${SECURITY_LIVE_TARGET} | cut -f 1 -d':' | xargs -I {} ssh {} 'sudo systemctl daemon-reload'
	echo ${SECURITY_LIVE_TARGET} | cut -f 1 -d':' | xargs -I {} ssh {} 'sudo service security restart'
