x .equ $10
y .equ $11
res .equ $12

.org $0240
mult 	LDA #0
	STA res
loop	LDA x
	AND #1
	BEQ next
	LDA y
	CLC
	ADC res
	STA res
next	LSR x
	BEQ end
	ASL y
	JMP loop
end 	LDA res
	RTS	

.org $0200
; Enter multiplicand in $10 and $11
; before running the program
; Result in A
	JSR mult
	BRK

.org $fffc
.db $00, $02