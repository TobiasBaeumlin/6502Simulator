; Lobyte of first summand at $10
x .equ $10
; Lobyte of second argument in $12
y .equ $12
; Lobyte of result in $14
z .equ $14

.org $0200
; Store summands
LDA #$A0
STA x
LDA #$01
STA x+1
LDA #$81
STA y
LDA #$10
STA y+1
; Call subroutine
JSR add16bit
; Load lobyte of result
LDA z

.org $02A0
; Adds two 16bit numbers stored in 
; x and y (little endian!)
; Result in z and z+1
add16bit	CLC
	LDA x
	ADC y
	STA z
	LDA x+1
	ADC y+1
	STA z+1
	RTS

.org $fffc
.db $00, $02