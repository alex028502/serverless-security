TEST_DIR=./tests
COV_DIR=coverage
BASH_COV_DIR=$(COV_DIR)/sh
BASH_COV_FILE=$(BASH_COV_DIR)/index.html
PY_COV_FILE=coverage.json
PY=venv/bin/python

TARGET_DIR=./.target
ENV_FILE=$(TARGET_DIR)/.env
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
	$(MAKE) -f $(MAKEFILE_LIST) $(COV_DIR)/index.html $(COV_DIR)/robots.txt $(COV_DIR)/favicon.ico
$(COV_DIR)/index.html:
	ls $(COV_DIR) | grep -v html | xargs -I {} echo '<a href="{}/index.html">{}</a>' > $@
	echo '<br />' this website is only to diplay the coverage reports >> $@
$(COV_DIR)/robots.txt:
	echo 'User-agent: * Disallow: /' > $@
$(COV_DIR)/favicon.ico:
	convert -size 16x16 xc:#0000FF $@
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
	. $(ENV_FILE) && [ "$$SECURITY_CAMERA_DEVS" = '/dev/video*' ]
	. $(ENV_FILE) && [ "$$GPIOZERO_PIN_FACTORY" = $(LIVE_PIN_FACTORY) ]
	$(PY) tools/service_value.py $(TARGET_DIR)/sensor.service Service EnvironmentFile \
		| xargs $(PY) ./tools/path_compare.py $(ENV_FILE)
	$(PY) tools/service_value.py $(TARGET_DIR)/sensor.service Service ExecStart \
		| xargs $(PY) ./tools/path_compare.py $(TARGET_DIR)/package/sensor.sh
	$(PY) tools/service_value.py $(TARGET_DIR)/sensor.service Service WorkingDirectory \
		| xargs $(PY) ./tools/path_compare.py $(TARGET_DIR)
	$(PY) tools/service_value.py $(TARGET_DIR)/sensor.service Service User \
		| xargs ./tools/assert.sh pi ==
	$(PY) tools/service_value.py $(TARGET_DIR)/sensor.service Unit Description \
		| xargs -I {} ./tools/assert.sh "detect motion" == "{}"
	$(PY) tools/service_value.py $(TARGET_DIR)/security.service Service EnvironmentFile \
		| xargs $(PY) ./tools/path_compare.py $(ENV_FILE)
	$(PY) tools/service_value.py $(TARGET_DIR)/security.service Service ExecStart \
		| xargs $(PY) ./tools/path_compare.py $(TARGET_DIR)/package/service.sh
	$(PY) tools/service_value.py $(TARGET_DIR)/security.service Service WorkingDirectory \
		| xargs $(PY) ./tools/path_compare.py $(TARGET_DIR)
	$(PY) tools/service_value.py $(TARGET_DIR)/security.service Unit Description \
		| xargs -I {} ./tools/assert.sh "wait for motion" == "{}"
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
