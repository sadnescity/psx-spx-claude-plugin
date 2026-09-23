---
name: cdrom-test-protection
description: "PSX CDROM drive: test commands (version/region/chipset/SCEx), secret unlock, Video CD commands, response timing and queueing, mainloop behavior. Use when working with CDROM test/debug commands, copy protection, or response timing."
---

##   CDROM - Test Commands
[CDROM - Test Commands - Version, Switches, Region, Chipset, SCEx](#cdrom---test-commands---version-switches-region-chipset-scex)<br/>
[CDROM - Test Commands - Test Drive Mechanics](#cdrom---test-commands---test-drive-mechanics)<br/>
[CDROM - Test Commands - Prototype Debug Transmission](#cdrom---test-commands---prototype-debug-transmission)<br/>
[CDROM - Test Commands - Read/Write Decoder RAM and I/O Ports](#cdrom---test-commands---readwrite-decoder-ram-and-io-ports)<br/>
[CDROM - Test Commands - Read HC05 SUB-CPU RAM and I/O Ports](#cdrom---test-commands---read-hc05-sub-cpu-ram-and-io-ports)<br/>



##   CDROM - Test Commands - Version, Switches, Region, Chipset, SCEx
#### 19h,20h --\> INT3(yy,mm,dd,ver)
Indicates the date (Year-month-day, in BCD format) and version of the HC05
CDROM controller BIOS. Known/existing values are:<br/>
```
  (unknown)        ;DTL-H2000 (with SPC700 instead HC05)
  94h,09h,19h,C0h  ;PSX (PU-7)               19 Sep 1994, version vC0 (a)
  94h,11h,18h,C0h  ;PSX (PU-7)               18 Nov 1994, version vC0 (b)
  94h,11h,28h,01h  ;PSX (DTL-H2000)          28 Nov 1994, version v01 (debug)
  95h,05h,16h,C1h  ;PSX (LATE-PU-8)          16 May 1995, version vC1 (a)
  95h,07h,24h,C1h  ;PSX (LATE-PU-8)          24 Jul 1995, version vC1 (b)
  95h,07h,24h,D1h  ;PSX (LATE-PU-8,debug ver)24 Jul 1995, version vD1 (debug)
  96h,08h,15h,C2h  ;PSX (PU-16, Video CD)    15 Aug 1996, version vC2 (VCD)
  96h,08h,18h,C1h  ;PSX (LATE-PU-8,yaroze)   18 Aug 1996, version vC1 (yaroze)
  96h,09h,12h,C2h  ;PSX (PU-18) (japan)      12 Sep 1996, version vC2 (a.jap)
  97h,01h,10h,C2h  ;PSX (PU-18) (us/eur)     10 Jan 1997, version vC2 (a)
  97h,08h,14h,C2h  ;PSX (PU-20)              14 Aug 1997, version vC2 (b)
  98h,06h,10h,C3h  ;PSX (PU-22)              10 Jun 1998, version vC3 (a)
  99h,02h,01h,C3h  ;PSX/PSone (PU-23, PM-41) 01 Feb 1999, version vC3 (b)
  A1h,03h,06h,C3h  ;PSone/late (PM-41(2))    06 Jun 2001, version vC3 (c)
  (unknown)        ;PS2,   xx xxx xxxx, late PS2 models...?
```

#### 19h,21h --\> INT3(flags)
Returns the current status of the POS0 and DOOR switches.<br/>
```
  Bit0   = HeadIsAtPos0 (0=No, 1=Pos0)
  Bit1   = DoorIsOpen   (0=No, 1=Open)
  Bit2   = EjectButtonOrOutSwOrSo? (DTL-H2000 only) (always 0 on retail)
  Bit3-7 = AlwaysZero
```

#### 19h,22h --\> INT3("for Europe")
```
  Caution: Supported only in BIOS version vC1 and up. Not supported in vC0.
```
Indicates the region that console is to be used in:<br/>
```
  INT5(11h,10h)      --> NTSC, Japan (vC0)         --> requires "SCEI" discs
  INT3("for Europe") --> PAL, Europe               --> requires "SCEE" discs
  INT3("for U/C")    --> NTSC, North America       --> requires "SCEA" discs
  INT3("for Japan")  --> NTSC, Japan / NTSC, Asia  --> requires "SCEI" discs
  INT3("for NETNA")  --> Region-free yaroze version--> requires "SCEx" discs
  INT3("for US/AEP") --> Region-free debug version --> accepts unlicensed CDRs
```
The CDROMs must contain a matching SCEx string accordingly.<br/>
The string "for Europe" does also suggest 50Hz PAL/SECAM video hardware.<br/>
The Yaroze accepts any normal SCEE,SCEA,SCEI discs, plus special SCEW discs.<br/>

#### 19h,23h --\> INT3("CXD2940Q/CXD1817Q/CXD2545Q/CXD1782BR") ;Servo Amplifier
#### 19h,24h --\> INT3("CXD2940Q/CXD1817Q/CXD2545Q/CXD2510Q")  ;Signal Processor
#### 19h,25h --\> INT3("CXD2940Q/CXD1817Q/CXD1815Q/CXD1199BQ") ;Decoder/FIFO
```
  Caution: Supported only in BIOS version vC1 and up. Not supported in vC0.
```
Indicates the chipset that the CDROM controller is intended to be used with.
The strings aren't always precisely correct (CXD1782BR is actually CXA1782BR,
ie. CXA, not CXD) (and CXD1199BQ chips exist on PU-7 boards, but later PU-8
boards do actually use CXD1815Q) (and CXD1817Q is actually CXD1817R) (and newer
PSones are using CXD2938Q or possibly CXD2941R chips, but nothing called
CXD2940Q).<br/>
Note: Yaroze responds by CXD1815BQ instead of CXD1199BQ (but not by CXD1815Q).<br/>

#### 19h,04h --\> INT3(stat) ;Read SCEx string (and force motor on)
Resets the total/success counters to zero, and does then try to read the SCEx
string from the current location (the SCEx is stored only in the Lead-In area,
so, if the drive head is elsewhere, it will usually not find any strings,
unless a modchip is permanently simulating SCEx strings).<br/>
This is a raw test command (the successful or unsuccessful results do not
lock/unlock the disk). The results can be read with command 19h,05h (which will
terminate the SCEx reading), or they can be read from RAM with command
19h,60h,lo,hi (which doesn't stop reading). Wait 1-2 seconds before expecting
any results.<br/>
Note: Like 19h,00h, this command forces the drive motor to spin at standard
speed (synchronized with the data on the disk), works even if the shell is open
(but stops spinning after a while if the drive is empty).<br/>

#### 19h,05h --\> INT3(total,success)  ;Get SCEx Counters
Returns the total number of "Sxxx" strings received (where at least the first
byte did match), and the number of full "SCEx" strings (where all bytes did
match). Typically, the values are "01h,01h" for Licensed PSX Data CDs, or
"00h,00h" for disk missing, unlicensed data CDs, Audio CDs.<br/>
The counters are reset to zero, and SCEx receive mode is active for a few
seconds after booting a new disk (on power up, on closing the drive door, on
sending a Reset command, and on sub\_function 04h). The disk is unlocked if the
"success" counter is nonzero, the only exception is sub\_function 04h which does
update the counters, but does not lock/unlock the disk.<br/>



##   CDROM - Test Commands - Test Drive Mechanics
Signal Processor and Servo Amplifier<br/>

#### 19h,50h,msb[,mid,[lsb[,xlo]]] --\> INT3(stat)
Sends an 8bit/16bit/24bit command to the hardware, depending on number of
parameters:<br/>
```
  1 byte  --> send CX(Xx)       ;short 8bit command
  2 bytes --> send CX(Xxxx)     ;longer 16bit command
  3 bytes --> send CX(Xxxxxx)   ;full 24bit command
  4 bytes --> send CX(Xxxxxxxx) ;extended 32bit command (BIOS vC3 only)
  4..15 bytes: acts same as max (3 or 4 bytes) (extra bytes are ignored)
  0 bytes or more than 15 bytes: generates an error
```

#### 19h,51h,msb[,mid,[lsb]] --\> INT3(stat,hi,lo)  ;BIOS vC2/vC3 only
Supported by newer CDROM BIOSes only (such that use CXD2545Q or newer chips).<br/>
Works same as 19h,50h, but does additionally receive a response.<br/>
The command is always sending a 24bit CX(Xxxxxx) command, but it doesn't verify
the number of parameter bytes (when using more than 3 bytes: extra bytes are
ignored, when using less than 3 bytes: garbage is appended, which is somewhat
valid because 8bit/16bit commands can be padded to 24bit size by appending
"don't care" bits).<br/>
The command can be used to send any CX(..) command, but actually it does make
sense only for the get-status commands, see below "19h,51h,39h,xxh"
description.<br/>

#### 19h,51h,39h,xxh --\> INT3(stat,hi,lo)  ;BIOS vC2/vC3 only
Supported by newer CDROM BIOSes only (such that use CXD2545Q or newer chips).<br/>
Sends CX(39xx) to the hardware, and receives a response (the response.hi byte
is usually 00h for 8bit responses, or 00h..01h for 9bit responses). For
example, this can be used to dump the Coefficient RAM.<br/>

#### 19h,03h --\> INT3(stat) ;force motor off
Forces the motor to stop spinning (ignored during spin-up phase).<br/>

#### 19h,17h --\> INT3(stat) ;force motor on, clockwise, super-fast
#### 19h,01h --\> INT3(stat) ;force motor on, anti-clockwise, super-fast
#### 19h,02h --\> INT3(stat) ;force motor on, anti-clockwise, super-fast
#### 19h,10h --\> INT3(stat) ;force motor on, anti-clockwise, super-fast
#### 19h,18h --\> INT3(stat) ;force motor on, anti-clockwise, super-fast
Forces the drive motor to spin at maximum speed (which is much faster than
normal or double speed), in normal (clockwise), or reversed (anti-clockwise)
direction. The commands work even if the shell is open. The commands do not try
to synchronize the motor with the data on the disk (and do thus work even if no
disk is inserted).<br/>

#### 19h,00h --\> INT3(stat) ;force motor on, clockwise (even if shell open)
This command seems to have effect only if the drive motor was off. If it was
off, it does FFh-fills the TOC entries in RAM, and seek to the begin of the TOC
at 98:30:00 or so (where minute=98 means minus two). From that location, it
follows the spiral on the disk, although it does occassionally jump back some
seconds. After clearing the TOC, the command does not write new data to the TOC
buffer in RAM.<br/>
Note: Like 19h,04h, this command forces the drive motor to spin at standard
speed (synchronized with the data on the disk), works even if the shell is open
(but stops spinning after a while if the drive is empty).<br/>

#### 19h,11h --\> INT3(stat) ;Move Lens Up (leave parking position)
#### 19h,12h --\> INT3(stat) ;Move Lens Down (enter parking position)
#### 19h,13h --\> INT3(stat) ;Move Lens Outwards (away from center of disk)
#### 19h,14h --\> INT3(stat) ;Move Lens Inwards (towards center of disk)
Moves the laser lens. The inwards/outwards commands do move ONLY the lens (ie.
unlike as for Seek commands, the overall-laser-unit remains in place, only the
lens is moved).<br/>

#### 19h,15h - if motor on: move head outwards + inwards + motor off
Moves the drive head to outer-most and inner-most position. Note that the drive
doesn't have a switch that'd tell the controller when it has reached the
outer-most position (so it'll forcefully hit against the outer edge) (ie. using
this command too often may destroy the drive mechanics).<br/>
Note: The same destructive hit-outer-edge effect happens when using Setloc/Seek
with too large values (like minute=99h).<br/>

#### 19h,16h --\> INT3(stat) ;Unknown / makes some noise if motor is on
#### 19h,19h --\> INT3(stat) ;Unknown / no effect
#### 19h,1Ah --\> INT3(stat) ;Unknown / makes some noise if motor is on
Seem to have no effect?<br/>
19h,16h seems to Move Lens Inwards, too.<br/>

#### 19h,06h,new --\> INT3(old) ;Adjust balance in RAM, and apply it via CX(30+n)
#### 19h,07h,new --\> INT3(old) ;Adjust gain in RAM, and apply it via CX(38+n)
#### 19h,08h,new --\> INT3(old) ;Adjust balance in RAM only
These commands are supported only by older CDROM BIOS versions (those with
CXA1782BR Servo Amplifier).<br/>
Later BIOSes will respond with INT5(11h,20h) when trying to use these commands
(because CXD2545Q and later Servo Amplifiers don't support the CX(30/38+n)
commands).<br/>



##   CDROM - Test Commands - Prototype Debug Transmission
#### Serial Debug Messages
Older CDROM BIOSes are supporting debug message transmission via serial bus,
using lower 3bit of the HC05 "databus" combined with the so-called "ROMSEL" pin
(which apparently doesn't refer to Read-Only-Memory, but rather something like
Runtime-Output-Message, or whatever).<br/>
Data is transferred in 24bit units (8bit command/index from HC05, followed by
16bit data to/from HC05), bigger messages are divided into multiple such 24bit
snippets.<br/>
There are no connectors for external debug hardware on any PSX mainboards, so
the whole stuff seems to be dating back to prototypes. And it seems to be
removed from later BIOSes (which appear to use "ROMSEL" as "SCLK"; for
receiving status info from the new CXD2545Q chips).<br/>

#### 19h,30h,index,dat1,dat2 --\> INT3(stat) ;Prototype/Debug stuff
#### 19h,31h,dat1,dat2 --\> INT3(stat) ;Prototype/Debug stuff
#### 19h,4xh,index --\> INT3(dat1,dat2) ;Prototype/Debug stuff
These functions are supported on older CDROM BIOS only; later BIOSes respond by
INT5(11h,10h).<br/>
The functions do not affect the CDROM operation (they do simple allow to
transfer data between Main CPU and external debug hardware).<br/>
Sub functions 30h and 31h may fail with INT5(11h,80h) when receiving wrong
signals on the serial input line.<br/>
Sub function "4xh" value can be 40h..4Fh (don't care).<br/>

#### INT5 Debug Messages
Alongsides to INT5 errors, the BIOS is usually also sending information via the
above serial bus (the error info is divided into multiple 8bit+16bit snippets,
and contains stat, error code, mode, current SubQ position, and most recently
issued command).<br/>



##   CDROM - Test Commands - Read/Write Decoder RAM and I/O Ports
Caution: Below commands 19h,71h..76h are supported only in BIOS version vC1 and
up. Not supported in vC0.<br/>

#### 19h,71h,index --\> INT3(databyte) ;Read single register
index can be 00h..1Fh, bigger values seem to be mirrored to "index AND 1Fh",
with one exception: index 13h in NOT mirrored, instead, index 33h, 53h, 93h,
B3h, D3h, F3h return INT5(stat+1,10h), and index 73h returns INT5(stat+1,20h).<br/>
Aside from returning a value, the commands seem to DO something (like moving
the drive head when a disk is inserted). Return values are usually:<br/>
```
  index     value
  00h       04h      ;04h=empty, 8Eh=licensed, 24h=audio
  01h       [0B1h]   ;DCh=empty/licensed, DDh=audio
  02h       00h
  03h       00h          ;or variable when disk inserted
  04h       00h
  05h       80h          ;or 86h or 89h when disk inserted
  06h       C0h
  07h       02h
  08h       8Ah
  09h       C0h
  0Ah       00h
  0Bh       C0h
  0Ch       [1F2h]
  0Dh       [1F3h]
  0Eh       00h          ;or 8Eh or E6h when disk inserted    ;D4h/audio
  0Fh       00h          ;or sometimes 01h when disk inserted ;50h/audio
  10h       C0h
  11h       E0h
  12h       71h
  13h       stat
  14h       FFh
  15h..1Fh  C0h-filled        ;or 17h --> DEh
```

#### 19h,72h,index,databyte --\> INT3(stat) ;Write single register
```
  ;other response on param xx16h,xx18h with xx>00h
```

#### 19h,73h,index,len --\> INT3(databytes...) ;Read multiple registers (bugged)
#### 19h,74h,index,len,databytes --\> INT3(stat) ;Write multiple registers (bugged)
Same as read/write single register, but trying to transfer multiple registers
at once. BUG: The transfer should range from 00h to len-1, but the loop counter
is left uninitialized (set to X=48h aka "command number 19h-minus-1-mul-2"
instead of X=00h). Causing to the function to read/write garbage at index
48h..FFh, it does then wrap to 00h and do the correct intended transfer, but
the preceeding bugged part may have smashed RAM or I/O ports.<br/>

#### 19h,75h --\> INT3(remain.lo,remain.hi,addr.lo,addr.hi) ;Get Host Xfer Info
Returns a 4-byte value. In my early tests, on the first day it returned
B1h,CEh,4Ch,01h, on the next day 2Ch,E4h,95h,D5h, and on all following days
00h,C0h,00h,00h (no idea why/where the earlier values came from).<br/>
The first byte seems to be always 00h; no matter of \[1F0h\].<br/>
The second byte seems to be always C0h; no matter of \[1F1h\].<br/>
The third,fourth bytes are \[1F2h,1F3h\].<br/>
That two bytes are 0Ch,08h after Read commands.<br/>
```
  The first bytes are NOT affected by:
  destroying [1F0h] via too-many-parameters in command-buffer,
  changes to [1F1h] which may occur after read command (eg. may be 20h)
```

#### 19h,76h,len\_lo,len\_hi,addr\_lo,addr\_hi --\> INT3(stat) ;Prepare SRAM Transfer
Prepare Transfer to/from 32K SRAM.<br/>
After INT3, data can be read (same way as sector data after INT1).<br/>



##   CDROM - Test Commands - Read HC05 SUB-CPU RAM and I/O Ports
#### 19h,60h,addr\_lo,addr\_hi --\> INT3(data) ;Read one byte from Drive RAM or I/O
Reads one byte from the controller's RAM or I/O area, see the memory map below
for more info. Among others, the command allows to read Subchannel Q data, eg.
at \[200h..209h\], including ADR=2/UPC/EAN and ADR=3/ISRC values (which are
suppressed by GetlocP). Eg. wait for ADR\<\>2, then for ADR=2, then read
the remaining 9 bytes (because of the delayed IRQs, this works only at single
speed) (at double speed one can read only 5 bytes before the values get
overwritten by new data). Unknown if older boards (with 4.00MHz oscillators)
are fast enough to read all 10 SubQ bytes.<br/>

#### CDROM Controller I/O Area and RAM Memory Map
First 40h bytes are I/O ports (as in MC68HC05 datasheet):<br/>
```
  000h 4        FF 7B 00 FF  (other when disk inserted)
  004h 5        11 00 20 20 0C
  009h 1        00 (when disk inserted: changes between 00 or 80)
  00Ah 2        71 00
  00Ch 1        00 (when disk inserted: changes between 00 or 80)
  00Dh 3        20 20 20
  010h 8        02 80 00 60 00 00 99(orBB) 98
  018h 4     changes randomly (even when no disk inserted)
  01Ch 3        40 00 41
  01Fh 1     changes randomly (even when no disk inserted)
  020h 30    20h-filled
  03Eh 2        82h 20h
```
Next 200h bytes are RAM:<br/>
```
  040h 4        08 00 00 00  ;or 98 07 xx 0B when disk inserted ;[40].Bit1=MUTE
  044h 4     00h-filled
  048h 3        40 20 00     ;or 58 71 0F when disk inserted
  04Bh 1     changes randomly (nodisk: 00 or 80 / disk: BFh)
  04Ch 1     Zero (or C0h)
  04Dh 3     MM:SS:FF (begin of current track MM:SS:00h) (or increasing addr)
  050h 10    Subchannel Q (adjusted position values)
  05Ah 2        ...
  05Ch 1     00h (or 64h)
  05Dh 3     MM:SS:FF (current read address) (sticky address during pause)
  060h 1     increments at circa 16Hz or so (or other rate when spinning)
  061h 12    00h-filled ;or else when disk inserted
  06Dh 1        01      ;or 0C when disk inserted
  06Eh 2     SetFilter setting (file,channel)
  070h 16    00h-filled ;or else when disk inserted
  080h 8     00h-filled
  088h 3        03:SS:FF (three, second, fraction)
  08Bh 3        03:SS:FF (three, second, fraction)
  08Eh 2        01 FF (or other values)
  090h 1        00h (or 91h when disk inserted + spinning)
  091h 13    Zero
  09Eh 1        00h (or 01h when disk inserted + spinning)
  09Fh 1     Zero
  0A0h 1     Always 23h
  0A1h 1        09h (5Dh when disk inserted)
  0A2h 7     00h-filled
  0A9h 1        40
  0AAh 4     00h-filled
  0AEh 1        00 (no disk) or 01 (disk) or so
  0AFh 1        00            ;or 06 when disk inserted
  0B0h 7        00 DC 00 02 00 E0 08             ;\or else when disk inserted
  0B7h 1        20         ;Bit6+7=MUTE          ;
  0B8h 3        DE 00 00                         ;/
  0BBh 1     SetMode setting (mode)
  0BCh 1     \ setting (stat)
  0BDh 3     00h-filled
  0C0h 6     FFh-filled            ;stack...                    ;\
  0C6h 1     Usually DFh           ;sometimes [0EBh and up] are non-FFh, too
  0C7h 15    FFh-filled            ;(depending on disk or commands or so)
  0D6h 1     Usually FDh (or FFh)  ;                            ;
  0D7h 24    FFh-filled                                         ; stack
  0EFh 4     on power-up FFh-filled, other once when disk read  ;
  0F3h 7     changes randomly (even when no disk inserted)      ;
  0FAh 6       2E 3C 2A D6 10 95                                ;/
  100h 2x99  TOC Entries for Start of Track 1..99 (MM:SS)
  1C6h 1     TOC First Track number (usually 01h)
  1C7h 1     TOC Last Track number (usually 01h or higher)
  1C8h 3     TOC Entry for Start of Lead-Out (MM:SS:FF)
  1CBh 2     Zero
  1CDh 1     Depends on disk (01 or 02 or 06) (or 00 when no disk)
  1CEh 1     Zero
  1CFh 1     Depends on disk (NULL minus N*6) (or 00 when no disk)
               (maybe reflection level / laser intensity or so)
                [1CDh..1CFh]
                01 00 E8 --> licensed/metalgear/kain
                01 00 EE --> licensed/alone2
                06 00 E2 or 00 00 02 00 E8 --> licensed/wipeout
                02 00 DC --> unlicensed/elo
                02 00 D6 --> unlicensed/driver
                00 00 EE --> audio/lola
                00 00 FA --> audio/marilyn
                00 00 F4 --> audio/westen
                00 00 00 --> disk missing
               last byte is always in steps of 6
  1D0h 4     SCEx String
  1D4h 4     Zero
  1D8h 2     SCEx Counters (total,success)  ;for command 19h,05h
  1DAh 6       00h-filled     (or ... SS:FF)
  1E0h 6     Command Buffer (usually 19h,60h,E2h,01h = Read RAM Command)
  1E6h 7       00h-filled (unless destroyed by more-than-6-byte-commands)
  1EDh 3     Setloc setting (MM:SS:FF)
  1F0h 1       00h          (unless destroyed by more-than-6-byte-commands)
  1F1h 3       C0h 00h 00h ;or 20h,0Ch,50h or C0h,0Ch,08h ;for command(19h,75h)
                           ;or 00h,00h,00h for audio
                           ;or 80h,00h,00h for disk missing
  1F4h 4       00h-filled ... or SCEx string
  1F8h 1       00h
  1F9h 1     Selected Target (parameter from Play and SetSession commands)
  1FAh 5       00h-filled       ;01 01 00 8B 00 00   ;or 01 02 8B 00 00
                       01 00 8B 00 00 -- audio/unlicensed
                       01 01 00 00 00 -- licensed
  1FFh 1       00h-on power up, changes when disk inserted  ;or 01 = Playing
    1FDh 3       MM:SS:FF (only during command 19h,00h) (MM=98..99=TOC)
  200h 10    Subchannel Q (real values)
  20Ah 2       whatever
  20Ch 1     Zero
  20Dh 1     Desired Session (from SetSession command)
  20Eh 1     Current Session (actual location of drive head)
  20Fh 1     Zero
  210h 10    Subchannel Q (adjusted position values)
  21Ah 6     00h-filled
  220h 4     Data Sector Header (MM:SS:FF:Mode)
  224h 4     Data Sector CD-XA Subheader (file,channel,sm,ci)
  228h 1         00h
  229h 1     Usually 00h (shortly other value on power-up, and maybe on seek)
  22Ah 1         10h (or 00h when no disk)
  22Bh 3     00h-filled
  22Eh 2         01,03 or 0A,00 or 03,01 (or else for other disk)
  230h 3     00h-filled (or other during spin-up / read-toc or so)
  233h 0Dh   00h-filled (unused RAM)
```
Other/invalid addresses are:<br/>
```
  240h..2FFh  - Invalid (00h-filled) (no ROM, RAM, or I/O mapped here)
  300h..3FFh  - Mirror of 200h..2FFh    ;\the BIOS is doing that
  400h..FFFFh - Mirrors of 000h..3FFh   ;/mirroring by software
```

#### DTL-H2000 Memory Map
This version allows to read the whole 64Kbyte memory space (withou mirroring
everything to first 300h bytes). I/O Ports and Variables are at different
locations:<br/>
```
  000h..0DFh   RAM Part 1 (C0h bytes)
  0E0h..0FFh   I/O Area
  100h..1DFh   RAM Part 2 (C0h bytes)
  1E0h..1FFh   I/O Area
  200h..2DFh   RAM Part 3 (100h bytes)
  2E0h..7FFFh  Unknown
  8000h-BFFFh  Unknown  (lower 16K of 32K EPROM) (or unused?)
  C000h-FFFFh  Firmware (upper 16K of 32K EPROM)
```

#### Writing to RAM
There is no command for writing to RAM. Except that, one can write to the
command/parameter buffer at 1E0h and up. Normally, the longest known command
should have 6 bytes (19h,76h,a,b,c,d), and longer commands results in "bad
number of parameters" response - however, despite of that error message, the
controller does still store ALL parameter bytes in RAM (at address 1E1h..2E0h,
then wrapping back to 1E1h). Whereas, writing more than 16 bytes (FIFO storage
size) will mirror the FIFO content twice, and more than 32 bytes (FIFO counter
size) will work only when feeding extra data into the FIFO during transmission.
Anyways, writing to 1E1h and up doesn't allow to do interesting things (such
like manipulating the stack and executing custom code on the CPU).<br/>

#### Subchannel Q Notes
The "adjusted position values" at 050h, 210h, 310h contain only position
information (with ADR=1) (the PSX seems to check only the lower 2bit of the
4bit ADR value, so it also treats ADR=5 as ADR=1, too). Additionally, during
Lead-In, bytes 7..9 are overwritten by the position value from bytes 3..5. The
"real values" contain unadjusted data, including ADR=2 and ADR=3 etc.<br/>



##   CDROM - Secret Unlock Commands
#### SecretUnlockPart1 - Command 50h --\> INT5(11h,40h)
#### SecretUnlockPart2 - Command 51h,"Licensed by" --\> INT5(11h,40h)
#### SecretUnlockPart3 - Command 52h,"Sony" --\> INT5(11h,40h)
#### SecretUnlockPart4 - Command 53h,"Computer" --\> INT5(11h,40h)
#### SecretUnlockPart5 - Command 54h,"Entertainment" --\> INT5(11h,40h)
#### SecretUnlockPart6 - Command 55h,\<region\> --\> INT5(11h,40h)
#### SecretUnlockPart7 - Command 56h --\> INT5(11h,40h)
```
  Caution: Supported only in BIOS version vC1 and up. Not supported in vC0.
  Caution: Supported only in Europe/USA. Nonfunctional in Japan/Asia.
  Caution: When unsupported, Parameter Fifo isn't cleared after the command.
```
Sending these commands with the correct strings (in order 50h through 56h) does
disable the "SCEx" protection. The region can be detected via test command
19h,22h, and must be translated to the following \<region\> string:<br/>
```
  "of America"    ;for NTSC/US          ;\
  "(Europe)"      ;for PAL/Europe       ; handled, and actually working
  "World wide"    ;for Yaroze           ;/
  "Inc."          ;for NTSC/JP          ;-non-functional
```
In the unlocked state, ReadN/ReadS are working for unlicensed CD-Rs, and for
imported CDROMs from other regions (both without needing modchips). However
there are some cases which may still cause problems: The GetID command (1Ah)
does still identify the disc as being unlicensed, same for the Get SCEx
Counters test command (19h,05h). And, if a game should happen to send the Reset
command (1Ch) for some weird reason, then the BIOS would forget the unlocking,
same for games that set the "HCRISD" I/O port bit. On the contrary,
opening/closing the drive door does not affect the unlocking state.<br/>
The commands have been discovered in September 2013, and appear to be supported
by all CDROM BIOS versions (from old PSXes up to later PSones).<br/>
Note that the commands do always respond with INT5 errors (even on successful
unlocking).<br/>
Japanese consoles are internally containing code for processing the Secret
Unlock commands, but they are not actually executing that code, and even if
they would do so: they are ignoring the resulting unlocking flag, making the
commands nonfunctional in Japan/Asia regions.<br/>

#### SecretLock - Command 57h --\> INT5(11h,40h)
Undoes the unlocking and restores the normal locked state (same happens when
sending the Unlocking commands in wrong order or with wrong parameters).<br/>

#### SecretCrash - Command 58h..5Fh --\> Crash
Jumps to a data area and executes random code. Results are more or less
unpredictable (as they involve executing undefined opcodes). Eventually the CPU
might hit a RET opcode and recover from the crash.<br/>



##   CDROM - Video CD Commands
```
  Caution: Supported only on SCPH-5903, not supported on any other consoles.
  Caution: When unsupported, Parameter Fifo isn't cleared after the command.
```

```
  1Fh VideoCD      sub,a,b,c,d,e   INT3(stat,a,b,c,d,e)   ;<-- SCPH-5903 only
  1Fh..4Fh -       -               INT5(11h,40h)  ;-Unused/invalid
```

#### VideoCdSio - Cmd 1Fh,01h,JoyL,JoyH,State,Task,0 --\> INT3(stat,req,mm,ss,ff,x)
The JoyL/JoyH bytes contain 16bit button (and drive door) bits:<br/>
```
  0  Drive Door  (0=Open)    (from CDROM stat bit4) ;Open
  1  Button /\   (0=Pressed) (from PSX pad bit12) ;N/A       ;PBC: Back/LevelUp
  2  Button []   (0=Pressed) (from PSX pad bit15) ;Enter Menu
  3  Button ()   (0=Pressed) (from PSX pad bit13) ;Leave Menu     ;PBC: Confirm
  4  Button ><   (0=Pressed) (from PSX pad bit14) ;N/A
  5  Start       (0=Pressed) (from PSX pad bit3)  ;Play/Pause
  6  Select      (0=Pressed) (from PSX pad bit0)  ;Stop (prompt restart/resume)
  7  Always 0    (0)         (fixed)              ;N/A
  8  DPAD Up     (0=Pressed) (from PSX pad bit4)  ;Menu Up           ;PBC: +1
  9  DPAD Right  (0=Pressed) (from PSX pad bit5)  ;Menu Right/change ;PBC: +10
  10 DPAD Down   (0=Pressed) (from PSX pad bit6)  ;Menu Down         ;PBC: -1
  11 DPAD Left   (0=Pressed) (from PSX pad bit7)  ;Menu Left/change  ;PBC: -10
  12 Button R1   (0=Pressed) (from PSX pad bit11) ;Prev Track/Restart Track
  13 Button R2   (0=Pressed) (from PSX pad bit9)  ;Fast Forward (slowly)
  14 Button L1   (0=Pressed) (from PSX pad bit10) ;Next Track (if any)
  15 Button L2   (0=Pressed) (from PSX pad bit8)  ;Fast Backward (slowly)
```
The State byte can be:<br/>
```
  00h  Motor Off (or spin-up)   (when stat.bit1=0)
  01h  Playing                  (when stat.bit7=1)
  02h  Paused (and not seeking) (when stat.bit6=0)
  (note: State remains unchanged when seeking)
```
The Task byte can be:<br/>
```
  00h = Confirms that "Tocread" (aka setsession 1) request was processed
  01h = Detect VCD Disc (used on power-up, and after door open) (after spin-up)
  02h = Handshake (request ack response)
  0Ah = Door opened during play (int5/door error)
  80h = No disc
  FFh = No change (nop)
```
The req byte in the INT3 response can be:<br/>
```
  00h  Normal (no special event occured and no action requested)
  01h  Request CD to Seek_and_play (using mm:ss:ff response parameter bytes)
  02h  Request CD to Pause                ;cmd(09h)    -->int3(stat),int2(stat)
  03h  Request CD to Stop                 ;cmd(08h)    -->int3(stat),int2(stat)
  04h  Request CD to Tocread (setsession1);cmd(12h,01h)-->int3(stat),int2(stat)
  05h  Handshake Command was processed, and this is the "ack" response
  06h  Request CD to Fast Forward         ;cmd(04h)    -->int3(stat)
  07h  Request CD to Fast Backward        ;cmd(05h)    -->int3(stat)
  80h  Detect Command was processed, and disc was detected as VCD
  81h  Detect Command was processed, and disc was detected as Non-VCD
```

#### VideoCdSwitch - Cmd 1Fh,02h,flag,x,x,x,x --\> INT3(stat,0,0,x,x,x)
```
  00h      = Normal PSX Mode  (PortF.3=LOW)  (Audio/Video from GPU/SPU chips)
  01h..FFh = Special VCD Mode (PortF.3=HIGH) (Audio/Video from MDEC/OSD chips)
```

#### Some findings on the SC430924 firmware...
The version/date is "15 Aug 1996, version C2h", although the "C2h" is
misleading: The firmware is nearly identical to version "C1h" from PU-8 boards
(the stuff added in normal "C2h" versions would be for PU-18 boards with
different cdrom chipset).<br/>

Compared to the original C1h version, there are only a few changes: A
initialization function for initializing port F on power-up. And new command
(command 1Fh, inserted in the various command tables), with two subfunctions
(01h and 02h):<br/>
- Command 1Fh,01h,a,b,c,d,e --\> INT3(stat,a,b,c,d,e) Serial 5-byte
read-write<br/>
- Command 1Fh,02h,v,x,x,x,x --\> INT3(stat,0,0,x,x,x) Toggle 1bit (port
F.bit3)<br/>
Whereas,<br/>
```
  x = don't care/garbage
  v = toggle state (00h=normal=PortF.3=LOW, 01h..FFh=special=PortF.3=HIGH)
      (toggle gpu vs mpeg maybe?)
  a,b,c,d,e = five bytes sent serially, and five bytes response received
      serially (send/receive done simultaneously)
```

The Port F bits are:<br/>
```
  Port F.Bit0 = Serial Data In
  Port F.Bit1 = Serial Data Out
  Port F.Bit2 = Serial Clock Out
  Port F.Bit3 = Toggle (0=Normal, 1=Special)
```

And that's about all. Ie. essentially, the only change is that the new command
controls Port F. There is no interaction with the remaining firmware (ie.
reading, seeking, and everything is working as usually, without any video-cd
related changes).<br/>
The SCEx stuff is also not affected (ie. Video CDs would be seen as unlicensed
discs, so the PSX couldn't read anything from those discs, aside from Sub-Q
position data, of course). The SCEx region is SCEI aka "Japan" (or actually for
Asia in this case).<br/>

#### Note
The SPU MUTE Flag (SPUCNT.14) does also affect VCD Audio (mute is applied to
the final analog audio amplifier). All other SPUCNT bits can be zero for VCD.<br/>



##   CDROM - Mainloop/Responses
#### SUB-CPU Mainloop
The SUB-CPU is running a mainloop that is handling hardware events (by simple
polling, not by IRQs):<br/>
```
  check for incoming sectors (from CDROM decoder)
  check for incoming commands (from Main CPU)
  do maintenance stuff on the drive mechanics
```
There is no fixed priority: if both incoming sector and incoming command are
present, then the SUB-CPU may handle either one, depending on which portion of
the mainloop it is currently executing.<br/>
There is no fixed timing: if the mainloop is just checking for a specific
event, then a new event may be processed immediately, otherwise it may take
whole mainloop cycle until the SUB-CPU sees the event.<br/>
Whereas, the mainloop cycle execution time isn't constant: It may vary
depending on various details. Especially, some maintenance stuff is only
handled approximately around 15 times per second (so there are 15 slow mainloop
cycles per second).<br/>

The order of steps that happen when sending a command to the CD controller look roughly like this:
```
e.g. SetMode:
1. Command busy flag set immediately.
2. Response FIFO is populated.
3. Command is being processed.
4. Command busy flag is unset and parameter fifo is cleared.
5. Shortly after (around 1000-6000 cycles later), CDROM IRQ is fired.
```


#### Responses
The PSX can deliver one INT after another. Instead of using a real queue, it's
merely using some flags that do indicate which INT(s) need to be delivered.
Basically, there seem to be two flags: One for Second Response (INT2), and one
for Data/Report Response (INT1). There is no flag for First Response (INT3);
because that INT is generated immediately after executing a command.<br/>
The flag mechanism means that the SUB-CPU cannot hold more than one undelivered
INT1. That, although the CDROM Decoder does notify the SUB-CPU about all newly
received sectors, and it can hold up to eight sectors in the 32K SRAM. However,
the SUB-CPU BIOS merely sets a sector-delivery-needed flag (instead of
memorizing which/how many sectors need to be delivered, and, accordingly, the
PSX can use only three of the available eight SRAM slots: One for currently
pending INT1, one for undelivered INT1, and one for currently/incompletely
received sector).<br/>

#### First Response (INT3) (or INT5 if failed)
The first response is sent immediately after processing a command. In detail:<br/>
The mainloop checks for incoming commands once every some clock cycles, and
executes commands under following condition:<br/>
```
  Main CPU has sent a command, AND, there is no INT pending
  (if an INT is pending, then the command won't be executed yet, but will be
  executed in following mainloop cycles; once when INT got acknowledged)
  (even if no INT is pending, the mainloop may generate INT1/INT2 before
  executing the command, if so, as said above, the command won't execute yet)
```
Once when the command gets executed it will sent the first response immediately
after the command execution (which may only take a few clock cycles, or some
more cycles, for example Init/ReadTOC do include some time consuming
initializations). Anyways, there will be no other INTs generated during command
execution, so once when the command execution has started, it's guaranteed that
the next INT will contain the first response.<br/>

#### Second Responses (INT2) (or INT5 if failed)
Some commands do send a second response after actual command execution:<br/>
```
  07h MotorOn    E -               INT3(stat), INT2(stat)
  08h Stop       E -               INT3(stat), INT2(stat)
  09h Pause      E -               INT3(stat), INT2(stat)
  0Ah Init         -               INT3(late-stat), INT2(stat)
  12h SetSession E session         INT3(stat), INT2(stat)
  15h SeekL      E -               INT3(stat), INT2(stat)  ;\use prior Setloc
  16h SeekP      E -               INT3(stat), INT2(stat)  ;/to set target
  1Ah GetID      E -               INT3(stat), INT2/5(stat,flg,typ,atip,"SCEx")
  1Dh GetQ       E adr,point       INT3(stat), INT2(10bytesSubQ,peak_lo)
  1Eh ReadTOC      -               INT3(late-stat), INT2(stat)
```
In some cases (like seek or spin-up), it may take more than a second until the
2nd response is sent.<br/>
It should be highly recommended to WAIT until the second response is generated
BEFORE sending a new command (it wouldn't make too much sense to send a new
command between first and second response, and results would be unknown, and
probably totally unpredictable).<br/>
Error Notes: If the command has been rejected (INT5 sent as 1st response) then
the 2nd response isn't sent (eg. on wrong number of parameters, or if disc
missing). If the command fails at a later stage (INT5 as 2nd response), then
there are cases where another INT5 occurs as 3rd response (eg. on
SetSession=02h on non-multisession-disk).<br/>

#### Data/Report Responses (INT1)
```
  03h Play       E (track)         INT3(stat), optional INT1(report bytes)
  04h Forward    E -               INT3(stat), optional INT1(report bytes)
  05h Backward   E -               INT3(stat), optional INT1(report bytes)
  06h ReadN      E -               INT3(stat), INT1(stat), datablock
  1Bh ReadS      E?-               INT3(stat), INT1(stat), datablock
```



##   CDROM - Response Timings
Here are some response timings, measured in 33MHz units on a PAL PSone. The
CDROM BIOSes mainloop is doing some maintenance stuff once and when, meaning
that the response time will be higher in such mainloop cycles (max values), and
less in normal cycles (min values). The maintenance timings do also depend on
whether the motor is on or off (and probably on various other factors like
seeking).<br/>

#### First Response
The First Response interrupt is sent almost immediately after processing the
command (that is, when the mainloop sees a new command without any old
interrupt pending). For Nop, timings are as so:<br/>
```
  Command            Average   Min       Max
  Nop (normal)       000c4e1h  0004a73h..003115bh
  Nop (when stopped) 0005cf4h  000483bh..00093f2h
```
Timings for most other commands should be similar as above. One exception is
the Init command, which is doing some initialization before sending the 1st
response:<br/>
```
  Init                   0013cceh  000f820h..00xxxxxh
```
The ReadTOC command is doing similar initialization, and should have similar
timing as Init command. Some (rarely used) Test commands include things like
serial data transfers, which may be also quite slow.<br/>

#### Second Response
```
  Command                Average   Min       Max
  GetID                  0004a00h  0004922h..0004c2bh
  Pause (single speed)   021181ch  020eaefh..0216e3ch ;\time equal to
  Pause (double speed)   010bd93h  010477Ah..011B302h ;/about 5 sectors
  Pause (when paused)    0001df2h  0001d25h..0001f22h
  Stop (single speed)    0d38acah  0c3bc41h..0da554dh
  Stop (double speed)    18a6076h  184476bh..192b306h
  Stop (when stopped)    0001d7bh  0001ce8h..0001eefh
```
Moreover, Seek/Play/Read/SetSession/MotorOn/Init/ReadTOC are sending second
responses which depend on seek time (and spin-up time if the motor was off).
The seek timings are still unknown, and they are probably quite complicated:<br/>
The CDROM BIOS seems to split seek distance somehow into coarse steps (eg.
minutes) and fine steps (eg. seconds/sectors), so 1-minute seek distance may
have completely different timings than 59-seconds distance.<br/>
The amount of data per spiral winding increases towards ends of the disc (so
the drive head will need to be moved by shorter distance when moving from
minute 59 to 60 as than moving from 00 to 01).<br/>
The CDROM BIOS contains some seek distance table, which is probably optimized
for 72-minute discs (or whatever capacity is used on original PSX discs).
80-minute CDRs may have tighter spiral windings (the above seek table is
probably causing the drive head to be moved too far on such discs, which will
raise the seek time as the head needs to be moved backwards to compensate that
error).<br/>

#### INT1 Rate
```
  Command                Average   Min       Max
  Read (single speed)    006e1cdh  00686dah..0072732h
  Read (double speed)    0036cd2h  00322dfh..003ab2bh
```
The INT1 rate needs to be precise for CD-DA and CD-XA Audio streaming, exact
clock cycle values should be: SystemClock\*930h/4/44100Hz for Single Speed (and
half as much for Double Speed) (the "Average" values are AVERAGE values, not
exact values).<br/>



##   CDROM - Response/Data Queueing
\[Below are some older/outdated test cases\]<br/>

#### Sector Buffer
The CDROM sector buffer is 32Kx8 SRAM (IC303). The buffer is apparently divided
into 8 slots, theoretically allowing to buffer up to 8 sectors.<br/>
BUG: The drive controller seems to allow only 2 of those 8 sectors (the oldest
sector, and the current/newest sector).<br/>
Ie. after processing the INT1 for the oldest sector, one would expect the
controller to generate another INT1 for next newer sector - but instead it
appears to jump directly to INT1 for the newest sector (skipping all other
unprocessed sectors). There is no known way to get around that effect.<br/>
So far, the big 32Kbyte buffer is entirely useless (the two accessible sectors
could have been as well stored in a 8Kbyte chip) (unless, maybe the 32Kbytes
have been intended for some error-correction "read-ahead" purposes, rather than
as "look-back" buffer for old sectors; one of the unused slots might be also
used for XA-ADPCM sectors).<br/>
The bottom line is that one should process INT1's as soon as possible (ie.
before the cdrom controller receives and skips further sectors). Otherwise
sectors would be lost without notice (there appear to be absolutely no overrun
status flags, nor overrun error interrupts).<br/>

#### Sector Buffer Test Cases
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Process INT1 --> receives sector header for 0:2:1
  Process INT1 --> receives sector header for 0:2:2
  Process INT1 --> receives sector header for 0:2:3
```
Above shows the normal flow when processing INT1's as they arise. Now,
inserting delays (and not processing INT1's during that delays):<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  delay(1)
  Process INT1 --> receives sector header for 0:2:1 (oldest sector)
  Process INT1 --> receives sector header for 0:2:6 (newest sector)
  Process INT1 --> receives sector header for 0:2:7 (next sector)
```
Above suggests that the CDROM buffer can hold max 2 sectors (the oldest and
current one). However, using a longer delay:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  delay(2)
  Process INT1 --> receives sector header for 0:2:9  (oldest/overwritten)
  Process INT1 --> receives sector header for 0:2:11 (newest sector)
  Process INT1 --> receives sector header for 0:2:12 (next sector)
```
Above indicates that sector buffer can hold 8 sectors (as the sector 1 slot is
overwritten by sector 9). And, another test with even longer delay:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  delay(3)
  Process INT1 --> receives sector header for 0:2:17 (currently received)
  Process INT1 --> receives sector header for 0:2:16 (newest full sector)
  Process INT1 --> receives sector header for 0:2:17 (next sector)
  Process INT1 --> receives sector header for 0:2:18 (next sector)
```
Above is a special case where sector 17 appears twice; the first one is the
sector 1 slot (which was overwritten by sector 9, and apparently then half
overwritten by sector 17).<br/>

#### Sector Buffer VS GetlocL Response Tests
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  GetlocL
  Process INT3 --> receives getloc info for 0:2:0
  Process INT1 --> receives sector header for 0:2:1
  Process INT1 --> receives sector header for 0:2:2
  Process INT1 --> receives sector header for 0:2:3
```
Another test, with Delay BEFORE Getloc:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  GetlocL
  Process INT1 --> receives sector header for 0:2:1
  Process INT3 --> receives getloc info for 0:2:6
  Process INT1 --> receives sector header for 0:2:6
  Process INT1 --> receives sector header for 0:2:7
```
Another test, with Delay AFTER Getloc:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  GetlocL
  Delay(1)
  Process INT3 --> receives getloc info for 0:2:0
  Process INT1 --> receives sector header for 0:2:5
  Process INT1 --> receives sector header for 0:2:6
  Process INT1 --> receives sector header for 0:2:7
```
Another test, with Delay BEFORE and AFTER Getloc:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  GetlocL
  Delay(1)
  Process INT1 --> receives sector header for 0:2:9
  Process INT1 --> receives sector header for 0:2:11
  Process INT3 --> receives getloc info for 0:2:12
  Process INT1 --> receives sector header for 0:2:12
  Process INT1 --> receives sector header for 0:2:13
```

#### Sector Buffer VS Pause Response Tests
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Pause
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```
Another test, with Delay BEFORE Pause:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  Pause
  Process INT1 --> receives sector header for 0:2:1 (oldest)
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```
Another test, with Delay AFTER Pause:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Pause
  Delay(1)
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```
Another test, with Delay BEFORE and AFTER Pause:<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  Pause
  Delay(1)
  Process INT1 --> receives sector header for 0:2:9 (oldest/overwritten)
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```
For above: Note that, despite of Pause, the CDROM is still writing to the
internal buffer (and overwrites slot 1 by sector 9) (this might be because the
Pause command isn't processed at all until INT1 is processed).<br/>

#### Double Commands (Getloc then Pause)
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  GetlocL
  Pause
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```
Another test,<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  GetlocL
  Pause
  Process INT1 --> receives sector header for 0:2:1
  Process INT1 --> receives sector header for 0:2:6
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```
Another test,<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  GetlocL
  Delay(1)
  Pause
  Process INT3 --> receives getloc info for 0:2:0 (first getloc response)
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```
Another test,<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  GetlocL
  Delay(1)
  Pause
  Process INT1 --> receives sector header for 0:2:9 (oldest/overwritten)
  Process INT3 --> receives stat=22h (first pause response)
  Process INT2 --> receives stat=02h (second pause response)
```

#### Double Commands (Pause then Getloc)
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Pause
  GetlocL
  Process INT3 --> receives getloc info for 0:2:0 (first getloc response)
  Process INT1 --> receives sector header for 0:2:1
  Process INT1 --> receives sector header for 0:2:2
  Process INT1 --> receives sector header for 0:2:3
```
Another test,<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  Pause
  GetlocL
  Process INT1 --> receives sector header for 0:2:1
  Process INT3 --> receives getloc info for 0:2:6 (first getloc response)
  Process INT1 --> receives sector header for 0:2:6
  Process INT1 --> receives sector header for 0:2:7
```
Another test,<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Pause
  Delay(1)
  GetlocL
  Process INT3 --> receives stat=22h (first pause response)
  Process INT3 --> receives getloc info for 0:2:6 (first getloc response)
  (No further INT's, ie. read is paused, but second-pause-response is lost).
```
Another test,<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Pause
  Delay(1)
  GetlocL
  Delay(1)
  Process INT3 --> receives stat=22h (first pause response)
  Process INT3 --> receives getloc info for 0:2:6 (first getloc response)
  Process INT2 --> receives stat=02h (second pause response)
```
Another test,<br/>
```
  Setloc(0:2:0)+Read
  Process INT1 --> receives sector header for 0:2:0
  Delay(1)
  Pause
  Delay(1)
  GetlocL
  Process INT1 --> receives sector header for 0:2:9
  Process INT1 --> receives sector header for 0:2:11
  Process INT3 --> receives getloc info for 0:2:12 (first getloc response)
  Process INT1 --> receives sector header for 0:2:12
  Process INT1 --> receives sector header for 0:2:13
```
