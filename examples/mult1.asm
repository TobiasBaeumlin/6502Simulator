x .equ $10
y .equ $11

.org $0240
mult 	LDX X
	INX
	LDA #0
loop	DEX
	BEQ end
	ADC y
	JMP loop
end	RTS

.org $0200
; Enter multiplicand in $10 and $11
; before running the program
; Result in A
	JSR mult
	BRK

.org $fffc
.db $00, $02