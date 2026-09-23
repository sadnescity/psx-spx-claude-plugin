---
name: cdrom-internal-decoder
description: "PSX CDROM internal: CXD1815Q sub-CPU configuration/status/address/misc registers, servo/signal processor commands (CXA1782BR, CXD2510Q, CXD2545Q, CXD2938Q), coefficient tables. Use when working with CDROM decoder/servo internals or chipset-specific commands."
---

##   CDROM Internal CXD1815Q Sub-CPU Configuration Registers
#### 00h - DRVIF - Drive Interface (W)
```
  0-1 "L"     Reserved (should be 0)
  2   LSB 1st CD DSP DATA order               (0=MSB first, 1=LSB first)
  3-4 BCK MD  CD DSP Number of BCLKs per WCLK (0=16, 1=24, 2=32, 3=Reserved)
  5   BCK RED Strobe DATA on BLCK Edge        (0=Falling Edge, 1=Rising Edge)
  6   LCH LOW Channel on LRCK=Low             (0=Right, 1=Left)
  7   C2PL1st      ... C2PO lower byte 1st
```

#### 01h - CONFIG 1 - Configuration 1 (W)
```
  0   HCLKDIS  HCLK Pin Output (0=8.4672MHz, 1=Disable; Fixed Low)
  1   CLKDIS   CLK Pin Output (0=16.9344MHz, 1=Disable; Fixed Low)
  2   9BITRAM  SRAM Databus width (0=8bit/normal, 1=9bit)
  3-4 RAM SZ   SRMA Address bus (0=32K, 1=64K, 2=128K, 3=Reserved)
  5   PRTYCTL      ... Priority Control
  6   XSLOW    Number of clock cycles per DMA cycle (0=12, 1=4) (for SRAM)
  7   "L"      Reserved (should be 0)
```

#### 02h - CONFIG 2 - Configuration 2 (W)
```
  0   "L"      Reserved (should be 0)
  1   DACODIS        .... DAC Out Disable
  2   DAMIXEN  Digital Audio Mixer Enable (0=Attentuator/Mixer for CD-DA, 1=No)
  3   SMBF2    Number of Sound Map Buffer Surfaces (0=Three, 1=Two)
  4   SPMCTL   Sound Parameter Majority Control (0=?)  ;\for ADPCM params
  5   SPECTL   Sound Parameter Error Control    (0=?)  ;/
  6-7 "L"      Reserved (should be 0)
```

#### 03h - DECCTL - Decoder Control (W)
```
  0-2 DECMD    Decoder Mode (0-7)
                 0 or 1  Decoder Disable            ;-disable sector reading
                 2 or 3  Monitor-only Mode          ;\no error correction
                 4       Write-only Mode            ;/
                 5       Real-time Correction Mode  ;\with error correction
                 6       Repeat Correction Mode     ;/
                 7       CD-DA Mode                 ;-audio
  3   AUTODIST Auto Distinction (0=Use MODESEL/FORMSEL bits, 1=Use Sector Hdr)
               (Error Correction is done according to above MODE/FORM values)
  4   FORMSEL  Form Select (0=FORM1, 1=FORM2) (must be 0 for MODE1)
  5   MODESEL  Mode Select (0=MODE1, 1=MODE2)
  6   ECCSTR   ECC Strategy (0=Normal, 1=Use Error Flags; requires 9bit SRAM)
  7   ENDLADR  Enable Drive Last Address    ...
```

#### 07h - CHPCTL - Chip Control (W)
```
  0   "L"      Reserved (should be 0)
  1   DBLSPD   Double Speed Mode (0=Normal, 1=Double) (init CD DSP first)
  2   RPSTART  Repeat Correction Start (0=No, 1=Start) (automatically cleared)
  3   SWOPEN   Sync Window Open (0=SyncControlledByIC, 1=OpenDetectionWindow)
  4   CD-DA    CD-DA Play     (0=No, 1=Playback CD-DA as audio)
  5   CDDAMUTE CD-DA Mute     (0=Normal, 1=Mute CD-DA Audio)
  6   RTMUTE   Real-time Mute (0=Normal, 1=Mute CDROM ADPCM)
  7   SMMUTE   Sound Map Mute (0=Normal, 1=Mute Sound Map ADPCM)
```



##   CDROM Internal CXD1815Q Sub-CPU Sector Status Registers
#### 00h - ECCSTS - ECC Status (R)
```
  0 CFORM   FORM assumed by Error Correction (0=FORM1, 1=FORM2)
  1 CMODE   MODE assumed by Error Correction (0=MODE1, 1=MODE2)
  2 ECCOK   ECC Okay (0=Bad, 1=Okay)
  3 EDCOK   EDC Okay (0=Bad, 1=Okay)
  4 CORDONE Correction Done (0=None, 1=Error occurred and was corrected)
  5 CORINH  Correction Inhibit (0=Okay,1=AUTODIST couldn't determine MODE/FORM)
  6 ERINBLK Erasure in Block (0=Okay, 1=At least 1 byte is wrong & uncorrected)
  7 EDCALL0 EDC all-zero  (0=No/EDC Exists, 1=Yes/All four EDC bytes are 00h)
```

#### 01h - DECSTS - Decoder Status (R)
```
  0   NOSYNC   No Sync       (0=Okay, 1=Sector Sync Mark Missing)
  1   SHRTSCT  Short Sector  (0=Okay, 1=Sector Sync Mark within Sector Data)
  2-4 -        Reserved (undefined)
  5   RTADPBSY Real-time ADPCM Busy (0=No, 1=Busy/playback)
  6-7 -        Reserved (undefined)
```

#### 02h - HDRFLG - Header/Subheader Error Flags for HDR/SHDR registers (R)
```
  0 CI      Error in 4th Subheader byte (Coding Info) (0=Okay, 1=Error)
  1 SUBMODE Error in 3rd Subheader byte (Submode)     (0=Okay, 1=Error)
  2 CHANNEL Error in 2nd Subheader byte (Channel)     (0=Okay, 1=Error)
  3 FILE    Error in 1st Subheader byte (File)        (0=Okay, 1=Error)
  4 MODE    Error in 4th Header byte (MODE)           (0=Okay, 1=Error)
  5 BLOCK   Error in 3rd Header byte (FF)             (0=Okay, 1=Error)
  6 SEC     Error in 2nd Header byte (SS)             (0=Okay, 1=Error)
  7 MIN     Error in 1st Header byte (MM)             (0=Okay, 1=Error)
```
Error flags for current sector are probably stored straight in this register
(ie. these flags are probably available even without using 9bit SRAM).<br/>
Or maybe not... if the chip supports receiving newer sectors during
time-consuming error corrections... then those newer would need to be stored in
SRAM, and would thus require 9bit SRAM for the error flags?<br/>

#### 03h - HDR - Header Bytes (R)
```
  1st read: 1st Header byte (MM)
  2nd read: 2nd Header byte (SS)
  3rd read: 3rd Header byte (FF)
  4th read: 4th Header byte (MODE)
```

#### 04h - SHDR - Subheader Bytes (R)
```
  1st read: 1st Subheader byte (File)
  2nd read: 2nd Subheader byte (Channel)
  3rd read: 3rd Subheader byte (Submode) (SM)
  4th read: 4th Subheader byte (Coding Info) (CI)
```
The contents of the HDRFLG, HDR, SHDR registers indicate:<br/>
```
      (1) The corrected value in the real-time correction or
          repeat correction mode
      (2) Value of the raw data from the drive in the monitor-only
          or write-only mode
    The CMOME? and CMODE bits (bits 1, 0) of ECCSTS indicate the FORM and MODE
    of the sector the decoder has discriminated by the raw data from the drive.
    Due to erroneous correction, the values of these bits may be at variance
    with those of the HDR register MODE byte and SHDR register submode byte
    bit5.
```

Unknown when 1st..4th read indices are reset for HDR and SHDR (maybe on access
to certain I/O ports, or maybe anytime when receiving a new sector), also
unknown what happens on 5th read and up.<br/>



##   CDROM Internal CXD1815Q Sub-CPU Address Registers
Drive Address -- used for storing incoming CDROM sectors in Buffer RAM<br/>
Host Address -- used for transferring Buffer RAM to (or from) Main CPU<br/>
ADPCM Address -- used for Real-time ADPCM audio output from Buffer RAM<br/>

