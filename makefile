TEST_DIR=./tests
CONF_DIR=$(TEST_DIR)/config
KEYS_DIR=$(TEST_DIR)/keys
IMGS=red blue
ADDRESSES=tools/addresses.py $(CONF_DIR)/settings.json
ADDITIONAL=$(TEST_DIR)/additional.txt
PY=venv/bin/python
PUB=public-key-1.asc
PRI=private-key-1.asc

# this file and test.mk are where I put any code that is not being covered by
# automated tests. That keeps it to a minimum.  I also learned the hard way that
# bashcov (https://github.com/infertux/bashcov) gets confused if a `makefile`
# is called inside the bashcov process.  So it worked out well to use `makefile`
# for the entry points where coverage is set up, and deployment tasks that I
# don't know how to test, and use bash for stuff that I can test.

.PHONY: install test e2e
install:
	./sysrq.sh
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
	[ "${SECURITY_LIVE_TARGET}" != "" ] # if the path makes no sense we'll find out soon
	timeout 10 ./tools/server-action/run.sh ${SECURITY_LIVE_TARGET} 'echo connected'
	venv/bin/ansible-playbook playbook.yml --limit prod -v
	./tools/server-action/run.sh ${SECURITY_LIVE_TARGET} 'sudo systemctl daemon-reload'
	./tools/server-action/run.sh ${SECURITY_LIVE_TARGET} 'sudo service security restart'
	./tools/server-action/run.sh ${SECURITY_LIVE_TARGET} 'sudo service sensor restart'
