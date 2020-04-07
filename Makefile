.PHONY: tests, codelines, doc, htmldoc, pdfdoc

tests:
	python3.7-coverage run --include './arpoc/*' -m pytest arpoc/tests || :
	python3.7-coverage html --skip-covered

clean:
	find -type d -name '__pycache__' -exec rm -rf '{}' + || :
	rm -rf deb_dist _build htmldoc latexdoc oidc_proxy.egg-info _templates _static dist
	rm -f oidc-proxy*.tar.gz
	rm -rf pdfdoc htmldoc

doc:
	PYTHONPATH=. run-parts docs/runners
	PYTHONPATH=. python3 arpoc/config.py > docs/gen/sample_config.yml
	plantuml -tsvg docs/gen/classes.plantuml
	inkscape docs/gen/classes.svg --export-pdf=docs/gen/classes.pdf
	pdfjam --paper a3 --landscape docs/gen/classes.pdf --outfile docs/gen/classes_a3.pdf
	sphinx-apidoc -o docs/api arpoc -f

htmldoc: doc
	sphinx-build -c docs -b html . htmldoc

pdfdoc: doc
	sphinx-build -c docs -b latex . latexdoc
	cd latexdoc; for i in plantuml*.pdf; do pdfcrop $$i $$i; done
	cd latexdoc && latexmk --pdf ARPOC.tex
	pdfunite latexdoc/ARPOC.pdf docs/gen/classes_a3.pdf doc_classdiagram.pdf
	cp latexdoc/ARPOC.pdf ./doc.pdf

codelines:
	cloc arpoc --exclude-dir=htmlcov,__pycache__

mypy:
	mypy arpoc --ignore-missing-imports --disallow-untyped-calls --no-site-packages --disallow-incomplete-defs --disallow-untyped-defs || :
