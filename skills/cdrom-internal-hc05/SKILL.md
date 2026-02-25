---
name: cdrom-internal-hc05
description: "PSX CDROM internal: Motorola MC68HC05 8-bit sub-CPU instruction set, on-chip I/O ports (port A-D, timer, SCI, SPI), PSX-specific I/O usage, selftest mode for 52pin/80pin chips. Use when reverse-engineering CDROM controller firmware or sub-CPU behavior."
---

#   CDROM Internal Info on PSX CDROM Controller
PSX software can access the CDROM via Port 1F801800h..1F801803h (as described
in the previous chapters). The following chapters describe the inner workings
of the PSX CDROM controller - this information is here for curiosity only -
normally PSX software cannot gain control of those lower-level stuff (although
some low level registers can be manipulated via Test commands, but that will
usually conflict with normal operation).<br/>

#### Motorola MC68HC05 (8bit single-chip CPU)
The Playstation CDROM drive is controlled by a MC68HC05 8bit CPU with on-chip
I/O ports and on-chip BIOS ROM. There is no way to reprogram that BIOS, nor to
tweak it to execute custom code in RAM.<br/>
[CDROM Internal HC05 Instruction Set](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-hc05-instruction-set)<br/>
[CDROM Internal HC05 On-Chip I/O Ports](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-hc05-on-chip-io-ports)<br/>
[CDROM Internal HC05 I/O Port Usage in PSX](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-hc05-io-port-usage-in-psx)<br/>
[CDROM Internal HC05 Motorola Selftest Mode](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-hc05-motorola-selftest-mode)<br/>
The PSX can read HC05 I/O Ports and RAM via Test Commands:<br/>
[CDROM - Test Commands - Read HC05 SUB-CPU RAM and I/O Ports](cdromdrive.md#cdrom-test-commands-read-hc05-sub-cpu-ram-and-io-ports)<br/>

#### Decoder/FIFO (CXD1199BQ or CXD1815Q)
This chip handles error correction and ADPCM decoding, and acts as some sort of
FIFO interface between main/sub CPUs and incoming cdrom sector data. On the
MIPS Main CPU it is controlled via Port 1F801800h..1F801803h.<br/>
[CDROM Controller I/O Ports](cdromdrive.md#cdrom-controller-io-ports)<br/>
On the HC05 Sub CPU it is controlled via Port A (data in/out), Port E
(address/index), and Port D (read/write/select signals); the HC05 doesn't have
external address/data bus, so one must manually access the CXD1815Q via those
ports.<br/>
[CDROM Internal CXD1815Q Sub-CPU Configuration Registers](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-cxd1815q-sub-cpu-configuration-registers)<br/>
[CDROM Internal CXD1815Q Sub-CPU Sector Status Registers](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-cxd1815q-sub-cpu-sector-status-registers)<br/>
[CDROM Internal CXD1815Q Sub-CPU Address Registers](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-cxd1815q-sub-cpu-address-registers)<br/>
[CDROM Internal CXD1815Q Sub-CPU Misc Registers](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-cxd1815q-sub-cpu-misc-registers)<br/>
The PSX can read/write the Decoder I/O Ports and SRAM via Test commands:<br/>
[CDROM - Test Commands - Read/Write Decoder RAM and I/O Ports](cdromdrive.md#cdrom-test-commands-readwrite-decoder-ram-and-io-ports)<br/>
The sector buffer used in the PSX is 32Kx8 SRAM. Old PU-7 boards are using
CXD1199BQ chips, later boards are using CXD1815Q, and even later boards have
the stuff intergrated in the SPU. Note: The CXD1199BQ/CXD1815Q are about 99%
same as described in CXD1199AQ datasheet.<br/>

#### Signal Processor and Servo Amplifier
Older PSX mainboards are using two separate chips:<br/>
[CDROM Internal Commands CX(0x..3x) - CXA1782BR Servo Amplifier](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-commands-cx0x3x-cxa1782br-servo-amplifier)<br/>
[CDROM Internal Commands CX(4x..Ex) - CXD2510Q Signal Processor](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-commands-cx4xex-cxd2510q-signal-processor)<br/>
Later PSX mainboards have the above intergrated in a single chip, with some
extended features:<br/>
[CDROM Internal Commands CX(0x..Ex) - CXD2545Q Servo/Signal Combo](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-commands-cx0xex-cxd2545q-servosignal-combo)<br/>
Later version is CXD1817R (Servo/Signal/Decoder Combo).<br/>
Even later PSX mainboards have it integrated in the Sound Chip: CXD2938Q
(SPU+CDROM) with some changed bits and New SCEx transfer:<br/>
[CDROM Internal Commands CX(0x..Ex) - CXD2938Q Servo/Signal/SPU Combo](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-commands-cx0xex-cxd2938q-servosignalspu-combo)<br/>
Finally, PM-41(2) boards are using a CXD2941R chip (SPU+CDROM+SPU\_RAM), unknown
if/how far the CDROM part of that chip differs from CXD2938Q.<br/>
Some general notes:<br/>
[CDROM Internal Commands CX(xx) - Notes](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-commands-cxxx-notes)<br/>
[CDROM Internal Commands CX(xx) - Summary of Used CX(xx) Commands](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-commands-cxxx-summary-of-used-cxxx-commands)<br/>
The PSX can manipulate the CX(..) registers via some test commands:<br/>
[CDROM - Test Commands - Test Drive Mechanics](cdromdrive.md#cdrom-test-commands-test-drive-mechanics)<br/>
Note: Datasheets for CXD2510Q/CXA1782BR/CXD2545Q do exist.<br/>

#### CDROM Pinouts
[Pinouts - DRV Pinouts](pinouts.md#pinouts-drv-pinouts)<br/>
[Pinouts - HC05 Pinouts](pinouts.md#pinouts-hc05-pinouts)<br/>



##   CDROM Internal HC05 Instruction Set
#### ALU, Load/Store, Jump/Call
```
  Opcode      Clk HINZC Name Syntax
  x6 ...      2-5 --NZ- LDA  MOV  A,<op>      ;A=op
  xE ...      2-5 --NZ- LDX  MOV  X,<op>      ;X=op
  x7 ...      4-6 --NZ- STA  MOV  <op>,A      ;op=A
  xF ...      4-6 --NZ- STX  MOV  <op>,X      ;op=X
  xC ...      2-4 ----- JMP  JMP  <op>        ;PC=op
  xD ...      5-7 ----- JSR  CALL <op>        ;[SP]=PC, PC=op
  xB ...      2-5 H-NZC ADD  ADD  A,<op>      ;A=A+op
  x9 ...      2-5 H-NZC ADC  ADC  A,<op>      ;A=A+op+C
  x0 ...      2-5 --NZC SUB  SUB  A,<op>      ;A=A-op
  x2 ...      2-5 --NZC SBC  SBC  A,<op>      ;A=A-op-C
  x4 ...      2-5 --NZ- AND  AND  A,<op>      ;A=A AND op
  xA ...      2-5 --NZ- ORA  OR   A,<op>      ;A=A OR op
  x8 ...      2-5 --NZ- EOR  XOR  A,<op>      ;A=A XOR op
  x1 ...      2-5 --NZC CMP  CMP  A,<op>      ;A-op
  x3 ...      2-5 --NZC CPX  CMP  X,<op>      ;X-op
  x5 ...      2-5 --NZ- BIT  TEST A,<op>      ;A AND op
  A7,AF,AC = Reserved (no STA/STX/JMP with immediate operand)
```
Operands can be...<br/>
```
  Opcode      Clk ALU/LDA/LDX      Clk STA/STX          Clk JMP/CALL
  Ax nn         2 cmd r,nn           - N/A              -/6 call relative (BSR)
  Bx nn         3 cmd r,[nn]         4 mov [nn],r       2/5 cmd nn
  Cx nn mm      4 cmd r,[nnmm]       5 mov [nnmm],r     3/6 cmd nnmm
  Dx nn mm      5 cmd r,[X+nnmm]     6 mov [X+nnmm],r   4/7 cmd X+nnmm
  Ex nn         4 cmd r,[X+nn]       5 mov [X+nn],r     3/6 cmd X+nn
  Fx            3 cmd r,[X]          4 mov [X],r        2/5 cmd X
```

#### Read-Modify-Write
```
  Opcode      Clk HINZC Name Syntax
  xC ...      3-6 --NZ- INC  INC op      ;increment   ;op=op+1
  xA ...      3-6 --NZ- DEC  DEC op      ;decrement   ;op=op-1
  xF ...      3-6 --01- CLR  ??  op,00h  ;clear       ;op=op AND 00h
  x3 ...      3-6 --NZ1 COM  NOT op      ;complement  ;op=op XOR FFh
  x0 ...      3-6 --NZC NEG  NEG op      ;negate      ;op=00h-op
  x9 ...      3-6 --NZC ROL  RCL op      ;rotate left through carry
  x6 ...      3-6 --NZC ROR  RCR op      ;rotate right through carry
  x8 ...      3-6 --NZC LSL  SHL op      ;shift left logical
  x4 ...      3-6 --0ZC LSR  SHR op      ;shift right logical
  x7 ...      3-6 --NZC ASR  SAR op      ;shift right arithmetic
  xD ...      3-5 --NZ- TST  TEST op,FFh ;test for negative or zero (AND FFh?)
  x1,x2,x5,xB,xE = Reserved (except for: 42 = MUL)
```
Operands can be...<br/>
```
  Opcode      Clk RMW          Clk CLR                Clk TST
  3x nn         5 cmd [nn]       5 MOV [nn],00h         4 TEST [nn],0FFh
  4x            3 cmd A          3 MOV A,00h,slow       3 TEST A,0FFh,slow
  5x            3 cmd X          3 MOV X,00h,slow       3 TEST X,0FFh
  6x nn         6 cmd [X+nn]     6 MOV [X+nn],00h       5 TEST [X+nn],0FFh
  7x            5 cmd [X]        5 MOV [X],00h          4 TEST [X],0FFh
```
CLR includes a dummy-read-cycle, whilst TST does omit the dummy-write cycle.<br/>
The ",slow" RMW opcodes are smaller, but slower than equivalent ALU opcodes.<br/>

#### Bit Manipulation and Bit Test with Relative Jump (to $+3+/-dd)
```
  Opcode      Clk HINZC Name  Syntax
  00h+i*2 nn dd 5 ----C BRSET JNZ [nn].i,dest  ;C=[nn].i, branch if set
  01h+i*2 nn dd 5 ----C BRCLR JZ  [nn].i,dest  ;C=[nn].i, branch if clear
  10h+i*2 nn    5 ----- BSET  SET [nn].i       ;set [nn].i
  11h+i*2 nn    5 ----- BCLR  RES [nn].i       ;clear [nn].i
```

#### Branch (Relative jump to $+2+/-nn)
```
  Opcode      Clk HINZC Name    Syntax
  20 nn         3 ----- BRA     JR  nn      ;branch always
  21 nn         3 ----- BRN     NUL nn      ;branch never
  22 nn         3 ----- BHI     JA  nn      ;if C=0 and Z=0, higher        ?
  23 nn         3 ----- BLS     JBE nn      ;if C=1 or Z=1, lower or same  ?
  24 nn         3 ----- BCC/BHS JNC/JAE nn  ;if C=0, carry clear, higher.same
  25 nn         3 ----- BCS/BLO JC/JB nn    ;if C=1, carry set, lower
  26 nn         3 ----- BNE     JNZ/JNE nn  ;if Z=0, not equal / not zero
  27 nn         3 ----- BEQ     JZ/JE nn    ;if Z=1, equal / zero
  28 nn         3 ----- BHCC    JNH nn      ;if H=0, half-carry clear
  29 nn         3 ----- BHCS    JH  nn      ;if H=1, half-carry set
  2A nn         3 ----- BPL     JNS nn      ;if S=0, plus / not signed
  2B nn         3 ----- BMI     JS  nn      ;if S=1, minus / signed
  2C nn         3 ----- BMC     JEI nn      ;if I=0, interrupt mask clear
  2D nn         3 ----- BMS     JDI nn      ;if I=1, interrupt mask set
  2E nn         3 ----- BIL     JIL nn      ;if XX=LO, interrupt line low
  2F nn         3 ----- BIH     JIH nn      ;if XX=HI, interrupt line high
  AD nn         6 ----- BSR     CALL relative nn  ;branch to subroutine always
```

#### Control/Misc
```
  Opcode      Clk HINZC Name Syntax
  9D            2 ----- NOP  NOP            ;no operation
  97            2 ----- TAX  MOV X,A        ;transfer A to X
  9F            2 ----- TXA  MOV A,X        ;transfer X to A
  9C            2 ----- RSP  MOV SP,00FFh   ;reset stack pointer (SP=00FFh)
  42           11 0---0 MUL  MUL X,A        ;X:A=X*A (unsigned multiply)
  81            6 ----- RTS  RET            ;return from subroutine
  80            9 xxxxx RTI  RETI           ;return from interrupt
  99            2 ----1 SEC  STC            ;set carry flag
  98            2 ----0 CLC  CLC            ;clear carry flag
  9B            2 -1--- SEI  DI             ;set interrupt mask (disable ints)
  9A            2 -0--- CLI  EI             ;clear interrupt mask (enable ints)
  8E          ..2 -0--- STOP STOP           ;?
  8F          ..2 -0--- WAIT WAIT           ;?
  83           10 -1--- SWI  SWI            ;software interrupt ...? PC=[FFFCh]
  <IRQ>         ? ????? Interrupt           ;?                       PC=[FFFxh]
  <RESET>       ? ????? Reset               ;?                       PC=[FFFEh]
  82,84..8D,90..96,9E = Reserved
```
MUL isn't supported in original "M146805 CMOS" family (MUL is used/supported in
PSX cdrom controller).<br/>

#### Registers
```
  A   8bit  accumulator
  X   8bit  index register
  SP  6bit  stack pointer (range 00C0h..00FFh)
  PC  16bit program pointer (range 0000h..FFFFh)
  CCR 5bit  condition code register (flags) (111HINZC)
```

#### Pushed on IRQ are:
```
  SP.highest PC.lo
             PC.hi
             X
             A
  SP.lowest  Flags (CCR, 5bit condition code register) (111HINZC)
```

#### Addressing Modes
```
  nn       immediate             ;00h..FFh
  [nn]     direct address        ;[0000h..00FFh]
  [nnmm]   extended address      ;[0000h..FFFFh]
  [X]      indexed, no offset    ;[0000h..00FFh]
  [X+nn]   indexed, 8bit offset  ;[0000h..01FEh]
  [X+nnmm] indexed, 16bit offset ;[0000h..FFFFh]
  [nn].i   bit                   ;[0000h..00FFh].bit0..7
  dd       relative              ;$+2..3+(-80h..+7Fh)
```
Notes:<br/>
```
  operand "X+nn" performs an unsigned addition, and can address 0000h..01FEh.
  16bit operands (nnmm) are encoded in BIG-ENDIAN format (same for pushed PC).
```

#### Exception Vectors
Exception vectors are 16bit BIG-ENDIAN values at FFF0h-FFFFh (or at FFE0h-FFEFh
when running in Motorola Bootstrap mode).<br/>
```
  Vector Prio Usage
  FFF0h  7=lo TBI Vector (Timebase)
  FFF2h  6    SSPI Vector (SPI bus)     (SPI1 and SPI2)
  FFF4h  5    Timer 2 Interrupt Vector  (Timer 2 Input/Compare)
  FFF6h  4    Timer 1 Interrupt Vector  (Timer 1 Input/Compare/Overflow)
  FFF8h  3    KWI Vector (Key Wakeup)   (KWI0..7 pins)
  FFFAh  2    External Interrupt Vector (/IRQ1 and /IRQ2 pins)
  FFFCh  none Software Interrupt Vector (SWI opcode)            ;\regardless of
  FFFEh  1=hi Reset Vector              (/RESET signal and COP) ;/CPU's "I"
```

#### Directives/Pseudos (used by a22i assembler; in no$psx utility menu)
```
  .hc05         select HC05 instruction set (default would be .mips)
  .nocash       select nocash syntax (default would be .native opcode names)
  db ...        define 8bit byte(s), or quoted ascii strings
  dw ...        define 16bit word(s) in BIG ENDIAN (for HC05 exception vectors)
  org nnnn      change origin for following opcodes
  end           end of file
  mov c,[nn].i  alias for "jnz [nn].i,$+3" (dummy jump & set carry=[nn].i)
```



##   CDROM Internal HC05 On-Chip I/O Ports
#### HC05 Port 3Eh - MISC - Miscellaneous Register (R/W)
```
  0    OPTM  Option Map Select (bank-switching for Port 00h..0Fh)
  1    FOSCE Fast (Main) Oscillator Enable (0=Disable OSC, 1=Normal)
  2-3  SYS   System Clock Select (0=OSC/2, 1=OSC/4, 2=OSC/64, 3=XOSC/2)
  4-5  -     Not used (0)
  6    STUP  XOSC Time Up Flag   (R)
  7    FTUP  OSC Time Up Flag    (R)   (0=Busy, 1=Ready/Good/Stable)
```
Note: For PSX, OSC is 4.0000MHz (PU-7/PU-8), 4.2336MHz (PU-18 and up). SysClk
is usually set to OSC/2, ie. around 2MHz.<br/>

#### HC05 Port OPTM=0:00h - PORTA - Port A Data Register (R/W)
#### HC05 Port OPTM=0:01h - PORTB - Port B Data Register (R)
#### HC05 Port OPTM=0:02h - PORTC - Port C Data Register (R/W)
#### HC05 Port OPTM=0:03h - PORTD - Port D Data Register (R/W)
#### HC05 Port OPTM=0:04h - PORTE - Port E Data Register (R/W)
#### HC05 Port OPTM=0:05h - PORTF - Port F Data Register (R) (undoc: R/W)
These are general purpose I/O ports (controlling external pins). Some ports are
Input-only, and some can be optionally used for special things (like IRQs,
SPI-bus, or as Timer input/output).<br/>
```
  PA.0-7  PAn   Port A Bit0..7 Input/Output            (0=Low, 1=High) (R/W)
  PB.0-7  PBn   Port B Bit0..7 Input        /KWI0..7   (0=Low, 1=High) (R)
  PC.0    PC0   Port C Bit0    Input/Output /SDI1 (SPI)(0=Low, 1=High) (R/W)
  PC.1    PC1   Port C Bit1    Input/Output /SDO1 (SPI)(0=Low, 1=High) (R/W)
  PC.2    PC2   Port C Bit2    Input/Output /SCK1 (SPI)(0=Low, 1=High) (R/W)
  PC.3    PC3   Port C Bit3    Input/Output /TCAP (T1) (0=Low, 1=High) (R/W)
  PC.4    PC4   Port C Bit4    Input/Output /EVI  (T2) (0=Low, 1=High) (R/W)
  PC.5    PC5   Port C Bit5    Input/Output /EVO  (T2) (0=Low, 1=High) (R/W)
  PC.6    PC6   Port C Bit6    Input/Output /IRQ2      (0=Low, 1=High) (R/W)
  PC.7    PC7   Port C Bit7    Input/Output /IRQ1      (0=Low, 1=High) (R/W)
  PD.0-7  PDn   Port D Bit0..7 Input/Output            (0=Low, 1=High) (R/W)
  PE.0-7  PEn   Port E Bit0..7 Input/Output            (0=Low, 1=High) (R/W)
  PF.0-7  PFn   Port F Bit0..7 Input/Undoc  A/D-input  (0=Low, 1=High) (R)(R/W)
```

#### HC05 Port OPTM=1:00h - DDRA - Port A Data Direction Register (R/W)
#### HC05 Port OPTM=1:02h - DDRC - Port C Data Direction Register (R/W)
#### HC05 Port OPTM=1:03h - DDRD - Port D Data Direction Register (R/W)
#### HC05 Port OPTM=1:04h - DDRE - Port E Data Direction Register (R/W)
#### HC05 Port OPTM=1:05h - DDRF - Port F Data Direction Register (undoc)
```
  DDRX.0-7  DDRXn Port X Data Direction Bit0..7 (0=Input, 1=Output) (R/W)
```
Officially, there are no DDRB and DDRF registers (Port B and F are always
Inputs). Although, actually, Motorola's Bootstrap RAM \<does\> manipulate
DDRF.<br/>

#### HC05 Port OPTM=1:08h - RCR1 - Resistor Control Register 1 (R/W)
#### HC05 Port OPTM=1:09h - RCR2 - Resistor Control Register 2 (R/W)
```
  RCR1.0    RAL   Port A.Bit0-3 Pullup Resistors (0=Off, 1=On)
  RCR1.1    RAH   Port A.Bit4-7 Pullup Resistors (0=Off, 1=On)
  RCR1.2    RBL   Port B.Bit0-3 Pullup Resistors (0=Off, 1=On)
  RCR1.3    RBH   Port B.Bit4-7 Pullup Resistors (0=Off, 1=On)
  RCR1.4    RGL   Port G.Bit0-3 Pullup Resistors (0=Off, 1=On) ;\
  RCR1.5    RGH   Port G.Bit4-7 Pullup Resistors (0=Off, 1=On) ; on chips
  RCR1.6    RHL   Port H.Bit0-3 Pullup Resistors (0=Off, 1=On) ; with Port G,H
  RCR1.7    RHH   Port H.Bit4-7 Pullup Resistors (0=Off, 1=On) ;/
  RCR2.0-7  RCn   Port C.Bit0-7 Pullup Resistors (0=Off, 1=On)
```

#### HC05 Port OPTM=1:0Ah - WOM1 - Open Drain Output Control Register 1 (R/W)
#### HC05 Port OPTM=1:0Bh - WOM2 - Open Drain Output Control Register 2 (R/W)
```
  WOM1.0   AWOML Port A.Bit0-3 Open Drain Mode when DDR=1 (0=No, 1=Open Drain)
  WOM1.1   AWOMH Port A.Bit4-5 Open Drain Mode when DDR=1 (0=No, 1=Open Drain)
  WOM1.2   GWOML Port G.Bit0-3 Open Drain Mode when DDR=1 (0=No, 1=Open Drain)
  WOM1.3   GWOMH Port G.Bit4-5 Open Drain Mode when DDR=1 (0=No, 1=Open Drain)
  WOM1.4   HWOML Port H.Bit0-3 Open Drain Mode when DDR=1 (0=No, 1=Open Drain)
  WOM1.5   HWOMH Port H.Bit4-5 Open Drain Mode when DDR=1 (0=No, 1=Open Drain)
  WOM1.6-7 -     Not used (0)
  WOM2.0-5 CWOMn Port C.Bit0..5 Open Drain Mode when DDR=1 (0=No, 1=Open Drain)
  WOM2.6-7 -     Not used (always both bits set)
```

==== Interrupts =====<br/>

#### HC05 Port OPTM=0:08h - INTCR - Interrupt Control Register (R/W)
```
  0-1  -     Not used (0)
  2    IRQ2S IRQ2 Select Edge-Sensitive Only (0=LowLevelAndNegEdge, 1=NegEdge)
  3    IRQ1S IRQ1 Select Edge-Sensitive Only (0=LowLevelAndNegEdge, 1=NegEdge)
  4    KWIE  Key Wakeup Interrupt Enable (0=Disable, 1=Enable)
  5    -     Not used (0)
  6    IRQ2E IRQ2 Interrupt Enable (0=Disable, 1=Enable)
  7    IRQ1E IRQ1 Interrupt Enable (0=Disable, 1=Enable)
```

#### HC05 Port OPTM=0:09h - INTSR - Interrupt Status Register (R and W)
```
  0    RKWIF Reset Key Wakeup Interrupt Flag (0=No Change, 1=Reset) (W)
  1    -     Not used (0)
  2    RIRQ2 Reset IRQ2 Interrupt Flag       (0=No Change, 1=Reset) (W)
  3    RIRQ1 Reset IRQ1 Interrupt Flag       (0=No Change, 1=Reset) (W)
  4    KWIF  Key Wakeup Interrupt Flag (PB/KWI)       (0=No, 1=IRQ) (R)
  5    -     Not used (0)
  6    IRQ2F IRQ2 Interrupt Flag (PC6)                (0=No, 1=IRQ) (R)
  7    IRQ1F IRQ1 Interrupt Flag (PC7)                (0=No, 1=IRQ) (R)
```

#### HC05 Port OPTM=1:0Eh - KWIE - Key Wakeup Interrupt Enable Register (R/W)
```
  0-7  KWIEn Port B.Bit0..7 Key Wakeup Interrupt Enable (0=Disable, 1=Enable)
```

==== SPI Bus ====<br/>

#### HC05 Port OPTM=0:0Ah - SPCR1 - Serial Peripheral Control Register 1 (R/W)
```
  0    SPRn  SPI Clock Rate (0=ProcessorClock/2, 1=ProcessorClock/16)
  1-3  -     Not used (0)
  4    MSTRn SPI Master Mode Select      (0=Slave/SCK.In, 1=Master/SCK.Out)
  5    DORDn SPI Data Transmission Order         (0=MSB First, 1=LSB First)
  6    SPEn  SPI Enable (SPI1:PortC, SPI2:PortG) (0=Disable, 1=Enable)
  7    SPIEn SPI Interrupt Enable (... ack HOW?) (0=Disable, 1=Enable)
```

#### HC05 Port OPTM=0:0Bh - SPSR1 - Serial Peripheral Status Register 1 (R)
```
  0-5  -     Not used (0)
  6    DCOLn SPI Data Collision Occurred         (0=No, 1=Collision)
  7    SPIFn SPI Transfer Complete Flag          (0=Busy, 1=Complete) (R)
```
Note: SPSR1.7 appears to be reset after reading SPSR1 (probably same for
SPSR1.6, and maybe also same for whatever SPI IRQ signal).<br/>

#### HC05 Port OPTM=0:0Ch - SPDR1 - Serial Peripheral Data Register 1 (R/W)
```
  0-7  BITn  Data to be sent / being received
```

==== Time Base / Config ====<br/>

#### HC05 Port 10h - TBCR1 - Time Base Control Register 1 (R/W)
```
  0-1  T2R   Timer2 Prescaler (0=SysClk, 1=SysClk/4, 2=SysClk/32, 3=SysClk/256)
  2-3  T3R   PWM Prescaler    (0=CLK3, 1=CLK3/2, 2=CLK3/8, 3=Timer2compare)
  4-6  -     Not used (0)
  7    TBCLK Time Base Clock (0=XOSC, 1=OSC/128) ;<-- write-able only ONCE
```

#### HC05 Port 11h - TBCR2 - Time Base Control Register 2 (R/W, some bits R or W)
```
  0    COPC  COP Clear 2bit COP timeout divider (0=No Change, 1=Clear) (W)
  1    COPE  COP Enable                          ;<-- write-able only ONCE
  2    -     Not used (0)
  3    RTBIF Reset Time Base Interrupt Flag (0=No Change, 1=Clear TBIF) (W)
  4-5  TBR   Time Base Interrupt Rate (0=TBCLK/128, 1=/4096, 2=/8192, 3=/16384)
  6    TBIE  Time Base Interrupt Enable (0=Disable, 1=Enable)
  7    TBIF  Time Base Interrupt Flag   (0=No, 1=IRQ)        (R)
```

#### HC05 Port OPTM=1:0Fh - MOSR - Mask Option Status Register (R)
```
  0-4  -     Not used (0)
  5    XOSCR XOSC Feedback Resistor (0=None, 1=Implemented)
  6    OSCR  OSC Feedback Resistor  (0=None, 1=Implemented)
  7    RSTR  /RESET Pullup Resistor (0=None, 1=Implemented)
```
Reading this register returns A0h (on PSX/PSone with 52pin chips).<br/>

==== Timer 1 ====<br/>

#### HC05 Port 12h - TCR - Timer 1 Control Register (R/W)
```
  0    OLVL  Output Level on TCMP pin on Compare Match? (0=Low, 1=High)
  1    IEDG  Input Edge on TCAP pin (0=NegativeEdge, 1=PositiveEdge)
  2-4  -     Not used (0)
  5    TOIE  Timer Overflow Interrupt Enable (0=Disable, 1=Enable)
  6    OC1IE Output Compare Interrupt Enable (0=Disable, 1=Enable)
  7    ICIE  Input Capture Interrupt Enable  (0=Disable, 1=Enable)
```

#### HC05 Port 13h - TSR - Timer 1 Status Register (R)
```
  0-4  -     Not used (0)
  5    TOF   Timer Overflow Flag (0=No, 1=Yes) (R) ;clear by Port 19h access
  6    OC1F  Output Compare Flag (0=No, 1=Yes) (R) ;clear by Port 17h access
  7    ICF   Input Capture Flag  (0=No, 1=Yes) (R) ;clear by Port 15h access
```

#### HC05 Port 14h - ICH - Timer 1 Input Capture High (undoc)
#### HC05 Port 15h - ICL - Timer 1 Input Capture Low (undoc)
```
  0-15 Capture Value
```

#### HC05 Port 16h - OC1H - Timer 1 Output Compare 1 High (undoc)
#### HC05 Port 17h - OC1H - Timer 1 Output Compare 1 Low (undoc)
```
  0-15 Compare Value
```

#### HC05 Port 18h - TCNTH - Timer 1 Counter 1 High (undoc)
#### HC05 Port 19h - TCNTL - Timer 1 Counter 1 Low (undoc)
```
  0-15 Counter
```

#### HC05 Port 1Ah - ACNTH - Alternate Counter High (undoc)
#### HC05 Port 1Bh - ACNTL - Alternate Counter Low (undoc)
```
  0-15 Alternate Counter (uh, what?)
```

==== Timer 2 ====<br/>

#### HC05 Port 1Ch - TCR2 - Timer 2 Control Register (R/W)
```
  0    OL2   Timer Output 2 Edge (0=Falling, 1=Rising)
  1    OE2   Timer Output 2 Enable (EVO) (0=Disable, 1=Enable)
  2    IL2   Timer Input 2 Edge/Level (0=Low/Falling, 1=High/Rising)
  3    IM2   Timer Input 2 Mode Select for EVI (0=EventMode, 1=GatedByCLK2)
  4    T2CLK Timer 2 Clock Select (0=CLK2 from Prescaler, 1=EXCLK from EVI)
  5    -     Not used (0)
  6    OC2IE Output Compare 2 Interrupt Enable    (0=Disable, 1=Enable)
  7    TI2IE Timer Input 2 Interrupt Enable (EVI) (0=Disable, 1=Enable)
```

#### HC05 Port 1Dh - TSR2 - Timer 2 Status Register (R/W)
```
  0-1  -     Not used (0)
  2    ROC2F Reset Output Compare 2 Interrupt Flag (0=No Change, 1=Clear) (W)
  3    RTI2F Reset Timer Input 2 Interrupt Flag    (0=No Change, 1=Clear) (W)
  4-5  -     Not used (0)
  6    OC2F  Output Compare 2 Interrupt Flag    (0=No, 1=Yes) (R)
  7    TI2F  Timer Input 2 Interrupt Flag (EVI) (0=No, 1=Yes) (R)
```

#### HC05 Port 1Eh - OC2 - Timer 2 Output Compare Register (R/W)
```
  0-7  Compare Value ("Transferred to buffer on certain events?")
```

#### HC05 Port 1Fh - TCNT2 - Timer 2 Counter Register (R) (W=Set Counter to 01h)
```
  0-7  Counter Value, incremented at T2R (set to 01h on Compare Matches)
```

==== Reserved ====<br/>

#### HC05 Port 3Fh - Unknown/Unused
Reading this port via Sony's test command returns 20h (same as openbus), but
reading it via Motorola's selftest function returns 00h (unlike openbus), so it
seems to have some unknown/undocumented function; bit5 might indicate selftest
mode, or it might reflect initialization of whatever other ports.<br/>

#### HC05 Port OPTM=0:06h..07h,0Dh..0Fh - Reserved
#### HC05 Port OPTM=1:01h,06h..07h,0Ch..0Dh - Reserved
#### HC05 Port 20h..3Dh - Reserved
These ports are unused/reserved. Trying to read them on a PSone does return 20h
(possibly the prefetched next opcode value from the RAM test command). Other
HC05 variants contain some extra features in these ports:<br/>
[CDROM Internal HC05 On-Chip I/O Ports - Extras](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-hc05-on-chip-io-ports-extras)<br/>
The PSX CDROM BIOS doesn't use any of these ports - execpt, it is writing
[20h]=2Eh (possibly to disable unused LCD hardware; which might be actually
present in the huge 80pin HC05 chips on old PU-7 mainboards).<br/>

#### HC05 Openbus
Openbus values can be read from invalid memory locations, on PSX with 52pin
chips:<br/>
```
  I/O bank 0:    0:06h..07h, 0:0Dh..0Fh
  I/O bank 1:    1:01h, 1:06h..07h, 1:0Ch..0Dh, and upper 4bit of 1:05h
  Unbanked I/O:  20h..3Dh
  Unused Memory: 0240h..0FFFh, 5000h..FDFFh
```
The returned openbus value depends on the opcode's memory operand:<br/>
```
  [nn],[mmnn],[nn+x],[mmnn+x] --> returns LAST byte of current opcode (=nn)
  [x]                         --> returns FIRST byte of following opcode
```



##   CDROM Internal HC05 On-Chip I/O Ports - Extras
#### HC05 Port OPTM=0:0Dh - SPCR2 - Serial Peripheral Control Register 2 (R/W)
#### HC05 Port OPTM=0:0Eh - SPSR2 - Serial Peripheral Status Register 2 (R)
#### HC05 Port OPTM=0:0Fh - SPDR2 - Serial Peripheral Data Register 2 (R/W)
This is a second SPI channel, works same as first SPI channel, but using the
lower 3bits of Port G (instead of Port C) for the SPI signals.<br/>

#### HC05 Port OPTM=0:06h - PORTG - Port G Data Register (R/W)
#### HC05 Port OPTM=0:07h - PORTH - Port H Data Register (R/W)
#### HC05 Port 3Ch - PORTJ - Port J Data Register (R/W)
```
  PG.0    PG0   Port G Bit0    Input/Output /SDI2      (0=Low, 1=High) (R/W)
  PG.1    PG1   Port G Bit1    Input/Output /SDO2      (0=Low, 1=High) (R/W)
  PG.2    PG2   Port G Bit2    Input/Output /SCK2      (0=Low, 1=High) (R/W)
  PG.3    PG3   Port G Bit3    Input/Output /TCMP      (0=Low, 1=High) (R/W)
  PG.4    PG4   Port G Bit4    Input/Output /PWM0      (0=Low, 1=High) (R/W)
  PG.5    PG5   Port G Bit5    Input/Output /PWM1      (0=Low, 1=High) (R/W)
  PG.6    PG6   Port G Bit6    Input/Output /PWM2      (0=Low, 1=High) (R/W)
  PG.7    PG7   Port G Bit7    Input/Output /PWM3      (0=Low, 1=High) (R/W)
  PH.0-7  PHn   Port H Bit0..7 Input/Output            (0=Low, 1=High) (R/W)
  PJ.0-3  PJn   Port J Bit0..3 Output                  (0=Low, 1=High) (R/W)
  PJ.4-7  -     Not used (0)
```

#### HC05 Port OPTM=1:06h - DDRG - Port G Data Direction Register (R/W)
#### HC05 Port OPTM=1:07h - DDRH - Port H Data Direction Register (R/W)
```
  0-7  DDRXn Port X Data Direction Bit0..7 (0=Input, 1=Output) (R/W)
```

#### HC05 Port 20h - LCDCR - LCD Control Register (R/W)
```
  0    -     Not used (0)
  1    PDH   Select Port D (H) (0=FP35-FP38 pins, 1=PD7-PD4 pins)
  2    PEL   Select Port E (L) (0=FP31-FP34 pins, 1=PE3-PE0 pins)
  3    PEH   Select Port E (H) (0=FP27-FP30 pins, 1=PE7-PE4 pins)
  4    -     Not used (0)
  5-6  DUTY  LCD Duty Select (...)
  7    LCDE  LCD Output Enable BP and FP pins (0=Disable, 1=Enable)
```

#### HC05 Port 21h..34h - LCDDR1..20 - LCD Data Register 1..20 (R/W)
```
  0-3  First Data Unit  ;\Fourty 4bit LCD values (in the twenty registers)
  4-7  Second Data Unit ;/(some duties use only the LSBs of that 4bit values)
```

#### HC05 Port 34h - PWMCR - PWM Pulse Width Modulation Control Register (R/W)
```
  0-3  CH0-3 PWM Channel 0..3 on Port G.Bit4-7 Enable (0=Disable, 1=Enable)
  4-7  -     Not used (0)
```

#### HC05 Port 35h - PWMCNT - PWM Counter Register (R) (W=Set Counter to FFh)
```
  0-7  PWM Counter, incremented at PHI2 (range 01h..FFh)
```

#### HC05 Port 36h - PWMDR0 - PWM Duty Register 0 (R/W)
#### HC05 Port 37h - PWMDR1 - PWM Duty Register 1 (R/W)
#### HC05 Port 38h - PWMDR2 - PWM Duty Register 2 (R/W)
#### HC05 Port 39h - PWMDR3 - PWM Duty Register 3 (R/W)
```
  0-7  Duty (N cycles High, 255-N cycles Low)
```

#### HC05 Port 3Ah - ADR - A/D Data Register (R)
```
  0-3  A/D Conversion result (probably unsigned, 00h=Lowest, FFh=Max voltage?)
```

#### HC05 Port 3Bh - ADSCR - A/D Status and Control Register (R/W)
```
  0-3  CH0-3 A/D Channel (0..7=PortF.Bit0-7, 8..0Fh=Reserved/Vref/FactorTest)
  4    -     Not used (0)
  5    ADON  A/D Charge Pump enable (0=Disable, 1=Enable)
  6    ADRC  A/D RC Oscillator On (0=Normal/Use CPU Clock, 1=Use RC Clock)
  7    COCO  A/D Conversion Complete (0=Busy, 1=Complete) (R)
```

#### HC05 Port 3Dh - PCR - Program Control Register (R/W) (for EPROM version)
```
  0    PGM   EPROM Program Command (0=Normal, 1=Apply Programming Power)
  1    ELAT  EPROM Latch Control (0=Normal/Read, 1=Latch/Write)
  2-7  RES   Reserved for Factory Testing (always 0 in user mode)
```



##   CDROM Internal HC05 I/O Port Usage in PSX
#### Port A - Data (indexed via Port E)
```
  porta.0-7 i/o  CXD1815Q.Data (indexed via Port E)
  porta.0   in   debug.dta.serial.in  ;\normally unused (exists in early bios)
  porta.1   out  debug.dta.serial.out ; (prototype/debug_status stuff)
  porta.2   out  debug.clk.serial.out ;/(with portc.5 = debug.select)
```

#### Port B - Inputs
```
  portb.0   in   F-BIAS  ;unused
  portb.1   in   SCEx input (serial 250 baud, received via 1000Hz timer2 irq)
  portb.2   in   LMTSW  aka /POS0        ;\pos0 and door switches
  portb.3   in   DOOR   aka SHELL_OPEN   ;/
  portb.4   in   TEST2
  portb.5   in   TEST1 (CL316) enter test mode (instead of mainloop)
  portb.6   in   COUT   ;<-- unused, extra pin, not "SENSE=COUT"
  portb.7   in   CXD2510Q.SENSE ;-from CXD2510Q (and forwarded from CXA1782BR)
```

#### Port C - Inputs/Outputs
```
  portc.0   in   CXD2510Q.SUBQ  ;\
  portc.1   in?  NC (SPI.OUT)   ; used via SPDR1 to receive SPI bus SUBQ data
  portc.2   out  CXD2510Q.SQCK  ;/
  portc.3   out  SPEED
  portc.4   out    ="SPEED XOR 1"  ... AL/TE ... or CG ... or MIRR ?
  portc.5   out  ROMSEL: debug.select   (or "SCLK" on later boards???)
  portc.6   in   CXD1815Q.XINT/IRQ2 ;unused (instead INTSTS bits are polled)
  portc.7   in   CXD2510Q.SCOR/IRQ1 ;used via polling INTSR.7 (not as irq)
```

#### Port D - Outputs
```
  portd.0   out  NC             ;-unused (always 1)
  portd.1   out  CXD2510Q.DATA  ;\serial bus for CXD2510Q
  portd.2   out  CXD2510Q.XLAT  ; (and also forwarded to CXA1782BR)
  portd.3   out  CXD2510Q.CLOK  ;/
  portd.4   out  CXD1815Q.DECCS ;\
  portd.5   out  CXD1815Q.DECWR ; control for data/index on Port A/E
  portd.6   out  CXD1815Q.DECRD ;/
  portd.7   out  LDON  ... IC723.Pin11 ... maybe "laser on" ?
```

#### Port E - Index (for data on Port A)
```
  porte.0-4 out  CXD1815Q.Index (for data on Port A)
  porte.5   out  NC, not used
  porte.6   out  NC, see "idx_4xh" maybe test signal ???
  porte.7   out? NC, TEST? configured as OUTPUT... but used as INPUT?
```

#### Port F - Motorola Bootstrap Serial I/O (not used in cdrom bios)
```
  portf.0   out  NC, TX         ;\
  portf.1   in   NC, RX         ; not used by sony's cdrom bios
  portf.2   out  NC, RTS        ; (but used by motorola's bootstrap rom)
  portf.3   out  NC, DTR        ;/
  portf.0   in   Serial Data In  (from daughterboard)  ;\
  portf.1   out  Serial Data Out   (to daughterboard)  ; usage in SCPH-5903
  portf.2   out  Serial Clock Out  (to daughterboard)  ; (PSX with Video CD)
  portf.3   out  Audio/Video Select (0=Normal, 1=VCD)  ;/
  portf.4-7 -    NC, not used (probably pins don't even exist)
```

#### Other HC05 I/O Ports
```
  SPI 1   - used for receiving SUBQ (via Port C)
  IRQ 1   - used for latching/polling SUBQ's "SCOR" (not used as interrupt)
  IRQ 2   - connects to CXD1815Q.XINT, but isn't actually used at all
  Timer 1 - unused
  Timer 2 - generates 1000Hz interrupts (for 250 baud "SCEx" string transfers)
  DDRx    - data directions for Port A-F (as listed above)
```
Note: The PSX has the HC05 clocked via 4.00MHz oscillator (older boards), or
via 4.3MHz signal from SPU (newer boards); internally, the HC05 is clocked at
half of those frequencies (ie. around 2 MHz).<br/>



##   CDROM Internal HC05 Motorola Selftest Mode
#### 52-pin HC05 chips (newer psx cdrom controllers)
52-pin chips are used on LATE-PU-8 boards, and on later boards ranging from
PU-18 up to PM-41(2).<br/>
[CDROM Internal HC05 Motorola Selftest Mode (52pin chips)](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-hc05-motorola-selftest-mode-52pin-chips)<br/>

#### 80-pin HC05 chips (older psx cdrom controllers)
80-pin chips are used PU-7, EARLY-PU-8, and PU-9 boards.<br/>
[CDROM Internal HC05 Motorola Selftest Mode (80pin chips)](cdrominternalinfoonpsxcdromcontroller.md#cdrom-internal-hc05-motorola-selftest-mode-80pin-chips)<br/>

#### 32-pin HC05 chips (joypad/mouse)
Sony's Digital Joypad and Mouse are using 32pin chips (with TQFP-32 package),
which are probably containing Motorola HC05 CPUs, too. Unknown if/how those
chips can be switched into bootstrap/dumping modes.<br/>

#### Pinouts
[Pinouts - HC05 Pinouts](pinouts.md#pinouts-hc05-pinouts)<br/>



##   CDROM Internal HC05 Motorola Selftest Mode (52pin chips)
#### Motorola Bootstrap ROM
The Motorola MC68HC05 chips are including a small bootstrap ROM which gets
activated upon /RESET when having two pins strapped to following levels:<br/>
```
  Pin30 PortC.6 (/IRQ2) (/XINT) ----> wire to 3.5V (VCC)
  Pin31 PortC.7 (/IRQ1) (SCOR)  ----> wire to 7V (2xVCC)
```
Moreover, two pins are needed on /RESET for selecting a specific test mode:<br/>
```
  Pin16 PortB.0 ----> ModeSelectBit0 (0=GND, 1=3.5V)
  Pin17 PortB.1 ----> ModeSelectBit1 (0=GND, 1=3.5V)
```
The selectable four modes are:<br/>
```
  Mode0: Jump to RAM Address 0040h (useless when RAM is empty)
  Mode1: Semifunctional Selftest (useless)
  Mode2: Upload 200h bytes to RAM & jump to 0040h (allows fast/custom dumping)
  Mode3: Download ROM as ASCII hexdump (nice, but very slow)
```
The upload/download functions are using following additional pins:<br/>
```
  Pin50 PortF.0 ----> TX output (11bytes: 0Dh,0Ah," AAAA DD ")
  Pin51 PortF.1 <---- RX input  (1byte: "!" to request next 11 bytes)
  Pin52 PortF.2 ----> RTS output or so (not needed)
  Pin1  PortF.3 ----> DTR output or so (not needed)
  Ground ------------ GND for RX/TX
```
RX/TX are RS232-like serial signals (but using other voltages, 0=0V and
1=3.5V). Transfer format is 8-N-1, ie. one startbit(0), 8 databits LSB first,
no parity, one stopbit(1). Baudrate is OSC/2/208 (ie. 9616 bps for 4.000MHz, or
10176 bps for 4.2336MHz clock derived from CXD2545Q/CXD2938Q).<br/>
Note: Above pins may vary on some chips (namely on chips that don't have
PortF). The pins for entering bootstrap mode (PortC in this case) should be
described in datasheets; but transfer protocol and mode selection (PortB) and
transmission (PortF) aren't officially documented.<br/>

#### Mode2: Upload 200h bytes to RAM & jump to 0040h
This mode is very simple and powerful: After /RESET, you send 200h bytes to the
RX input (without any response on TX output), the bytes are stored at
0040h..023Fh in RAM, and the chip jumps to 0040h after transferring the last
byte. The uploaded program can contain a custum highspeed dumping function, or
perform hardware tests, etc. A custom dumping function for PSX/PSone can be
found at:<br/>
```
  http://www.psxdev.net/forum/viewtopic.php?f=70&t=557
```
After uploading the 200h-byte dumping function it will respond by send 4540h
bytes (containing some ASCII string, the 16.5Kbyte ROM image, plus dumps for
RAM and (banked) I/O port region, plus openbus tests for unused memory and I/O
regions.<br/>

#### Wiring for Mode2 on PSX/PSone consoles with 52-pin HC05 chips
```
                            .------------ pin31, PC7, SCOR, cut the connection
                   39       |   27               to Signal Processor,
                 .-----------------.             then wire Pin31 to 7.5V
              40 |                 | 26
                 |  C nnnn         |
                 |  SC4309nnPB     |
                 |  G63C 185       |
  pin50, TX <--- |                 | ---- pin17, PB1, SCEX, wire to 3.5V,
  pin51, RX ---> |                 |                  for Mode2 Selection
              52 | O               | 14
                 '-----------------'
                   1            13
```
Good places to pick 3.5V and 7.5V from nice solder pads are:<br/>
```
  CN602.Pin1  = 7.5V     ;\on PSX boards (with either 5pin or
  CN602.Pin3  = 3.5V     ;/               7pin CN602 connectors)
  IC601.Pin1  = 7.5V     ;-on PSone boards (3pin 78M05 voltage regulator)
  IC102.Pin32 = 3.5V     ;-on PSone boards (32pin Main BIOS ROM chip)
```
The SCOR trace on Pin31, connects to Signal Processor...<br/>
```
  CXD2510Q.Pin63  (eg. on PU-8 boards)   ;\
  CXD2545Q.Pin74  (eg. on PU-18 boards)  ; either one of these, depending
  CXD1817R.Pin49  (eg. on PU-20 boards)  ; on which chipset you have
  CXD2938Q.Pin77  (eg. on PM-41 boards)  ;
  CXD2941R.Pin85  (eg. PM-41(2) boards)  ;/
```
cut that trace (preferably on the PCB between two vias or test points, so you
can later repair it easily) (better don't try to lift Pin31, it breaks off
easily)<br/>
Note: Mode2 also requires Pin16=Low, and Pin30=High (but PSX/PSone boards
should have those pins at that voltages anyways).<br/>

#### Mode3: Download ROM as ASCII hexdump
This mode is very slow and not too powerful. But it may useful if you can't get
Mode2 working for whatever reason. Wiring for Mode3 is same as above, plus
PortB.0=3.5V. In this mode, the chip will send one 0Dh,0Ah," AAAA DD " string
immediately after /RESET (with 16bit address "AAAA" (initially 1000h), and 8bit
data "DD"). Thereafter the chip will wait for incoming commands:<br/>
```
  4-digit ASCII HEX address --> change address, and return 0Dh,0Ah," AAAA DD "
  chr(00h) --> increment address, and return 0Dh,0Ah," AAAA DD "
  chr(07h) --> jump to current address (not so useful)
  other characters --> same as chr(00h)
  All digits/characters sent to RX input will produce an echo on TX output.
```
Basic setup would be wiring RX to GND (the chip will treat that as infinite
stream of start bits with chr(00h), so it will respond by sending data from
increasing addresses automatically; the increment wraps from 4FFFh to FE00h
(skipping the gap between Main ROM and Bootstrap ROM), and also wraps from
FFFFh to 0000h; transfer is ultraslow: 13 characters needed per dumped byte:
chr(00h) to chip, chr(00h) echo from chip, and 0Dh,0Ah," AAAA DD " from chip.<br/>



##   CDROM Internal HC05 Motorola Selftest Mode (80pin chips)
#### 80pin Sony 4246xx chips
And for anyone else planning to try this, these are the connections:<br/>
```
  Pin PortC
  46  PC7/IRQ1 (SCOR) disconnect from PCB, then wire the pin to Vtst (7.6V)
  45  PC6/IRQ2 (/XINT) wire to Vdd (3.5V) (you have to solder to the pin)
```
In bootstrap mode, Port A is used as follows:<br/>
```
  Pin PortA DDRA Usage
  23  PA0   in   RXD
  24  PA1   out  TXD
  25  PA2   in   -
  26  PA3   in   Testmode.bit0 (GND=0, 3.5V=1)
  27  PA4   in   Testmode.bit1 (GND=0, 3.5V=1)
  28  PA5   in   Testmode.bit2 (GND=0, 3.5V=1)
  29  PA6   out  RTS (don't care)
  30  PA7   out  -
```
The selectable testmodes are:<br/>
```
  PA5 PA4 PA3  Effect
  0   x   x    Jump to 0040h      ;\
  1   0   0    Test (complex)     ; not so useful
  1   0   1    Test (simple loop) ;/
  1   1   0    ROM Dump 4200h bytes (plain binary, non-ASCII)
  1   1   1    RAM Upload 100h bytes to 0040h..013Fh, then jump to 0040h
```
RX/TX are plain binary (non-ASCII), baudrate is 9600 (when using 4.000MHz
oscillator), transfer format is 8,N,2 (aka 8,N,1 with an extra pause bit).<br/>

#### Wiring for Upload/Download on PSX consoles with 80-pin HC05 chips
```
                  .------------ pin46, PC7/IRQ1, SCOR, cut & wire to 7.5V
                  |.----------- pin45, PC6/IRQ2, wire to 3.5V
         60       ||  41
       .-----------------.
    61 |               o | 40
       |  Sony Computer  |           ,----- pin28, PA5, wire to 3.5V
       |  Entertainment  | _________/  ,--- pin27, PA4, wire to 3.5V
       |  Inc. (C) E35D  | ==========='---- pin26, PA3, mode select
       |     4246xx 185  | ----> pin24, PA1, TXD (for ROM dump)
       |                 | <---- pin23, PA0, RXD (for RAM upload)
    80 | O               | 21
       '-----------------'
         1            20
```
Good places to pick 3.5V and 7.5V from nice solder pads are:<br/>
```
  CN602.Pin1  = 7.5V     ;\on PSX boards (with 7pin CN602 connectors)
  CN602.Pin3  = 3.5V     ;/
```
Credits to TriMesh for finding the 80pin chip's bootstrap signals.<br/>

#### Other 80pin chips
DTL-H100x uses 80pin chip with onchip PROM (chip text "(M) MC68HC705L15",
instead of "Sony [...] 4246xx"), wiring for serial dumping on that is unknown
(the bootstrap ROM may be a little different because it should contain PROM
burning functions). PU-9 boards boards seem to use a similar PROM (with some
sticker on it).<br/>
DTL-H2000 uses 80pin CXP82300 chip with socketed piggyback 32pin EPROM - that
chip is a Sony SPC700 CPU, not a Motorola HC05 CPU. Accordingly there's no
Motorola Bootstrap mode in it, but of course one can simply dump the EPROM with
standard eprom utilities, as done by TriMesh).<br/>



