---
name: bios-boot-internals
description: "PSX BIOS internals: boot sequence, internal functions, PC file server (DTL-H), TTY console (std_io), character sets (Shift-JIS/ASCII), control blocks (TCB/EvCB/FCB), BIOS versions and patches. Use when analyzing boot process, BIOS internals, or patching BIOS behavior."
---

##   BIOS Internal Boot Functions
#### A(45h) - init\_a0\_b0\_c0\_vectors
Copies the three default four-opcode handlers for the A(NNh),B(NNh),C(NNh)
functions to A00000A0h..A00000CFh.<br/>

#### C(07h) - InstallExceptionHandlers()  ;destroys/uses k0/k1
Copies the default four-opcode exception handler to the exception vector at
80000080h..8000008Fh, and, for whatever reason, also copies the same opcodes to
80000000h..8000000Fh.<br/>

#### C(08h) - SysInitMemory(addr,size)
Initializes the address (A000E000h) and size (2000h) of the allocate-able
Kernel Memory region, and, seems to deallocate any memory handles which may
have been allocated via B(00h).<br/>

#### C(09h) - SysInitKernelVariables()
Zerofills all Kernel variables; which are usually at [00007460h..0000891Fh].<br/>
Note: During the boot process, the BIOS accidently overwrites the first opcode
of this function (by the last word of the A0h table), so, thereafter, this
function won't work anymore (nor would it be of any use).<br/>

#### C(12h) - InstallDevices(ttyflag)
Initializes the size and address of the File and Device Control Blocks (FCBs
and DCBs). Adds the TTY device by calling "KernelRedirect(ttyflag)", and the
CDROM and Memory Card devices by calling "AddCDROMDevice()" and
"AddMemCardDevice()".<br/>

#### C(1Ch) - AdjustA0Table()
Copies the B(32h..3Bh) and B(3Ch..3Fh) function addresses to A(00h..09h) and
A(3Bh..3Eh). Apparently Sony's compiler/linker can't insert the addresses in
the A0h table directly at compilation time, so this function is used to insert
them during execution of the boot code.<br/>



##   BIOS More Internal Functions
Below are mainly internally used device related subfunctions.<br/>

#### Internal Device Stuff
```
  A(5Bh) dev_tty_init()                                      ;PS2: SystemError
  A(5Ch) dev_tty_open(fcb,and unused:"path\name",accessmode) ;PS2: SystemError
  A(5Dh) dev_tty_in_out(fcb,cmd)                             ;PS2: SystemError
  A(5Eh) dev_tty_ioctl(fcb,cmd,arg)                          ;PS2: SystemError
  A(5Fh) dev_cd_open(fcb,"path\name",accessmode)
  A(60h) dev_cd_read(fcb,dst,len)
  A(61h) dev_cd_close(fcb)
  A(62h) dev_cd_firstfile(fcb,"path\name",direntry)
  A(63h) dev_cd_nextfile(fcb,direntry)
  A(64h) dev_cd_chdir(fcb,"path")
  A(65h) dev_card_open(fcb,"path\name",accessmode)
  A(66h) dev_card_read(fcb,dst,len)
  A(67h) dev_card_write(fcb,src,len)
  A(68h) dev_card_close(fcb)
  A(69h) dev_card_firstfile(fcb,"path\name",direntry)
  A(6Ah) dev_card_nextfile(fcb,direntry)
  A(6Bh) dev_card_erase(fcb,"path\name")
  A(6Ch) dev_card_undelete(fcb,"path\name")
  A(6Dh) dev_card_format(fcb)
  A(6Eh) dev_card_rename(fcb1,"path\name1",fcb2,"path\name2")
  A(6Fh) ?   ;card ;[r4+18h]=00000000h  ;card_clear_error(fcb) or so
  A(96h) AddCDROMDevice()
  A(97h) AddMemCardDevice()
  A(98h) AddDuartTtyDevice()   ;PS2: SystemError
  A(99h) add_nullcon_driver()
  B(47h) AddDrv(device_info)  ;subfunction for AddXxxDevice functions
  B(48h) DelDrv(device_name_lowercase)
  B(5Bh) ChangeClearPAD(int)   ;pad AND card (ie. used also for Card)
  C(15h) _cdevinput(circ,char)
  C(16h) _cdevscan()
  C(17h) _circgetc(circ)    ;uses r5 as garbage txt for _ioabort
  C(18h) _circputc(char,circ)
```

#### Device Names
Device Names are case-sensitive (usually lowercase, eg. "bu" for memory cards).
In filenames, the device name may be followed by a hexadecimal 32bit
non-case-sensitive port number (eg. "bu00:" for selecting the first memory card
slot). Accordingly, the device name should not end with a hexdigit (eg. "usb:"
would be treated as device "us" with port number 0Bh).<br/>
Standard device names are "cdrom:", "bu00:", "bu10:", "tty00:". Other,
nonstandard devices are:<br/>
```
  Castlevania is trying to access an unknown device named "sim:".
  Caetla (a firmware replacement for Cheat Devices) supports "pcdrv:" device.
```



##   BIOS PC File Server
#### DTL-H2000
Below BRK's are internally used in DTL-H2000 BIOS for two devices: "mwin:"
(Message Window) and "sim:" (CDROM Sim).<br/>

#### Caetla Blurb
Caetla (a firmware replacement for Cheat Devices) supports "pcdrv:" device, the
SN systems (=what?) device extension to access files on the drive of the pc.
This fileserver can be accessed by using the kernel functions, with the
"pcdrv:" device name prefix to the filenames or using the SN system calls.<br/>
The following SN system calls for the fileserver are provided. Accessed by
setting the registers and using the break command with the specified field.<br/>
The break functions have argument(s) in A1,A2,A3 (ie. unlike normal BIOS
functions not in A0,A1,A2), and TWO return values (in V0, and V1).<br/>

#### BRK(101h) - PCInit() - Inits the fileserver
No parameters.<br/>

#### BRK(102h) - PCCreat(filename, fileattributes) - Creates a new file on PC
```
  out: V0  0 = success, -1 = failure
       V1  file handle or error code if V0 is negative
```
Attributes Bits (standard MSDOS-style):<br/>
```
  bit0     Read only file (R)
  bit1     Hidden file    (H)
  bit2     System file    (S)
  bit3     Not used       (zero)
  bit4     Directory      (D)
  bit5     Archive file   (A)
  bit6-31  Not used       (zero)
```

#### BRK(103h) - PCOpen(filename, accessmode) - Opens a file on the PC
```
  out: V0  0 = success, -1 = failure
       V1  file handle or error code if V0 is negative
```

#### BRK(104h) - PCClose(filehandle) - Closes a file on the PC
```
  out: V0  0 = success, -1 = failure
       V1  0 = success, error code if V0 is negative
```

#### BRK(105h) - PCRead(filehandle, length, memory\_destination\_address)
```
  out: V0  0 = success, -1 = failure
       V1  number of read bytes or error code if V0 is negative.
```
Note: PCRead does not stop at EOF, so if you set more bytes to read than the
filelength, the fileserver will pad with zero bytes. If you are not sure of the
filelength obtain the filelength by PClSeek (A2=0, A3=2, V1 will return the
length of the file, don't forget to reset the file pointer to the start before
calling PCread!)<br/>

#### BRK(106h) - PCWrite(filehandle, length, memory\_source\_address)
```
  out: V0  0 = success, -1 = failure
       V1  number of written bytes or error code if V0 is negative.
```

#### BRK(107h) - PClSeek(filehandle, file\_offset, seekmode) - Change Filepos
seekmode may be from 0=Begin of file, 1=Current fpos, or 2=End of file.<br/>
```
  out: V0  0 = success, -1 = failure
       V1  file pointer
```



