### Set TEX build utilities ###
LATEX	= latex --shell-escape
BIBTEX	= bibtex
INDEX	= makeindex
PS_PDF	= ps2pdf
DVI_PS	= dvips
XDVI	= xdvi -gamma 4
GH		= gv

### Set document variables ###
SRC	:= $(shell egrep -l '^[^%]*\\begin\{document\}' *.tex)
DVI = $(SRC:%.tex=%.dvi)
PS	= $(SRC:%.tex=%.ps)
PDF	= $(SRC:%.tex=%.pdf)

### Main target ###
all: pdf_compile
pdf: pdf_compile purge

pdf_compile: $(PDF)

# Compile TEX to DVI
$(DVI): %.dvi: %.tex
	$(LATEX) $<
	$(BIBTEX) $(<:%.tex=%)
	$(INDEX) $(<:%.tex=%)
	$(LATEX) $<
	$(LATEX) $<

# Convert DVI to PS
$(PS): %.ps: %.dvi
	$(DVI_PS) -R -Poutline -t letter $< -o $@

# Convert PS to PDF
$(PDF): %.pdf: %.ps
	$(PS_PDF) $<

### Display results ###
show: $(DVI)
	@for i in $(DVI) ; do $(XDVI) $$i & done

showps: $(PS)
	@for i in $(PS) ; do $(GH) $$i & done

### Clean project ###
purge:
	rm -f *.aux *.log *.bbl *.blg *.ps *.dvi *.out *.pyg *.synctex.gz *.toc *.lot *.lof *.idx *.ind *.ilg

clean: purge
	rm -f $(PDF)

### List all phony target names ###
.PHONY: all show clean ps pdf showps