#### 05h - CMADR - Drive Current Minute Address (R)
```
  0-6   CMADR    Address bit10-16 (in 1Kbyte steps)
  7     -        Reserved (undefined)
```
Indicates the start address of the most recently decoded sector (called "Minute
Address" because it points to the MM byte of the MM:SS:FF:MODE sector header).
Normally, CMADR should be forwarded to Host:<br/>
```
  HADR = (CMADR AND 7Fh)*400h+offset
  HXFR = length OR 4000h
```
Whereas, offset would be usually 00h, 04h, or 0Ch (to start reading from the
begin of the sector, or to skip 4-byte MODE1 header, or 12-byte MODE2 header).
And length would be usually 800h (normal data sector), or 924h (entire sector,
excluding the leading 12 sync-bytes). Length bit14 is undocumented/reserved,
but the PSX CDROM BIOS does set that bit for whatever reason.<br/>
Alternately, the sector can be forwarded to the Real-time ADPCM decoder:<br/>
```
  ADPMNT = (CMADR AND 7Fh) OR 80h
```

#### 19h - ADPMNT - ADPCM "MNT" Address (W)
```
  0-6   ADPxxx  ADPCM source Address bit10-16 (in 1Kbyte-steps)
  7     RTADPEN Real-time ADPCM Enable (0=Disable, 1=Enable Real-time ADPCM)
```

#### 04h - DLADR-L, Drive Last Address, bit0-7 (W)
#### 05h - DLADR-M, Drive Last Address, bit8-15 (W)
#### 06h - DLADR-H, Drive Last Address, bit16 (W)
```
  0-16  DLADR  Addr. bit0-16     ...
  17-23 "L"    Reserved (should be 0)
```

#### 10h - DADRC-L - Drive Address Counter, bit0-7 (W)
#### 11h - DADRC-M - Drive Address Counter, bit8-15 (W)
#### 12h - DADRC-H - Drive Address Counter, bit16 (W)
```
  0-16  DADRC    Incrementing Drive-to-Buffer Write Address, bit0-16
  17-23 "L"      Reserved (should be 0)
```

#### 0Eh - DADRC-L - Drive Address Counter, Bit0-7 (R)
#### 0Fh - DADRC-M - Drive Address Counter, Bit8-15 (R)
```
  0-15  DADRC Address bit0-15  ;bit16 is in Port 0Bh            ...
```

#### 0Ch - HXFR-L - Host Transfer Length, bit0-7 (W)
#### 0Dh - HXFR-H - Host Transfer Length, bit8-11 and stuff (W)
```
  0-11  HXFR     number of data bytes, bit0-11 (0..FFFh)       ...
  12    HADR.16  HADR  bit16
  13    "L"      Reserved (should be 0)
  14    "L" ??   Reserved (should be 0)   ;<-- XXX but on PSX: Always 1 !?!
                                          ;    seems to Disable INT8 ?!!!
  15    DISHXFRC Disable HXFRC (0=Use HXFRC, 1=Disable, Infinite-or-Zero Len?)
```

#### 0Eh - HADR-L - Host Transfer Address, bit0-7 (W)
#### 0Fh - HADR-M - Host Transfer Address, bit8-15 (W)
```
  0-15  HADR     Addr. bit0-15  ;bit16 in Port 0Dh    ...
```

#### 0Ah - HXFRC-L - Host Transfer Remain Counter, bit0-7 (R)
#### 0Bh - HXFRC-H - Host Transfer Remain Counter, bit8-11, and other bits (R)
```
  0-11  HXFRC Host Transfer Counter bit0-11 (number of remaining bytes)
  12    HADRC bit16  ;MSB of Port 0Ch/0Dh
  13    DADRC bit16  ;MSB of Port 0Eh/0Fh
  14-15 -     Reserved (undefined) (usually both bits set)
```

#### 0Ch - HADRC-L - Host Transfer Address Counter, bit0-7 (R)
#### 0Dh - HADRC-M - Host Transfer Address Counter, bit8-15 (R)
```
  0-15  HADRC Address bit0-15  ;bit16 is in Port 0Bh
```
"This counter keeps the addresses which write or read the data with host
into/from the buffer.<br/>
When data from the host is written into the buffer or data to the host is read
from the buffer, the HADRC value is output from MA0 to 16. HADRC is incremented
each time one byte of data from the drive is read from the buffer (BFRD is
high) or written into the buffer (BFWR is high)."<br/>

#### Note
When reading from SRAM, data seems to go through a 8-byte data fifo, the HXFRC
(remain) and HADRC (addr) values aren't aware of that FIFO (ie. if there's data
in the fifo, then addr will be 8 bigger and remain 8 smaller than what has
arrived at the host).<br/>

#### Unclear Notes
"If sound map data is to be transferred before the data is transferred
(immediately after the host has set the BFRD and BFWR bits (bits 7 and 6) of
the HCHPCTL register high)":<br/>
```
  900h is loaded into HXFRC
  and 600Ch, 6A0Ch, or 740Ch is loaded into HADRC
  (at least, supposedly, above addresses , for cases when using 32K SRAM)
```
"At any other time":<br/>
```
  HADR and HXFR are loaded into HADRC and HXFRC
```
Unknown what the above crap is trying to say exactly.<br/>
"At any other time" does apparently refer to cases when transfers get started
(whilst during transfer, the address/remain values are obviously
increasing/decreasing).<br/>
For sound map, theoretically, the SMEN bit should be set, but above does
somewhat suggest that BFRD or BFWR (or actually: both BFRD and BFWR) need to be
set...?<br/>

#### Sector Buffer Memory Map (32Kx8 SRAM)
```
  0000h 1st Sector (at 0000h..0923h) (unused gap at 0924h..0BFFh)
  0C00h 2nd Sector (at 0C00h..1523h) (unused gap at 1524h..17FFh)
  1800h 3rd Sector (at 1800h..2123h) (unused gap at 2124h..23FFh)
  2400h 4th Sector (at 2400h..2D23h) (unused gap at 2D24h..2FFFh)
  3000h 5th Sector (at 3000h..3923h) (unused gap at 3924h..3BFFh)
  3C00h 6th Sector (at 3C00h..4523h) (unused gap at 4524h..47FFh)
  4800h 7th Sector (at 4800h..5123h) (unused gap at 5124h..53FFh)
  5400h 8th Sector (at 5400h..5D23h) (unused gap at 5D24h..5FFFh)
  6000h Soundmap ADPCM Buffer (at 600Ch..690Bh) (gaps at 6000h and 690Ch)
  6A00h Soundmap ADPCM Buffer (at 6A0Ch..730Bh) (gaps at 6A00h and 730Ch)
  7400h Soundmap ADPCM Buffer (at 740Ch..7D0Bh) (gaps at 7400h and 7D0Ch)
  7E00h Unknown/Unused
```



##   CDROM Internal CXD1815Q Sub-CPU Misc Registers
#### 16h - HIFCTL - Host Interface Control (W)
```
  0-2  HINT    Request Host Interrupt (INT1..INT7, or 0=None/No change)
  3-7  "L"     Reserved (should be 0)
```

#### 11h - HIFSTS - Host Interface Status (R)
```
  0-2 HINTSTS  Pending Host Interrupt (INT1..INT7, or 0=None/All acknowledged)
  3   DMABUSY  DMA Busy (0=Data FIFO Empty and HXFRC=0, 1=Data Transfer Busy)
  4   PRMRRDY  Parameter Read Ready (0=Parameter FIFO Empty, 1=Ready/Not Empty)
  5   RSLEMPT  Result Empty         (0=Response FIFO Not Empty, 1=Empty)
  6   RSLWRDY  Result Write Ready   (0=Response FIFO Full, 1=Ready/Not Full)
  7   BUSYSTS  Command Busy Status  (0=Command Not Empty, 1=Ack'ed by CLRBUSY)
```

#### 0Ah - CLRCTL - Clear Control (W)
```
  0   RESYNC   Sync with CD DSP (0=No change, 1=Resync, eg. after speed change)
  1-3 "L"      Reserved (should be 0)
  4   RTADPCLR Abort Real-time ADPCM (0=No Change, 1=Abort; when ADPMNT.7=0)
  5   CLRRSLT  Clear Reply FIFO     (0=No change, 1=Acknowledge; clear FIFO)
  6   CLRBUSY  Acknowledge Command  (0=No change, 1=Acknowledge; clear BUSYSTS)
  7   CHPRST   Chip Reset           (0=No change, 1=Do Chip Initialization)
```