##   BIOS TTY Console (std\_io)
#### A(3Fh) - Printf(txt,param1,param2,etc.) - Print string to console
```
  in:  A0                     Pointer to 0 terminated string
       A1,A2,A3,[SP+10h..]    Argument(s)
```
Prints the specified string to the TTY console. Printf does internally use
"putchar" to output the separate characters (and expands char 09h and
0Ah accordingly).<br/>
The string can contain C-style escape codes (prefixed by "%" each):<br/>
```
  c         display ASCII character
  s         display ASCII string
  i,d,D     display signed Decimal number (d/i=default32bit, D=force32bit)
  u,U       display unsigned Decimal number (u=default32bit, U=force32bit)
  o,O       display unsigned Octal number (o=default32bit, O=force32bit)
  p,x,X     display unsigned Hex number (p=lower/force32bit, x=lower, X=upper)
  n         write 32bit/16bit string length to [parameter] (default32bit)
```
Additionally, following prefixes (inserted between "%" and escape code):<br/>
```
  + or SPC  show leading plus or space character in positive signed numbers
  NNN       fixed width (for padding or so) (first digit must be 1..9) (not 0)
  .NNN      fixed width (for clipping or so)
  *         variable width (using one of the parameters) (negative=ending_spc)
  .*        variable width
  -         force ending space padding (in case of width being specified)
  #         show leading "0x" or "0X" (hex), or ensure 1 leading zero (octal)
  0         show leading zero's
  L         unknown/no effect?
  h,l       force 16bit (h=halfword), or 32bit (l=long/word)
```
The force32bit codes (D,U,O,p,l) are kinda useless since the PSX defaults to
32bit parameters anyways. The force16bit code (h) may be useful as "%hn"
(writeback 16bit value), otherwise it's rather useless, unless signed 16bit
parameters have garbage in upper 16bit, for unsigned 16bit parameters it
doesn't work at all (accidently sign-expands 16bit to 32bit, and then displays
that signed 32bit value as giant unsigned value). Printf supports only octal,
decimal, and hex (but not binary).<br/>

#### A(3Eh) or B(3Fh) - puts(src) - Write string to TTY
```
  in: R4=address of string (terminated by 00h)
```
Like "printf", but doesn't resolve any "%" operands. Empty strings are handled
in a special way: If R4 points to a 00h character then nothing is output (as
one would expect it), but, if R4 is 00000000h then "\<NULL\>" is output
(only that six letters; without appending any CR or LF).<br/>

#### A(3Dh) or B(3Eh) - gets(dst) - Read string from TTY (keyboard input)
```
  in: r4=dst (pointer to a 128-byte buffer) - out: r2=dst (same is incoming r4)
```
Internally uses "getchar" to receive the separate characters (which are
thus masked by 7Fh). The received characters are stored in the buffer, and are
additionally sent back as echo to the TTY via std\_out\_putc.<br/>
The following characters are handled in a special way: 09h (TAB) is replaced by
a single SPC. 08h or 7FH (BS or DEL) are removing the last character from the
buffer (unless it is empty) and send 08h,20h,08h (BS,SPC,BS) to the TTY. 0Dh or
0Ah (CR or LF) do terminate the input (append 00h to the buffer, send 0Ah to
the TTY, which is expanded to 0Dh,0Ah by the std\_out\_putc function, and do then
return from the gets function).<br/>
The sequence 16h,NNh forces NNh to be stored in the buffer (even if NNh is a
special character like 00h..1Fh or 7Fh). If the buffer is full (circa max 125
chars, plus one extra byte for the ending 00h), or if an unknown control code
in range of 00h..1Fh is received without the 16h prefix, then 07h (BELL) is
sent to the TTY.<br/>

#### A(3Bh) or B(3Ch) - getchar() - Read character from TTY
Reads one character from the TTY console, by internally redirecting to
"read(0,tempbuf,1)". The returned character is ANDed by 7Fh (so, to read a
fully intact 8bit character, "read(0,tempbuf,1)" must be used instead of
this function).<br/>

#### A(3Ch) or B(3Dh) - putchar(char) - Write character to TTY
Writes the character to the TTY console, by internally redirecting to
"write(1,tempbuf,1)". Char 09h (TAB) is expanded to one or more SPC
characters, until reaching the next tabulation boundary (every 8 characters).
Char 0Ah (LF) is expanded to 0Dh,0Ah (CR,LF). Other special characters (which
should be handled at the remote terminal side) are 08h (BS, backspace, move
cursor one position to the left), and 07h (BELL, produce a short beep sound).<br/>

#### C(13h) - FlushStdInOutPut()
Closes and re-opens the std\_in (fd=0) and std\_out (fd=1) file handles.<br/>

#### C(1Bh) - KernelRedirect(ttyflag)  ;PS2: ttyflag=1 causes SystemError
Removes, re-mounts, and flushes the TTY device, the parameter selects whether
to mount the real DUART-TTY device (r4=1), or a Dummy-TTY device (r4=0), the
latter one sends any std\_out to nowhere. Values other than r4=0 or r4=1 do
remove the device, but do not re-mount it (which might result in problems).<br/>
Caution: Trying to use r4=1 on a PSX that does not has the DUART hardware
installed causes the BIOS to hang (so one should first detect the DUART
hardware, eg. by writing two different bytes to Port 1F802020h.1st/2nd access,
and the read and verify that two bytes).<br/>

