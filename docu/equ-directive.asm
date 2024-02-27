xx .equ $AA00
yy .equ $AAB0
LDA xx
CLC
ADC xx+1
SEC
SBC yy
.org $AA00 
.db 42,50
.org $AAB0
.db 92