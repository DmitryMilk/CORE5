[pulse1prolog]
	nop			;= 4, =balance_many
	ret nz			;= 5, =balance_many
	ld      l, (hl)		;= 7, =balance_many
	inc     hl		;= 6, =balance_many
	add     hl, hl		;= 11, =balance_many

[part1]
	ld      sp, vars	;= 10
	
	pop     hl		;= 10, freq1
	add     hl, de		;= 11
	pop     de		;= 10, freq2
	add     ix, de		;= 15
	pop     de		;= 10, freq3
	add     iy, de		;= 15
	ex      de, hl		;= 4
	
	exx			;= 4
	
	pop     hl		;= 10, freq4
	add     hl, bc		;= 11

[interval1epilog]
	ld      b, h		;= 4
	ld      c, l		;= 4
	
	inc     hl		;= 6, =balance_many
	add     hl, hl		;= 11, =balance_many
	
	pop     hl		;= 10, freq5
	add     hl, de		;= 11

	ld      a, 0		;= 7, =balance_set_include_pulse1end
	sub     a		;= 4, =balance_set_exclude_pulse1end
	out     (0FEh), a	;= 11

[pulse2prolog]
	; start of pulse 2
	inc	de		;= 6, =balance_many
	pop     de		;= 10, wave2
	ld      a, (de)		;= 7, =balance_many

[part2]
	ld      e, ixh		;= 8
	ld      a, (de)		;= 7
	pop     de		;= 10, wave3
	ld      e, iyh		;= 8
	ex      de, hl		;= 4

	add     (hl)		;= 7
	
	add     hl, hl		;= 11, =balance_many
	
	pop     hl		;= 10, wave4
	ld      l, b		;= 4
	add     (hl)		;= 7
	
	pop     hl		;= 10, wave5
	ld      l, d		;= 4
	add     (hl)		;= 7
	
	exx			;= 4
	
	ld      h, b		;= 4, wave1
	ld      l, d		;= 4
	add     (hl)		;= 7
	
	dec     c		;= 4

[interval2epilog]
	ld      l, (hl)		;= 7, =balance_many
	inc     hl		;= 6, =balance_many
	add     hl, hl		;= 11, =balance_many
	
	jp nz,	iloop		;= 10
	ret			;= 10, jump [frmexit]



[pulse1epilog]
	ld      a, 0FFh		;= 7, =balance_set_include_pulse1start
	cpl			;= 4, =balance_set_exclude_pulse1start
	out     (0FEh), a	;= 11
	; end of pulse 1
[interval1prolog]
	nop			;= 4, =balance_many
	ret nz			;= 5, =balance_many
	ex      af, af'		;= 4


[pulse2epilog]
	ex      af, af'		;= 4
	nop			;= 4, =balance_many
	ret nz			;= 5, =balance_many
	out     (0FEh), a	;= 11
	; end of pulse 2
[interval2prolog]
	nop			;= 4, =balance_many
	ret nz			;= 5, =balance_many
	ex      af, af'		;= 4

