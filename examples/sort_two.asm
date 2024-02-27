; Labels must be defined before
; usage to use them with zeropage
; mode
.org 50 
xx .db 50, 40

.org $00
start  LDA xx
          CMP xx+1
          BMI end ; already sorted
          LDX xx+1
          STA xx+1
          STX xx
end   BRK



