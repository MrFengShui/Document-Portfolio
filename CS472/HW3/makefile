CC       = gcc
CFLAG    = -Wall -Wshadow -Werror -Wformat -Wimplicit -Wundef -Wuninitialized -Wunused -Wunreachable-code -g -o

all: clean latex main

main: 
	${CC} ${CFLAG} main main.c show_endian.c calc_cache.c

latex: dvi ps pdf

dvi: writeup.tex
	latex writeup.tex

ps: dvi
	dvips -R -Poutline -t letter writeup.dvi -o writeup.ps

pdf: ps
	ps2pdf writeup.ps

clean:
	rm -f *.aux *.log *.dvi *.out *.ps *.pdf main
