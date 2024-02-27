x .equ $10
y .equ $11
z .equ $12

.org $0200
; Store first summand in $10
LDA #$40
STA x
; Store second summand in $11
LDA #$50
STA y
JSR add
; Load result in accumulator
LDA z

.org $02A0
add	CLC
	LDA x
	ADC y
	STA z
	RTS

.org $fffc
.db $00, $02