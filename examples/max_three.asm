.org $20
lst .db 4, 5, 3
max .equ $10

.org $0200
	LDA lst
	STA max
	LDA  lst+1
	CMP max
	BMI next
	STA max
next 	LDA lst+2
	CMP max
	BMI end
	STA max
end 	LDA max
	BRK

.org $FFFC
.db $00, $02