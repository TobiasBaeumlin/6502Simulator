LDA #$A0
STA $B0
LDY $10,X
STX $10,Y
LDA $10AA
STA $10AA,X
STA $FF00,Y
LDA ($20,X)
LDA ($30),Y
