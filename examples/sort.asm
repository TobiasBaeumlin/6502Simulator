.org $10 
lst .db 3,1,5,2,6,4
.org $20
len .db 6


.org $200
; we loop to the second last element
start  DEC len  
           LDA len
; if len is 0, we're done
           BEQ end     
; index starts at 0
           LDX #0
loop   LDA lst,X
; compare consecutive elements
           CMP lst+1,X	
           BMI cont
; switch them if necessary
           LDY lst+1,X
           STA lst+1,X
           STY lst,X
cont   INX
; compare index with length
           CPX len
; loop if index is smaller
           BMI loop
; start over from beginning
           JMP start
end    BRK
           
.org $fffc
.db $00,$02