#### 07h - INTSTS - Interrupt Status (R) - (0=No, 1=IRQ)
#### 09h - INTMSK - Interrupt Mask (W) - (0=Disable, 1=Enable)
#### 0Bh - CLRINT - Clear Interrupt Status (W) - (0=No change, 1=Clear/Ack)
```
  0   HCRISD   Host Chip Reset Issued
  1   HSTCMND  Host Command                ...
  2   DECINT   Decoder Interrupt           ..
  3   HDMACMP  Host DMA Complete           .   <-- PSX: used for retry ?!?!!!
  4   RTADPEND Real-time ADPCM end
  5   RSLTEMPT Result Empty
  6   DECTOUT  Decoder Time Out
  7   DRVOVRN  Drive Overrun
```

#### 12h - HSTPRM - Host Parameter (R)
```
  0-7  Param FIFO (check HIFSTS.4 to see if the FIFO is empty)
```
HIFSTS.4 goes off when all bytes read.<br/>
Said to have 8-byte FIFO in CXD1199AQ datasheet.<br/>
But, PSX has 16-byte Parameter FIFO...!?!<br/>

#### 13h - HSTCMD - Host Command (R)
```
  0-7  Command (check INTSTS.1 or HIFSTS.7 to see if a command was sent)
```
Command should be ack'ed via CLRINT.1 and CLRCTL.6.<br/>

#### 17h - RESULT - Response FIFO (W)
```
  0-7  Data (has 8-byte FIFO)
```
Said to have 8-byte FIFO in CXD1199AQ datasheet.<br/>
But, PSX has 16-byte Response FIFO...!?!<br/>

#### 08h - ADPCI - ADPCM Coding Information (R)
```
  0   S/M      ADPCM Stereo/Mono        (0=Mono, 1=Stereo)
  1   -        Reserved (undefined)
  2   FS       ADPCM Sampling Frequency (0=37.8kHz, 1=18.9kHz)
  3   -        Reserved (undefined)
  4   BITLNGTH ADPCM Sample Bit Length  (0=Normal/4bit, 1=8bit)
  5   ADPBUSY  ADPCM Decoding           (0=No, 1=Yes/Busy)
  6   EMPHASIS ADPCM Emphasis           (0=Normal/Off, 1=On)
  7   MUTE     DA Data is Muted (uh?)   (0=No, 1=Yes/Muted)
```
Unknown if ADPCI is affected by configurations by Main-CPU's Sound Map ADPCM or
by Sub-CPU's Real-time ADPCM (or by both)?<br/>
Note: Bit5,7 are semi-undocumented in the datasheet (mentioned in the ADPCI
description, but missing in overall register summary).<br/>

#### 1Bh - RTCI - Real-time ADPCM Coding Information (W)
```
  0    S/M      ADPCM Stereo/Mono        (0=Mono, 1=Stereo)
  1    "L"      Reserved (should be 0)
  2    FS       ADPCM Sampling Frequency (0=37.8kHz, 1=18.9kHz)
  3    "L"      Reserved (should be 0)
  4    BITLNGTH ADPCM Sample Bit Length  (0=Normal/4bit, 1=8bit)
  5    "L"      Reserved (should be 0)
  6    EMPHASIS ADPCM Emphasis           (0=Normal/Off, 1=On)
  7    "L"      Reserved (should be 0)
```

#### 06h,09h,10h,14h..1Fh - Reserved (R)
```
  0-7  Reserved (undefined)
```
Of these, 09h and 10h are officially unused/reserved. And addresses 06h and
14h..1Fh aren't officially mentioned to exist at all.<br/>
Trying to read these registers on a PSone returns Data=C0h for 06h, 09h, 10h,
15h-16h, 18h-1Fh, and Data=FFh for 14h, and Data=DEh for 17h.<br/>

#### 08h,13h-15h,18h,1Ah,1Ch-1Fh - Reserved (W)
```
  0-7  Reserved (should be 00h) (or don't write at all)
```
Of these, 09h,13h-15h,18h,1Ah are officially unused/reserved. And addresses
1Ch-1Fh aren't officially mentioned to exist at all.<br/>



##   CDROM Internal Commands CX(0x..3x) - CXA1782BR Servo Amplifier
#### CXA1782BR - CX(0x) - Focus Servo Control - "FZC" FocusZeroCross at SENS pin
```
  23-20 4bit  Command (00h)
  19    1bit  FS4 Focus Servo (0=Off, 1=On)
  18    1bit  FS3 DEFECT
  17    1bit  FS2 Enable Focus Search Voltage (0=Off, 1=On)
  16    1bit  FS1 Select Focus Search Voltage (0=Falling, 1=Rising)
  15-0  16bit Unused (don't care)
```
For Focus Search: Keep FS1=on, and toggle FS2 on and off (this will generate a
waveform, and SENS will indicate when reaching a good focus voltage).<br/>

#### CXA1782BR - CX(1x) - Tracking/Brake/Sled - "DEFECT" at SENS pin
```
  23-20 4bit  Command (01h)
  19    1bit  TG1,TG2 ON/OFF Tracking Servo Gain Up/Normal (hmmm?)
  18    1bit  Brake Circuit ON/OFF
  17-16 2bit  PS Sled Kick Height (0=+/-1, 1=+/-2, 2=Undoc, 3="Don't use"?)
  15-0  16bit Unused (don't care)
```
Note: The PSX CDROM BIOS does use the "Undoc" setting (ie. bit17=1), but the
effect is undoc/unknown?<br/>
Note: CX(1x) works different on CXD2545Q (some bits are moved around, and the
"SledKickHeight" bits are renamed to "SledKickLevel" and moved to different/new
CX(3X) commands.<br/>

#### CXA1782BR - CX(2x) - Tracking and Sled Servo Control - "TZC" at SENS pin
```
  23-20 4bit  Command (02h)
  19-18 2bit  Tracking Control (0=Off, 1=Servo On, 2=F-Jump, 3=R-Jump) ;TM1,3,4
  17-16 2bit  Sled Control     (0=Off, 1=Servo On, 2=F-Fast, 3=R-Fast) ;TM2,5,6
  15-0  16bit Unused (don't care)
```

#### CXA1782BR - CX(3x) - "Automatic Adjustment Comparator Output" at SENS pin
```
  23-20 4bit  Command (03h)
  19    1bit  Value to be adjusted (0=Balance, 1=Gain)
  18-16 3bit  New Balance or Gain value (depending on above bit)
  15-0  16bit Unused (don't care)
```
Note: CX(3x) is extended and works very different on CXD2545Q.<br/>

#### CXA1782BR Command 4x..7x - "HIGH-Z" at SENS pin
```
  N-N   4bit  Command (04h..07h)
```

#### CXA1782BR Command 8x..Fx - "UNSPECIFIED???" at SENS pin
```
  N-N   4bit  Command (08h..0Fh)
```

#### Note
The Servo Amplifier isn't directly connected to the CPU. Instead, it's
connected as a slave device to the Signal Processor. There are two ways to
access the Servo Amplifier:<br/>
1) The CPU can send CX(0X..3X) commands to the Signal Processor (which will
then forward them to the Servo Amplifier).<br/>
2) The Signal Processor can send CX(0X..3X) commands to the Servo Amplifier
(this happens during CX(4xxx) Auto Sequence command).<br/>



##   CDROM Internal Commands CX(4x..Ex) - CXD2510Q Signal Processor
#### CXD2510Q - CX(4xxx) - Auto Sequence
```
  23-20 4bit  Command (4)
  19-16 4bit  AS3-0 Auto Sequence Command (see below)
  15-12 4bit  MT3-0 Max Timer Value (N timer units, or 0=Invalidate Timer)
  11    1bit  LSSL  Timer Units     (0=2.9ms, 1=186ms) (for above MT value)
  10-8  3bit  Unused (zero)
  7-0   8bit  Unused (don't care)
```
Values for AS (Auto Sequence Command):<br/>
```
  00h     Cancel
  04h/05h Forward/Reverse Fine Search   ;<--sends CX(25h) ;\these do internally
  07h     Focus-On                      ;<--sends CX(02h) ; send commands to
  08h/09h Forward/Reverse 1 Track Jump  ;\                ; CXA1782BR
  0Ah/0Bh Forward/Reverse 10 Track Jump ;   sends CX(25h) ; and, auto sequence
  0Ch/0Dh Forward/Reverse 2N Track Jump ;/                ;/is interrupted?
  0Eh/0Fh Forward/Reverse 1N Track Move ;<--CXD2545Q only(Reserved on CXD2510Q)
  01h..03h,06h = Reserved
```

