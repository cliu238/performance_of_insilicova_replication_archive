CITATION_STYLE=paper/citation-style-springer-vancouver-brackets.csl
PAPER_METADATA=paper/metadata.yml
PAPER_REFS=paper/references.bib
PAPER_DRAFTS:=paper/drafts
PAPER_MD=paper/paper.md

vpath %.md paper
vpath %.docx $(PAPER_DRAFTS)

.PHONY: all
all: docs download prep mapped results figures paper.docx

.PHONY: download
download:
	python src/download.py

.PHONY: prep
prep:
	python src/prep.py

.PHONY: mapped
mapped:
	python src/map_insilico.py
	python src/map_tariff.py

.PHONY: results
results: paper/numbers/*.yml
	python src/results.py

.PHONY: figures
figures:
	python src/figures.py

paper.md: paper/templates/*.md
	python src/paper.py

paper.docx: $(PAPER_MD) $(PAPER_REFS) $(PAPER_METADATA) $(CITATION_STYLE)
	pandoc --filter pandoc-citeproc --bibliography=$(PAPER_REFS) \
	--csl $(CITATION_STYLE) $(PAPER_MD) $(PAPER_METADATA) -o $(PAPER_DRAFTS)/$@

.PHONY: docs
docs:
	$(MAKE) html -C docs
