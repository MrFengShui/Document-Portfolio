CC       = gcc
CFLAG    = -Wall -Wshadow -Werror -Wformat -Wimplicit -Wundef -Wuninitialized -Wunused -Wunreachable-code -g -o
LIBS     = -lpthread
SRC      = main
TEX      = writing

all: clean ${SRC}

${SRC}: clean
	${CC} ${CFLAG} ${SRC} ${SRC}.c frexp.c arithm.c extract.c

latex: dvi ps pdf

dvi: ${TEX}.tex
	latex ${TEX}.tex

ps: dvi
	dvips -R -Poutline -t letter ${TEX}.dvi -o ${TEX}.ps

pdf: ps
	ps2pdf ${TEX}.ps

clean:
	rm -f *.aux *.log *.dvi *.out *.ps *.pdf ${SRC}