.PHONY: tests, codelines

tests:
	cd oidcproxy && \
	python3.7-coverage run --include './*' -m pytest && \
	python3.7-coverage html

clean:
	find -type d -name '__pycache__' -exec rm -rf '{}' +

doc:
	sphinx-apidoc -o docs/api oidcproxy -f
	sphinx-build -b html . htmldoc

codelines:
	cloc oidcproxy --exclude-dir=htmlcov,__pycache__