#### Activating std\_io
The std\_io functions can be enabled via C(1Bh) KernelRedirect(ttyflag), the
BIOS is unable to detect the presence of the TTY hardware, by default the BIOS
bootcode disables std\_io by setting the initial KernelRedirect value at
[A000B9B0h] to zero, this is hardcoded shortly after the POST(E) output:<br/>
```
  call    output_post_r4        ;\output POST(E)
  +mov    r4,0Eh                ;/
  mov     r1,0A0010000h         ;\set [0A000B9B0h]=0 ;TTY=dummy/off
  call    reset_cont_d_3        ; and call reset_cont_d_3
  +mov    [r1-4650h],0          ;/
```
assuming that R28=A0010FF0h, the last 3 opcodes of above code can be replaced
by:<br/>
```
  mov     r1,1h                 ;\set [0A000B9B0h]=1 ;TTY=duart/on
  call    reset_cont_d_3        ; and call reset_cont_d_3
  +mov    [r28-4650h-0ff0h],r1  ;/
```
with that patch, the BIOS bootcode (and many games) are sending debug messages
to the debug terminal, via expansion port, see:<br/>
[EXP2 Dual Serial Port (for TTY Debug Terminal)](../expansion-port/SKILL.md#exp2-dual-serial-port-for-tty-debug-terminal)<br/>
Note: The nocash BIOS automatically detects the DUART hardware, and activates
TTY if it is present.<br/>

#### B(49h) - PrintInstalledDevices()
Uses printf to display the long and short names from the DCB of the currently
installed devices. Doesn't do anything else. There's no return value.<br/>

#### Note
Several BIOS functions are internally using printf to output status
information, timeout, and error messages, etc. So, trying to close the TTY file
handles (fd=0 and fd=1) would cause such functions to work unstable.<br/>



##   BIOS Character Sets
#### B(51h) - Krom2RawAdd(shiftjis\_code)
```
  In: r4  = 16bit Shift-JIS character code
  Out: r2 = address in BIOS ROM of the desired character (or -1 = error)
```
r4 should be 8140h..84BEh (charset 2), or 889Fh..9872h (charset 3).<br/>

#### B(53h) - Krom2Offset(shiftjis\_code)
```
  In: r4  = 16bit Shift-JIS character code
  Out: r2 = offset within charset (without charset base address)
```
This is a subfunction for B(51h) Krom2RawAdd(shiftjis\_code).<br/>

#### Character Sets in ROM (112Kbytes)
The character sets are located at BFC64000h and up, intermixed with some other
stuff:<br/>
```
  BFC64000h  Charset 1 (16x15 pix, letters with accent marks)    (NOT in JAPAN)
  BFC65CB6h  Garbage   (four-and-a-half reverb tables, ioports, printf strings)
  BFC66000h  Charset 2 (16x15 pix, various alphabets, english, greek, etc.)
  BFC69D68h  Charset 3 (16x15 pix, japanese or chinese symbols or so)
  BFC7F8DEh  Charset 4 (8x15 pix, mainly ASCII letters)
  BFC7FE6Fh  Charset 5 (8x15 pix, additional punctuation marks)    (NOT in PS2)
  BFC7FF32h  Version   (Version and Copyright strings)        (NOT in SCPH1000)
  BFC7FF8Ch  Charset 6 (8x15 pix, seven-and-a-half japanese chars) (NOT in PS2)
  BFC80000h  End       (End of 512kBYTE BIOS ROM)
```
Charset 1 (and Garbage) is NOT included in japanese BIOSes (in the SCPH1000
version that region contains uncompressed program code, in newer japanese
BIOSes that regions are zerofilled)<br/>
Charset 1 symbols are as defined in JIS-X-0212 char(2661h..2B77h), and EUC-JP
char(8FA6E1h..8FABF7h).<br/>
Version (and Copyright) string is NOT included in SCPH1000 version (that BIOS
includes further japanese 8x15 pix chars in that region).<br/>
For charset 2 and 3 it may be recommended to use the B(51h)
Krom2RawAdd(shiftjis\_code) to obtain the character addresses. Not sure if that
BIOS function (or another BIOS function) allows to retrieve charset 1, 4, 5,
and 6 addresses?<br/>
Charset 4 is halfwidth, single-byte Shift JIS codes 21h through 7Eh. This
matches ASCII except code 5Ch which is the halfwidth yen sign (¥) and 7Eh which
is overline (‾).<br/>
Charset 5 contains overhead/combining tilde, backslash (\\), broken bar (¦),
Shift JIS codes A1h through A5h and B0h, DEh, and DFh, left double quotation
mark (“), left single quotation mark (‘), and tilde (~).<br/>
Charset 6 is Shift JIS codes 82A5h through 82ACh, but in halfwidth, and the
last one is cut off.

##   BIOS Control Blocks
#### Exception Control Blocks (ExCB) (4 blocks of 8 bytes each)
```
  00h 4   ptr to first element of exception chain
  04h 4   not used (zero)
```

#### Event Control Blocks (EvCB) (usually 16 blocks of 1Ch bytes each)
```
  00h 4   class  (events are triggered when class and spec match)
  04h 4   status (0=free,1000h=disabled,2000h=enabled/busy,4000h=enabled/ready)
  08h 4   spec   (events are triggered when class and spec match)
  0Ch 4   mode   (1000h=execute function/stay busy, 2000h=no func/mark ready)
  10h 4   ptr to function to be executed when ready (or 0=none)
  14h 8   not used (uninitialized)
```

#### Thread Control Blocks (TCB) (usually 4 blocks of 0C0h bytes each)
```
  00h 4   status        (1000h=Free TCB, 4000h=Used TCB)
  04h 4   not used      (set to 1000h by OpenTh) (not for boot executable?)
  08h 80h r0..r31       (entries for r0/zero and r26/k0 are unused)
  88h 4   cop0r14/epc   (aka r26/k0 and pc when returning from exception)
  8Ch 8   hi,lo         (the mul/div registers)
  94h 4   cop0r12/sr    (stored/restored by exception, NOT init by OpenTh)
  98h 4   cop0r13/cause (stored when entering exception, NOT restored on exit)
  9Ch 24h not used      (uninitialized)
```

#### Process Control Block (1 block of 4 bytes)
```
  00h 4   ptr to TCB of current thread
```
The PSX supports only one process, and thus only one Process Control Block.<br/>

#### File Control Blocks (FCB) (16 blocks of 2Ch bytes each)
```
  00h 4  status (0=Free FCB) (nonzero=accessmode)
  04h 4  cdrom: disk_id (checksum across path table of the corresponding disk),
         memory card: port number (00h=slot1, 10h=slot2)
  08h 4  transfer address (for dev_in_out function)
  0Ch 4  transfer length  (for dev_in_out function)
  10h 4  current file position
  14h 4  device flags (copy of DCB[04h])
  18h 4  error  ;used by B(55h) - _get_error(fd)
  1Ch 4  Pointer to DCB for the file
  20h 4  filesize
  24h 4  logical block number (start of file) (for cdrom: at least)
  28h 4  file control block number (simply 0..15 for FCB number 0..15)
```

#### Device Control Blocks (DCB) (10 blocks of 50h bytes each)
```
  00h 4   ptr to lower-case short name ("cdrom", "bu", "tty") (or 0=Free DCB)
  04h 4   device flags (cdrom=14h, bu=14h, tty/dummy=1, tty/duart=3)
  08h 4   sector size  (cdrom=800h, bu=80h, tty=1)
  0Ch 4   ptr to upper-case long name  ("CD-ROM", "MEMORY CARD", "CONSOLE")
  10h 4   ptr to init()                                         (TTY only)
  14h 4   ptr to open(fcb,"path\name",accessmode)
  18h 4   ptr to in_out(fcb,cmd)                                (TTY only)
  1Ch 4   ptr to close(fcb)
  20h 4   ptr to ioctl(fcb,cmd,arg)                             (TTY only)
  24h 4   ptr to read(fcb,dst,len)
  28h 4   ptr to write(fcb,src,len)
  2Ch 4   ptr to erase(fcb,"path\name")
  30h 4   ptr to undelete(fcb,"path\name")
  34h 4   ptr to firstfile2(fcb,"path\name",direntry)
  38h 4   ptr to nextfile(fcb,direntry)
  3Ch 4   ptr to format(fcb)
  40h 4   ptr to cd(fcb,"path")                            (CDROM only)
  44h 4   ptr to rename(fcb1,"path\name1",fcb2,"path\name2")
  48h 4   ptr to remove()
  4Ch 4   ptr to testdevice(fcb,"path\name")
```



##   BIOS Versions
#### Kernel Versions
For the actual kernel, there seem to be only a few different versions. Most
PSX/PSone's are containing the version from 1995 (which is kept 1:1 the same in
all consoles; without any PAL/NTSC related customizations).<br/>
```
  28-Jul-1994  "DTL-H2000"                   ;v0.x (pre-retail devboard)
  22-Sep-1994  "CEX-1000 KT-3  by S.O."      ;v1.0 through v2.0
  no-new-date  "CEX-3000 KT-3  by K.S."      ;v2.1 only (old Port 1F801060h)
  27-Jul-1995  "Konami OS by T.H."           ;Twinkle System
  01-Sep-1995  "Konami OS by T.H."           ;Konami GV, GQ, System 573
  04-Dec-1995  "CEX-3000/1001/1002 by K.S."  ;v2.2 through v4.5 (except v4.0)
  29-May-1997  "CEX-7000/-7001 by K.S.    "  ;v4.0 only (new Port 1F801010h)
  17-Jan-2000  "PS compatible mode by M.T."  ;v5.0 (Playstation 2)
```
The date and version string can be retrieved via GetSystemInfo(index).<br/>
The "CEX-7000/-7001" version was only "temporarily" used (when the kernel/gui
grew too large they changed the ROM size from 512K to 1024K; but did then
figure out that they could use a self-decompressing GUI to squeeze everything
into 512K; but they did accidentally still use the 1024K setting) (newer
consoles fixed that and switched back to the old version from 1995) (aside from
the different date/version string, the only changed thing is the opcode at
BFC00000h, which initializes port 1F801010h to BIOS ROM size of 1MB, instead of
512KB; no idea if that BIOS does actually contain additional data?).<br/>
The "CEX-3000 KT-3" version is already almost same as "CEX-3000/1001/1002",
aside from version/date, the only differences are at offset BFC00014h..1Fh, and
BFC003E0h (both related to Port 1F801060h).<br/>

