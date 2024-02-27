; Constants and data here

.org $0200
; Entry point here

; Set reset vector to entry point
.org $fffc
.db $00, $02