#### CXD2510Q - CX(5x) - Blind,Brake,Overflow Timer
```
  23-20 4bit  Command (5)
  19-16 4bit  TR3-0 Timer (N*0.022ms for Blind/Overflow, N*0.045ms for Brake)
  15-8  8bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```

#### CXD2510Q - CX(6xx) - SledKick,Brake,Kick Timer
```
  23-20 4bit  Command (6)
  19-16 4bit  SD3-0 Timer KICK.D (N*2.9ms for Fine Search? else N*1.45ms?)
  15-12 4bit  KF3-0 Timer KICK.F (N*0.09ms)
  11-8  4bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```

#### CXD2510Q - CX(7xxxx) - Track jump count setting (for Auto Sequence Command)
```
  23-20 4bit  Command (7)
  19-4  16bit Track Jump Count Setting (0..65535) for Command 4x
  3-0   4bit  Unused (don't care)
```

#### CXD2510Q - CX(8xx) - MODE Specification
```
  23-20 4bit  Command (8)
  19    1bit  CDROM        (0=Audio, 1=CDROM; no average and pre-value stuff)
  18    1bit  DOUT Mute    (0=Not muted, 1=Mute DOUT)
  17    1bit  D.out Mute-F (0=Not muted, 1=Mute DA)
  16    1bit  WSEL         (0=Enhanced Sync Window, 1=Enhanced Anti-Rolling)
  15    1bit  VCO SEL      (0=Double Correction, 1=Quadruple Correction)
  14    1bit  ASHS         (0=Double Correction, 1=Quadruple Correction)
  13    1bit  SOCT         (0=Output SubQ to SQSO, 1=Output Each? to SQSO)
  12    1bit  Unused (zero)
  11-8  4bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```

#### CXD2510Q - CX(9xx) - Function Specification
```
  23-20 4bit  Command (9)
  19    1bit  DCLV ON-OFF (complex stuff, related to gain and frequencies)
  18    1bit  DSPB ON-OFF (0=Normal Speed, 1=Double Speed; fixed pitch)
  17    1bit  ASEQ ON-OFF (select output on SENS pin)
  16    1bit  DPLL ON-OFF (0=Analog RFPLL, 1=Digital RFPLL)
  15-14 1bit  Bilingual Audio (0=Stereo, 1=RightOnly, 2=LeftOnly, 3=Mute)
  13    1bit  FLFC (normally 0)
  12    1bit  Unused (zero)
  11-8  4bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```

#### CXD2510Q - CX(Axx) - Audio Control
```
  23-20 4bit  Command (0Ah)
  19    1bit  Vari Up   (write 1-then-0 to increase pitch by +0.1%)
  18    1bit  Vari Down (write 1-then-0 to decrease pitch by -0.1%)
  17    1bit  Mute (0=Not muted; unless muted elsewhere, 1=Mute & Peak=0)
  16    1bit  ATT  (0=Attentuation off, 1=Minus 12 dB)
  15-14 2bit  PCT  (0=Normal, 1=LevelMeter, 2=PeakMeter, 3=Normal) (0-1=QuadC2)
  13-12 2bit  Unused (zero)
  11-8  4bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```
Normal: SQSO outputs... WHAT?<br/>
PeakMeter: SQSO outputs highest peak ever on any channel (bit15: usually 0)<br/>
LevelMeter: SQSO outputs recent peak (with bit15 toggled: 0=Right, 1=Left)<br/>

#### CXD2510Q - CX(Bxxxx) - Traverse Monitor Counter Setting
```
  23-20 4bit  Command (0Bh)
  19-4  16bit Traverse Monitor Count (used when monitored by COMP and COUT) (?)
  3-0   4bit  Unused (don't care)
```

#### CXD2510Q - CX(Cxx) - Spindle Servo Coefficient Setting
```
  23-20 4bit  Command (0Ch)
  19-18 2bit  Gain MDP for CLVP mode (0=-6db, 1=0dB, 1=+6dB, 3=Reserved)
  17-16 2bit  Gain MDS for CLVS/CLVP (0=-12dB, 1=-6dB, 2=0dB, 3=Reserved)
  15    1bit  Zero (zero)
  14    1bit  Gain DCLV0 overall gain (0=0dB, 1=+6dB
  13-12 2bit  Unused (zero)
  11-8  4bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```

#### CXD2510Q - CX(Dx) - CLV Control
```
  23-20 4bit  Command (0Dh)
  19    1bit  DCLV PWM MD Digital CLV PWM mode  (0=Use MDS+MDP, 1=Ternary MDP)
  18    1bit  TB Bottom Hold in CLVS/CLVH modes (0=At cycle RFCK/32, 1=RFCK/16)
  17    1bit  TP Peak Hold in CLVS mode         (0=At cycle RFCK/4, 1=RFCK/2)
  16    1bit  Gain CLVS for CLVS mode (0=0dB, 1=+6dB)(always +6dB in CLVP mode)
  15-8  8bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```

#### CXD2510Q - CX(Ex) - CLV Mode
```
  23-20 4bit  Command (0Eh)
  19-16 4bit  CM3-0
  15-8  8bit  Unused (don't care on CXD2510Q, zero on CXD2545Q)
  7-0   8bit  Unused (don't care)
```
Values for CM (CLV Mode):<br/>
```
  00h Stop  Spindle Motor Stop mode
  06h CLVA  Automatic CLVS/CLVP switching mode, normally used for playback
  08h Kick  Spindle Motor Forward rotation mode
  0Ah Brake Spindle Motor Reverse rotation mode
  0Ch CLVH  Peak hold at 34kHz
  0Eh CLVS  Rough Servo Mode, RF-PLL related
  0Fh CLVP  PLL Servo mode
```

#### N/A - CX(F) - Reserved
```
  23-0  N/A  Don't use
```

#### SUBQ Output
```
 80bit subq
 15bit peak level (lsb first) (absolute/unsigned value)
 1bit  peak l/r flag (aka appears as "MSB" of peak level)
```
L/R is toggled after each SUBQ reading, however the PSX Report mode does
usually forward SUBQ only every 10 frames, so it stays stuck in one setting
(but may toggle after one second; ie. every 75 frames). And, peak is reset
after each read, so 9 of the 10 frames are lost.<br/>

#### CXD2510Q - SENS output
```
  Index         ASEQ=0  ASEQ=1   ;<-- ASEQ can be set via CX(9xx)
  0X            HighZ   SEIN (FZC)                     ;\aka SENS output
  1X            HighZ   SEIN (A.S)    ... aka DEFECT   ; from CXA1782BR
  2X            HighZ   SEIN (T.Z.C)  ... aka TZC      ; forwarded through
  3X            HighZ   SEIN (SSTOP)  ... aka Gain/Bal ;/CXD2510Q
  4X            HighZ   XBUSY
  5X            HighZ   FOK
  6X            HighZ   SEIN (HighZ)
  AX            GFS     GFS
  BX            COMP    COMP
  CX            COUT    COUT
  EX            /OV64   /OV64
  7X-9X,DX,FX   HighZ   0
```
Whereas,<br/>
```
 FZC    Focus Zero Cross
 DEFECT Defect?
 TZC    Tracking Zero Cross
 SSTOP  Gain or Balance adjust reached wanted level
 XBUSY  Low while the auto sequencer operation is busy
 FOK    High for "focus OK" (same as FOK pin)
 GFS    High when the played back frame sync is obtained with correct timing
 COMP   Measures the number of tracks set with Reg B. High when Reg B is
          latched, low when the initial Reg B number is input by CNIN
 COUT   Measures the number of tracks set with Reg B. High when Reg B is
          latched, toggles each time the Reg B number is input by CNIN. While
          $44 and $45 are being executed, toggles with each CNIN 8-count
          instead of the Reg B number
 OV64   Low when filtered EFM signal is lengthened by 64 channel clock
          pulses or more
```



