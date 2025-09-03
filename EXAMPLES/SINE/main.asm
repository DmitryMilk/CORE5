	device	zxspectrum48

	org     8000h
start:
	di
	
	ld      bc, 0		; init voice 4 phase
	ld      de, 0		; init voice 5 phase
	exx
	ld      de, 0		; init voice 1 phase
	ld      ix, 0		; init voice 2 phase
	ld      iy, 0		; init voice 3 phase
	
	ld      bc, zeros	; init voice1 wave pointer and loop counter
	
	ld	hl, 0DE7h	; A4
	ld	(freq2), hl
	ld	hl, wavesin
	ld	(wave2), hl
	
	ld	hl, zeros
	ld	(wave3), hl
	ld	(wave4), hl
	ld	(wave5), hl
	
	sub     a
	ex      af, af'
	sub     a
	
nextframe:
	
	include core5.asm
	
	align   256
wavesin incbin  'waves/wavesin.dat'
zeros	incbin  'waves/zeros.dat'
	
end:
	emptytap 'sine.tap'
	savetap  'sine.tap', CODE, 'sine', start, end-start
