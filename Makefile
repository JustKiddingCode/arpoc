.PHONY: tests, codelines, doc, htmldoc, pdfdoc

tests:
	cd oidcproxy && \
	python3.7-coverage run --include './*' -m pytest && \
	python3.7-coverage html

clean:
	find -type d -name '__pycache__' -exec rm -rf '{}' +

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
