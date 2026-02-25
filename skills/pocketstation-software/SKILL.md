---
name: pocketstation-software
description: "Pocketstation software: SWI function reference (misc, comms, execute, date/time, flash), BU protocol commands (standard memory card + Pocketstation extensions), file header/icon format, XBOO cable upload. Use when working with Pocketstation software, BIOS calls, or memory card protocol."
---

##   Pocketstation SWI Function Summary
#### SWI Function Summary
BIOS functions can be called via SWI opcodes (from both ARM and THUMB mode) (in
ARM mode, the SWI function number is in the lower 8bit of the 24bit field;
unlike as for example on the GBA, where it'd be in the upper 8bit). Parameters
(if any) are passed in r0,r1,r2. Return value is stored in r0 (all other
registers are left unchanged).<br/>
```
  SWI 00h - Reset()   ;don't use            out: everything destroyed
  SWI 01h - SetCallbacks(index,proc)        out: old proc
  SWI 02h - CustomSwi2(r0..r6,r8..r10)      out: r0
  SWI 03h - FlashWriteVirtual(sector,src)   out: 0=okay, 1=failed
  SWI 04h - SetCpuSpeed(speed)              out: old_speed
  SWI 05h - SenseAutoCom()                  out: garbage
  SWI 06h - GetPtrToComFlags()              out: ptr (usually 0C0h)
  SWI 07h - ChangeAutoDocking(flags.16-18)  out: incoming flags AND 70000h
  SWI 08h - PrepareExecute(flag,dir_index,param)  out: dir_index (new or old)
  SWI 09h - DoExecute(snapshot_saving_flag) out: r0=r0 (failed) or r0=param
  SWI 0Ah - FlashReadSerial()               out: F_SN
  SWI 0Bh - ClearComFlagsBit10()            out: new [ComFlags] (with bit10=0)
  SWI 0Ch - SetBcdDateTime(date,time)       out: garbage (RTC_DATE/10000h)
  SWI 0Dh - GetBcdDate()                    out: date (with century in MSBs)
  SWI 0Eh - GetBcdTime()                    out: time and day-of-week
  SWI 0Fh - FlashWriteSerial(serial_number) out: garbage (r0=0) ;old BIOS only!
  SWI 10h - FlashWritePhysical(sector,src)  out: 0=okay, 1=failed
  SWI 11h - SetComOnOff(flag)               out: garbage retadr to swi handler
  SWI 12h - TestSnapshot(dir_index)         out: 0=normal, 1=MCX1 with 1,0,"SE"
  SWI 13h - GetPtrToAlarmSetting()          out: ptr to alarm_setting
  SWI 14h - GetPtrToPtrToSwiTable()         out: ptr-to-ptr to swi_table
  SWI 15h - MakeAlternateDirIndex(flag,dir_index)  out: alt_dir_index (new/old)
  SWI 16h - GetDirIndex()                   out: dir_index (or alternate)
  SWI 17h - GetPtrToFunc3addr()             out: ptr to func3 address
  SWI 18h - FlashReadWhateverByte(sector)   out: [8000000h+sector*80h+7Eh]
  SWI 19h..FFh - garbage
  SWI 100h..FFFFFFh - mirrors of SWI 00h..FFh
```
The BIOS uses the same memory region for SWI and IRQ stacks, so both may not
occur simultaneously, otherwise one stack would be destroyed by the other
(normally that is no problem; IRQs are automatically disabled by the CPU during
SWI execution, SWIs aren't used from inside of default IRQ handlers, and SWIs
shouldn't be used from inside of hooked IRQ handlers).<br/>



##   Pocketstation SWI Misc Functions
#### SWI 01h - SetCallbacks(index,proc)
```
  r0=0  Set SWI 02h callback               (r1=proc, or r1=0=reset/default)
  r0=1  Set IRQ callback                   (r1=proc, or r1=0=none/default)
  r0=2  Set FIQ callback                   (r1=proc, or r1=0=none/default)
  r0=3  Set Download Notification callback (r1=proc, or r1=0=bugged/default)
```
All callbacks are called via BX opcodes (ie. proc.bit0 can be set for THUMB
code). SetCallbacks returns the old proc value (usually zero). The callbacks
are automatically reset to zero when (re-)starting an executable, or when
returning control to the GUI, so there's no need to restore the values by
software.<br/>

#### IRQ and FIQ Callbacks
Registers r0,r1,r12 are pushed by the kernels FIQ/IRQ handlers (so the
callbacks can use that registers without needing to push them). The FIQ handler
can additionally use r8..r11 without pushing them (the CPU uses a separate set
of r8..r12 registers in FIQ mode, nethertheless, the kernel DOES push r12 in
FIQ mode, without reason). Available stack is 70h bytes for the FIQ callback,
and 64h bytes for the IRQ callback.<br/>
The callbacks don't receive any incoming parameters, and don't need to respond
with a return value. The callback should return to the FIQ/IRQ handler (via
normal BX r14) (ie. it should not try to return to User mode).<br/>
The kernel IRQ handler does (after the IRQ callback) process IRQ-11 (IOP)
(which does mainly handle docking/undocking), and IRQ-9 (RTC) (which increments
the century if the year wrapped from 99h to 00h).<br/>
And the kernel FIQ handler does (before the FIQ callback) process IRQ-6 (COM)
(which does, if ComFlags.Bit9 is set, handle bu\_cmd's) (both IRQs and FIQs are
disabled, and the main program is stopped until the bu\_cmd finishes, or until a
joypad command is identified irrelevant, among others that means that
sound/timer IRQs aren't processed during that time, so audio output may become
distorted when docked).<br/>
When docked, the FIQ callback should consist of only a handful of opcodes, eg.
it may contain a simple noise, square wave generator, or software based sound
"DMA" function, but it should not contain more time-consuming code like sound
envelope processing; otherwise IRQ-6 (COM) cannot be executed fast enough to
handle incoming commands.<br/>

#### SWI 02h - CustomSwi2(r0..r6,r8..r10)      out: r0
Calls the SWI2 callback function (which can be set via SWI 01h). The default
callback address is 00000000h (so, by default, it behaves identically as SWI
00h). Any parameters can be passed in r0..r6 and r8..r10 (the other registers
aren't passed to the callback function). Return value can be stored in r0 (all
other registers are pushed/popped by the swi handler, as usually). Available
space on the swi stack is 38h bytes.<br/>
SWI2 can be useful to execute code in privileged mode (eg. to initialize FIQ
registers r8..r12 for a FIQ based sound engine) (which usually isn't possible
because the main program runs in non-privileged user mode).<br/>

#### SWI 04h - SetCpuSpeed(speed)              out: old\_speed
Changes the CPU speed. The BIOS uses it with values in range 01h..07h. Unknown
if value 00h can be also used? The function also handles values bigger than
07h, of which, some pieces of BIOS code look as if 08h would be the maximum
value...?<br/>
Before setting the new speed, the function sets F\_WAIT1 and F\_WAIT2 to
00000000h (or to 00000010h if speed.bit3=1). After changing the speed (by
writing the parameter to CLK\_MODE) it does wait until the new speed is applied
(by waiting for CLK\_MODE.bit4 to become zero). The function returns the old
value of CLK\_MODE, anded with 0Fh.<br/>



##   Pocketstation SWI Communication Functions
Communication (aka BU Commands, received from the PSX via the memory card slot)
can be handled by the pocketstations kernel even while a game is running.
However, communications are initially disabled when starting a game, so the
game should enable them via SWI 11h, and/or via calling SWI 05h once per frame.<br/>

#### SWI 11h - SetComOnOff(flag)
Can be used to enable/disable communication. When starting an executable,
communication is initially disabled, so it'd be a good idea to enable them
(otherwise the PSX cannot communicate with the Pocketstation while the game is
running).<br/>
When flag=0, disables communication: Intializes the COM\_registers, disables
IRQ-6 (COM), and clears ComFlags.9. When flag=1, enables communication:
Intializes the COM\_registers, enables IRQ-6 (COM), sets ComFlags.9 (when
docked), or clears Sys.Flags.9 (when undocked), and sets FAST cpu\_speed=7 (only
when docked). The function returns garbage (r0=retadr to swi\_handler).<br/>

#### SWI 06h - GetPtrToComFlags()
Returns a pointer to the ComFlags word in RAM, which contains several
communication related flags (which are either modified upon docking/undocking,
or upon receiving certain bu\_cmd's). The ComFlags word consists of the
following bits:<br/>
```
  0-3   Whatever (set/cleared when docked/undocked, and modified by bu_cmd's)
  4-7   Not used (should be zero)
  8     IRQ-11 (IOP) occurred  (set by irq handler, checked/cleared by SWI 05h)
  9     Communication Enabled And Docked (0=No, 1=Yes; prevents DoExecute)
  10    Reject writes to Broken Sector Region (sector 16..55)     (0=No, 1=Yes)
  11    Start file request (set by bu_cmd_59h, processed by GUI, not by Kernel)
  12-15 Not used (should be zero)
  16    Automatically power-down DAC audio on insert/removal      (0=No, 1=Yes)
  17    Automatically power-down IRDA infrared on insert/removal  (0=No, 1=Yes)
  18    Automatically adjust LCD screen rotate on insert/removal  (0=No, 1=Yes)
  19-27 Not used (should be zero)
  28    Indicates if a standard bu_cmd (52h/53h/57h) was received (0=No, 1=Yes)
  29    Set date/time request  (set by bu_cmd FUNC0, processed by BIOS)
  30    Destroy RTC and Start GUI request  (set by bu_cmd_59h, dir_index=FFFEh)
  31    Not used (should be zero)
```
Bit16-18 can be changed via SWI 07h, ChangeAutoDocking(flags). Bit10 can be
cleared by SWI 0Bh, ClearComFlagsBit10().<br/>

#### SWI 07h - ChangeAutoDocking(flags.16-18)
```
  0-15  Not used (should be zero)
  16    Automatically power-down DAC audio on insert/removal     (0=No, 1=Yes)
  17    Automatically power-down IRDA infrared on insert/removal (0=No, 1=Yes)
  18    Automatically adjust LCD screen rotate on insert/removal (0=No, 1=Yes)
  19-31 Not used (should be zero)
```
Copies bit16-18 of the incoming parameter to ComFlags.16-18, specifying how the
kernel IRQ-11 (IOP) handler shall process docking/undocking from the PSX
cartridge slot. The function returns the incoming flags value ANDed with
70000h.<br/>

#### SWI 0Bh - ClearComFlagsBit10()
Resets ComFlags.Bit10, ie. enables bu\_cmd\_57h (write\_sector) to write to the
Broken Sector region in FLASH memory (sector 16..55). SWI 0Bh returns the
current ComFlags value (the new value, with bit10=0).<br/>
Aside from calling SWI 0Bh, ComFlags.10 is also automatically cleared upon
IRQ-10 (IOP) (docking/undocking). ComFlags.10 can get set/cleared by the
Download Notification callback.<br/>

#### SWI 05h - SenseAutoCom()
Checks if docking/undocking has occurred (by examining ComFlags.8, which gets
set by the kernel IRQ-11 (IOP) handler). If that flag was set, then the
function does reset it, and does then reset FUNC3=0000h and [0CAh]=00h (both
only if docked, not when undocked), and, no matter if docked or undocked, it
enables communication; equivalent to SetComOnOff(1); which sets/clears
ComFlags.9. The function returns garbage (r0=whatever).<br/>
The GUI is calling SWI 05h once per frame. The overall purpose is unknown. It's
a good idea to reset FUNC3 and to Enable Communication (although that'd be
required only when docked, not when undocked), but SWI 05h is doing that only
on (un-)docking transitions (not when it was already docked). In general, it'd
make more sense to do proper initializations via SWI 11h and SWI 17h as than
trusting SWI 05h to do the job. The only possibly useful effect is that SWI 05h
does set/clear ComFlags.9 when docked/undocked.<br/>

#### SWI 17h - GetPtrToFunc3addr()
Returns a pointer to a halfword in RAM which contains the FUNC3 address (for
bu\_cmd\_5bh and bu\_cmd\_5ch). The address is only 16bit, originated at 02000000h
in FLASH (ie. it can be only in the first 64K of the file), bit0 can be set for
THUMB code. The default address is zero, which behaves bugged: It accidently
sets [00000004h]=00000000h, ie. replaces the Undefined Instruction exception
vector by a "andeq r0,r0,r0" opcode, due to that NOP-like opcode, any Undefined
Instruction exceptions will run into the SWI vector at [00000008h], and
randomly execute an SWI function; with some bad luck that may execute one of
the FlashWrite functions and destroy the saved files.<br/>
Although setting 0000h acts bugged, one should restore that setting before
returning control to GUI or other executables; otherwise the address would
still point to the FUNC3 address of the old unloaded executable, which is worse
than the bugged effect.<br/>
The FUNC3 address is automatically reset to 0000h when (if) SWI 05h
(SenseAutoCom) senses new docking.<br/>

#### Download Notification callback
Can be used to mute sound during communication, see SWI 01h,
SetCallbacks(index,proc), and BU Command 5Dh for details.<br/>



##   Pocketstation SWI Execute Functions
#### SWI 08h - PrepareExecute(flag,dir\_index,param)
dir\_index should be 0=GUI, or 1..15=First block of game. When calling
DoExecute, param is passed to the entrypoint of the game or GUI in r0 register
(see notes on GUI \<param\> values belows). For games, param may be
interpreted in whatever way.<br/>
When flag=0, the function simply returns the old dir\_index value. When flag=1,
the new dir\_index and param values are stored in Kernel RAM (for being used by
DoExecute); the values are stored only if dir\_index=0 (GUI), or if dir\_index
belongs to a file with "SC" and "MCX0" or "MCX1" IDs in it's title sector. If
dir\_index was accepted, then the new dir\_index value is returned, otherwise the
old dir\_index is returned.<br/>

#### GUI \<param\> values - for PrepareExecute(1,0,param)
PrepareExecute(1,0,param) prepares to execute the GUI (rather than a file).
When executing the GUI, \<param\> consists of the following destructive
bits:<br/>
```
  0-7  Command number (see below, MSBs=Primary command, LSBs=another dir_index)
  8    Do not store Alarm setting in Kernel RAM (0=Normal, 1=Don't store)
  9-31 Not used (should be zero)
```
The command numbers can be:<br/>
```
  Command 0xh --> Erase RTC time/date
  Command 1xh --> Enter GUI Time Screen with speaker symbol
  Command 20h --> Enter GUI Time Screen with alarm symbol
  Command 2xh --> Prompt for new Date/Time, then start dir_index (x)
  Command 3xh --> Enter GUI File Selection Screen, with dir_index (x) selected
  Command xxh --> Erase RTC time/date (same as Command 0xh)
```
For Command 2xh and 3xh, the lower 4bit of the command (x) must be a valid
dir\_index of the 1st block of a pocketstation executable, otherwise the BIOS
erases the RTC time/date. Bit8 is just a "funny" nag feature, allowing the user
to change the alarm setting, but with the changes being ignored (bit8 can be
actually useful in BU Command 59h, after FUNC2 was used for changing alarm).<br/>

#### SWI 09h - DoExecute(), or DoExecute(snapshot\_saving\_flag) for MCX1
Allows to return control to the GUI (when dir\_index=0), or to start an
executable (when dir\_index=1..15). Prior to calling DoExecute, parameters
should be set via PrepareExecute(1,dir\_index,param), when not doing that,
DoExecute would simply restart the current executable (which may be a desired
effect in some cases).<br/>
The "snapshot\_saving\_flag" can be ommited for normal (MCX0) files, that
parameter is used only for special (MCX1) files (see Snapshot Notes for
details).<br/>
Caution: DoExecute fails (and returns r0=unchanged) when ComFlags.9=1 (which
indicates that communications are enabled, and that the Pocketstation is
believed to be docked to the PSX). ComFlags.9 can be forcefully cleared by
calling SetComOnOff(0), or it can be updated according to the current
docking-state by calling SetComOnOff(1) or SenseAutoCom().<br/>

#### SWI 16h - GetDirIndex()
Returns the dir\_index for the currently executed file. If that value is zero,
ie. if there is no file executed, ie. if the function is called by the GUI,
then it does instead return the "alternate" dir\_index (as set via SWI 15h).<br/>

#### SWI 15h - MakeAlternateDirIndex(flag,dir\_index)  out: alt\_dir\_index (new/old)
Applies the specified dir\_index as "alternate" dir\_index (for being retrieved
via SWI 16h for whatever purpose). The dir\_index is applied only when flag=1,
and only if dir\_index is 0=none, or if it is equal to the dir\_index of the
currently executed file (ie. attempts to make other files being the "alternate"
one are rejected). If successful, the new dir\_index is returned, otherwise the
old dir\_index is returned (eg. if flag=0, or if the index was rejected).<br/>

#### SWI 12h - TestSnapshot(dir\_index)
Tests if the specified file contains a load-able snapshot, ie. if it does have
the "SC" and "MCX1" IDs in the title sector, and the 01h,00h,"SE" ID in the
snapshot header. If so, it returns r0=1, and otherwise returns r0=0.<br/>

#### Snapshot Notes (MCX1 Files)
Snapshots are somewhat automatically loaded/saved when calling DoExecute:<br/>
If the old file (the currently executed file) contains "SC" AND "MCX1" IDs in
the title sector, then the User Mode CPU registers and User RAM at 200h..7FFh
are automatically saved in the files snapshot region in FLASH memory, with the
snapshot\_saving\_flag being applied as bit0 of the 0xh,00h,"SE" ID of the
snapshot header).<br/>
If the new file (specified in dir\_index) contains load-able snapshot data (ie.
if it has "SC" and "MCX1" IDs in title sector, and 01h,00h,"SE" ID in the
snapshot region), then the BIOS starts the saved snapshot data (instead of
restarting the executable at its entrypoint). Not too sure if that feature is
really working... the snapshot loader seems to load User RAM from the wrong
sectors... and it seems to jump directly to User Mode return address... without
removing registers that are still stored on SWI stack... causing the SWI stack
to underflow after loading one or two snapshots...?<br/>



##   Pocketstation SWI Date/Time/Alarm Functions
#### SWI 0Ch - SetBcdDateTime(date,time)
Sets the time and date, the parameters are having the same format as SWI 0Dh
and SWI 0Eh return values (see there). The SWI 0Ch return value contains only
garbage (r0=RTC\_DATE/10000h).<br/>

#### SWI 0Dh - GetBcdDate()
```
  0-7   Day     (01h..31h, BCD)
  8-11  Month   (01h..12h, BCD)
  16-31 Year    (0000h..9999h, BCD)
```
Returns the current date, the lower 24bit are read from RTC\_DATE, the century
in upper 8bit is read from Kernel RAM.<br/>

#### SWI 0Eh - GetBcdTime()
```
  0-7   Seconds     (00h..59h, BCD)
  8-15  Minutes     (00h..59h, BCD)
  16-23 Hours       (00h..23h, BCD)
  24-31 Day of week (1=Sunday, ..., 7=Saturday)
```
Returns the current time and day of week, read from RTC\_TIME.<br/>

#### SWI 13h - GetPtrToAlarmSetting()
Returns a pointer to a 64bit value in Kernel RAM, the upper word (Bit32-63)
isn't actually used by the BIOS, except that, the bu\_cmd FUNC3 does transfer
the whole 64bits. The meaning of the separate bits is:<br/>
```
  0-7   Alarm Minute    (00h..59h, BCD)
  8-15  Alarm Hour      (00h..23h, BCD)
  16    Alarm Enable    (0=Off, 1=On)
  17    Button Lock     (0=Normal, 1=Lock) (pressing all 5 buttons in GUI)
  18-19 Volume Shift    (0=Normal/Loud, 1=Medium/Div4, 2=Mute/Off)
  20-22 Not used        (should be zero)
  23    RTC Initialized (0=Not yet, 1=Yes, was initialized from within GUI)
  24-31 Not used        (should be zero)
  32-63 Pointer to 8x8 BIOS Charset (characters "0"..."9" plus strange symbols)
```
The RTC hardware doesn't have a hardware-based alarm feature, instead, the
alarm values must be compared with the current time by software. Alarm is
handled only by the GUI portion of the BIOS. The Kernel doesn't do any alarm
handling, so alarm won't occur while a game is executed (unless the game
contains code that handles alarm).<br/>
Games are usually using only the lower 16bit of the charset address, ORed with
04000000h (although the full 32bit is stored in RAM).<br/>
```
  CHR(00h..09h) = Digits "0..9"
  CHR(0Ah) = Space " "
  CHR(0Bh) = Colon ":"
  CHR(0Ch) = Button Lock (used by Final Fantasy 8's Chocobo World)
  CHR(0Dh) = Speaker Medium; or loud if followed by chr(0Eh)
  CHR(0Eh) = Speaker Loud; to be appended to chr(0Dh)
  CHR(0Fh) = Speaker Off
  CHR(10h) = Battery Low (used by PocketMuuMuu's Cars)
  CHR(11h) = Alarm Off
  CHR(12h) = Alarm On
  CHR(13h) = Memory Card symbol
```



##   Pocketstation SWI Flash Functions
#### SWI 10h - FlashWritePhysical(sector,src)
Writes 80h-bytes at src to the physical sector number (0..3FFh, originated at
08000000h), and does then compare the written data with the source data.
Returns 0=okay, or 1=failed.<br/>

#### SWI 03h - FlashWriteVirtual(sector,src)
The sector number (0..3FFh) is a virtual sector number (originated at
02000000h), the function uses the F\_BANK\_VAL settings to translate it to a
physical sector number, and does then write the 80h-bytes at src to that
location (via the FlashWritePhysical function). Returns 0=okay, or 1=failed (if
the write failed, or if the sector number exceeded the filesize aka the
virtually mapped memory region).<br/>

#### SWI 0Ah - FlashReadSerial()
Returns the 32bit value from the two 16bit F\_SN registers (see F\_SN for
details).<br/>

#### SWI 0Fh - FlashWriteSerial(serial\_number)    ;old BIOS only!
Changes the 32bit F\_SN value in the "header" region of the FLASH memory. The
function also rewrites the F\_CAL value (but it simply rewrites the old value,
so it's left unchanged). The function isn't used by the BIOS, no idea if it is
used by any games. No return value (always returns r0=0).<br/>
This function is supported by the old "061" version BIOS only (the function is
padded with jump opcodes which hang the CPU in endless loops on newer "110"
version).<br/>

#### SWI 18h - FlashReadWhateverByte(sector)
Returns [8000000h+sector\*80h+7Eh] AND 00FFh. Purpose is totally unknown... the
actual FLASH memory doesn't contain any relevant information at that locations
(eg. the in the directory sectors, that byte is unused, usually zero)... and,
reading some kind of status or manufacturer information would first require to
command the hardware to output that info...?<br/>



##   Pocketstation SWI Useless Functions
#### SWI 00h - Reset()   ;don't use, destroys RTC settings
Reboots the pocketstation, similar as when pressing the Reset button. Don't
use! The BIOS bootcode does (without any good reason) reset the RTC registers
and alarm/century settings in RAM to Time 00:00:00, Date 01 Jan 1999, and Alarm
00:00 disabled, so, after reset, the user would need to re-enter these values.<br/>
Aside from the annoying destroyed RTC settings, the function is rather
unstable: it does jump to address 00000000h in RAM, which should usually
redirect to 04000000h in ROM, however, most pocketstation games are programmed
in C language, where "pointer" is usually pronounced "pointer?" without much
understanding of whether/why/how to initialize that "strange things", so
there's a good probability that one of the recently executed games has
accidently destroyed the reset vector at [00000000h] in battery-backed RAM.<br/>

#### SWI 14h - GetPtrToPtrToSwiTable()
Returns a pointer to a word in RAM, which contains another pointer which
usually points to SWI table in ROM. Changing that word could be (not very)
useful for setting up a custom SWI table in FLASH or in RAM. When doing that,
one must restore the original setting before returning control to the GUI or to
another executable (the setting isn't automatically restored).<br/>

#### SWI service routine
The default SWI service routine is slightly finicky<br/>
```arm
push {r1-r12, lr} @ Backup SVC-mode registers
mrs r12, spsr     @ Old CPSR in r12
nop

@ Check if we were previously in Thumb mode
@ And adjust LR accordingly to fetch the SWI comment field
tst r12, #0x20
subeq lr, #2
sub lr, #2

@ Fetch the comment field
ldrh r12, [lr]
and r12, #0xFF

@ Load function pointer for SWI handler and call it
mov lr, #0xE0 ; Pointer to SWI table in LR
ldr r11, [lr]
add r11, r11, r12, lsl #2 @ r11 = &swi_table[comment]
ldr r11, [r11] @ Get function pointer
mov lr, pc     @ Set LR to return address
bx r11         @ Call SWI handler

@ Restore SVC regs, return from SWI service routine and restore SPSR into CPSR
pop {r1-r12, pc}^
```
It's important that the SWI service routine use a 16-bit load to fetch the comment field, as most memory on the Pocketstation can't be safely read using `ldrb`. Any custom handler needs to do the same, otherwise it won't work on real hardware. Also, for emulator developers, be wary of the last `pop` as it abuses an ldm edge case (S bit set with r15 in rlist - restores registers properly and then does CPSR = SPSR)<br/>

##   Pocketstation BU Command Summary
The Pocketstation supports the standard Memory Card commands (Read Sector,
Write Sector, Get Info), plus a couple of special commands.<br/>

#### BU Command Summary
```
  50h  Change a FUNC 03h related value or so
  51h  N/A
  52h  Standard Read Sector command
  53h  Standard Get ID command
  54h  N/A
  55h  N/A
  56h  N/A
  57h  Standard Write Sector command
  58h  Get an ID or Version value or so
  59h  Prepare File Execution with Dir_index, and Parameter
  5Ah  Get Dir_index, ComFlags, F_SN, Date, and Time
  5Bh  Execute Function and transfer data from Pocketstation to PSX
  5Ch  Execute Function and transfer data from PSX to Pocketstation
  5Dh  Execute Custom Download Notification Function   ;via SWI 01h with r0=3
  5Eh  Get-and-Send ComFlags.bit1,3,2
  5Fh  Get-and-Send ComFlags.bit0
```
Commands 5Bh and 5Ch can use the following functions:<br/>
```
  FUNC 00h - Get or Set Date/Time
  FUNC 01h - Get or Set Memory Block
  FUNC 02h - Get or Set Alarm/Flags
  FUNC 03h - Custom Function 3              ;via SWI 17h, GetPtrToFunc3addr()
  FUNC 80h..FFh - Custom Functions 80h..FFh ;via Function Table in File Header
```



##   Pocketstation BU Standard Memory Card Commands
For general info on the three standard memory card commands (52h, 53h, 57h),
and for info on the FLAG response value, see:<br/>
[Memory Card Read/Write Commands](controllersandmemorycards.md#memory-card-readwrite-commands)<br/>

#### BU Command 52h (Read Sector)
Works much as on normal memory cards, except that, on the Pocketstation, the
Read Sector command return 00h as dummy values; instead of the "(pre)" dummies
that occur on normal memory cards.<br/>
The Read Sector command does reproduce the strange delay (that occurs between
5Ch and 5Dh bytes), similar as on normal original Sony memory cards, maybe
original cards did (maybe) actually DO something during that delay period, the
pocketstation BIOS simply blows up time in a wait loop (maybe for compatibility
with original cards).<br/>

#### BU Command 53h (Get ID)
The Get ID command (53h) returns exactly the same values as normal original
Sony memory cards.<br/>

#### BU Command 57h (Write Sector)
The Write Sector command has two new error codes (additonally to the normal
47h="G"=Good, 4Eh="N"=BadChecksum, FFh=BadSector responses). The new error
codes are (see below for details):<br/>
```
  FDh Reject write to Directory Entries of currently executed file
  FEh Reject write to write-protected Broken Sector region (sector 16..55)
```
And, like Read Sector, it returns 00h instead of "(pre)" as dummy values.<br/>

#### Write Error Code FDh (Directory Entries of currently executed file)
The FDh error code is intended to prevent the PSX bootmenu (or other PSX games)
to delete the currently executed file (which would crash the pocketstation -
once when the deleted region gets overwritten by a new file), because the PSX
bootmenu and normal PSX games do not recognize the new FDh error code the
pocketstation does additionally set FLAG.3 (new card), which should be
understood by all PSX programs.<br/>
The FDh error code occurs only on directory sectors of the file (not on its
data blocks). However, other PSX games should never modify files that belong to
other games (so there should be no compatibility problem with other PSX
programs that aren't aware of the file being containing currently executed
code).<br/>
However, the game that has created the executable pocketstation file must be
aware of that situation. If the file is broken into a Pocketstation Executable
region and a PSX Gameposition region, then it may modify the Gameposition stuff
even while the Executable is running. If the PSX want to overwrite the
executable then it must first ensure that it isn't executed (eg. by retrieving
the dir\_index of the currently executed file via BU Command 5Ah, and comparing
it against the first block number in the files FCB at the PSX side; for file
handle "fd", the first block is found at "[104h]+fd\*2Ch+24h" in PSX memory).<br/>

#### Write Error Code FEh (write-protected Broken Sector region, sector 16..55)
The write-protection is enabled by ComFlags.bit10 (which can be set/cleared via
BU Command 5Dh). That bit should be set before writing Pocketstation
excecutables (the Virtual Memory banking granularity is 2000h bytes, which
allows to map whole blocks only, but cannot map single sectors, which would be
required for files with broken sector replacements).<br/>
Unlike Error FDh, this error code doesn't set FLAG.3 for notifying normal PSX
programs about the error (which is no problem since normally Error FEh should
never occur since ComFlags.10 is usually zero). For more info on ComFlags.10,
see SWI 0Bh aka ClearComFlagsBit10(), and BU Command 5Dh.<br/>



##   Pocketstation BU Basic Pocketstation Commands
#### BU Command 50h (Change a FUNC 03h related value or so)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  50h  FLAG  Send Command 50h
  VAL  00h   Send new [0CAh], receive length of following data (00h)
```
Might be somehow related to FUNC 03h...?<br/>

#### BU Command 58h (Get an ID or Version value or so)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  58h  FLAG  Send Command 58h
  (0)  02h   Send dummy/zero, receive length of following data (02h)
  (0)  01h   Send dummy/zero, receive whatever value           (01h)
  (0)  01h   Send dummy/zero, receive another value            (01h)
```

#### BU Command 59h (Prepare File Execution with Dir\_index, and Parameter)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  59h  FLAG  Send Command 59h
  (0)  06h   Send dummy/zero, receive length of following data (06h)
  NEW  OLD   Send new dir_index.8-15, receive old dir_index.8-15
  NEW  OLD   Send new dir_index.0-7, receive old dir_index.0-7
  PAR  (0)   Send exec_parameter.0-7, receive dummy/zero
  PAR  (0)   Send exec_parameter.8-15, receive dummy/zero
  PAR  (0)   Send exec_parameter.16-23, receive dummy/zero
  PAR  (0)   Send exec_parameter.24-31, receive dummy/zero
```
The new dir\_index can be the following:<br/>
```
  0000h..000Fh --> Request to Start GUI or File (with above parameter bits)
  0010h..FFFDh --> Not used, acts same as FFFFh (see below)
  FFFEh --> Request to Destroy RTC and Start GUI (with parameter 00000000h)
  FFFFh --> Do nothing (transfer all bytes, but don't store the new values)
```
Upon dir\_index=0000h (Start GUI) or 0001..000Fh (start file), a request flag in
ComFlags.11 is set, the GUI does handle that request, but the Kernel doesn't
handle it (so it must be handled in the game; ie. check ComFlags.11 in your
mainloop, and call DoExecute when that bit is set, there's no need to call
PrepareExecute, since that was already done by the BU Command).<br/>
Caution: When dir\_index=0000h, then \<param\> should be a value that does
NOT erase the RTC time/date (eg. 10h or 20h) (most other values do erase the
RTC, see SWI 08h for details).<br/>
Upon dir\_index=FFFEh, a similar request flag is set in ComFlags.30, and, the
Kernel (not the GUI) does handle that request in its FIQ handler (however, the
request is: To reset the RTC time/date and to start the GUI with uninitialized
irq/svc stack pointers, so this unpleasant and bugged feature shouldn't ever be
used). Finally, dir\_index=FFFFh allows to read the current dir\_index value
(which could be also read via BU Command 5Ah).<br/>

#### BU Command 5Ah (Get Dir\_index, ComFlags, F\_SN, Date, and Time)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  5Ah  FLAG  Send Command 5Ah
  (0)  12h   Send dummy/zero, receive length of following data (12h)
  (0)  INDX  Send dummy/zero, receive curr_dir_index.bit8-15   (00h)
  (0)  INDX  Send dummy/zero, receive curr_dir_index.bit0-7    (00h..0Fh)
  (0)  FLG   Send dummy/zero, receive ComFlags.bit0            (00h or 01h)
  (0)  FLG   Send dummy/zero, receive ComFlags.bit1            (00h or 01h)
  (0)  FLG   Send dummy/zero, receive ComFlags.bit3            (00h or 01h)
  (0)  FLG   Send dummy/zero, receive ComFlags.bit2            (00h or 01h)
  (0)  SN    Send dummy/zero, receive F_SN.bit0-7              (whatever)
  (0)  SN    Send dummy/zero, receive F_SN.bit8-15             (whatever)
  (0)  SN    Send dummy/zero, receive F_SN.bit16-23            (whatever)
  (0)  SN    Send dummy/zero, receive F_SN.bit24-31            (whatever)
  (0)  DATE  Send dummy/zero, receive BCD Day                  (01h..31h)
  (0)  DATE  Send dummy/zero, receive BCD Month                (01h..12h)
  (0)  DATE  Send dummy/zero, receive BCD Year                 (00h..99h)
  (0)  DATE  Send dummy/zero, receive BCD Century              (00h..99h)
  (0)  TIME  Send dummy/zero, receive BCD Second               (00h..59h)
  (0)  TIME  Send dummy/zero, receive BCD Minute               (00h..59h)
  (0)  TIME  Send dummy/zero, receive BCD Hour                 (00h..23h)
  (0)  TIME  Send dummy/zero, receive BCD Day of Week          (01h..07h)
```
At midnight, the function may accidently return the date for the old day, and
the time for the new day.<br/>

#### BU Command 5Eh (Get-and-Send ComFlags.bit1,3,2)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  5Eh  FLAG  Send Command 5Eh
  (0)  03h   Send dummy/zero, receive length of following data (03h)
  NEW  OLD   Send new ComFlags.bit1, receive old ComFlags.bit1 (00h or 01h)
  NEW  OLD   Send new ComFlags.bit3, receive old ComFlags.bit3 (00h or 01h)
  NEW  OLD   Send new ComFlags.bit2, receive old ComFlags.bit2 (00h or 01h)
```

#### BU Command 5Fh (Get-and-Send ComFlags.bit0)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  5Fh  FLAG  Send Command 5Fh
  (0)  01h   Send dummy/zero, receive length of following data (01h)
  NEW  OLD   Send new ComFlags.bit0, receive old ComFlags.bit0 (00h or 01h)
```



##   Pocketstation BU Custom Pocketstation Commands
#### BU Command 5Bh (Execute Function and transfer data from Pocketstation to PSX)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  5Bh  FLAG  Send Command 5Bh
  FUNC FFh   Send Function Number, receive FFh (indicating variable length)
  (0)  LEN1  Send dummy/zero, receive length of parameters (depending on FUNC)
  ...  (0)   Send parameters (LEN1 bytes), and receive dummy/zero
   <-------- at this point, the function is executed for the first time
  (0)  LEN2  Send dummy/zero, receive length of data (depending on FUNC)
  (0)  ...   Send dummy/zero, receive data (LEN2 bytes) from pocketstation
  (0)  FFh   Send dummy/zero, receive FFh
   <-------- at this point, the function is executed for the second time
```
See below for more info on the FUNC value and the corresponding functions.<br/>

#### BU Command 5Ch (Execute Function and transfer data from PSX to Pocketstation)
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  5Ch  FLAG  Send Command 5Ch
  FUNC FFh   Send Function Number, receive FFh (indicating variable length)
  (0)  LEN1  Send dummy/zero, receive length of parameters (depending on FUNC)
  ...  (0)   Send parameters (LEN1 bytes), and receive dummy/zero
   <-------- at this point, the function is executed for the first time
  (0)  LEN2  Send dummy/zero, receive length of data (depending on FUNC)
  ...  (0)   Send data (LEN2 bytes) to pocketstation, receive dummy/zero
  (0)  FFh   Send dummy/zero, receive FFh
   <-------- at this point, the function is executed for the second time
```
See below for more info on the FUNC value and the corresponding functions.<br/>

#### BU Command 5Dh (Execute Custom Download Notification Function)
Can be used to notify the GUI (or games that do support this function) about
following "download" operations (or uploads or other BU commands).<br/>
BU commands are handled inside of the kernels FIQ handler, that means both IRQs
and FIQs are disabled during a BU command transmission, so any IRQ or FIQ based
audio frequency generators will freeze during BU commands. To avoid distorted
noise, it's best to disable sound for the duration specified in bit0-7. If the
PSX finishes before the originally specified duration has expired, then it can
resend this command with bit8=1 to notify the pocketstation that the "download"
has completed.<br/>
```
  Send Reply Comment
  81h  N/A   Memory Card Access
  5Dh  FLAG  Send Command 5Dh
  (0)  03h   Send dummy/zero, receive length of following data (03h)
  VAL  (0)   Send receive value.16-23 (whatever), receive dummy/zero
  VAL  (0)   Send receive value.8-15 (download flags), receive dummy/zero
  VAL  (0)   Send receive value.0-7 (download duration), receive dummy/zero
```
The Download Notification callback address can be set via SWI 01h,
SetCallbacks(3,proc), see there for details. At kernel side, the function
execution is like so:<br/>
```
  If value.8-15 = 00h, then ComFlags.bit10=1, else ComFlags.bit10=0.
  If download_callback<>0 then call download_callback with r0=value.0-23.
```
In the GUI, the bu\_cmd\_5dh\_hook/callback handles parameter bits as so (and
games should probably handle that bits in the same fashion, too):<br/>
```
  bit0-7  download duration   (in whatever units... 30Hz, RTC, seconds...?)
  bit8    download finished   (0=no, 1=yes, cancel any old/busy duration)
  bit9-23 not used by gui
```
If PSX games send any of the standard commands (52h,53h,57h) to access the
memory card without using command 5Dh, then GUI automatically sets the duration
to 01h (and pauses sound only for that short duration).<br/>

#### FUNC 00h - Get or Set Date/Time (FUNC0)
LEN1 is 00h (no parameters), and LEN2 is 08h (eight data bytes):<br/>
```
  DATE  Get or Send BCD Day         (01h..31h)
  DATE  Get or Send BCD Month       (01h..12h)
  DATE  Get or Send BCD Year        (00h..99h)
  DATE  Get or Send BCD Century     (00h..99h)
  TIME  Get or Send BCD Second      (00h..59h)
  TIME  Get or Send BCD Minute      (00h..59h)
  TIME  Get or Send BCD Hour        (00h..23h)
  TIME  Get or Send BCD Day of Week (01h..07h)
```
At midnight, the function may accidently return the date for the old day, and
the time for the new day.<br/>

#### FUNC 01h - Get or Set Memory Block (FUNC1)
LEN1 is 05h (five parameters bytes):<br/>
```
  ADDR  Send Pocketstation Memory Address.bit0-7
  ADDR  Send Pocketstation Memory Address.bit8-15
  ADDR  Send Pocketstation Memory Address.bit16-23
  ADDR  Send Pocketstation Memory Address.bit24-31
  LEN2  Send Desired Data Length (00h..80h, automatically clipped to max=80h)
```
LEN2 is variable (using the 5th byte of the above parameters):<br/>
```
  ...   Get or Send LEN2 Data byte(s), max 80h bytes
```
Can be used to write to RAM (and eventually also to I/O ports; when you know
what you are doing). In the read direction it can read almost anything: RAM,
BIOS ROM, I/O Ports, Physical and Virtual FLASH memory. Of which, trying to
read unmapped Virtual FLASH does probably (?) cause a Data Abort exception (and
crash the Pocketstation), so that region may be read only if a file is loaded
(check that dir\_index isn't zero, via BU Command 5Ah, and, take care not to
exceed the filesize of that file).<br/>
BUG: When sending more than 2 data bytes in the PSX-to-Pocketstation direction,
then ADDR must be word-aligned (the BIOS tries to handle odd destination
addresses, but when doing that, it messes up the alignment of another internal
pointer).<br/>

#### FUNC 02h - Get or Set Alarm/Flags (FUNC2)
LEN1 is 00h (no parameters), and LEN2 is 08h (eight data bytes):<br/>
```
  DATA  Get or Send Alarm.bit0-7,   Alarm Minute    (00h..59h, BCD)
  DATA  Get or Send Alarm.bit8-15,  Alarm Hour      (00h..23h, BCD)
  DATA  Get or Send Alarm.bit16-23, Flags, see SWI 13h, GetPtrToAlarmSetting()
  DATA  Get or Send Alarm.bit24-31, Not used (usually 00h)
  DATA  Get or Send Alarm.bit32-39, BIOS Charset Address.0-7
  DATA  Get or Send Alarm.bit40-47, BIOS Charset Address.8-15
  DATA  Get or Send Alarm.bit48-55, BIOS Charset Address.16-23
  DATA  Get or Send Alarm.bit56-63, BIOS Charset Address.24-31
```
Changing the alarm value while the GUI is running works only with some
trickery: For a sinister reason, the GUI copies the alarm setting to User RAM
when it gets started, that copy isn't affected by FUNC2, so the GUI believes
that the old alarm setting does still apply (and writes that old values back to
Kernel RAM when leaving the GUI). The only workaround is:<br/>
Test if the GUI is running, if so, restart it via Command 59h (with
dir\_index=0, and param=0120h or similar, ie. with param.bit8 set), then execute
FUNC2, then restart the GUI again (this time with param.bit8 zero).<br/>

#### FUNC 03h - Custom Function 3 (aka FUNC3)
LEN1 is 04h (fixed) (four parameters bytes):<br/>
```
  VAL   Send Parameter Value.bit0-7
  VAL   Send Parameter Value.bit8-15
  VAL   Send Parameter Value.bit16-23
  VAL   Send Parameter Value.bit24-31
```
LEN2 is variable (depends on the return value of the 1st function call):<br/>
```
  ...   Get or Send LEN2 Data byte(s)
```
The function address can be set via SWI 17h, GetPtrToFunc3addr(), see there for
details.<br/>
Before using FUNC 03h one must somehow ensure that the desired file is loaded
(and that it does have initialized the function address via SWI 17h, otherwise
the pocketstation would crash).<br/>
The FUNC3 address is automatically reset to 0000h when (if) SWI 05h
(SenseAutoCom) senses new docking.<br/>
Note: The POC-XBOO circuit uses FUNC3 to transfer TTY debug messages.<br/>

#### FUNC 80h..FFh - Custom Function 80h..FFh
LEN1 is variable (depends on the LEN1 value in Function Table in File Header):<br/>
```
  ...   Send LEN1 Parameter Value(s), max 80h bytes (destroys Kernel when >80h)
```
LEN2 is variable (depends on the return value of the 1st function call):<br/>
```
  ...   Get or Send LEN2 Data byte(s), max 80h bytes (clipped to max=80h)
```
The function addresses (and LEN1 values) are stored in the Function Table FLASH
memory (see Pocketstation File Header for details).<br/>
```
      ;above LEN1 should be 00h..80h (the parameters are stored
      ;in a 80h-byte buffer in kernel RAM, so len LEN1=81h..FFh would
      ;destroy the kernel RAM that is located after that buffer)
```
Before using FUNC 80h..FFh one must somehow ensure that the desired file is
loaded (ie. that the function table with the desired functions is mapped to
flash memory; otherwise the pocketstation would crash).<br/>

#### First Function Call (Pre-Data)
Incoming parameters on 1st Function Call:<br/>
```
  r0=flags (09h=Pre-Data to PSX, or 0Ah=Pre-Data from PSX)
  r1=pointer to parameter buffer (which contains LEN1 bytes) (in Kernel RAM)
```
Return Value on 1st Function Call:<br/>
```
  r0 = Pointer to 64bit memory location (or r0=00000000h=Failed)
```
That 64bits are:<br/>
```
  0-31    BUF2 address of data buffer (src/dst)
  32-63   LEN2 (00000000h..00000080h) (clipped to max 00000080h if bigger)
```
dst is written in 8bit units<br/>
src is read in 16bit units (and then split to 8bit units)<br/>

#### Second Function Call (Post-Data)
Incoming parameters on 2nd Function Call:<br/>
```
  r0=flags (11h=Post-Data to PSX, 12h=Post-Data from PSX; plus 04h if Bad-Data)
  r1=pointer to data buffer (which contains LEN2 bytes) (BUF2 address)
```
Return Value on 2nd Function Call:<br/>
```
  There's no return value required on 2nd call (although the kernel
  functions seem to return the same stuff as on 1st call).
```

#### Function flags (r0)
For each function, there is only one single function vector which is called for
both To- and From-PSX, and both Pre- and Post-Data, and also on errors. The
function must decipher the flags in r0 to figure out which of that operations
it should handle:<br/>
```
  0    To-PSX   (when used by Command 5Bh)
  1    From-PSX (when used by Command 5Ch)
  2    Error occurred during Data transfer
  3    Pre-Data
  4    Post-Data
  5-31 Not used (zero)
```
There are only six possible flags combinations:<br/>
```
  09h Pre-Data to PSX
  0Ah Pre-Data from PSX
  11h Post-Data to PSX
  12h Post-Data from PSX
  15h Post-Bad-Data to PSX
  16h Post-Bad-Data from PSX
```
The kernel doesn't call FUNC 03h if the Error bit is set (ie. Post-Bad-Data
needs to be handled only by FUNC 80h..FFh, not by FUNC 03h.)<br/>



##   Pocketstation File Header/Icons
#### Pocketstation File Content
Pocketstation files consists of the following elements (in that order):<br/>
```
  PSX Title Sector              ;80h bytes
  PSX Colored Icon(s)           ;(hdr[02h] AND 0Fh)*80h bytes
  Pocketstation Saved Snapshot  ;800h bytes if hdr[52h]="MCX1", else 0 bytes
  Pocketstation Function Table  ;(hdr[57h]*8+7Fh) AND NOT 7Fh bytes
  Pocketstation File Viewer Mono Icon     ;hdr[50h]*80h bytes
  Pocketstation Executable Mono Icon List ;hdr[56h]*8 bytes
  Body (Pocketstation Executable Code/Data, PSX Game Position, Exec-Icons)
```
The Title sector contains some information about the size of the above regions,
but not about their addresses (ie. to find a given region, one must compute the
size of the preceeding regions).<br/>

#### Special "P" Filename in Directory Sector
For pocketstation executables, the 7th byte of the filename must be a "P" (for
other files that location does usually contain a "-", assuming the file uses a
standard filename, eg. "BESLES-12345abcdefgh" for a Sony licensed european
title).<br/>

#### Special Pocketstation Entries in the Title Sector at [50h..5Fh]
```
  50h 2  Number of File Viewer Mono Icon Frames (or 0000h=Use Exec-Icons)
  52h 4  Pocketstation Identifier ("MCX0"=Normal, "MCX1"=With Snapshot)
  56h 1  Number of entries in Executable Mono Icon List (01h..FFh)
  57h 1  Number of BU Command 5Bh/5Ch Get/Set Functions (00h..7Fh, usually 00h)
  58h 4  Reserved (zero)
  5Ch 4  Entrypoint in FLASH1 (ie. Fileoffset plus 02000000h) (bit0=THUMB)
```
In normal PSX files, the region at 50h..5Fh is usually zerofilled. For more
info on the standard entries in the Title Sector (and for info on Directory
Entries), see:<br/>
[Memory Card Data Format](controllersandmemorycards.md#memory-card-data-format)<br/>

#### Snapshot Region (in "MCX1" Files only)
For a load-able snapshot the Snapshot ID must be 01h,00h,"SE", the Kernel uses
snapshots only once (after loading a snapshot, it forcefully changes the ID to
00h,00h,"SE" in FLASH memory).<br/>
```
  000h  r1..r12 (ie. without r0)
  030h  r13_usr (sp_usr)
  034h  r14_usr (lr_usr)
  038h  r15     (pc)
  03Ch  psr_fc
  040h  Snapshot ID (0xh,00h,"SE")
  044h  unused (3Ch bytes)
  200h  Copy of user RAM at 200h..7FFh
```
For MCX1 files, snapshots can be automatically loaded and saved via the SWI
09h, DoExecute function (the snapshot handling seems to be bugged though; see
SWI 09h for details).<br/>

#### Function Table (FUNC 80h..FFh)
The table can contain 00h..7Fh entries, for FUNC 80h..FFh. Each entry occupies
8 bytes:<br/>
```
  00h 4   LEN1 (00000000h..00000080h) (destroys Kernel RAM if bigger)
  04h 4   Function Address (bit0 can be set for THUMB code)
```
If the number of table entries isn't a multiple of 10h, then the table should
be zero-padded to a multiple of 80h bytes (the following File Viewer Mono Icon
data is located on the next higher 80h-byte boundary after the Function Table).<br/>
For details see BU Commands 5Bh and 5Ch.<br/>

#### File Viewer Mono Icon
Animation Length (0001h..any number) (icon frames) is stored in hdr[50h], for
the File Viewer Icon, the Animation Delay is fixed (six 30Hz units per frame).<br/>
The File Viewer Icon is shown in the Directory Viewer (which is activated when
holding the Down-button pressed for some seconds in the GUI screen with the
speaker and memory card symbols, and which shows icons for all files, including
regular PSX game positions, whose colored icons are converted without any
contrast optimizations to unidentify-able dithered monochrome icons). If the
animation length of the File Viewer Icon is 0000h, then the Directory Viewer
does instead display the first Executable Mono Icon.<br/>
Each icon frame is 32x32 pixels with 1bit color depth (32 words, =128 bytes),<br/>
```
  1st word = top-most scanline, 31st word = bottom-most scanline
  bit0 = left-most pixel, bit31 = right-most pixel (0=white, 1=black)
```
A normal icon occupies 80h bytes, animated icons have more than one frame and
do occupy N\*80h bytes.<br/>

#### Executable Mono Icon List
The number of entries in the Executable Mono Icon List is specified in hdr[56h]
(usually 01h). Each entry in the Icon List occupies 8 bytes:<br/>
```
  00h 2  Animation Length (0001h..any number) (icon frames)
  02h 2  Animation Delay (N 30Hz units per icon frame)
  04h 4  Address of icon frame(s) in Virtual FLASH (at 02000000h and up)
```
The icon frame(s) can be anywhere on a word-aligned location in the file Body
(as specified in the above Address entry), the format of the frame(s) is the
same as for File Viewer Mono Icons (see there).<br/>
The Executable Icons are shown in the Executable File Selection Menu (which
occurs when pressing Left/Right buttons in the GUI). Pressing Fire button in
that menu starts the selected executable. If the Icon List has more than 1
entry, then pressing Up/Down buttons moves to the previous/next entry (this
just allows to view the corresponding icons, but doesn't have any other
purpose, namely, the current list index is NOT passed to the game when starting
it).<br/>
The Executable Mono Icon List is usually zero-padded to 80h-bytes size
(although that isn't actually required, the following file Body could start at
any location).<br/>

#### Entrypoint
The whole file (including the header and icons) gets mapped to 02000000h and
up. The entrypoint can be anywhere in the file Body, and it gets called with a
parameter value in r0 (when started by the GUI, that parameter is always zero,
but it may be nonzero when the executable was started by a game, ie. the
\<param\> from SWI 08h, PrepareExecute, or the \<param\> from BU
Command 59h).<br/>
Caution: Games (and GUI) are started with the ARM CPU running in Non-privileged
User Mode (however, there are several ways to hook IRQ/FIQ handlers, and from
there one can switch to Privileged System Mode).<br/>

#### Returning to the GUI
Games should always include a way to return to the GUI (eg. an option in the
game over screen, a key combination, a watchdog timer, and/or the docking
signal) (conventionally, games should prompt Exit/Continue when holding Fire
pressed for 5 seconds), otherwise it wouldn't be possible to start other games
- except by pushing the Reset button (which is no good idea since the bizarre
BIOS reset handler does reset the RTC time for whatever reason).<br/>
The kernel doesn't pass any return address to the entrypoint (neither in R14,
nor on stack). To return control to the GUI, use SWI functions
PrepareExecute(1,0,GetDirIndex()+30h), and then DoExecute(0).<br/>



##   Pocketstation File Images
Pocketstation files are normally stored in standard Memory Card images,<br/>
[Memory Card Images](controllersandmemorycards.md#memory-card-images)<br/>

#### Pocketstation specific files
Aside from that standard formats, there are two Pocketstation specific formats,
the "SC" and "SN" variants. Both contain only the raw file, without any
Directory sectors, and thus not including a "BESLESP12345"-style filename
string. The absence of the filename means that a PSX game couldn't (re-)open
these files via filenames, so they are suitable only for "standalone"
pocketstation games.<br/>

#### Pocketstation .BIN Files ("SC" variant)
Contains the raw Pocketstation Executable (ie. starting with the "SC" bytes in
the title sector, followed by icons, etc.), the filesize should be padded to a
2000h-byte block boundary.<br/>

#### Pocketstation .BIN Files ("SN" variant)
This is a strange incomplete .BIN file variant which starts with a 4-byte ID
("SN",00h,00h), which is directly followed by executable code, without any
title sector, and without any icons.<br/>
```
  It seems as if the file (including the 4-byte ID) is intended to be
  mapped to address 02000000h, and that the entrypoint is fixed at
  02000004h (in ARM state).
  Since the File doesn't have a valid file header with "SC" and "MCXn" IDs,
  it won't be recognized by real hardware, the PSX BIOS would treat it as
  a corrupted/deleted file, the Pocketstation BIOS would treat it as a
  non-executable file.
  So, that fileformat is apparently working only on whatever emulators,
  apparently on the one developed by SN Systems.
  If one should want to use that files on real hardware, one could add
  a 2000h byte stub at the begin of the file; with valid headers, and
  with a small executable that remaps the "SN" stuff to 02000000h via
  the F_BANK_VAL registers.
  Ah, and the "SN" files seem to access RAM at 01000000h and up, unknown
  if RAM is mirrored to that location on real hardware, reportedly that
  region is unused... and doesn't contain RAM...?
    Some games use The Undefined Instruction for TTY Output.
    Most games do strange 8bit writes to LCD_MODE+0 and LCD_MODE+1
    The games usually don't allow to return to the GUI (except by Reset).
```
The filesize is don't care (no padding to block, sector, word, or halfword
boundaries required).<br/>



##   Pocketstation XBOO Cable
This circuit allows to connect a pocketstation to PC parallel port, allowing to
upload executables to real hardware, and also allowing to download TTY debug
messages (particulary useful as the 32x32 pixel LCD screen is way too small to
display any detailed status info).<br/>

#### POC-XBOO Circuit
Use a standard parallel port cable (with 36pin centronics connector or 25pin DB
connector) and then build a small adaptor like this:<br/>
```
  Pin CNTR  DB25          Pocketstation          _______________________
  ACK 10    10  --------- 1 JOYDTA              |       |       |       |
  D0  2     2   --------- 2 JOYCMD              | 9 7 6 | 5 4 3 |  2 1  | CARD
  GND 19-30 18-25 ------- 4 GND                 |_______|_______|_______|
  D1  3     3   --------- 6 /JOYSEL              _______________________
  D2  4     4   --------- 7 JOYCLK              |       |       |       |
  PE  12    12  --------- 9 /JOYACK (/IRQ7)     | 9 8 7 | 6 5 4 | 3 2 1 | PAD
  NC -------------------- 8 /JOYGUN (/IRQ10)     \______|_______|______/
  NC -------------------- 3 7.5V (rumble.supply)
  SUPPLY.5V --|>|---|>|-- 5 3.5V (VCC) (eg. PC's +5V via two 1N4001 diodes)
  SUPPLY.0V ------------- 4 GND (not needed when same as GND on CNTR/DB25)
```
The circuit is same as for "Direct Pad Pro" (but using a memory card connector
instead of joypad connector, and needing +5V from PC power supply instead of
using parallel port D3..D7 as supply). Note: IRQ7 is optional (for faster/early
timeout).<br/>

#### POC-XBOO Upload
The upload function is found in no$gba "Utility" menu. It does upload the
executable and autostart it via standard memory card/pocketstation commands
(ie. it doesn't require any special transmission software installed on the
pocketstation side).<br/>
Notes: Upload is overwriting ALL files on the memory card, and does then
autostart the first file. Upload is done as "read and write only if different",
this provides faster transfers and higher lifetime.<br/>

#### POC-XBOO TTY Debug Messages
TTY output is conventionally done by executing the ARM CPU's Undefined Opcode
with an ASCII character in R0 register (for that purpose, the undef opcode
handler should simply point to a MOVS PC,LR opcode).<br/>
That kind of TTY output works in no$gba's pocketstation emulation. It can be
also used via no$gba's POC-XBOO cable, but requires some small customization in
the executable:<br/>
First of, the executable needs "TTY+" ID in some reserved bytes of the title
sector (telling the xboo uploader to stay in transmission mode and to keep
checking for TTY messages after the actual upload):<br/>
```
  TitleSector[58h] = "TTY+"
```
With that ID, and with the XBOO-hardware being used, the game will be started
with with "TTY+" in R0 (notifying it that the XBOO hardware is present, and
that it needs to install special transmission handlers):<br/>
```arm
 ;------------------
 .data?
 org  200h
 ...
 tty_bufsiz equ 128  ;max=128=fastest (can be smaller if you are short of RAM)
 func3_info:                                       ;\ ;\
  func3_buf_base     dd 0   ;fixed="func3_buf"     ;  ;  func3_info+00h
  func3_buf_len      dd 0   ;range=0..128          ;/ ;  func3_info+04h
  func3_stack        dd 0                             ;  func3_info+08h
  func3_buffer:      defs tty_bufsiz                  ;/ func3_info+0Ch
 ptr_to_comflags     dd 0
 ...
 .code
 ...
 ;------------------
 tty_wrchr:   ;in: r0=char
  dd      0e6000010h ;=undef opcode            ;-Write chr(r0) to TTY
  bx      lr
 ;------------------
 init_tty:  ;in: r0=param (from entrypoint)
  ldr     r1,=2B595454h ;"TTY+"                ;\check if xboo-cable present
  cmp     r1,r0                                ; (r0=incoming param from
  beq     @@tty_by_xboo_cable                  ;/executable's entrypoint)
 ;- - -
  mov     r1,0                                 ;\dummy und_handler
  ldr     r2,=0e1b0f00eh  ;=movs r15,r14       ; (just return from exception,
  str     r2,[r1,04h]  ;und_handler            ;/for normal cable-less mode)
  b       @@finish
 ;---
 @@tty_by_xboo_cable:
  swi     17h  ;GetPtrToFunc3addr()            ;\
  ldr     r1,=(tty_func3_handler AND 0ffffh)   ; init FUNC3 aka TTY handler
  strh    r1,[r0]                              ;/
  ldr     r1,=func3_info                       ;\
  mov     r0,0                             ;\  ; mark TTY as len=empty
  str     r0,[r1,4]        ;func3_buf_len  ;/  ; and
  add     r0,r1,0ch ;=func3_buffer         ;\  ; init func3 base
  str     r0,[r1,0]        ;func3_buf_base ;/  ;/
  mov     r1,0                                 ;\
  ldr     r2,=0e59ff018h  ;=ldr r15,[pc,NN]    ;
  str     r2,[r1,04h]  ;und_handler            ; special xboo und_handler
  add     r2,=tty_xboo_und_handler             ;
  str     r2,[r1,24h]  ;und_vector             ;/
 @@finish:
  swi     06h ;GetPtrToComFlags()              ;\
  ldr     r1,=ptr_to_comflags                  ; get ptr to ComFlags
  str     r0,[r1]                              ;/
  bx      lr
 ;------------------
 tty_xboo_und_handler:   ;in: r0=char
  ldr     r13,=func3_info ;aka sp_und          ;-base address (in sp_und)
  str     r12,[r13,8] ;func3_stack             ;-push r12
 @@wait_if_buffer_full:                        ;\
  ldr     r12,=ptr_to_comflags                 ; ;\exit if execute file request
  ldr     r12,[r12]  ;ptr to ComFlags          ; ; ComFlg.Bit11 ("bu_cmd_59h"),
  ldr     r12,[r12]  ;read ComFlags            ; ; ie. allow that flag to be
  tst     r12,1 shl 11  ;test bit11            ; ; processed by main program,
  bne     @@exit                               ; ;/without hanging here
  ldrb    r12,[r13,4] ;func3_buf_len           ; wait if buffer full
  cmp     r12,tty_bufsiz                       ; (until drained by FIQ)
  beq     @@wait_if_buffer_full                ;/
  mov     r12,1bh+0c0h  ;mode=und, FIQ/IRQ=off ;\disable FIQ (no COMMUNICATION
  mov     cpsr_ctl,r12                         ;/interrupt during buffer write)
  ldrb    r12,[r13,4]  ;func3_buf_len          ;\
  add     r12,1        ;raise len              ; write char to buffer
  strb    r12,[r13,4]  ;func3_buf_len          ; and raise buffer length
  add     r12,0ch-1    ;=func3_buffer+INDEX    ;
  strb    r0,[r13,r12] ;append char to buf     ;/
 @@exit:
  ldr     r12,[r13,8]  ;func3_stack            ;-pop r12
  movs    r15,r14        ;return from exception (and restore old IRQ/FIQ state)
 ;------------------
 tty_func3_handler:   ;in: r0=flags, r1=ptr
  tst     r0,10h  ;test if PRE/POST data (pre: Z, post: NZ)
 ;ldreq   r1,[r1]   ;read 32bit param (aka the four LEN1 bytes of FUNC3)
  ldr     r0,=func3_info   ;ptr to two 32bit values (FUNC3 return value)
  movne   r1,0                           ;\for POST data: mark buffer empty
  strne   r1,[r0,4] ;func3_buf_len=0     ;/
  bx      lr                             ;-for PRE data: return r0=func3_info
```
Usage: Call "init\_tty" at the executable's entrypoint (with incoming R0 passed
on). Call "tty\_wrchr" to output ASCII characters.<br/>
Note: The TTY messages are supported only in no$gba debug version (not no$gba
gaming version).<br/>
