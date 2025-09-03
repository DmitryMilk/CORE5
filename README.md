GENERAL
=======

This is only a core of beeper sound engine, not a full-fledged engine.

It is assumed that engine will play music by "frames" of length about 20-30 milliseconds,
during which any parameters (frequencies, waveforms) remains unchanged.

This core provides playing of a frame with specified parameters (frequencies and waveforms).
This core DOES NOT provide any interframe logic (changing notes, timbres, modulations) - it's all up to engine.

DETAILS
=======

Music is played by 5 tonal voices as sum of 8-bit-signed integer samples at samplerate 8.4 kHz.

Each tonal voice can be considered as arbitrary waveform generator. Cyclic waveform is specified by 256 8-bit-signed samples.
Frequency of generator is specified as fixedpoint (0.16) ratio to samplerate.

There are no more parameters of voice (volume or somethin other).
Volume, timbre and timbral modulations must be implemented in the waveform itself.
For example, silence of voice - must be just waveform of 256 zero samples.

Entrypoint of frame: **iloop**.

State of tonal voices is stored in register pairs:

- main de:	voice1 phase
- ix:		voice2 phase
- iy:		voice3 phase
- shadow bc:	voice4 phase
- shadow de:	voice5 phase

So, these registers must remain unchanged after interframe manipulations.

Also, main accumulator (register **a**) must remain unchanged, since it stores output value for next sample
(calculated during previous sample).

Shadow accumulator is free for use (so, **EX af, af'** can be used to save main accumulator during interframe logic).

Main register **c** serves as samples counter.
Frame is finished, when countdown reaches 0.

Parameters of voices: 

- main register **b** (voice 1 waveform pointer's high byte)

and next 16-bit variables:

- **freq1**: voice 1 frequency
- **freq2**: voice 2 frequency
- **freq3**: voice 3 frequency
- **freq4**: voice 4 frequency
- **freq5**: voice 5 frequency

- **wave2**: voice 2 waveform pointer (must be aligned 256)
- **wave3**: voice 3 waveform pointer (must be aligned 256)
- **wave4**: voice 4 waveform pointer (must be aligned 256)
- **wave5**: voice 5 waveform pointer (must be aligned 256)

Variable **frmexit** contains address to exit when frame is finished.

HOW TO BUILD
============

Run pulses.py to generate _codegen/pulses.asm_
