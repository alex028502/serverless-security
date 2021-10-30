TEST_DIR=./tests
COV_DIR=coverage
BASH_COV_DIR=$(COV_DIR)/sh
BASH_COV_FILE=$(BASH_COV_DIR)/index.html
PY_COV_FILE=coverage.json
PY=venv/bin/python

TARGET_DIR=./.target
DATA_DIR=$(TARGET_DIR)/data
DATA_FILE=$(DATA_DIR)/testfile
TARGET_VENV=$(TARGET_DIR)/venv
LIVE_PIN_FACTORY=native


.PHONY: lint coverage $(COV_DIR)/index.html checks $(TARGET_DIR) e2e playbooks
default: test lint check-coverage
lint:
	$(PY) -m black . --check
	$(PY) -m flake8 .
	node_modules/.bin/eslint -f unix .
test: checks
	$(PY) -m coverage erase
	rm -rf ./$(COV_DIR)
	mkdir $(COV_DIR)
	rm -f $(PY_COV_FILE)
	bundle exec bashcov -- misc/check-check-install.sh
	COVERAGE_PROCESS_START=.coveragerc node_modules/.bin/nyc bundle exec bashcov -- ./test.sh
	COVERAGE_PROCESS_START=.coveragerc bundle exec bashcov -- misc/ansible-test.sh $(TARGET_DIR)
	$(PY) -m coverage combine
	$(PY) -m coverage report
	$(PY) -m coverage html
	$(PY) -m coverage json
	node_modules/.bin/nyc report --reporter html
	$(MAKE) -f $(MAKEFILE_LIST) $(COV_DIR)/index.html
$(COV_DIR)/index.html:
	ls $(COV_DIR) | grep -v html | xargs -I {} echo '<a href="{}/index.html">{}</a>' > $@
check-coverage:
	node_modules/.bin/nyc check-coverage
	cat $(PY_COV_FILE) | jq .totals.percent_covered | grep -w 100
	cat $(BASH_COV_FILE) | grep covered_percent | grep -w 100
checks:
	cat .simplecov | grep $(BASH_COV_DIR)
	cat pyproject.toml | grep $(COV_DIR)/py
	cat .nycrc.json | grep $(COV_DIR)/js
$(TARGET_DIR):
	rm -rf $@
	mkdir $@
deploy: $(TARGET_DIR) redeploy
	ls $</requirements.txt
	ls $</package
	ls $</venv
mangle:
	$(TARGET_DIR)/venv/bin/pip install flask
	rm $(TARGET_DIR)/package/monitor.py
	touch $(TARGET_DIR)/package/does-not-belong.txt
compare-reqs:
	! diff requirements.txt setup/requirements.txt | grep '>'
	diff requirements.txt setup/requirements.txt | grep '<' > /dev/null
e2e: compare-reqs deploy
	ls $(DATA_DIR)
	[ -z "$(ls -A $(DATA_DIR))" ] # thanks https://superuser.com/a/352290
	! ls $(DATA_FILE)
	touch $(DATA_FILE)
	ls $(DATA_FILE)
	$(MAKE) -f $(MAKEFILE_LIST) source-check
	$(MAKE) -f $(MAKEFILE_LIST) venv-check
	$(MAKE) -f $(MAKEFILE_LIST) mangle
	! $(MAKE) -f $(MAKEFILE_LIST) source-check
	! $(MAKE) -f $(MAKEFILE_LIST) venv-check 
	$(MAKE) -f $(MAKEFILE_LIST) redeploy
	ls $(DATA_FILE)
	$(MAKE) -f $(MAKEFILE_LIST) source-check
	$(MAKE) -f $(MAKEFILE_LIST) venv-check
	$(MAKE) -f $(MAKEFILE_LIST) e2e-test
config-test:
	. $(TARGET_DIR)/.env && [ "$$SECURITY_CAMERA_DEVS" = '/dev/video*' ]
	. $(TARGET_DIR)/.env && [ "$$GPIOZERO_PIN_FACTORY" = $(LIVE_PIN_FACTORY) ]
	. $(TARGET_DIR)/.env && grep $${SECURITY_CAMERA_HOME} $(TARGET_DIR)/sensor.service
	. $(TARGET_DIR)/.env && grep $${SECURITY_CAMERA_HOME} $(TARGET_DIR)/security.service
	. $(TARGET_DIR)/.env && $(PY) tools/path_compare.py $${SECURITY_CAMERA_HOME} $(TARGET_DIR)
	. $(TARGET_DIR)/.env && $(PY) tools/path_compare.py $${SECURITY_CAMERA_VENV} $(TARGET_VENV)
e2e-test: config-test
	$(PY) -m pytest --sut=$(TARGET_DIR)/package --interpreter=$(TARGET_VENV)/bin/python -vvx
source-check:
	diff $(TARGET_DIR)/package package --exclude __pycache__ --exclude '*.pyc'
	! find $(TARGET_DIR)/package -name '*.pyc' | grep . # thanks https://serverfault.com/a/225827
	! find $(TARGET_DIR)/package -name '__pycache__' | grep .
venv-check:
	./tools/venv-run.sh $(TARGET_DIR)/venv ./tools/pip-freeze.sh | diff - $(TARGET_DIR)/requirements.txt
redeploy:
	venv/bin/ansible-playbook playbook.yml -vv -ltest
