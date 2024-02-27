.org $20
x .db 4
y .db 7
max .equ $10

.org $0200
	LDA x
	STA max
	CMP y
	BPL end
	LDA y
	STA max
end 	LDA max
	BRK

.org $FFFC
.db $00, $02