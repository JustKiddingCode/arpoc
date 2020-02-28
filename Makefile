.PHONY: tests, codelines, doc, htmldoc, pdfdoc

tests:
	python3.7-coverage run --include './oidcproxy/*' -m pytest oidcproxy/tests || :
	python3.7-coverage html --skip-covered

clean:
	find -type d -name '__pycache__' -exec rm -rf '{}' + || :
	rm -rf deb_dist _build htmldoc latexdoc oidc_proxy.egg-info _templates _static dist
	rm -f oidc-proxy*.tar.gz
	rm -rf pdfdoc htmldoc

doc:
	PYTHONPATH=. run-parts docs/runners
	PYTHONPATH=. python3 oidcproxy/config.py > docs/gen/sample_config.yml
	sphinx-apidoc -o docs/api oidcproxy -f

htmldoc: doc
	sphinx-build -c docs -b html . htmldoc

pdfdoc: doc
	sphinx-build -c docs -b latex . latexdoc
	cd latexdoc && latexmk --pdf OIDCProxy.tex
	cp latexdoc/OIDCProxy.pdf ./doc.pdf

codelines:
	cloc oidcproxy --exclude-dir=htmlcov,__pycache__

mypy:
	mypy oidcproxy --ignore-missing-imports --disallow-untyped-calls --no-site-packages --disallow-incomplete-defs --disallow-untyped-defs || :
