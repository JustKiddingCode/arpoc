.PHONY: tests

tests:
	cd oidcproxy && \
	python3.7-coverage run --include './*' -m pytest && \
	python3.7-coverage html
