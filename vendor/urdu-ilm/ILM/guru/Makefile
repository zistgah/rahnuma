#Project ILM — shaili guru (C) — urdu
#Copyright (C) 1993-2026 Abhishek Choudhary. GNU GPL v2 or later.
EXECDIR=/usr/bin
R=../../Romenagri
CHAIN=fixuninum | ../fixarabnum | $(R)/fltr_ur_hi | iconv -f utf-8 -t utf-16 | uni2acii | acii2cf | tail +2

all: h2c_urdu c2h_urdu

h2c_urdu: h2c_urdu.uhin
	cat $< | $(CHAIN) > h2c_urdu.lex
	flex -8 -olexyy.c h2c_urdu.lex
	gcc lexyy.c -o$@ -lfl

c2h_urdu: c2h_urdu.uhin
	cat $< | $(CHAIN) > c2h_urdu.lex
	flex -8 -olexyy.c c2h_urdu.lex
	gcc lexyy.c -o$@ -lfl

install: all
	install h2c_urdu $(INSTROOT)$(EXECDIR)/h2c_urdu
	install c2h_urdu $(INSTROOT)$(EXECDIR)/c2h_urdu

clean:
	rm -f lexyy.c *.lex h2c_urdu c2h_urdu
