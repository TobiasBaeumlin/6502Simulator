.org $02A0
; Listenelemente
list .db 31,3,59,1,56,2
; Länge der Liste
len .db 5        
max .equ $05
.org $0200
	LDX len
	DEX      
; 1. Listenenlement als vorläufiges
; Maximum
	LDA list      
	STA max
; Listenelement von hinten nach
; vorne in den Accumulator laden
loop	LDA list,X
; Akutelles Maximum subtrahieren
	SBC max
	BCS next
; Subtraktion hat keinen Übertrag
; Neues grösstes Element gefunden
	LDA list,X
	STA max
next	DEX
	BNE loop

; Resetvektor setzen
.org $fffc
.db $00,$02
.end