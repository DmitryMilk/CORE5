@ECHO OFF
SET Z80_COMPILER=sjasmplus.exe
SET Z80_COMPILE_OPTIONS=--syntax=a --lst


:simple_build
pulses.py
IF ERRORLEVEL 1 GOTO fail

:compile

%Z80_COMPILER% %Z80_COMPILE_OPTIONS% main.asm
IF ERRORLEVEL 1 GOTO fail

GOTO exit
:fail

echo ""
echo ===============FAIL!!!=========================
echo ""

erase *.tap
erase *.sna
erase *.lst

:exit
