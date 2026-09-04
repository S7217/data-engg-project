.PHONY: help new check ready test lint validate deploy-dev ci

help:        ## Show targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

new:         ## Scaffold the spec chain for an object: make new OBJ=fct_x TIER=2
	python3 harness/tools/scaffold.py $(OBJ) --tier $(TIER)

check:       ## Harness checks: contracts, traceability, naming
	python3 harness/tools/check.py

ready:       ## Is one object ready? make ready OBJ=fct_x
	python3 harness/tools/ready.py $(OBJ)

test:        ## Unit tests with JUnit evidence in reports/
	@mkdir -p reports
	@# exit 5 = no tests collected: acceptable only while no implementation spec exists
	uv run pytest --junitxml=reports/junit.xml -q || [ $$? -eq 5 -a -z "$$(ls docs/20-impl-spec/*.impl.md 2>/dev/null)" ]

lint:        ## Ruff + naming
	uv run ruff check src tests
	python3 harness/tools/lint_naming.py src

validate:    ## Bundle validation, dev target
	databricks bundle validate -t dev

deploy-dev:  ## Validate, check, then deploy to dev (test/prod deploy through CI only)
	$(MAKE) validate check
	databricks bundle deploy -t dev

ci:          ## What CI runs before merge
	$(MAKE) check lint test
	databricks bundle validate -t dev
	databricks bundle validate -t test
	databricks bundle validate -t prod