#### Bootmenu/Intro Versions
This portion was updated more often. It's customized for PAL/NTSC displays,
japanese/english language, and (maybe?) region/licence string checks. The
SCPH1000 uses uncompressed Bootmenu/Intro code with "\<S\>" intro, but
without "PS" intro (or, "PS" is shown only on region matches?), newer versions
are using selfdecompressing code, with both intro screens. The GUI in older PSX
models looks like a drawing program for children, the GUI in newer PSX models
and in PSone's looks more like a modernized bathroom furniture, unknown how the
PS2 GUI looks like?<br/>
Games are communicating only with the Kernel, so the differences in the
Bootmenu/Intro part should have little or effect on compatibility (although
some I/O ports might be initialized differently, and although some games might
(accidently) read different (garbage) values from the ROM).<br/>
```
  Ver  CRC32    Used in                      System ROM Version  Kernel
  0.xj 18D0F7D8 DTL-H2000                    (no version string) dtlh2000
  1.0j 3B601FC8 SCPH-1000 and DTL-H1000      (no version string) cex1000
  1.1j 3539DEF6 SCPH-3000 and DTL-H1000H     "1.1 01/22/95"      ""
  2.0a 55847D8C DTL-H1001                    "2.0 05/07/95 A"    ""
  2.0e 9BB87C4B SCPH-1002 and DTL-H1002      "2.0 05/10/95 E"    ""
  2.1j BC190209 SCPH-3500                    "2.1 07/17/95 J"    cex3000
  2.1a AFF00F2F SCPH-1001 and DTL-H1101      "2.1 07/17/95 A"    ""
  2.1e 86C30531 SCPH-1002 and DTL-H1102      "2.1 07/17/95 E"    ""
  2.2j 24FC7E17 SCPH-5000 and DTL-H1200      "2.2 12/04/95 J"    cex3000/100x
  2.2a 37157331 SCPH-1001 and DTL-H1201/3001 "2.2 12/04/95 A"    ""
  2.2e 1E26792F SCPH-1002 and DTL-H1202/3002 "2.2 12/04/95 E"    ""
  2.2v 446EC5B2 SCPH-5903 (VCD, 1Mbyte)      "2.2 12/04/95 J"    ""
  2.2d DECB22F5 DTL-H1100                    "2.2 03/06/96 D"    ""
  3.0j FF3EEB8C SCPH-5500                    "3.0 09/09/96 J"    ""
  3.0a 8D8CB7E4 SCPH-5501/7003               "3.0 11/18/96 A"    ""
  3.0e D786F0B9 SCPH-5502/5552               "3.0 01/06/97 E"    ""
  4.0j EC541CD0 SCPH-7000/9000               "4.0 08/18/97 J"    cex7000
  4.1w B7C43DAD SCPH-7000W                       ...XXX...
  4.1a 502224B6 SCPH-7001/7501/7503/9001     "4.1 12/16/97 A"    cex3000/100x
  4.1e 318178BF SCPH-7002/7502/9002          "4.1 12/16/97 E"    ""
  4.3j F2AF798B SCPH-100  (PSone)            "4.3 03/11/00 J"    ""
  4.4a 6A0E22A0 SCPH-101  (PSone)            "4.4 03/24/00 ..XXX..
  4.4e 0BAD7EA9 SCPH-102  (PSone)            "4.4 03/24/00 E"    ""
  4.5a 171BDCEC SCPH-101  (PSone)            "4.5 05/25/00 A"    ""
  4.5e 76B880E5 SCPH-102  (PSone)            "4.5 05/25/00 E"    ""
  5.0t B7EF81A9 SCPH10000 (Playstation 2)    "5.0 01/17/00 T"    PS compatible
```
The System ROM Version string can be found at BFC7FF32h (except in v1.0).<br/>

v2.2j/a/e use exactly the same GUI as v2.1 (only the kernel was changed). v2.2d
is almost same as v2.2j (but with some GUI patches or so).<br/>
v4.1 and v4.5 use exactly the same GUI code for "A" and "E" regions (the only
difference is the last byte of the version string; which does specify whether
the GUI shall use PAL or NTSC).<br/>
v5.0 is playstation 2 bios (4MB) with more or less backwards compatible kernel.<br/>

#### Character Set Versions
The 16x15 pixel charsets at BFC66000h and BFC69D68h are included in all BIOSes,
however, the 16x15 portion for letters with accent marks at BFC64000h is
included only in non-japanese BIOSes, and in some newer japanese BIOSes (not
included in v4.0j, but they are included in v4.3j).<br/>
The 8x15 pixel charset with characters 21h..7Fh is included in all BIOSes. In
the SCPH1000, this region is followed by additional 8x15 punctuation marks at
char 80h and up, however, this region is missing in PS2 BIOS. Moreover, some
BIOSes include an incomplete 8x15 japanese character set (which ends abruptly
at BF7FFFFFh), in newer BIOSes, some of theses chars are replaced by the
version string at BFC7FF32h, and, the remaining 8x15 japanese chars were
removed in the PS2 BIOS version.<br/>