##   CDROM Internal Commands CX(0x..Ex) - CXD2545Q Servo/Signal Combo
#### CXD2545Q - CX(0x) and CX(2x) - same as CXA1782BR Servo Amplifier
[CDROM Internal Commands CX(0x..3x) - CXA1782BR Servo Amplifier](#cdrom-internal-commands-cx0x3x---cxa1782br-servo-amplifier)<br/>

#### CXD2545Q - CX(4x..Ex) - same as CXD2510Q Signal Processor
[CDROM Internal Commands CX(4x..Ex) - CXD2510Q Signal Processor](#cdrom-internal-commands-cx4xex---cxd2510q-signal-processor)<br/>
One small difference is that the CXD2545Q supports a new "M Track Move"
function as part of the CX(4xxx) command. And, some "don't care" bits are now
reserved (ie. some commands need to be padded with additional leading "0"
bits).<br/>

#### CXD2545Q - CX(1x) - Anti Shock/Brake/Tracking Gain/Filter
```
  23-20 4bit  Command (01h)
  19    1bit  Anti Shock (0=Off, 1=On)
  18    1bit  Brake      (0=Off, 1=On)
  17    1bit  Tracking Gain (0=Normal, 1=Up)
  16    1bit  Tracking Gain Filter (0=Select 1, 1=Select 2)
  15-0  16bit Unused (don't care)
```

#### CXD2545Q - CX(30..33) - Sled Kick Level
```
  23-20 4bit  Command (03h)
  19-18 2bit  Subcommand (0)
  17-16 2bit  Sled Kick Level (0=+/-1, 1=+/-2, 2=+/-3, 3=+/-4)
  15-0  16bit Unused (don't care)
```

#### CXD2545Q - CX(34xxxx) - Write to Coefficient RAM
```
  23-16 8bit  Command (34h)
  15    1bit  Zero (0)
  14-8  7bit  Address (00h..4Fh = Select Coefficient K00..K4F)
  7-0   8bit  Data    (00h..FFh = New value)
  PLUS  8bit  Eight more bits on PSone (!)
```
Allows to change the default preset coefficient values,<br/>
[CDROM Internal Coefficients (for CXD2545Q)](#cdrom-internal-coefficients-for-cxd2545q)<br/>

#### CXD2545Q - CX(34Fxxx) - Write to Special Register
```
  23-12 12bit Command (34Fh)
  11-10 2bit  Index (0=TRVSC, 1=FBIAS, 2=?, 3=?)
  9-0   10bit Data (for FBIAS: bit0=don't care)
```

#### CXD2545Q - CX(35xxxx) - FOCUS SEARCH SPEED/VOLTAGE/AUTO GAIN
```
  23-16 8bit  Command (35h)
  15-14 2bit  FT  Focus Search-up speed 1
  13-8  6bit  FS  Focus Search limit voltage (default 011000b) (+/-1.875V)
  7     1bit  FTZ Focus Search-up speed 2
  6-0   7bit  FG  AGF Convergence Gain Setting (default 0101101b)
```

#### CXD2545Q - CX(36xxxx) - DTZC/TRACK JUMP VOLTAGE/AUTO GAIN
```
  23-16 8bit  Command (36h)
  15    1bit  Zero (0)
  14    1bit  DTZC DTZC Delay (0=4.25us/Default, 1=8.5us)
  13-8  6bit  TJ   Track Jump voltage (default 001110b) (+/-1.09V)
  7     1bit  Zero (0)
  6-0   7bit  TG   AGT Convergence Gain Setting (default 0101110b)
```

#### CXD2545Q - CX(37xxxx) - FZSL/SLED MOVE/Voltage/AUTO GAIN
```
  23-16 8bit  Command (37h)
  15-14 2bit  FZS              XXX pg. 84
  13-8  6bit  SM    Sled Move Voltage
  7     1bit  AGS
  6     1bit  AGJ
  5     1bit  AGGF
  4     1bit  AGGT
  3     1bit  AGV1
  2     1bit  AGV2
  1     1bit  AGHS
  0     1bit  AGHT
```

#### CXD2545Q - CX(38xxxx) - Level/Auto Gain/DFSW (Initialize)
```
  23-16 8bit  Command (38h)
  15    1bit  VCLM VC level measurement on/off
  14    1bit  VCLC VC level compensation for FCS_In Register on/off
  13    1bit  FLM  Focus zero level measurement on/off
  12    1bit  FLC0 Focus zero level compensation for FZC Register on/off
  11    1bit  RFLM RF zero level measurement on/off
  10    1bit  RFLC RF zero level compensation on/off
  9     1bit  AGF  Focus automatic gain adjustment on/off
  8     1bit  AGT  Tracking automatic gain adjustment on/off
  7     1bit  DFSW Defect switch disable (1=disable defect measurement)
  6     1bit  LKSW Lock switch (1=disable sled free-running prevention)
  5     1bit  TBLM Traverse center measurement on/off
  4     1bit  TCLM Tracking zero level measurement on/off
  3     1bit  FLC1 Focus zero level compensation for FCS_In Register on/off
  2     1bit  TLC2 Traverse center compensation on/off
  1     1bit  TLC1 Tracking zero level compensation on/off
  0     1bit  TLC0 VC level compensation for TRK/SLD_In register on/off
```
VCLM,FLM,RFLM,TCLM are accepted every 2.9ms.<br/>

#### CXD2545Q - CX(39xx) - Select internal RAM/Registers for serial readout
```
  23-16 8bit  Command (39h)
  15    1bit  DAC Serial data readout DAC mode on/off
  14-8  7bit  SD  Serial readout data select (see below)
  7-0   8bit  Unused (don't care)
```
Serial Readout Addresses:<br/>
```
  Addr    Data  Content
  00h     8bit  VC input signal
  01h     8bit  SE input signal
  02h     8bit  TE input signal
  03h     8bit  FE input signal
  04h-07h 9bit  TE AVRG register (mirrored to 04h-07h)
  08h-0Bh 9bit  FE AVRG register (mirrored to 08h-0Bh)
  0Ch-0Fh 9bit  VC AVRG register (mirrored to 0Ch-0Fh)
  12h     8bit  RFDC envelope (peak)
  13h     8bit  RFDC envelope (bottom)
  1Ch     9bit  TRVSC register
  1Dh     9bit  FBIAS register
  1Eh     8bit  RFDC input signal
  1Fh     8bit  RF AVRG register
  20h-3Fh 16bit Data RAM        (M00-M1F)
  40h-7Fh 8bit  Coefficient RAM (K00-K3F) (note: K40-K4F cannot be read out)
```

#### CXD2545Q - CX(3Ax000) - Focus BIAS addition enable
```
  23-16 8bit  Command (3Ah)
  15    1bit  Zero (0)
  14    1bit  FBON: FBIAS register addition (0=off, 1=Add FBIAS to FCS)
  13-0  14bit Zero (0)
```

#### CXD2545Q - CX(3Bxxxx) - Operation for MIRR/DFCT/FOK
```
  23-16 8bit  Command (3Bh)
  15-14 2bit  SFO  FOK Slice Level (...depends on SFOX)
  13-12 2bit  SDF  DFCT Slice Level (0=89mV, 1=134mV, 2=179mV, 3=224mV)
  11-10 2bit  MAX  DFCT Maximum Time (0=No Limit, 1=2ms, 2=2.36ms, 3=2.72ms)
  9     1bit  SFOX FOK Slice Level (...depends on SFO)
  8     1bit  BTF  Bottom Hold Double-Speed Count-Up mode for MIRR (0=off)
  7-6   2bit  D2V  Peak Hold 2 for DFCT (0=22.05kHz, 1=44.1, 2=88.2, 3=176.4)
  5-4   2bit  D1V  Peak Hold 1 for DFCT (0=176.4kHz, 1=352.8, 2=705.6, 3=1411)
  3-0   4bit  Zero (0)
```

#### CXD2545Q - CX(3Cxxxx) - TZC for COUT SLCT HPTZC (Default)
```
  23-16 8bit  Command (3Ch)
  15-0  16bit Unused (don't care)
```

#### CXD2545Q - CX(3Dxxxx) - TZC for COUT SLCT DTZC
```
  23-16 8bit  Command (3Dh)
  15-0  16bit Unused (don't care)
```

#### CXD2545Q - CX(3Exxxx) - Filter
```
  23-16 8bit  Command (3Eh)
  15-14 2bit  F1NDM FCS servo filter 1st stage (1=normal, 2=down)
  13-12 2bit  F3NUM FCS servo filter 3rd stage (1=normal, 2=up)
  11-10 2bit  T1NDM TRK servo filter 1st stage (1=normal, 2=down)
  9-8   2bit  T3NUM TRK servo filter 3rd stage (1=normal, 2=up)
  7     1bit  DFIS  FCS hold filter input extraction node (0=M05, 1=M04)
  6     1bit  TLCD  Mask TLC2 set by D2 of CX(38) only when FOK low
  5     1bit  RFLP  Pass signal from RFDC pin through low-pass-filter
  4-0   5bit  Zero (0)
```

#### CXD2545Q - CX(3Fxxxx) - Others
```
  23-16 8bit  Command (3Fh)          ... XXX pg. 89
  15-14 2bit  Unused (0)
  13-12 2bit  XTD
  11    1bit  Unused (0)
  10-8  3bit  DRR
  7     1bit  Unused (0)
  6     1bit  ASFG
  5     1bit  Unused (0)
  4     1bit  LPAS
  3-2   2bit  SRO
  1-0   2bit  Unused (0)
```

#### CXD2545Q feedback on 39xx: see pg. 77 (eg. 390C = VC AVRG)
XXX<br/>

#### CXD2545Q - SENS output
```
  Index          ASEQ=0  ASEQ=1           Length
  $0X            Z       FZC              -
  $1X            Z       AS               -
  $2X            Z       TZC              -
  $38            Z       AGOK*1           -
  $38            Z       XAVEBSY*1        -
  $30-37,$3A-3F  Z       SSTP             -
  $3904          Z       TE Avrg Reg.     9 bit
  $3908          Z       FE Avrg Reg.     9 bit
  $390C          Z       VC Avrg Reg.     9 bit
  $391C          Z       TRVSC Reg.       9 bit
  $391D          Z       FB Reg.          9 bit
  $391F          Z       RFDC Avrg Reg.   8 bit
  $4X            Z       XBUSY            -
  $5X            Z       FOK              -
  $6X            Z       0                -
  $AX            GFS     GFS              -
  $BX            COMP    COMP             -
  $CX            COUT    COUT             -
  $EX            OV64    OV64             -
  $7X-9X,DX,FX   Z       0                -
```
\*1 $38 outputs AGOK during AGT and AGF command settings, and XAVEBSY during
AVRG measurement.<br/>
SSTP is output in all other cases.<br/>



##   CDROM Internal Commands CX(0x..Ex) - CXD2938Q Servo/Signal/SPU Combo
Most commands are same as on CXD2545Q. New/changed commands are:<br/>

#### CXD2938Q - CX(349xxxxx) - New SCEx
Older PSX consoles have received the "SCEx" string at 250 baud via HC05
PortB.bit1, which allowed modchips to injected faked "SCEx" signals to that
pin. To prevent that, the CXD2938Q contains some new 32bit commands that allow
to receive somewhat encrypted "SCEx" strings via SPI bus. The used commands
are:<br/>
```
  CX(34910000) NewScexStopReading
  CX(3491xy80) NewScexRandomKey(xy)
  CX(34920000) NewScexFlushResyncOrSo
  CX(34944A00) NewScexInitValue1
  CX(3498C000) NewScexInitValue2
  CX(349C1000) NewScexThis   ;\inverse  ;\use CX(3C2080) for COUT selection
  CX(349D1000) NewScexThat   ;/of COUT  ;/
```
The relevant command is NewScexRandomKey(xy) which does send a random value
(x=01h..0Fh, and y=01h), and does then receive a 12-byte response via SPI bus
(which is normally used to receive SUB-Q data).<br/>
```
  1st byte: Unknown/unused (normally ADR/Control) ;\these should be probably
  2nd byte: Unknown/unused (normally Track)       ; set to some invalid values
  3rd byte: Unknown/unused (normally Index/Point) ;/to avoid SUB-Q confusion
  4th..10th byte: SCEx data or Dummy bytes (depending on xy.bit7..1)
  11th..12th byte: Unknown/unused (normally Audio Peak level)
```
The 12-byte packet does contain one SCEx character encoded in 4th..10th byte
corresponding to Flags in "xy" bit 7..1 (in that order):<br/>
All bytes with Flag=1 are ORed together to compute a Character byte (those
bytes could be all set to 53h for "S", or if more than one flag is set, it
could be theoretically split to something like 41h and 12h).<br/>
All bytes with Flag=0 are ORed together to compute a Dummy byte. If the
Character byte is same as the Dummy byte, then it gets destroyed by setting
Character=00h (to avoid that, one could set all dummies to 00h, or set one or
more dummies to FFh, for example).<br/>
Finally, "xy" bit0=0 indicates that the resulting character byte is inverted
(XORed by FFh), however, the CDROM BIOS does always use bit0=1, so the
inversion feature is never used.<br/>
For the whole SCEx string, there must be at least one 00h byte inserted between
each character (or some Char=Dummy mismatch, which results in Char=00h either),
and there should be a few more 00h bytes preceeding the first character ("S").<br/>
Note: Modchips didn't bother to reproduce that new SCEx transfers, instead they
have simply bypassed it by injecting the 250 baud SCEx string to some analog
lower level signal.<br/>

#### CXD2938Q - CX(3Bxxxx) - Some Changed Bits
Same as in older version, but initialized slightly differently: CXD2545Q used
CX(3B2250) whilst CXD2938Q is using CX(3B7250).<br/>

#### CXD2938Q - CX(3Cxxxx) - TzcCoutSelect with New/Changed Extra Bits
The CXD2545Q used two 8bit commands, CX(3C) and CX(3D), for TzcOut selection,
which are now replaced by a single 24bit command, CX(3Cxxxx), and which do
include a new mode related to New SCEx.<br/>
```
  CXD2545Q   CXD2938Q
  CX(3C)     CX(3C0080) TzcCoutSelectHPTZC;\ <--formerly CX(3C)
  -          CX(3C2080) TzcCoutSelectSCEX ;  <--special NewScex mode
  CX(3D)     CX(3C4080) TzcCoutSelectDTZC ;/ <--formerly CX(3D)
```

#### CXD2938Q - CX(8xxxxx) - Disc Mode with New/Changed Extra Bits
Command CX(8xx) has been 12bit wide on CXD2545Q, and is now expanded 24bit
width (with some changed/unknown bits).<br/>
```
  CXD2545Q   CXD2938Q
  CX(8180)   CX(810408) MODE = Audio (CD-DA)
  CX(8120)   CX(812400) MODE = Audio (CD-DA) (manual SPI bus access)
  CX(8980)   CX(890408) MODE = CDROM (Data)
  -          CX(898000) MODE = CDROM (Data) (used on RESET)
```

#### CXD2938Q - CX(9xx000) - Normal/Double Speed with New Extra Bits
Command CX(9xx) has been 12bit wide on CXD2545Q (with bit12=reserved/zero), and
is now expanded 24bit width (with bit12=unknown/one and bit11-0=unknown/zero).<br/>

#### CXD2938Q - CX(Dx0000) and CX(Ex0000) - New Zero Padding
Commands CX(Dx) and CX(Ex) have been 8bit wide on CXD2545Q, and are now
zeropadded to 24bit width, ie. CX(Dx0000) and CX(Ex0000). Unknown if the extra
bits are hiding any extra features. In practice, the CDROM BIOS is always
setting them zero (except in some test commands which are accidently still
using the old 8bit form, resulting in garbage in lower 16bits).<br/>



##   CDROM Internal Commands CX(xx) - Notes
#### Serial Command Transmission (for Signal Processor and Servo Amplifier)
Commands are sent serially LSB first via DATA,CLOK,XLAT pins: DATA+CLOK are
used to send commands to the chip, command execution is then applied by
dragging XLAT low for a moment.<br/>
Commands can be up to 24bits in length, but unused LSBs (the "don't care" bits)
can be omitted; the PSX BIOS clips the length to 8bit/16bit where possible (due
to the LSB-first transfer order, the chip does treat the most recently
transferred bit as MSB=bit23, and there's no need to transfer the LSBs if they
aren't used).<br/>
Aside from being used as command number, the four most recently transferred
bits are also used to select SENS status feedback (for the SENS selection it
doesn't matter if the four bits were terminated by XLAT or not).<br/>

#### Sled Motor / Track Jumps / Tracking
The Sled motor moves the drive head to the current read position. On a Compact
Disc, the term "Track" does normally refer to Audio tracks (songs). But the
drive hardware uses the terms "Track" and "Tracking" for different purposes:<br/>
Tracking appears to refer to moving the Optics via magnets (ie. moving only the
laser/lens, without actually moving the whole sled) (this is done for fine
adjustments, and it seems to happen more or less automatically; emulators can
just return increasing sectors without needing to handle special tracking
commands).<br/>
Track jumps refer to moving the entire Sled, one "track" is equal to one spiral
winding (1.6 micrometers). One winding contains between 9 sectors on innermost
windings, and 22.5 sectors on outermost windings (the PSX cdrom bios is
translating the sector-distance to non-linear track-distance, and emulators
must undo that translation; otherwise the sled doesn't arrive at the intended
location; the cdrom bios will retry seeking a couple of times and eventually
settle down at the desired location - but it will timeout if the sled emulation
is too inaccurate).<br/>
The PSX hardware uses two mechanisms for moving the Sled:<br/>
Command CX(4xxx) Forward/Reverse Track Jump: allows to move the sled by
1..131070 tracks (ie. max 210 millimeters), and the hardware does stop
automatically after reaching the desired distance.<br/>
Command CX(2x) Forward/Reverse Fast Sled: moves the sled continously until it
gets stopped by another command (in this mode, software can watch the COUT
signal, which gets toggled each "N" tracks; whereas "N" can be selected via
Command CX(Bxxxx), which is configured to N=100h in PSX).<br/>
The PSX cdrom bios is issuing another Fast Sled command (in opposite direction)
after Fast Sled commands, emulators must somehow interprete this as "sled
slowdown" (rather than as actually moving the sled in opposite direction, which
could move the sled miles away from the target). For some reason vC1 BIOS is
using a relative short slowdown period, whilst vC2/vC3 are using much longer
slowdown periods (probably related to different SledKickHeight aka
SledKickLevel settings and/or to different Sled Move Voltage settings).<br/>

#### Focus / Gain / Balance
The hardware includes commands for adjusting & measuring
focus/gain/balance. Emulators can just omit that stuff, and can always
signalize good operation (except that one should emulate failures for Disc
Missing; and eventually also for cases like Laser=Off, or Spindle=Stopped).<br/>
Focus does obviously refer to moving the lens up/down. Gain does probably refer
to reflection level/laser intensity. Balance might refer to tracking
adjustments or so.<br/>



##   CDROM Internal Commands CX(xx) - Summary of Used CX(xx) Commands
The PSX CDROM BIOS versions vC1, vC2, and vC3 are using following CX()
commands:<br/>
```
<B>  <--vC1-->  <--vC2-->  <--vC3--></B>
<B>  CXD2510Q   CXD2545Q   CXD2938Q</B>
  CX(00)     CX(00)     CX(00)     AllFocusSwitchesOff
  CX(02)     CX(02)     CX(02)     FocusSearchVoltageFalling
  CX(03)     CX(03)     CX(03)     FocusSearchVoltageRising ;ForTestOnly
  CX(08)     CX(08)     CX(08)     FocusServoOn
  CX(0C)     CX(0C)     CX(0C)     FocusServoOnAndDefectOn ;diff.usage vC# ?
  -----
  CX(11)     -          -          SledKickHeight2
  CX(12)     -          -          SledKickHeightInvalid
  CX(19)     -          -          TrackingGainAndSledKickHeight2
  CX(1D)     -          -          TrackingGainBrakeAndSledKickHeight2
  CX(1E)     -          -          TrackingGainBrakeAndSledKickHeightInvalid
  -----
  -          CX(11)     CX(11)     AntiShockOff            ;\
  -          CX(13)     CX(13)     AntiShockOffGainUp      ;
  -          CX(17)     CX(17)     AntiShockOffGainUpBrake ;/
  -----
  CX(20)     CX(20)     CX(20)     SledAndTrackingOff
  CX(21)     CX(21)     CX(21)     SledServoOn          ;ForTestOnly
  CX(22)     CX(22)     CX(22)     SledFastForward
  CX(23)     CX(23)     CX(23)     SledFastReverse
  CX(24)     -          -          TrackingServoOn
  CX(25)     CX(25)     CX(25)     SledAndTrackingServoOn
  -          CX(26)     CX(26)     SledFastForwardAndTrackingServoOn
  CX(28)     CX(28)     CX(28)     TrackingForwardJump  ;ForTestOnly
  CX(2C)     CX(2C)     CX(2C)     TrackingReverseJump  ;ForTestOnly
  -----
  CX(30+n)   -          -          BalanceAdjust(0..7)
  CX(38+n)   -          -          GainAdjust(0..7)
  -----
  -          CX(30)     CX(30)     SetSledKickLevel1       ;\
  -          CX(31)     CX(31)     SetSledKickLevel2       ;
  -          CX(32)     CX(32)     SetSledKickLevel3       ;/
  -----
  -          CX(3400E6) CX(3400E6) SetK00toE6hSledInputGain            ;def=E0h
  -          CX(340730) CX(340730) SetK07to30hSledAutoGain       ;blah ;def=30h
  -          CX(34114A) CX(34114A) SetK11to4AhFocusOutputGain          ;def=32h
  -          CX(341330) CX(341330) SetK13to30hFocusAutoGain      ;blah ;def=30h
  -          CX(341D6F) CX(341D6F) SetK1Dto6FhTrackingLowBoostFilterAL ;def=44h
  -          CX(341F64) CX(341F64) SetK1Fto64hTrackingLowBoostFilterBL ;def=5Eh
  -          CX(342220) CX(342220) SetK22to20hTrackingOutputGain       ;def=18h
  -          CX(342330) CX(342330) SetK23to30hTrackingAutoGain   ;blah ;def=30h
  -          CX(342D28) CX(342D28) SetK2Dto28hFocusGainDownOutputGain  ;def=1Bh
  -          CX(343E70) CX(343E70) SetK3Eto70hTrackingGainUpOutputGain ;def=57h
  -          -          CX(34910000) NewScexStopReading      ;\
  -          -          CX(3491x180) NewScexRandomKey(x)     ;
  -          -          CX(34920000) NewScexFlushResyncOrSo  ; SCEX SPECIAL
  -          -          CX(34944A00) NewScexInitValue1       ; see also:
  -          -          CX(3498C000) NewScexInitValue2       ; CX(3C2080)
  -          -          CX(349C1000) NewScexThis   ;\inverse ;
  -          -          CX(349D1000) NewScexThat   ;/of COUT ;/
  -          CX(34F000) CX(34F000) SetTRVSCto000h
  -          CX(34Fxxx) CX(34Fxxx) SetFBIAStoNNNh
  -----
  -          CX(3740AA) CX(3740AA) SetSMto00h      ;\set SM to 0,6,7,9
  -          CX(3746AA) CX(3746AA) SetSMto06h      ; (sled move voltage)
  -          CX(3747AA) CX(3747AA) SetSMto07h      ; (and init several
  -          CX(3749AA) CX(3749AA) SetSMto09h      ;/fixed settings)
  -----
  -          CX(380010) CX(380010) ModeMeasureTrackingZeroLevel ;\Measure modes
  -          CX(380800) CX(380800) ModeMeasureRfZeroLevel       ; (accepted
  -          CX(382000) CX(382000) ModeMeasureFocusZeroLevel    ; every 2.9ms)
  -          CX(388000) CX(388000) ModeMeasureVcLevel           ;/
  -          CX(38140A) CX(38140A) ModeCompensate
  -          CX(38140E) CX(38140E) ModeCompensateAndTraverseCenter
  -          CX(38148A) CX(38148A) ModeCompensateAndDefectOff
  -          CX(38148E) CX(38148E) ModeCompensateAndDefectOffTraverseCenter
  -          CX(3814AA) CX(3814AA) ModeCompensateAndStuffAndMeasureTraverse ;!
  -          CX(38150A) CX(38150A) ModeCompensateAndTrackingAutoGain
  -          CX(38150E) CX(38150E) ModeCompensateAndTrackingAutoGain
  -          CX(38160A) CX(38160A) ModeCompensateAndFocusAutoGain
  -----
  -          CX(391E)   -          SenseRFDCinputSignalWithoutDAC  ;\rather
  -          CX(3983)   -          SenseFEinputSignalWithDAC       ;/unused
  -          CX(399C)   -          SenseTRVSCregisterWithDAC       ;\only if
  -          CX(399D)   -          SenseFBIASregisterWithDAC       ;/TEST1=LOW
  -----
  -          CX(3A0000) CX(3A0000) FocusBiasAdditionOff            ;\
  -          CX(3A4000) CX(3A4000) FocusBiasAdditionOn             ;/
  -          CX(3B2250)!CX(3B7250)!InitOperationForMirrDfctFok <-- vC2/vC3 DIFF
  -          CX(3C)  !!!CX(3C0080) TzcCoutSelectHPTZC;\ <--formerly CX(3C)
  -          -       !!!CX(3C2080) TzcCoutSelectSCEX ;  <--special NewScex mode
  -          CX(3D)  !!!CX(3C4080) TzcCoutSelectDTZC ;/ <--formerly CX(3D)
  -          CX(3E0000) CX(3E0000) InitFilterBits                  ;\
  -          CX(3E0008) CX(3E0008) InitFilterBitsInvalid           ;/
  -          CX(3F0008) CX(3F0008) InitOtherStuff                  ;-
  -----
  CX(4000)   CX(4000)   CX(4000)   AutoSeqCancel
  CX(4700)   CX(4700)   CX(4700)   AutoSeqFocusOn
  CX(4800)   CX(4800)   CX(4800)   Forward1track
  CX(4900)   CX(4900)   CX(4900)   Reverse1track
  CX(4C00)   CX(4C00)   CX(4C00)   Forward2Ntrack
  CX(4D00)   CX(4D00)   CX(4D00)   Reverse2Ntrack
  -----
  CX(54)     CX(54)     CX(54)     BlindBrakeOverflowTimer=4
  CX(5A)     CX(5A)     CX(5A)     BlindBrakeOverflowTimer=A
  CX(6100)   CX(6100)   CX(6100)   SledKickBrakeKickTimer
  CX(70xxx0) CX(70xxx0) CX(70xxx0) TrackJumpCountSetting
  CX(8180)   CX(8180)!!!CX(810408) MODE = Audio (CD-DA)
  -          CX(8120)!!!CX(812400) MODE = Audio (CD-DA) (manual SPI bus access)
  -          -          CX(810000/UNUSED)
  -          -          CX(812000/UNUSED)
  CX(8980)   CX(8980)   CX(890408) MODE = CDROM (Data)
  -          -          CX(898000) MODE = CDROM (Data) (used on RESET)
  CX(9B00)   CX(9B00)!!!CX(9B1000) NormalSpeed
  CX(9F00)   CX(9F00)!!!CX(9F1000) DoubleSpeed
  CX(A040)   CX(A040)   CX(A040)   Attentuation Off
  CX(A140)   CX(A140)   CX(A140)   Attentuation -12 dB
  CX(B01000) CX(B01000) CX(B01000) TraverseMonitorCounterSetting
  CX(C600)   CX(C600)   CX(C600)   SpindleServoCoefficientSetting
  CX(D7)     CX(D7)     CX(D70000) ClvControl (fixed)
  CX(E0)     CX(E0)     CX(E00000) SpindleMotorStop
  -          -          CX(E02000) <-- aka bugged CX(E0) with CRAP=2000h
  CX(E6)     CX(E6)     CX(E60000) AutomaticNormal
  CX(E8)     CX(E8)     CX(E80000) SpindleMotorForward
  -          -          CX(E8crap) <-- aka bugged CX(E8) with CRAP=xxxxh
  CX(EA)     CX(EA)     CX(EA0000) SpindleMotorReverse
  -          -          CX(EAcrap) <-- aka bugged CX(EA) with CRAP=xxxxh
  CX(EE)     CX(EE)     CX(EE0000) RoughServo
  -----
  CX(F)      CX(F)      CX(F)      Unused (N/A)
  -----
  CX(Xx)     CX(Xx)     CX(Xx)       ;\
  CX(Xxxx)   CX(Xxxx)   CX(Xxxx)     ; TestCommand (cmd_19h_50h)
  CX(Xxxxxx) CX(Xxxxxx) CX(Xxxxxx)   ;
  -          -          CX(Xxxxxxxx) ;/
  -          CX(Xxxxxx) CX(Xxxxxx) SerialSense, CX(Xxxx) with extra 8bit junk
```
Note: for vC2, some CX(38xxxx) values may differ depending on
"set\_mid\_lsb\_to\_140Eh".<br/>
For vC2, CX(Dx) and CX(Ex) should be officially zero-padded to CX(Dx00) and
CX(Ex00), but the vC2 BIOS doesn't do that, it still uses short 8bit form.<br/>
For vC2, CX(Dx) and CX(Ex) should be apparently zero-padded to CX(Dx0000) and
CX(Ex0000), at least, the vC3 BIOS is doing so (except on some test comannds
that do still use the CX(Ex) short form).<br/>

#### Used Sense Values
```
  sense(30)  SEIN.BAL       ;vC2: SSTP
  sense(38)  SEIN.GAIN      ;vC2: AGOK(AGT/AGF) or XAVEBSY(AVRG) or SSTP(else?)
  sense(40)  XBUSY (low=AutoSeqBusy)
  sense(50)  FOK   (high=FokusOkay)
  sense(A0)  GFS   (high=GoodFrameSync, ie. CorrectPlaybackSpeed)
  sense(C5)  COUT  (toggles each 100h 'tracks') (100h=selected via CX(B01000))
  sense(EA)  /OV64 (low=EFM too long?)
```



##   CDROM Internal Coefficients (for CXD2545Q)
The CXD2545Q contains Preset Coefficients in internal ROM, which are copied to
internal Coefficient RAM shortly after Reset. CX(34xxxx) allows to change those
RAM settings, and CX(39xxxx) allows to readout some of those values serially.<br/>

#### CXD2545Q - Coefficient Preset Values
```
  Addr Val Expl.
  K00  E0  Sled input gain
  K01  81  Sled low boost filter A-H
  K02  23  Sled low boost filter A-L
  K03  7F  Sled low boost filter B-H
  K04  6A  Sled low boost filter B-L
  K05  10  Sled output gain
  K06  14  Focus input gain
  K07  30  Sled auto gain
  K08  7F  Focus high cut filter A
  K09  46  Focus high cut filter B
  K0A  81  Focus low boost filter A-H
  K0B  1C  Focus low boost filter A-L
  K0C  7F  Focus low boost filter B-H
  K0D  58  Focus low boost filter B-L
  K0E  82  Focus phase compensate filter A
  K0F  7F  Focus defect hold gain
  K10  4E  Focus phase compensate filter B
  K11  32  Focus output gain
  K12  20  Anti shock input gain
  K13  30  Focus auto gain
  K14  80  HPTZC / Auto Gain High pass filter A
  K15  77  HPTZC / Auto Gain High pass filter B
  K16  80  Anti shock high pass filter A
  K17  77  HPTZC / Auto Gain low pass filter B
  K18  00  Fix (should not change this preset value)
  K19  F1  Tracking input gain
  K1A  7F  Tracking high cut filter A
  K1B  3B  Tracking high cut filter B
  K1C  81  Tracking low boost filter A-H
  K1D  44  Tracking low boost filter A-L
  K1E  7F  Tracking low boost filter B-H
  K1F  5E  Tracking low boost filter B-L
  K20  82  Tracking phase compensate filter A
  K21  44  Tracking phase compensate filter B
  K22  18  Tracking output gain
  K23  30  Tracking auto gain
  K24  7F  Focus gain down high cut filter A
  K25  46  Focus gain down high cut filter B
  K26  81  Focus gain down low boost filter A-H
  K27  3A  Focus gain down low boost filter A-L
  K28  7F  Focus gain down low boost filter B-H
  K29  66  Focus gain down low boost filter B-L
  K2A  82  Focus gain down phase compensate filter A
  K2B  44  Focus gain down defect hold gain
  K2C  4E  Focus gain down phase compensate filter B
  K2D  1B  Focus gain down output gain
  K2E  00  Not used
  K2F  00  Not used
  K30  80  Fix (should not change this preset value)
  K31  66  Anti shock low pass filter B
  K32  00  Not used
  K33  7F  Anti shock high pass filter B-H
  K34  6E  Anti shock high pass filter B-L
  K35  20  Anti shock filter comparate gain
  K36  7F  Tracking gain up2 high cut filter A
  K37  3B  Tracking gain up2 high cut filter B
  K38  80  Tracking gain up2 low boost filter A-H
  K39  44  Tracking gain up2 low boost filter A-L
  K3A  7F  Tracking gain up2 low boost filter B-H
  K3B  77  Tracking gain up2 low boost filter B-L
  K3C  86  Tracking gain up phase compensate filter A
  K3D  0D  Tracking gain up phase compensate filter B
  K3E  57  Tracking gain up output gain
  K3F  00  Not used
  K40  04  Tracking hold filter input gain
  K41  7F  Tracking hold filter A-H
  K42  7F  Tracking hold filter A-L
  K43  79  Tracking hold filter B-H
  K44  17  Tracking hold filter B-L
  K45  6D  Tracking hold filter output gain
  K46  00  Not used
  K47  00  Not used
  K48  02  Focus hold filter input gain
  K49  7F  Focus hold filter A-H
  K4A  7F  Focus hold filter A-L
  K4B  79  Focus hold filter B-H
  K4C  17  Focus hold filter B-L
  K4D  54  Focus hold filter output gain
  K4E  00  Not used
  K4F  00  Not used
```
