.org 50 
lst .db 50, 20, 30

.org $00
start   LDA lst
           CMP lst+1
           BMI next       ; 1st < 2nd
           LDX lst+1
           STA lst+1
           STX lst
next   LDA lst+1
           CMP lst+2
           BMI next2       ; 2nd < 3rd
           LDX lst+2
           STA lst+2
           STX lst+1
next2 LDA lst
           CMP lst+1
           BMI end         ; 1st < 2nd
           LDX lst+1
           STA lst+1
           STX lst
end    BRK