##   BIOS Patches
The original PSX Kernel mainly consists of messy and unstable compiler
generated code, and, to the worst, the \<same\> author seems to have
attempted to use assembler code in some places. In result, most commercial
games are causing a greater mess by inserting patches in the kernel code...<br/>
Which has been a nasty surprise when making the nocash PSX bios; which
obviously wasn't compatible with these patches. The only solutions would have
been to insert hundreds of NOPs to make my bios \<exactly\> as bloated as
the original bios (which I really didn't want to do), or to create
anti-patch-patches.<br/>

#### Patches and Anti-Patch-Patches
As shown below, all known patches are invoked by a B(56h) or B(57h) function
call. In the nocash PSX bios, these two functions are examining the following
opcodes, if the opcodes are a known patch, then the BIOS reproduces the desired
behaviour, and does then continue normal execution after those opcodes. If the
opcodes are unknown, then the BIOS simply locks up; and shows an error message
with the address of that opcodes in the TTY window; info about any such unknown
opcodes would be welcome!<br/>

#### Compatibility
If you want to (or need to) use patches, please use byte-identical opcodes as
commercial games do (as shown below; only the "xxxx" address digits are don't
care), so the nocash PSX bios (or other homebrewn BIOSes) can detect and
reproduce them. Or alternately, don't use the BIOS, and access I/O ports
directly, which is much better and faster anyways.<br/>

#### patch\_missing\_cop0r13\_in\_exception\_handler:
In newer Kernel version, the exception handler reads cop0r13/cause to r2,
examines the Excode value in r2, and if the exception was caused by an
interrupt, and if the next opcode (at EPC) is a GTE/COP2 command, then it does
increment EPC by 4. The GTE commands are executed even if an interrupt occurs
simultaneously, so, without adjusting EPC, the command would be executed twice.
With some commands that'd just waste some clock cycles, with other commands it
may cause data to be written twice to the GTE FIFOs, or may re-use the result
from the 1st command execution as input to the 2nd execution.<br/>
The old "CEX-1000 KT-3" Kernel version did examine r2, but it "forgot" to
previously load cop0r13 to r2, so it did randomly examine a garbage value. The
patch inserts the missing opcode, used in elo2 at 80033740h, and in Pandemonium
II at 8007F3FCh:<br/>
```
  240A00B0 mov  r10,0B0h                      ;\   00000000 nop
  0140F809 call r10                           ;    00000000 nop
  24090056 +mov  r9,56h                       ;/   241A0100 mov k0,100h
  3C0Axxxx mov  r10,xxxx0000h                 ;\   8F5A0008 mov k0,[k0+8h]
  3C09xxxx mov  r9,xxxx0000h                  ;    00000000 nop
  8C420018 mov  r2,[r2+06h*4] ;=C(06h)        ;    8F5A0000 mov k0,[k0]
  254Axxxx add  r10,xxxxh ;=@@new_data        ;    00000000 nop
  2529xxxx add  r9,xxxxh  ;=@@new_data_end    ;/   235A0008 addt k0,8h
          @@copy_lop:                         ;\   AF410004 mov [k0+4h],r1
  8D430000 mov  r3,[r10]                      ;    AF420008 mov [k0+8h],r2
  254A0004 add  r10,4h                        ;    AF43000C mov [k0+0Ch],r3
  24420004 add  r2,4h                         ;    AF5F007C mov [k0+7Ch],ra
  1549FFFC jne  r10,r9,@@copy_lop             ;    40026800 mov r2,cop0r13
  AC43FFFC +mov [r2-4h],r3                    ;/   00000000 nop
```
Alternately, same as above, but using k0/k1 instead of r10/r9, used in Ridge
Racer at 80047B14h:<br/>
```
  240A00B0 mov  r10,0B0h                      ;\     00000000 nop
  0140F809 call r10                           ;      00000000 nop
  24090056 +mov r9,56h                        ;/     241A0100 mov  k0,100h
  3C1Axxxx mov  k0,xxxx0000h                  ;\     8F5A0008 mov  k0,[k0+8h]
  3C1Bxxxx mov  k1,xxxx0000h                  ;      00000000 nop
  8C420018 mov  r2,[r2+06h*4] ;=C(06h)        ;      8F5A0000 mov  k0,[k0]
  275Axxxx add  k0,xxxxh  ;=@@new_data        ;      00000000 nop
  277Bxxxx add  k1,xxxxh  ;=@@new_data_end    ;/     235A0008 addt k0,8h
          @@copy_lop:                         ;\     AF410004 mov  [k0+4h],r1
  8F430000 mov  r3,[k0]                       ;      AF420008 mov  [k0+8h],r2
  275A0004 add  k0,4h                         ;      AF43000C mov  [k0+0Ch],r3
  24420004 add  r2,4h                         ;      AF5F007C mov  [k0+7Ch],ra
  175BFFFC jne  k0,k1,@@copy_lop              ;      40026800 mov  r2,cop0r13
  AC43FFFC +mov [r2-4h],r3                    ;/     00000000 nop
```
Alternately, slightly different code used in metal\_gear\_solid at 80095CC0h, and
in alone1 at 800A3ECCh:<br/>
```
  24090056 mov  r9,56h                        ;\
  240A00B0 mov  r10,0B0h                      ; B(56h) GetC0Table
  0140F809 call r10                           ;
  00000000 +nop                               ;/
  8C420018 mov  r2,[r2+06h*4] ;=00000C80h = exception_handler = C(06h)
  00000000 nop
  24420028 add  r2,28h
  00407821 mov  r15,r2
  3C0Axxxx lui  r10,xxxxh ;\@@ori_data        ;\
  254Axxxx add  r10,xxxxh ;/                  ;
  3C09xxxx lui  r9,xxxxh  ;\@@ori_data_end    ; @@ori_data:
  2529xxxx add  r9,xxxxh  ;/                  ;  AF410004 mov [k0+4h],r1
          @@verify_lop:                       ;  AF420008 mov [k0+8h],r2
  8D430000 mov  r3,[r10]                      ;  AF43000C mov [k0+0Ch],r3
  8C4B0000 mov  r11,[r2]                      ;  AF5F007C mov [k0+7Ch],ra
  254A0004 add  r10,4h                        ;  40037000 mov r3,cop0r14
  146B000E jne  r3,r11,@@verify_mismatch      ;  00000000 nop
  24420004 +add r2,4h                         ;
  1549FFFA jne  r10,r9,@@verify_lop           ;
  00000000 +nop                               ;/
  01E01021 mov  r2,r15
  3C0Axxxx lui  r10,xxxxh ;\@@new_data        ;\
  254Axxxx add  r10,xxxxh ;/                  ;
  3C09xxxx lui  r9,xxxxh  ;\@@new_data_end    ; @@new_data:
  2529xxxx add  r9,xxxxh  ;/                  ;  AF410004 mov [k0+4h],r1
          @@copy_lop:                         ;  AF420008 mov [k0+8h],r2
  8D430000 mov  r3,[r10]                      ;  40026800 mov r2,cop0r13
  00000000 nop                                ;  AF43000C mov [k0+0Ch],r3
  AC430000 mov  [r2],r3                       ;  40037000 mov r3,cop0r14
  254A0004 add  r10,4h                        ;  AF5F007C mov [k0+7Ch],ra
  1549FFFB jne  r10,r9,@@copy_lop             ;
  24420004 +add r2,4h                         ;/
          @@verify_mismatch:
```
Alternately, a bugged/nonfunctional homebrew variant (used by Hitmen's
"minimum" demo):<br/>
```
  ;BUG1: 8bit "movb r6" should be 32bit "mov r6"
  ;BUG2: @@copy_lop should transfer 6 words (not 7 words)
  ;BUG3: and, asides, the minimum demo works only with PAL BIOS (not NTSC)
  0xxxxxxx call xxxxxxxxh               ;\B(56h) GetC0Table
  00000000 +nop                         ;/(mov r8,0B0h, jmp r8, +mov r9,56h)
  3C04xxxx mov  r4,xxxx0000h  ;\@@ori_data
  2484xxxx add  r4,xxxxh      ;/
  90460018 movb r6,[r2+06h*4] ;BUG1 ;exception_handler = C(06h)
  24870018 add  r7,r4,18h ;@@ori_end     ;\
  24C50028 add  r5,r6,28h ;C(06h)+28h    ;
  00A03021 mov  r6,r5                    ;                   @@ori_data:
          @@verify_lop:                  ;  80086520 AF410004 mov [k0+4h],r1
  8CA30000 mov  r3,[r5]                  ;  80086524 AF420008 mov [k0+8h],r2
  8C820000 mov  r2,[r4]                  ;  80086528 AF43000C mov [k0+0Ch],r3
  00000000 nop                           ;  8008652C AF5F007C mov [k0+7Ch],ra
  1462000C jne  r3,r2,@@verify_mismatch  ;  80086530 40037000 mov r3,cop0r14
  24840004 +add r4,4h                    ;  80086534 00000000 nop
  1487FFFA jne  r4,r7,@@verify_lop       ;                   @@ori_end:
  24A50004 +add r5,4h                    ;/
  00C02821 mov  r5,r6                    ;\                  @@new_data:
  3C04xxxx mov  r4,xxxx0000h ;\@@new_data;  80086538 AF410004 mov [k0+4h],r1
  2484xxxx add  r4,xxxxh     ;/          ;  8008653C AF420008 mov [k0+8h],r2
  2483001C add  r3,r4,1Ch ;@@bugged_end  ;  80086540 40026800 mov r2,cop0r13
          @@copy_lop:                    ;  80086544 AF43000C mov [k0+0Ch],r3
  8C820000 mov  r2,[r4]                  ;  80086548 40037000 mov r3,cop0r14
  24840004 add  r4,4h                    ;  8008654C AF5F007C mov [k0+7Ch],ra
  ACA20000 mov  [r5],r2                  ;                   @@new_end:
  1483FFFC jne  r4,r3,@@copy_lop         ;  80086550 00000000 nop  ;BUG2
  24A50004 +add r5,4h                    ;/                  @@bugged_end:
          @@verify_mismatch:
```

#### early\_card\_irq\_patch:
Because of a hardware glitch the card IRQ cannot be acknowledged while the
external IRQ signal is still LOW, making it neccessary to insert a delay that
waits until the signal gets HIGH before acknowledging the IRQ.<br/>
The original BIOS is so inefficient that it takes hundreds of clock cycles
between the interrupt request and the IRQ acknowledge, so, normally, it doesn't
require an additional delay.<br/>
However, the central mistake in the IRQ handler is that it doesn't memorize
which IRQ has originally triggered the interrupt. For example, it may get
triggered by a timer IRQ, but a newer card IRQ may occur during IRQ handling,
in that case, the card IRQ may get processed and acknowledged without the
required delay.<br/>
Used in Metal Gear Solid at 8009AA5Ch, and in alone1 at 800AE2F8h:<br/>
```
  24090056 mov  r9,56h    ;\                  ;        @@new_data:
  240A00B0 mov  r10,0B0h  ; B(56h) GetC0Table ;3C02A001 lui  r2,0A001h
  0140F809 call r10       ;                   ;2442DFAC sub  r2,2054h
  00000000 +nop           ;/                  ;00400008 jmp  r2 ;=@@new_cont_d
  8C420018 mov  r2,[r2+06h*4] ;\get C(06h)    ;00000000 +nop    ;=A000DFACh
  00000000 nop                ;/              ;00000000 nop
  8C430070 mov  r3,[r2+70h]   ;\              ;        @@new_data_end:
  00000000 nop                ; get           ;        @@new_cont_d:
  3069FFFF and  r9,r3,0FFFFh  ; early_card    ;8C621074 mov  r2,[r3+1074h]
  00094C00 shl  r9,10h        ; irq_handler   ;00000000 nop
  8C430074 mov  r3,[r2+74h]   ;               ;30420080 and  r2,80h ;I_STAT.7
  00000000 nop                ;               ;1040000B jz   r2,@@ret
  306AFFFF and  r10,r3,0FFFFh ;/              ;00000000 +nop
  012A1821 add  r3,r9,r10                     ;        @@wait_lop:
  24620028 add  r2,r3,28h ;=early+28h         ;8C621044 mov  r2,[r3+1044h]
  3C0Axxxx lui  r10,xxxxh ;\@@new_data        ;00000000 nop
  254Axxxx sub  r10,xxxxh ;/                  ;30420080 and  r2,80h ;JOY_STAT.7
  3C09xxxx lui  r9,xxxxh  ;\@@new_data_end    ;1440FFFC jnz  r2,@@wait_lop
  2529xxxx sub  r9,xxxxh  ;/                  ;00000000 +nop
          @@copy_lop:                         ;3C020001 lui  r2,0001h
  8D430000 mov  r3,[r10]                      ;8C42DFFC mov  r2,[r2-2004h]
  00000000 nop                                ;00000000 nop
  AC430000 mov  [r2],r3                       ;00400008 jmp  r2 ;=[0000DFFCh]
  254A0004 add  r10,4h                        ;00000000 +nop
  1549FFFB jne  r10,r9,@@copy_lop             ;        @@ret:
  24420004 +add r2,4h                         ;03E00008 ret
  3C010001 lui  r1,0001h      ;\[DFFCh]=r2    ;00000000 +nop
  0xxxxxxx call xxxxxxxxh     ; and call ...  ;
  AC22DFFC +mov [r1-2004h],r2 ;/              ;
```
Alternately, elo2 uses slightly different code at 8003961Ch:<br/>
```
  240A00B0 mov  r10,0B0h  ;\                  ;        @@new_data:
  0140F809 call r10       ; B(56h) GetC0Table ;3C02xxxx lui  r2,8xxxh
  24090056 +mov r9,56h    ;/                  ;2442xxxx sub  r2,xxxxh
  8C420018 mov  r2,[r2+06h*4] ;\get C(06h)    ;00400008 jmp  r2 ;=@@new_cont_d
  00000000 nop                ;/              ;00000000 +nop    ;=8xxxxxxxh
  8C430070 mov  r3,[r2+70h]   ;\              ;00000000 nop
  00000000 nop                ; get           ;        @@new_data_end:
  3069FFFF and  r9,r3,0FFFFh  ; early_card    ;        @@new_cont_d:
  8C430074 mov  r3,[r2+74h]   ; irq_handler   ;8C621074 mov  r2,[r3+1074h]
  00094C00 shl  r9,10h        ;               ;00000000 nop
  306AFFFF and  r10,r3,0FFFFh ;               ;30420080 and  r2,80h ;I_STAT.7
  012A1821 add  r3,r9,r10     ;/              ;1040000B jz   r2,@@ret
  3C0Axxxx mov  r10,xxxx0000h                 ;00000000 +nop
  3C09xxxx mov  r9,xxxx0000h                  ;        @@wait_lop:
  24620028 add  r2,r3,28h ;=early+28h         ;8C621044 mov  r2,[r3+1044h]
  254Axxxx sub  r10,xxxxh ;=@@new_data        ;00000000 nop
  2529xxxx sub  r9,xxxxh  ;=@@new_data_end    ;30420080 and  r2,80h ;JOY_STAT.7
          @@copy_lop:                         ;1440FFFC jnz  r2,@@wait_lop
  8D430000 mov  r3,[r10]                      ;00000000 +nop
  254A0004 add  r10,4h                        ;3C02xxxx lui  r2,8xxxh
  24420004 add  r2,4h                         ;8C42xxxx mov  r2,[r2-xxxxh]
  1549FFFC jne  r10,r9,@@copy_lop             ;00000000 nop
  AC43FFFC +mov [r2-4h],r3                    ;00400008 jmp  r2 ;=[8xxxxxxxh]
  3C018xxx mov  r1,8xxx0000h  ;\[...]=r2,     ;00000000 +nop
  0xxxxxxx call xxxxxxxxh     ; and call ...  ;        @@ret:
  AC22xxxx +mov [r1+xxxxh],r2 ;/              ;03E00008 ret
           ...                                ;00000000 +nop
```
Note: The above @@wait\_lop's should be more preferably done with timeouts (else
they may hang endless if a Sony Mouse is newly connected; the mouse does have
/ACK stuck LOW on power-up).<br/>

