; main b:	voice 1 wave pointer (high byte)
; main c:	samples counter inside frame
; main de:	voice1 phase (fixedpoint 8.8)
; ix:		voice2 phase (fixedpoint 8.8)
; iy:		voice3 phase (fixedpoint 8.8)
; shadow bc:	voice4 phase (fixedpoint 8.8)
; shadow de:	voice5 phase (fixedpoint 8.8)

iloop:
	ld      l, a		;= 4
tbl_ptr	equ $ + 1
	ld      h, plstbl0/512	;= 7
	add     hl, hl		;= 11
	ld      sp, hl		;= 6
	sub     a		;= 4
	out     (0FEh), a	;= 11
	ret			;= 10,  jump to specific plsvariantN

vars:
freq1	dw	100h 		; voice 1 phase delta
freq2	dw	100h		; voice 2 phase delta
freq3	dw	100h		; voice 3 phase delta
freq4	dw	100h		; voice 4 phase delta
freq5	dw	100h		; voice 5 phase delta
wave2	dw	zeros		; voice 2 wave pointer (aligned 256)
wave3	dw	zeros		; voice 3 wave pointer (aligned 256)
wave4	dw	zeros		; voice 4 wave pointer (aligned 256)
wave5	dw	zeros		; voice 5 wave pointer (aligned 256)
frmexit	dw      iloop		; address to exit, when frame finished

	include 'codegen/pulses.asm'

;-----------------------------------------------
;	align   256
;zeros	incbin  'waves/zeros.dat'
;-----------------------------------------------

