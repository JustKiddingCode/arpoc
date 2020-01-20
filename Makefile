.PHONY: tests, codelines, doc, htmldoc, pdfdoc

tests:
	python3.7-coverage run --include './oidcproxy/*' -m pytest oidcproxy/tests
	python3.7-coverage html

clean:
	find -type d -name '__pycache__' -exec rm -rf '{}' +
	rm -rf deb_dist _build htmldoc latexdoc oidc_proxy.egg-info _templates _static dist
	rm oidc-proxy*.tar.gz

doc:
	python3 oidcproxy/config.py > docs/gen/sample_config.yml
	sphinx-apidoc -o docs/api oidcproxy -f

htmldoc: doc
	sphinx-build -b html . htmldoc

pdfdoc: doc
	sphinx-build -b latex . latexdoc
	cd latexdoc && latexmk --pdf OIDCProxy.tex
	cp latexdoc/OIDCProxy.pdf ./doc.pdf

codelines:
	cloc oidcproxy --exclude-dir=htmlcov,__pycache__