#### patch\_uninstall\_early\_card\_irq\_handler:
Used to uninstall the "early\_card\_irq\_vector" (the BIOS installs that vector
from inside of B(4Ah) InitCARD2(pad\_enable), and, without patches, the BIOS
doesn't allow to uninstall it thereafter).<br/>
Used in Breath of Fire III (SLES-01304) at 8017E790, and also in Ace Combat 2
(SLUS-00404) at 801D23F4:<br/>
```
  240A00B0 mov  r10,0B0h          ;\
  0140F809 call r10               ; B(56h) GetC0Table
  24090056 +mov r9,56h            ;/
  3C0Axxxx mov  r10,xxxx0000h
  3C09xxxx mov  r9,xxxx0000h
  8C420018 mov  r2,[r2+06h*4] ;=00000C80h = exception_handler = C(06h)
  254Axxxx add  r10,xxxxh ;@@new_data
  2529xxxx add  r9,xxxxh  ;@@new_data_end
          @@copy_lop:             ;\  @@new_data:
  8D430000 mov  r3,[r10]          ;    00000000 nop
  254A0004 add  r10,4h            ;    00000000 nop
  24420004 add  r2,4h             ;    00000000 nop
  1549FFFC jne  r10,r9,@@copy_lop ;   @@new_data_end:
  AC43006C +mov [r2+70h-4],r3     ;/
```
Alternately, more inefficient, used in Blaster Master-Blasting Again
(SLUS-01031) at 80063FF4h, and Raiden DX at 80029694h:<br/>
```
  24090056 mov  r9,56h            ;\
  240A00B0 mov  r10,0B0h          ; B(56h) GetC0Table
  0140F809 call r10               ;
  00000000 +nop                   ;/
  8C420018 mov  r2,[r2+06h*4] ;=00000C80h = exception_handler = C(06h)
  3C0Axxxx mov  r10,xxxx0000h ;\@@new_data
  254Axxxx add  r10,xxxxh     ;/
  3C09xxxx mov  r9,xxxx0000h  ;\@@new_data_end
  2529xxxx add  r9,xxxxh      ;/
          @@copy_lop:             ;\
  8D430000 mov  r3,[r10]          ;   @@new_data:
  00000000 nop                    ;    00000000 nop
  AC430070 mov  [r2+70h],r3       ;    00000000 nop
  254A0004 add  r10,4h  ;src      ;    00000000 nop
  1549FFFB jne  r10,r9,@@copy_lop ;   @@new_data_end:
  24420004 +add r2,4h   ;dst      ;/
```
Note: the above code is same as "patch\_install\_lightgun\_irq\_handler", except
that it writes to r2+70h, instead of r2+80h.<br/>

#### patch\_card\_specific\_delay:
Same purpose as the "early\_card\_irq\_patch" (but for the command/status bytes
rather than for the data bytes). The patch looks buggy since it inserts the
delay AFTER the acknowledge, but it DOES work (the BIOS accidently acknowledges
the IRQ twice; and the delay occurs PRIOR to 2nd acknowledge).<br/>
Used in Metal Gear Solid at 8009AAF0h, and in Legacy of Kain at 801A56D8h, and
in alone1 at 800AE38Ch:<br/>
```
  24090057 mov  r9,57h   ;\                   ;         @@new_data:
  240A00B0 mov  r10,0B0h ; B(57h) GetB0Table  ; 3C08A001 lui  r8,0A001h
  0140F809 call r10      ;/                   ; 2508DF80 sub  r8,2080h
  00000000 +nop                               ; 0100F809 call r8 ;=A000DF80h
  8C42016C mov  r2,[r2+5Bh*4] ;B(5Bh)         ; 00000000 +nop
  00000000 nop                                ; 00000000 nop
  8C4309C8 mov  r3,[r2+9C8h]  ;blah           ;         @@new_data_end:
  3C0Axxxx lui  r10,xxxxh ;\@@new_data        ; 946F000A movh r15,[r3+0Ah]
  254Axxxx sub  r10,xxxxh ;/                  ; 3C080000 mov  r8,0h
  3C09xxxx lui  r9,xxxxh  ;\@@new_data_end    ; 01E2C025 or   r24,r15,r2
  2529xxxx sub  r9,xxxxh  ;/                  ; 37190012 or   r25,r24,12h
          @@copy_lop:                         ; A479000A movh [r3+0Ah],r25
  8D480000 mov  r8,[r10]                      ; 24080028 mov  r8,28h
  00000000 nop                                ;         @@wait_lop:
  AC4809C8 mov  [r2+9C8h],r8   ;B(5Bh)+9C8h.. ; 2508FFFF sub  r8,1h
  254A0004 add  r10,4h                        ; 1500FFFE jnz  r8,@@wait_lop
  1549FFFB jne  r10,r9,@@copy_lop             ; 00000000 +nop
  24420004 +add r2,4h                         ; 03E00008 ret  ;above delay is
           ...                                ; 00000000 +nop ;in UNCACHED RAM
```
Alternately, slightly different code used in elo2 at800396D4h, and in Resident
Evil 2 at 800910E4h:<br/>
```
  240A00B0 mov  r10,0B0h ;\                   ;         @@swap_begin:
  0140F809 call r10      ; B(57h) GetB0Table  ; 3C088xxx lui  r8,8xxxh
  24090057 +mov r9,57h   ;/                   ; 2508xxxx sub  r8,xxxxh
  8C42016C mov  r2,[r2+5Bh*4] ;B(5Bh)         ; 0100F809 call r8 ;=8xxxxxxxh
  3C0Axxxx mov  r10,xxxx0000h                 ; 00000000 +nop
  3C09xxxx mov  r9,xxxx0000h                  ; 00000000 nop
  8C4309C8 mov  r3,[r2+9C8h] ;blah            ;         @@swap_end:
  254Axxxx sub  r10,xxxxh  ;=@@swap_begin     ;         ;- -  -
  2529xxxx sub  r9,xxxxh   ;=@@swap_end       ; 00000000 nop
          @@swap_lop:                         ; 240800C8 mov  r8,0C8h
  8C4309C8 mov  r3,[r2+9C8h] ;B(5Bh)+9C8h..   ;         @@wait_lop:
  8D480000 mov  r8,[r10]                      ; 2508FFFF sub  r8,1h
  254A0004 add  r10,4h                        ; 1500FFFE jnz  r8,@@wait_lop
  AD43FFFC mov  [r10-4h],r3                   ; 00000000 +nop
  24420004 add  r2,4h                         ; 03E00008 ret  ;above delay is
  1549FFFA jne  r10,r9,@@swap_lop             ; 00000000 +nop ;in CACHED RAM
  AC4809C4 +mov [r2+9C4h],r8                  ;
```

#### patch\_card\_info\_step4:
The "card\_info" function sends an incomplete read command to the card; in order
to receive status information. After receiving the last byte, the function does
accidently send a further byte to the card, so the card responds by another
byte (and another IRQ7), which is not processed nor acknowledged by the BIOS.
This patch kills the opcode that sends the extra byte.<br/>
Used in alone1 at 800AE214h:<br/>
```
  24090057 mov  r9,57h                        ;\
  240A00B0 mov  r10,0B0h                      ; B(57h) GetB0Table
  0140F809 call r10                           ;
  00000000 +nop                               ;/
  240A0009 mov  r10,9h        ;=blah
  8C42016C mov  r2,[r2+5Bh*4] ;=B(5Bh)
  00000000 nop
  20431988 addt r3,r2,1988h   ;=B(5Bh)+1988h  ;\store a NOP,
  0xxxxxxx call xxxxxxxxh                     ; and call ...
  AC600000 +mov [r3],0        ;=nop           ;/
```

#### patch\_pad\_error\_handling\_and\_get\_pad\_enable\_functions:
If a transmission error occurs (or if there's no controller connected), then
the Pad handler handler does usually issue a strange chip select signal to the
OTHER controller slot, and does then execute the bizarre\_pad\_delay function.
The patch below overwrites that behaviour by NOPs. Purpose of the original (and
patched) behaviour is unknown.<br/>
Used by Perfect Assassin at 800519D4h:<br/>
```
  240A00B0 mov  r10,0B0h                      ;\
  0140F809 call r10                           ; B(57h) GetB0Table
  24090057 +mov r9,57h                        ;/
  8C42016C mov  r2,[r2+5Bh*4] ;=B(5Bh)
  3C01xxxx mov  r1,xxxx0000h
  20430884 addt r3,r2,884h    ;B(5Bh)+884h
  AC23xxxx mov  [r1+xxxxh],r3 ;<--- SetPadEnableFlag()
  3C01xxxx mov  r1,xxxx0000h
  20430894 addt r3,r2,894h    ;B(5Bh)+894h
  2409000B mov  r9,0Bh        ;len
  AC23xxxx mov  [r1+xxxxh],r3 ;<--- ClearPadEnableFlag()
          @@fill_lop:                         ;\
  2529FFFF sub  r9,1h                         ;
  AC400594 mov  [r2+594h],0   ;B(5Bh)+594h..  ; erase error handling
  1520FFFD jnz  r9,@@fill_lop                 ;
  24420004 +add r2,4h                         ;/
```
Alternately, same as above, but with inefficient nops, used by Sporting Clays
at 8001B4B4h:<br/>
```
  24090057 mov  r9,57h       ;\
  240A00B0 mov  r10,0B0h     ; B(57h) GetB0Table
  0140F809 call r10          ;
  00000000 +nop              ;/
  8C42016C mov  r2,[r2+5Bh*4]
  2409000B mov  r9,0Bh ;len
  20430884 addt r3,r2,884h
  3C01xxxx mov  r1,xxxx0000h
  AC23xxxx mov  [r1+xxxxh],r3 ;<--- SetPadEnableFlag()
  20430894 addt r3,r2,894h
  3C01xxxx mov  r1,xxxx0000h
  AC23xxxx mov  [r1+xxxxh],r3 ;<--- ClearPadEnableFlag()
          @@fill_lop:         ;\
  AC400594 mov  [r2+594h],0   ;
  24420004 add  r2,4h         ; erase error handling
  2529FFFF sub  r9,1h         ;
  1520FFFC jnz  r9,@@fill_lop ;
  00000000 +nop               ;/
```
Alternately, same as above, but without getting PadEnable functions, used in
Pandemonium II (at 80083C94h and at 8010B77Ch):<br/>
```
  240A00B0 mov  r10,0B0h              ;\
  0140F809 call r10                   ; B(57h) GetB0Table
  24090057 +mov r9,57h                ;/
  8C42016C mov  r2,[r2+5Bh*4] ;=B(5Bh)
  2409000B mov  r9,0Bh        ;len            ;\
          @@fill_lop:                         ;
  2529FFFF sub  r9,1h                         ; erase error handling
  AC400594 mov  [r2+594h],0   ;B(5Bh)+594h..  ;
  1520FFFD jnz  r9,@@fill_lop                 ;
  24420004 +add r2,4h                         ;/
```

#### patch\_optional\_pad\_output:
The normal BIOS functions are only allowing to READ from the controllers, but
not to SEND data to them (which would be required to control Rumble motors, and
to auto-activate Analog mode without needing the user to press the Analog
button). Internally, the BIOS does include some code for sending data to the
controller, but it doesn't offer a function vector for setting up the data
source address, and, even if that would be supported, it clips the data bytes
to 00h or 01h. The patch below retrieves the required SetPadOutput function
address (in which only the src1/src2 addresses are relevant, the blah1/blah2
values aren't used), and suppresses clipping (ie. allows to send any bytes in
range 00h..FFh).<br/>
Used in Resident Evil 2 at 80091914h:<br/>
```
  240A00B0 mov  r10,0B0h                      ;\
  0140F809 call r10                           ; B(57h) GetB0Table
  24090057 +mov r9,57h                        ;/
  8C42016C mov  r2,[r2+5Bh*4] ;B(5Bh)
  3C0Axxxx mov  r10,xxxx0000h
  3C09xxxx mov  r9,xxxx0000h
  3C01xxxx mov  r1,xxxx0000h
  204307A0 addt r3,r2,7A0h    ;B(5Bh)+7A0h
  254Axxxx add  r10,xxxxh  ;=@@new_data
  2529xxxx add  r9,xxxxh   ;=@@new_data_end
  AC23xxxx mov  [r1-xxxxh],r3 ;<--- SetPadOutput(src1,blah1,src2,blah2)
          @@double_copy_lop:                  ;\
  8D430000 mov  r3,[r10]                      ;           @@new_data:
  254A0004 add  r10,4h                        ;   00551024 and     r2,r21
  AC4303D8 mov  [r2+3D8h],r3  ;<--- here      ;   00000000 nop
  24420004 add  r2,4h                         ;   00000000 nop
  1549FFFB jne  r10,r9,@@double_copy_lop      ;   00000000 nop
  AC4304DC +mov [r2+4DCh],r3  ;<--- here      ;/          @@new_data_end:
```
Alternately, more inefficient (with NOPs), used in Lemmings at 80036618h:<br/>
```
  24090057 mov  r9,57h                        ;\
  240A00B0 mov  r10,0B0h                      ; B(57h) GetB0Table
  0140F809 call r10                           ;
  00000000 +nop                               ;/
  3C0Axxxx mov  r10,xxxx0000h
  254Axxxx add  r10,xxxxh    ;=@@new_data
  3C09xxxx movp r9,xxxx0000h
  2529xxxx add  r9,xxxxh     ;=@@new_data_end
  8C42016C mov  r2,[r2+5Bh*4] ;B(5Bh)
  00000000 nop
  204307A0 addt r3,r2,7A0h    ;B(5Bh)+7A0h
  3C01xxxx mov  r1,xxxx0000h
  AC23xxxx mov  [r1+xxxxh],r3 ;<--- SetPadOutput(src1,blah1,src2,blah2)
          @@double_copy_lop:                  ;\
  8D430000 mov  r3,[r10]                      ;           @@new_data:
  00000000 nop                                ;   00551024 and     r2,r21
  AC4303D8 mov  [r2+3D8h],r3                  ;   00000000 nop
  AC4304E0 mov  [r2+4E0h],r3                  ;   00000000 nop
  24420004 add  r2,4h                         ;   00000000 nop
  254A0004 add  r10,4h                        ;           @@new_data_end:
  1549FFF9 jne  r10,r9,@@double_copy_lop      ;
  00000000 +nop                               ;/
```

#### patch\_no\_pad\_card\_auto\_ack:
This patch suppresses automatic IRQ0 (vblank) acknowleding in the Pad/Card IRQ
handler, that, even if auto-ack is enabled. Obviously, one could as well
disable auto-ack via B(5Bh) ChangeClearPAD(int), so this patch is total
nonsense. Used in Resident Evil 2 at 800919ACh:<br/>
```
  240A00B0 mov   r10,0B0h                      ;\
  0140F809 call  r10                           ; B(57h) GetB0Table
  24090057 +mov  r9,57h                        ;/
  8C42016C mov   r2,[r2+5Bh*4] ;=B(5Bh)
  240A0009 mov   r10,9h        ;len            ;\
  2043062C addt  r3,r2,62Ch    ;=B(5Bh)+62Ch   ;
          @@fill_lop:                          ;
  254AFFFF sub   r10,1h                        ;
  AC600000 mov   [r3],0                        ;
  1540FFFD jnz   r10,@@fill_lop                ;
  24630004 +add  r3,4h                         ;/
```
Alternately, same as above, but more inefficient, used in Sporting Clays at
8001B53Ch:<br/>
```
  24090057 mov   r9,57h                        ;\
  240A00B0 mov   r10,0B0h                      ; B(57h) GetB0Table
  0140F809 call  r10                           ;
  00000000 +nop                                ;/
  240A0009 mov   r10,9h    ;len
  8C42016C mov   r2,[r2+5Bh*4]
  00000000 nop
  2043062C addt  r3,r2,62Ch
          @@fill_lop:                          ;\
  AC600000 mov   [r3],0                        ;
  24630004 add   r3,4h                         ;
  254AFFFF sub   r10,1h                        ;
  1540FFFC jnz   r10,@@fill_lop                ;
  00000000 +nop                                ;/
```
Either way, no matter if using the patch or if using ChangeClearPAD(int),
having auto-ack disabled allows to install a custom vblank IRQ0 handler, which
is probably desired for most games, however, mind that the PSX BIOS doesn't
actually support the same IRQ to be processed by two different IRQ handlers,
eg. the custom handler may acknowledge the IRQ even when the Pad/Card handler
didn't process it, so pad input may become bumpy.<br/>

#### patch\_install\_lightgun\_irq\_handler:
Used in Sporting Clays at 80027D68h (when Konami Lightgun connected):<br/>
```
  240A00B0 mov  r10,0B0h     ;\
  0140F809 call r10          ; B(56h) GetC0Table
  24090056 +mov r9,56h       ;/
  3C0Axxxx mov  r10,xxxx0000h ;src
  3C09xxxx mov  r9,xxxx0000h  ;src.end
  8C420018 mov  r2,[r2+06h*4] ;C(06h)
  254Axxxx add  r10,xxxxh     ;src
  2529xxxx add  r9,xxxxh      ;src.end (=src+10h)
          @@copy_lop:              ;\    ;        @@src:
  8D430000 mov  r3,[r10]           ;     ;3C02xxxx mov  r2,xxxx0000h
  254A0004 add  r10,4h             ;     ;2442xxxx add  r2,xxxxh
  24420004 add  r2,4h              ;     ;0040F809 call r2  ;lightgun_proc
  1549FFFC jne  r10,r9,@@copy_lop  ;     ;00000000 +nop
  AC43007C +mov [r2+80h-4],r3      ;/             @@src_end:
```
Alternately, same as above, but more inefficient, used in DQM (Dragon Quest
Monsters 1&2) at 80089390h (install) and 800893F8h (uninstall):<br/>
```
  24090056 mov  r9,56h        ;\
  240A00B0 mov  r10,0B0h      ; B(56h) GetC0Table
  0140F809 call r10           ;
  00000000 +nop               ;/
  8C420018 mov  r2,[r2+06h*4] ;=00000C80h = exception_handler = C(06h)
  3C0Axxxx mov  r10,xxxx0000h ;\@@new_data (3xNOP)
  254Axxxx add  r10,-xxxxh    ;/
  3C09xxxx mov  r9,xxxx0000h  ;\@@new_data_end
  2529xxxx add  r9,-xxxxh     ;/
          @@copy_lop:             ;\
  8D430000 mov  r3,[r10]          ; @@new_data: ;for (un-)install...
  00000000 nop                    ; 00000000 nop / 3C02xxxx mov r2,xxxx0000h
  AC430080 mov  [r2+80h],r3       ; 00000000 nop / 2442xxxx add r2,-xxxxh
  254A0004 add  r10,4h            ; 00000000 nop / 0040F809 call r2  ;proc
  1549FFFB jne  r10,r9,@@copy_lop ; @@new_data_end:
  24420004 +add r2,4h             ;/
```
Some lightgun games (eg. Project Horned Owl) do (additionally to above stuff)
hook the exception vector at 00000080h, the hook copies the horizontal
coordinate (timer0) to a variable in RAM, thus getting the timer0 value
"closest" to the actual IRQ execution. Doing that may eliminate some
unpredictable timing offsets that could be caused by cache hits/misses during
later IRQ handling (and may also eliminate a rather irrelevant 1-cycle
inaccuracy depending on whether EPC was pointing to a GTE opcode, and also
eliminates constant cycle offsets depending on whether early\_card\_irq\_handler
was installed and enabled, and might eliminate timing differences for different
BIOS versions).<br/>

#### set\_conf\_without\_realloc:
Used in Spec Ops Airborne Commando at 80070AE8h, and also in the homebrew game
Roll Boss Rush at 80010B68h and 8001B85Ch. Purpose is unknown (maybe to
override improperly defined .EXE headers).<br/>
```
  8C030474 mov   r3,[200h+(9Dh*4)]      ;\get ptr to A(9Dh) GetConf (done so,
  00000000 nop                          ;/as there's no "GetA0Table" funtion)
  94620000 movh  r2,[r3+0h] ;lui msw    ;\
  84630004 movhs r3,[r3+4h] ;lw lsw+8   ; extract ptr to "boot_cnf_values"
  00021400 shl   r2,10h     ;msw*10000h ; (from first 2 opcodes of GetConf)
  2442FFF8 sub   r2,8h      ;undo +8    ;
  00431021 add   r2,r3      ;lsw        ;/
  AC450000 mov   [r2+0h],r5 ;num_TCB    ;\set num_EvCB,num_TCB,stacktop
  AC440004 mov   [r2+4h],r4 ;num_EvCB   ; (unlike A(9Ch) SetConf, without
  03E00008 ret                          ; actually reallocting anything)
  AC460008 +mov  [r2+8h],r6 ;stacktop   ;/
```

#### Cheat Devices
CAETLA detects the PSX BIOS version by checksumming BFC06000h..BFC07FFFh and
does then use some hardcoded BIOS addresses based on that checksum. The reason
for doing that is probably that the Pre-Boot Expansion ROM vector is called
with the normal A0h/B0h/C0h vectors being still uninitialized.<br/>
Problems are that the hardcoded addresses won't work with all BIOSes (eg. not
with the no$psx bios clone, probably also not with the newer PS2 BIOS),
moreover, the checksumming can fail with patched original BIOSes (eg. no$psx
allows to enable TTY debug messages and to skip the BIOS intro).<br/>
The Cheat Firmwares are probably also hooking the Vblank handler, and maybe
also some other functions.<br/>
ACTION REPLAY (at least later versions like 2.81) uses the Pre-Boot handler to
set a COP0 hardware breakpoint at 80030000h and does then resume normal BIOS
booting (which will then initialize important things like A0h/B0h/C0h tables,
and will then break when starting the GUI code at 80030000h).<br/>
XPLORER searches opcode 24040385h at BFC06000h and up, and does then place a
COP0 opcode fetch breakpoint at the opcode address+10h (note: this is within a
branch delay slot, which makes COP0 emulation twice as complicated). XPLORER
does also require space in unused BIOS RAM addresses (eg. Xplorer v3.20: addr
7880h at 1F002280h, addr 017Fh at 1F006A58h).<br/>

#### Note
Most games include two or three patches. The only game that I've seen so far
that does NOT use any patches is Wipeout 2097.<br/>
