.org $20
lst .db 4, 5, 3, 5, 2, 6,  1, 4
len .db 8
max .equ $10

.org $0200
LDX #0
LDA lst
STA max
loop INX
         LDA lst,X 
         CMP max
         BMI next
         STA max
next CPX len
         BMI loop
end  LDA max
BRK

.org $FFFC
.db $00, $02