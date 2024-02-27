.org $200
far .equ $f000
next .equ $0000
label LDX #100
         JMP far
.org $f000
         JMP (next) 
        STX $10 
        LDA #1
        JMP label
.org $fffc
.db $00,$02           ; Reset vector
.org 0
.db $00,$02