.org $20
lst .db 4, 1, 10, 4, 1, 4, 5
endlst
sum .equ $10

.org $0200
; Compute length of list
	LDA #endlst
	SEC
	SBC #lst
; Length in X register
	TAX
; Sum is 0 initially
	LDA #0
	STA sum
	LDX len
loop	LDA lst-1,X
	ADC sum
	STA sum
	DEX
	BNE loop
	BRK

.org $FFFC
.db $00, $02