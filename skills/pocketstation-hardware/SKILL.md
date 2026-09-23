---
name: pocketstation-hardware
description: "Pocketstation hardware: ARM7TDMI CPU, I/O map, memory map (2KB RAM, 128KB flash), LCD/buzzer, interrupts, timers, RTC, infrared, SIO/IrDA communication, power control, battery. Use when working with Pocketstation hardware or peripherals."
---

#   Pocketstation
[Pocketstation Overview](#pocketstation-overview)<br/>
[Pocketstation I/O Map](#pocketstation-io-map)<br/>
[Pocketstation Memory Map](#pocketstation-memory-map)<br/>
[Pocketstation IO Video and Audio](#pocketstation-io-video-and-audio)<br/>
[Pocketstation IO Interrupts and Buttons](#pocketstation-io-interrupts-and-buttons)<br/>
[Pocketstation IO Timers and Real-Time Clock](#pocketstation-io-timers-and-real-time-clock)<br/>
[Pocketstation IO Infrared](#pocketstation-io-infrared)<br/>
[Pocketstation IO Memory-Control](#pocketstation-io-memory-control)<br/>
[Pocketstation IO Communication Ports](#pocketstation-io-communication-ports)<br/>
[Pocketstation IO Power Control](#pocketstation-io-power-control)<br/>
[Pocketstation SWI Function Summary](../pocketstation-software/SKILL.md#pocketstation-swi-function-summary)<br/>
[Pocketstation SWI Misc Functions](../pocketstation-software/SKILL.md#pocketstation-swi-misc-functions)<br/>
[Pocketstation SWI Communication Functions](../pocketstation-software/SKILL.md#pocketstation-swi-communication-functions)<br/>
[Pocketstation SWI Execute Functions](../pocketstation-software/SKILL.md#pocketstation-swi-execute-functions)<br/>
[Pocketstation SWI Date/Time/Alarm Functions](../pocketstation-software/SKILL.md#pocketstation-swi-datetimealarm-functions)<br/>
[Pocketstation SWI Flash Functions](../pocketstation-software/SKILL.md#pocketstation-swi-flash-functions)<br/>
[Pocketstation SWI Useless Functions](../pocketstation-software/SKILL.md#pocketstation-swi-useless-functions)<br/>
[Pocketstation BU Command Summary](../pocketstation-software/SKILL.md#pocketstation-bu-command-summary)<br/>
[Pocketstation BU Standard Memory Card Commands](../pocketstation-software/SKILL.md#pocketstation-bu-standard-memory-card-commands)<br/>
[Pocketstation BU Basic Pocketstation Commands](../pocketstation-software/SKILL.md#pocketstation-bu-basic-pocketstation-commands)<br/>
[Pocketstation BU Custom Pocketstation Commands](../pocketstation-software/SKILL.md#pocketstation-bu-custom-pocketstation-commands)<br/>
[Pocketstation File Header/Icons](../pocketstation-software/SKILL.md#pocketstation-file-headericons)<br/>
[Pocketstation File Images](../pocketstation-software/SKILL.md#pocketstation-file-images)<br/>
[Pocketstation XBOO Cable](../pocketstation-software/SKILL.md#pocketstation-xboo-cable)<br/>



##   Pocketstation Overview
#### Sony's Pocketstation (SCPH-4000) (1998)
The Pocketstation is a memory card with built-in LCD screen and buttons; aside
from using it as memory storage device, it can be also used as miniature
handheld console.<br/>

```
  CPU        ARM7TDMI (32bit RISC Processor) (variable clock, max 7.995MHz)
  Memory     2Kbytes SRAM (battery backed), 16Kbytes BIOS ROM, 128Kbytes FLASH
  Display    32x32 pixel LCD (black and white) (without any grayscales)
  Sound      Mini Speaker "(12bit PCM) x 1 unit" / "8bit PCM with 12bit range"
  Controls   5 input buttons, plus 1 reset button
  Infrared   Bi-directional (IrDA based)
  Connector  Playstation memory card interface
  RTC        Battery backed Real-Time Clock with time/date function
  Supply     CR2032 Battery (3VDC) (used in handheld mode, and for SRAM/RTC)
    _________
   / _______ \
  | |       | |
  | |  LCD  | |                                __
  | |_______| |                Side Views     | _|
  |\_________/|                               || <-------- Button Cover
  |   O       |          (Closed)      (Open) ||
  | O   O   O |    ____________          _____||  .------- Reset Button
  |   O       |   | LCD  \____ |        | LCD \|__|_
  |___________|   |___________||        |___________| <--- Memory card plug
```

#### The RTC Problem
The main problem of the Pocketstation seems to be that it tends to reset the
RTC to 1st January 1999 with time 00:00:00 whenever possible.<br/>
The BIOS contains so many RTC-reset functions, RTC-reset buttons, RTC-reset
flags, RTC-reset communication commands, RTC-reset parameters, RTC-reset
exceptions, RTC-reset sounds, and RTC-reset animations that it seems as if Sony
actually WANTED the Time/Date to be destroyed as often as possible.<br/>
The only possible reason for doing this is that the clock hardware is so
inaccurate that Sony must have decided to "solve" the problem at software
engineering side, by erasing the RTC values before the user could even notice
time inaccuracies.<br/>

#### CPU Specs
For details on the ARM7TDMI CPUs opcodes and exceptions, check GBATEK at,<br/>
<http://problemkaputt.de/gbatek.htm> (or .txt)<br/>
The GBA uses an ARM7TDMI CPU, too.<br/>

Thanks to Exophase, Orion, Fezzik, Dr.Hell for Pocketstation info.<br/>



##   Pocketstation I/O Map
#### Memory and Memory-Control Registers
```
  00000000h RAM        (2KB RAM) (first 512 bytes bytes reserved for kernel)
  02000000h FLASH1     Flash ROM (virtual file-mapped addresses in this region)
  04000000h BIOS_ROM      Kernel and GUI (16KB)
  06000000h F_CTRL        Control of Flash ROM
  06000004h F_STAT        Unknown?
  06000008h F_BANK_FLG    FLASH virtual bank mapping enable flags(16 bits)(R/W)
  0600000Ch F_WAIT1       waitstates...?
  06000010h F_WAIT2       waitstates, and FLASH-Write-Control-and-Status...?
  06000100h F_BANK_VAL    FLASH virtual bank mapping addresses (16 words) (R/W)
  06000300h F_EXTRA       Extra FLASH (256 bytes, including below F_SN, F_CAL)
  06000300h F_SN_LO       Extra FLASH Serial Number LSBs (nocash: 6BE7h)
  06000302h F_SN_HI       Extra FLASH Serial Number MSBs (nocash: 426Ch)
  06000304h F_?           Extra FLASH Unknown ?          (nocash: 05CAh)
  06000306h F_UNUSED1     Extra FLASH Unused halfword    (nocash: FFFFh)
  06000308h F_CAL         Extra FLASH LCD Calibration    (nocash: 001Ah)
  0600030Ah F_UNUSED2     Extra FLASH Unused halfword    (nocash: FFFFh)
  0600030Ch F_?           Extra FLASH Unknown ?          (nocash: 0010h)
  0600030Eh F_UNUSED3     Extra FLASH Unused halfword    (nocash: FFFFh)
  06000310h F_UNUSED4     Extra FLASH Unused (310..3FFh) (nocash: FFFFh-filled)
  08000000h FLASH2        Flash ROM (128KB) (physical addresses in this region)
  08002A54h F_KEY1        Flash Unlock Address 1 (W)
  080055AAh F_KEY2        Flash Unlock Address 2 (W)
```
#### Interrupts and Timers
```
  0A000000h INT_LATCH     Interrupt hold (R)
  0A000004h INT_INPUT     Interrupt Status (R)
  0A000008h INT_MASK_READ Read Interrupt Mask (R)
  0A000008h INT_MASK_SET  Set Interrupt Mask (W)
  0A00000Ch INT_MASK_CLR  Clear Interrupt Mask (W)
  0A000010h INT_ACK       Clear Interrupt hold (W)
  0A800000h T0_RELOAD     Timer 0 Maximum value
  0A800004h T0_COUNT      Timer 0 Current value
  0A800008h T0_MODE       Timer 0 Mode
  0A800010h T1_RELOAD     Timer 1 Maximum value
  0A800014h T1_COUNT      Timer 1 Current value
  0A800018h T1_MODE       Timer 1 Mode
  0A800020h T2_RELOAD     Timer 2 Maximum value
  0A800024h T2_COUNT      Timer 2 Current value
  0A800028h T2_MODE       Timer 2 Mode
  0B000000h CLK_MODE      Clock control (CPU and Timer Speed) (R/W)
  0B000004h CLK_STOP      Clock stop (Sleep Mode)
  0B800000h RTC_MODE      RTC Mode
  0B800004h RTC_ADJUST    RTC Adjust
  0B800008h RTC_TIME      RTC Time (R)
  0B80000Ch RTC_DATE      RTC Date (R)
```
#### Communication Ports, Audio/Video
```
  0C000000h COM_MODE      Com Mode
  0C000004h COM_STAT1     Com Status Register 1 (Bit1=Error)
  0C000008h COM_DATA      Com RX Data (R) and TX Data (W)
  0C000010h COM_CTRL1     Com Control Register 1
  0C000014h COM_STAT2     Com Status Register 2 (Bit0=Ready)
  0C000018h COM_CTRL2     Com Control Register 2
  0C800000h IRDA_MODE     Infrared Control (R/W)
  0C800004h IRDA_DATA     Infrared TX Data
  0C80000Ch IRDA_MISC     Infrared Unknown/Reserved
  0D000000h LCD_MODE      Video Control (R/W)
  0D000004h LCD_CAL       Video Calibration (?)
  0D000100h LCD_VRAM      Video RAM (80h bytes; 32x32bit) (R/W)
  0D800000h IOP_CTRL      IOP control
  0D800004h IOP_STAT      Read Current Start/Stop bits? (R)
  0D800004h IOP_STOP      Stop bits? (W)
  0D800008h IOP_START     Start bits? (W)
  0D80000Ch IOP_DATA      IOP data?   (not used by bios)
  0D800010h DAC_CTRL      DAC Control (R/W)
  0D800014h DAC_DATA      DAC data
  0D800020h BATT_CTRL     Battery Monitor Control
```
BIOS and FLASH can be read only in 16bit and 32bit units (not 8bit).<br/>
Upon reset, BIOS ROM is mirrored to address 00000000h (instead of RAM).<br/>
For most I/O ports, it is unknown if they are (R), (W), or (R/W)...?<br/>
I/O ports are usually accessed at 32bit width, occassionally some ports are
(alternately) accessed at 16bit width. A special case are the F\_SN registers
which seem to be required to be accessed at 16bit (not 32bit).<br/>

#### Memory Access Time
Memory Access Time for Opcode Fetch:<br/>
```
  WRAM        1 cycle (for ARM and THUMB)
  FLASH       2 cycles (for ARM), or 1 cycle (for THUMB)
  BIOS        ?
```
Memory Access Time for Data Read/Write:<br/>
```
  WRAM (and some F_xxx ports)                    1 cycle
  VIRT/PHYS/XTRA_FLASH, BIOS, VRAM, I/O          2 cycles
```
For data access, it doesn't matter if the access is 8bit/16bit/32bit (unlike as
for opcode fetch, where 16bit/thumb can be faster than 32bit/arm). There seems
to be no timing differences for sequential/non-sequential access.<br/>
Additional memory waitstates can be added via F\_WAIT2 (and F\_WAIT1 maybe).<br/>

#### Invalid/Unused Memory Locations
```
  00000800h-00FFFFFFh  Mirrors of 00000000h-000007FFh (2K RAM)
  01000000h-01FFFFFFh  Invalid (read causes data abort) (unused 16MB area)
  020xxxxxh-0201FFFFh  Invalid (read causes data abort) (disabled FLASH banks)
  02020000h-02FFFFFFh  Invalid (read causes data abort) (no Virt FLASH mirrors)
  03000000h-03FFFFFFh  Invalid (read causes data abort) (unused 16MB area)
  04004000h-04FFFFFFh  Mirrors of 04000000h-04003FFFh (16K BIOS)
  05000000h-05FFFFFFh  Invalid (read causes data abort)
  06000014h-060000FFh   Zerofilled (or maybe mirror of a ZERO port?) (F_xxx)
  06000140h-060002FFh   Zerofilled (or maybe mirror of a ZERO port?) (F_xxx)
  06000400h-06FFFFFFh   Zerofilled (or maybe mirror of a ZERO port?) (F_xxx)
  07000000h-07FFFFFFh  Invalid (read causes data abort) (unused 16MB area)
  08020000h-08FFFFFFh  Mirrors of 08000000h-0801FFFFh (128K Physical FLASH)
  09000000h-09FFFFFFh  Invalid (read causes data abort) (unused 16MB area)
  0A000014h-0A7FFFFFh  Mirrors of 0A000008h-0A00000Bh (INT_MASK_READ) (I_xxx)
  0A80000Ch            Mirror of 0A800000h-0A800003h (T0_RELOAD) (T0_xxx)
  0A80001Ch            Mirror of 0A800000h-0A800003h (T0_RELOAD) (T1_xxx)
  0A80002Ch            Mirror of 0A800000h-0A800003h (T0_RELOAD) (T2_xxx)
  0A800030h-0AFFFFFFh  Mirrors of 0A800000h-0A800003h (T0_RELOAD) (T_xxx)
  0B000008h-0B7FFFFFh  Mirrors of .... ? (CLK_xxx)
  0B800010h-0BFFFFFFh  Mirrors of 0B800008h-0B80000Bh (RTC_TIME)
  0C00000Ch-0C00000Fh  Zero (COM_xxx)
  0C00001Ch-0C7FFFFFh   Zerofilled (or maybe mirror of a ZERO port?) (COM_xxx)
  0C800008h-0CFFFFFFh   ? (IRDA_xxx)
  0D000008h-0D0000FFh   Zerofilled (or maybe mirror of a ZERO port?) (LCD_xxx)
  0D000180h-0D7FFFFFh   Zerofilled (or maybe mirror of a ZERO port?) (LCD_xxx)
  0D800018h             ? (DAC_xxx)
  0D80001Ch             ? (DAC_xxx)
  0D800024h-0DFFFFFFh   Zerofilled (or maybe mirror of a ZERO port?) (BATT_xxx)
  0E000000h-FFFFFFFFh  Invalid (read causes data abort) (unused 3872MB area)
```

#### Unsupported 8bit Reads
```
  02000000h-0201FFFFh VIRT_FLASH   ;\
  04000000h-04FFFFFFh BIOS_ROM     ; "garbage_byte" (see below)
  06000300h-060003FFh EXTRA_FLASH  ;
  08000000h-08FFFFFFh PHYS_FLASH   ;/
  0A800001h-0AFFFFFFh Timer area, odd addresses (with A0=1) mirror to 0A800001h
  0B800001h-0BFFFFFFh RTC area, odd addresses (with A0=1) mirror to ...?
```

#### Unsupported 16bit Reads
```
  0B800002h-0BFFFFFEh RTC area, odd addresses (with A1=1) mirror to 0B80000Ah
```

#### garbage\_byte (for unsupported 8bit reads)
The "garbage\_byte" depends on the LSBs of the read address, prefetched opcodes,
and recent data fetches:<br/>
```
  garbage_word = (prefetch OR (ramdata AND FFFFFFD0h))
  garbage_byte = (garbage_word shr (8*(addr and 3))) AND FFh
```
For ARM code, the "prefetch" is the 2nd next opcode after the LDRB:<br/>
```
  prefetch.bit0-31  = [curr_arm_opcode_addr+8]    ;-eg. from arm LDRB
```
For THUMB code, the "prefetch" is the 2nd next opcode after the LDRB (no matter
if that opcode is word-aligned or not), combined with the most recent ARM
opcode prefetch (eg. from the BX opcode switched from ARM to THUMB mode; that
value may get changed on interrupts):<br/>
```
  prefetch.bit0-15  = [recent_arm_opcode_addr+8]  ;-eg. from arm BX to thumb
  prefetch.bit16-31 = [curr_thumb_opcode_addr+4]  ;-eg. from thumb LDRB
```
The "ramdata" is related to most recent RAM read (eg. from POP or LDR opcodes
that have read data from RAM; however, writes to RAM, or literal pool reads
from FLASH don't affect it):<br/>
```
  ramdata.bit0-31   = [recent_ram_read_addr]      ;-eg. from LDR/POP from RAM
```
There might be some more/unknown things that affect the garbage (eg. opcode
fetches from RAM instead of FLASH, partial 8bit/16bit data reads from RAM, or
reads from I/O areas, current CPU clock speed, or unpredictable things like
temperature).<br/>
Note: The garbage\_byte is "used" by the pocketstation "Rockman" series games.<br/>



##   Pocketstation Memory Map
#### Overall Memory Map
```
  00000000h RAM      RAM (2K)   (or mirror of BIOS ROM upon reset)
  02000000h FLASH1   Flash ROM  (virtual file-mapped addresses in this region)
  04000000h BIOS_ROM BIOS (16K) (Kernel and GUI)
  06000300h F_SN...  Seems to contain a bunch of additional FLASH bytes?
  08000000h FLASH2   Flash ROM  (128K) (physical addresses in this region)
  0D000100h LCD_VRAM Video RAM  (128 bytes) (32x32 pixels, 1bit per pixel)
```

#### 00000000h..000001FFh - Kernel RAM
The first 200h bytes of RAM are reserved for the kernel.<br/>
```
  0000000h 20h  Exception handler opcodes (filled with LDR R15,[$+20h] opcodes)
  0000020h 20h  Exception handler addresses (in ARM state, no THUMB bit here)
  0000040h 80h  Sector buffer (and BU command parameter work space)
  00000C0h 8    ComFlags (see GetPtrToComFlags(), SWI 06h for details)
  00000C8h 2    BU Command FUNC3 Address (see GetPtrToFunc3addr() aka SWI 17h)
  00000CAh 1    Value from BU Command_50h, reset by SWI 05h (sense_auto_com)
  00000CBh 2    Not used
  00000CDh 1    Old Year (BCD, 00h..99h) (for sensing wrapping to new century)
  00000CEh 1    Alternate dir_index (when [0D0h]=0) (see SWI 15h and SWI 16h)
  00000CFh 1    Current Century (BCD, 00h..99h) (see GetBcdDate() aka SWI 0Dh)
  00000D0h 2    Current dir_index (for currently executed file, or 0=GUI)
  00000D2h 2    New dir_index (PrepareExecute(flag,dir_index,param), SWI 08h)
  00000D4h 4    New param     (PrepareExecute(flag,dir_index,param), SWI 08h)
  00000D8h 8    Alarm Setting        (see GetPtrToAlarmSetting() aka SWI 13h)
  00000E0h 4    Pointer to SWI table (see GetPtrToPtrToSwiTable() aka SWI 14h)
  00000E4h 3x4  Memory Card BU Command variables
  00000F0h 1    Memory Card FLAG byte (bit3=new_card, bit2=write_error)
  00000F1h 1    Memory Card Error offhold (0=none, 1=once)
  00000F2h 6    Not used
  00000F8h 4x4  Callback Addresses (set via SetCallbacks(index,proc), SWI 01h)
  0000108h 4    Snapshot ID (0xh,00h,"SE")
  000010Ch 74h  IRQ and SWI stack (stacktop at 180h)
  0000180h 80h  FIQ stack (stacktop at 200h)
```
Although one can modify that memory, one usually shouldn't do that, or at least
one must backup and restore the old values before returning control to the GUI
or to other executables. Otherwise, the only way to restore the original values
would be to press the Reset button (which would erase the RTC time/date).<br/>

#### 00000200h..000007FFh - User RAM and User stack (stacktop at 800h)
This region can be freely used by the game. The memory is zerofilled when the
game starts.<br/>

#### 02000000h - FLASH1 - Flash ROM (virtual file-mapped addresses in this region)
This region usually contains the currently selected file (including its title
and icon sectors), used to execute the file in this region, mapped to continous
addresses at 2000000h and up.<br/>

#### 08000000h - FLASH2 - Flash ROM (128K) (physical addresses in this region)
This region is used by the BIOS when reading the memory card directory (and
when writing data to the FLASH memory). The banking granularity is 2000h bytes
(one memory card block), that means that the hardware cannot map Replacement
Sectors which may be specified in the for Broken Sector List.<br/>

#### 04000000h - BIOS ROM (16K) - Kernel and GUI
```
  4000000h 1E00h Begin of Kernel (usually 1E00h bytes)
  4000014h 4     BCD Date in YYYYMMDDh format (19981023h for ALL versions)
  4001DFCh 4     Core Kernel Version  (usually "C061" or "C110")
  4001E00h 2200h Begin of GUI (usually 2200h bytes)
  4003FFCh 4     Japanese GUI Version (usually "J061" or "J110")
```
The "110" version does contain some patches, but does preserve same function
addresses as the "061" version, still it'd be no good to expect the BIOS to
contain any code/data at fixed locations (except maybe the GUI version string).
Kernel functions can be accessed via SWI Opcodes, and, from the PSX-side, via
BU Commands.<br/>

#### Bus-Width Restrictions
FLASH and BIOS ROM seem to be allowed to be read only in 16bit and 32bit units,
not in 8bit units? Similar restrictions might apply for some I/O ports...? RAM
can be freely read/written in 8bit, 16bit, and 32bit units.<br/>

#### Waitstates
Unknown if and how many waitstates are applied to the different memory regions.
The F\_WAIT1 and F\_WAIT2 registers seem to be somehow waitstate related. FLASH
memory does probably have a 16bit bus, so 32bit data/opcode fetches might be
slower then 16bit reads...? Similar delays might happen for other memory and
I/O regions...?<br/>



##   Pocketstation IO Video and Audio
#### 0D000000h - LCD\_MODE - LCD control word (R/W)
```
  0-2  Draw mode; seems to turn off bits of the screen;
         0: All 32 rows on      ;\
         1: First 8 rows on     ;
         2: Second 8 rows on    ;
         3: Third 8 rows on     ; (these are not necessarily all correct?)
         4: Fourth 8 rows on    ;
         5: First 16 rows on    ;
         6: Middle 16 rows on   ;
         7: Bottom 16 rows on   ;/
  3    CPEN      (0=Does some weird fade out of the screen, 1=Normal)
  4-5  Refresh rate
         0: Makes a single blue (yes, blue, yes, on a black/white display)
            line appear at the top or middle of the screen - don't use!
         1: 64Hz? (might be 32Hz too, like 2)
         2: 32Hz
         3: 16Hz (results in less intensity on black pixels)
  6    Display active                (0=Off, 1=On)
  7    Rotate display by 180 degrees (0=For Handheld Mode, 1=For Docked Mode)
  8-31 Unknown (should be zero)
```
Software should usually set LCD\_MODE.7 equal to INT\_INPUT.Bit11 (docking flag).
In handheld mode, the button-side is facing towards the player, whilst in
Docked mode (when the Pocketstation is inserted into the PSX controller port),
the button-side is facing towards the PSX, so the screen coordinates become
vice-versa, which can be "undone" by the Rotation flag.<br/>

#### 0D000004h - LCD\_CAL - LCD Calibration (maybe contrast or so?)
Upon the reset, the kernel sets LCD\_CAL = F\_CAL AND 0000003Fh. Aside from that,
it doesn't use LCD\_CAL.<br/>

#### 0D000100h..D00017Fh - LCD\_VRAM - 32x32 pixels, 1bit color depth (R/W)
This region consists of 32 words (32bit values),<br/>
```
  [D000100h]=Top, through [D00017Ch]=Bottom-most scanline
```
The separate scanlines consist of 32bit each,<br/>
```
  Bit0=Left, through Bit31=Right-most Pixel (0=White, 1=Black)
```
That [D000100h].Bit0=Upper-left arrangement applies if the Rotate bit in
LCD\_MODE.7 is set up in the conventional way, if it is set the opposite way,
then it becomes [D00017Ch].Bit31=Upper-left.<br/>
The LCD\_VRAM area is reportedly mirrored to whatever locations?<br/>

#### 0D800010h - DAC\_CTRL - Audio Control (R/W)
```
  0     Audio Enable enable    (0=Off, 1=On)
  1-31  Unknown, usually zero
```
Note: Aside from the bit in DAC\_CTRL, audio must be also enabled/disabled via
IOP\_STOP/IOP\_START bit5. Unknown if/which different purposes that bits have.<br/>

#### 0D800014h - DAC\_DATA - Audio D/A Converter
Unknown how many bits are passed to the D/A converter, probably bit8-15, ie. 8
bits...?<br/>
```
  0-7   Probably unused, usually zero (or fractional part when lowered volume)
  8-15  Signed Audio Outut Level (usually -7Fh..+7Fh) (probably -80h works too)
  16-31 Probably unused, usually sign-expanded from bit15
```
The Pocketstation doesn't have any square wave or noise generator (nor a sound
DMA channel). So the output levels must be written to DAC\_DATA by software,
this is usually done via Timer1/IRQ-8 (to reduce CPU load caused by high audio
frequencies, it may be much more recommended to use Timer2/FIQ-13, because the
FIQ handler doesn't need to push r8-r12).<br/>
For example, to produce a 1kHz square wave, the register must be toggled
high/low at 2kHz rate. If desired, multiple channels can be mixed by software.
High frequencies and multiple voices may require high CPU speed settings, and
thus increase battery consumption (aside from that, battery consumption is
probably increased anyways when the speaker is enabled).<br/>



##   Pocketstation IO Interrupts and Buttons
#### 0A000004h - INT\_INPUT - Raw Interrupt Signal Levels (R)
```
  Bit   Type    Meaning
  0     IRQ     Button Fire     (0=Released, 1=Pressed)
  1     IRQ     Button Right    (0=Released, 1=Pressed)
  2     IRQ     Button Left     (0=Released, 1=Pressed)
  3     IRQ     Button Down     (0=Released, 1=Pressed)
  4     IRQ     Button Up       (0=Released, 1=Pressed)
  5     ?       Unknown?        (?)
  6     FIQ (!) COM              ;for the COM_registers?      (via /SEL Pin?)
  7     IRQ     Timer 0
  8     IRQ     Timer 1
  9     IRQ     RTC (square wave) (usually 1Hz) (when RTC paused: 4096Hz)
  10    IRQ     Battery Low     (0=Normal, 1=Battery Low)
  11    IRQ     Docked ("IOP")  (0=Undocked, 1=Docked to PSX) (via VCC Pin?)
  12    IRQ     Infrared Rx
  13    FIQ (!) Timer 2
  14-15 N/A     Not used
```
The buttons are usually read directly from this register (rather than being
configured to trigger IRQs) (except in Sleep mode, where the Fire Button IRQ is
usually used to wakeup). Also, bit9-11 are often read from this register.<br/>
The direction keys seem to be separate buttons, ie. unlike as on a joystick or
DPAD, Left/Right (and Up/Down) can be simultaneously pressed...?<br/>

#### 0A000008h - INT\_MASK\_SET - Set Interrupt Mask (W)
#### 0A00000Ch - INT\_MASK\_CLR - Clear Interrupt Mask (W)
#### 0A000008h - INT\_MASK\_READ - Read Interrupt Mask (R)
```
  INT_MASK_SET  Enable Interrupt Flags         (0=No change, 1=Enable)   (W)
  INT_MASK_CLR  Disable Interrupt Flags        (0=No change, 1=Disable)  (W)
  INT_MASK_READ Current Interrupt Enable Flags (0=Disabled, 1=Enabled)   (R)
```
The locations of the separate bits are same as in INT\_INPUT (see there).<br/>

#### 0A000000h - INT\_LATCH - Interrupt Request Flags (R)
#### 0A000010h - INT\_ACK - Acknowledge Interrupts (W)
```
  INT_LATCH Latched Interrupt Requests   (0=None, 1=Interrupt Request)   (R)
  INT_ACK   Clear Interrupt Requests     (0=No change, 1=Acknowledge)    (W)
```
The locations of the separate bits are same as in INT\_INPUT (see there).<br/>
The interrupts seem to be edge-triggered (?), ie. when the corresponding bits
in INT\_INPUT change from 0-to-1. Unknown if the request bits get set when the
corresponding interrupt is disabled in INT\_MASK...?<br/>

ATTENTION: The GUI doesn't acknowledge Fire Button interrupts on wakeup... so,
it seems as if button interrupts are NOT latched... ie. the button "INT\_LATCH"
bits seem to be just an unlatched mirror of the "INT\_INPUT" bits... that might
also apply for some other interrupt...?<br/>
However, after wakeup, the gui does DISABLE the Fire Button interrupt, MAYBE
that does automatically acknowledge it... in that case it might be latched...?<br/>

Reading outside the readable region (that is where exactly?) seems to mirror to
0A000008h. Enabling IRQs for the buttons seems to make it impossible to poll
them... is that really true?<br/>



##   Pocketstation IO Timers and Real-Time Clock
#### Timer and RTC interrupts
```
  INT_INPUT.7     Timer 0 IRQ    ;used as 30Hz frame rate IRQ by GUI
  INT_INPUT.8     Timer 1 IRQ    ;used as Audio square wave IRQ by GUI
  INT_INPUT.13    Timer 2 FIQ (this one via FIQ vector, not IRQ vector)
  INT_INPUT.9     RTC IRQ (usually 1Hz) (or 4096Hz when RTC paused)
```

#### 0A800000h - T0\_RELOAD - Timer 0 Reload Value
#### 0A800010h - T1\_RELOAD - Timer 1 Reload Value
#### 0A800020h - T2\_RELOAD - Timer 2 Reload Value
```
  0-15  Reload Value (when timer becomes less than zero)
```
Writes to this register are ignored if the timer isn't stopped?<br/>

#### 0A800004h - T0\_COUNT - Timer 0 Current value
#### 0A800014h - T1\_COUNT - Timer 1 Current value
#### 0A800024h - T2\_COUNT - Timer 2 Current value
```
  0-15  Current value (decrementing)
```
Timer interrupts: The timers will automatically raise interrupts if they're
enabled, there's no need to set a bit anywhere for IRQs (but you need to enable
the respect interrupts in INT\_MASK).<br/>

#### 0A800008h - T0\_MODE - Timer 0 Control
#### 0A800018h - T1\_MODE - Timer 1 Control
#### 0A800028h - T2\_MODE - Timer 2 Control
```
  0-1  Timer Divider (0=Div2, 1=Div32, 2=Div512, 3=Div2 too)
  2    Timer Enable  (0=Stop, 1=Decrement)
  3-15 Unknown (should be zero)
```
Timers are clocked by the System Clock (usually 4MHz, when CLK\_MODE=7), divided
by the above divider setting. Note that the System Clock changes when changing
the CPU speed via CLK\_MODE, so Timer Divider and/or Timer Reload must be
adjusted accordingly.<br/>

#### 0B800000h - RTC\_MODE - RTC control word
```
  0    Pause RTC (0=Run/1Hz, 1=Pause/4096Hz)
  1-3  Select value to be modified via RTC_ADJUST
  4-31 Not used?
```
The selection bits can be:<br/>
```
  00h = Second        ;\
  01h = Minute        ;
  02h = Hour          ; used in combination with RTC_ADJUST
  03h = Day of Week   ; while RTC is paused
  04h = Day           ;
  05h = Month         ;
  06h = Year          ;/
  07h = Unknown       ;-usually used when RTC isn't paused
```
When paused, the RTC IRQ bit in INT\_INPUT.9 runs at 4096Hz (instead 1Hz).<br/>

#### 0B800004h - RTC\_ADJUST - Modify value (write only)
Writing a value here seems to increment the current selected parameter (by the
RTC control). What is perhaps (?) clear is that you have to wait for the RTC
interrupt signal to go low before writing to this.<br/>

#### 0B800008h - RTC\_TIME - Real-Time Clock Time (read only) (R)
```
  0-7   Seconds     (00h..59h, BCD)
  8-15  Minutes     (00h..59h, BCD)
  16-23 Hours       (00h..23h, BCD)
  24-31 Day of week (1=Sunday, ..., 7=Saturday)
```
Reading RTC\_TIME seems to be somewhat unstable: the BIOS uses a read/retry
loop, until it has read twice the same value (although it does read the whole
32bit at once by a LDR opcode, the data is maybe passed through a 8bit or 16bit
bus; so the LSBs might be a few clock cycles older than the MSBs...?).<br/>

#### 0B80000Ch - RTC\_DATE - Real-Time Clock Date (read only) (R)
```
  0-7   Day     (01h..31h, BCD)
  8-11  Month   (01h..12h, BCD)
  16-23 Year    (00h..99h, BCD)
  24-31 Unknown? (this is NOT used as century)
```
Reading RTC\_DATE seems to require the same read/retry method as RTC\_TIME (see
there). Note: The century is stored in battery-backed RAM (in the reserved
kernel RAM region) rather than in the RTC\_DATE register. The whole date,
including century, can be read via SWI 0Dh, GetBcdDate().<br/>



##   Pocketstation IO Infrared
The BIOS doesn't contain any IR functions (aside from doing some basic
initialization and power-down stuff).<br/>
IR is used in Final Fantasy 8's Chocobo World (press Left/Right in the Map
screen to go to the IR menu), and in Metal Gear Solid Integral (Press Up in the
main screen), and in PDA Remote 1 & 2 (one-directional TV remote control).<br/>

#### 0C800000h - IRDA\_MODE - Controlling the protocol - send/recv, etc. (R/W)
```
  0    Transfer Direction  (0=Receive, 1=Transmit)
  1    Disable IRDA        (0=Enable, 1=Disable)
  2    Unknown (reportedly IR_SEND_READY, uh?)
  3    Unknown (reportedly IR_RECV_READY, uh?)
  4-31 Unknown (should be zero)
```

#### 0C800004h - IRDA\_DATA - Infrared TX Data
```
  0    Transmit Data in Send Direction (0=LED Off, 1=LED On)
  1-31 Unknown (should be zero)
```
Bits are usually encoded as long or short ON pulses, separated by short OFF
pulses. Where long is usually twice as long as short.<br/>

#### 0C80000Ch - IRDA\_MISC
Unknown? Reportedly reserved.<br/>

#### INT\_INPUT.12 - IRQ - Infrared RX Interrupt
Seems to get triggered on raising or falling (?) edges of incoming data. The
interrupt handler seems to read the current counter value from one of the
timers (usually Timer 2, with reload=FFFFh) to determine the length of the
incoming IR pulse.<br/>

#### IR Notes
Mind that IR hardware usually adopts itself to the normal light conditions, so
if it receives an IR signal for a longer period, then it may treat that as the
normal light conditions (ie. as "OFF" state). To avoid that, one would usually
send a group of ON-OFF-ON-OFF pulses, instead of sending a single long ON
pulse:<br/>
```
   ___------------------___  One HIGH bit send as SINGLE-LONG-ON pulse   (BAD)
   ___-_-_-_-_-_-_-_-_-____  One HIGH bit send as MULTIPLE-ON-OFF pulses (OK)
```
that might be maybe done automatically by the hardware...?<br/>

Reportedly, Bit4 of Port 0D80000Ch (IOP\_DATA) is also somewhat IR related...?<br/>



##   Pocketstation IO Memory-Control
#### 06000000h - F\_CTRL
```
  0-31  Unknown
```
Written values are:<br/>
```
  00000000h  Used when disabling all virtual flash banks
  00000001h  Used before setting new virtual bank values
  00000002h  Used after setting virtual bank enable bits
  03h        Replace ROM at 00000000h by RAM (used after reset)
```
The GUI does additionally read from this register (and gets itself trapped in a
bizarre endless loop if bit0 was zero). Unknown if it's possible to re-enable
ROM at location 00000000h by writing any other values to this register?<br/>

#### 06000004h F\_STAT
```
  0-31  Unknown
```
The kernel issues a dummy read from this address (before setting F\_CTRL to
00000001h).<br/>

#### 06000008h F\_BANK\_FLG  ;FLASH virtual bank mapping enable flags (16 bits)(R/W)
```
  0-15   Enable physical banks 0..15 in virtual region (0=Disable, 1=Enable)
  16-31  Unknown (should be zero)
```

#### 06000100h F\_BANK\_VAL  ;FLASH virtual bank mapping addresses (16 words)(R/W)
This region contains 16 words, the first word at 06000100h for physical bank 0,
the last word at 0600013Ch for physical bank 15. Each word is:<br/>
```
  0-3    Virtual bank number
  4-31   Should be 0
```
Unused physical banks are usually mapped to 0Fh (and are additionally disabled
in the F\_BANK\_FLG register).<br/>

#### 0600000Ch F\_WAIT1     ;waitstates...?
```
  0..3   Unknown/not tested
  4      hangs hardware? but that bit is used in some cases!
  5..31  Unknown/not tested
```
Unknown, seems to control some kind of memory waitstates for FLASH (or maybe
RAM or BIOS ROM). Normally it is set to the following values:<br/>
```
  F_WAIT1=00000000h when CPU Speed = 00h..07h
  F_WAIT1=00000010h when CPU Speed = 08h..0Fh
```
Note: The kernels Docking/Undocking IRQ-11 handler does additionally do this:
"F\_WAIT1=max(08h,(CLK\_MODE AND 0Fh))" (that is a bug, what it actually wants to
do is to READ the current F\_WAIT.Bit4 setting).<br/>

#### 06000010h F\_WAIT2     ;waitstates, and FLASH-Write-Control-and-Status...?
```
  0      no effect? but that bit is used in some cases! maybe write-enable?
  1      hangs hardware?
  2      no effect?           READ: indicates 0=write-busy, 1=ready?  (R)
  3      hangs hardware?
  4      makes FLASH slower?
  5      makes WRAM and F_xxx as slow as other memory (0=1 cycle, 1=2 cycles)
  6      hangs hardware? but that bit is used in some cases!
  7      no effect?
  8..31  Unknown/not tested
```
Unknown, seems to control some kind of memory waitstates, maybe for another
memory region than F\_WAIT1, or maybe F\_WAIT2 is for writing, and F\_WAIT1 for
reading or so. Normally it is set to the following values:<br/>
```
  F_WAIT2=00000000h when CPU Speed = 00h..07h  ;\same as F_WAIT1
  F_WAIT2=00000010h when CPU Speed = 08h..0Fh  ;/
```
In SWI 0Fh and SWI 10h it is also set to:<br/>
```
  F_WAIT2=00000021h  ;SWI 10h, FlashWritePhysical(sector,src)
  F_WAIT2=00000041h  ;SWI 0Fh, FlashWriteSerial(serial_number)
```
Before completion, those SWIs do additionally,<br/>
```
  wait until reading returns F_WAIT2.Bit2 = 1
  and then set F_WAIT2=00000000h
```

#### 08002A54h - F\_KEY1 - Flash Unlock Address 1 (W)
#### 080055AAh - F\_KEY2 - Flash Unlock Address 2 (W)
Unlocks FLASH memory for writing. The complete flowchart for writing sector
data (or header values) is:<br/>
```
  if write_sector                               ;\
    F_WAIT2=00000021h                           ; write enable or so
  if write_header                               ;
    F_WAIT2=00000041h                           ;/
  [80055AAh]=FFAAh                              ;\
  [8002A54h]=FF55h                              ; unlock flash
  [80055AAh]=FFA0h                              ;/
  if write_sector                               ;\
    for i=0 to 3Fh                              ;
      [8000000h+sector*80h+i*2]=src[i*2]        ; write data
  if write_header                               ;
    [8000000h]=new F_SN_LO value                ;
    [8000002h]=new F_SN_HI value                ;
    [8000008h]=new F_CAL value                  ;/
  first, wait 4000 clock cycles                 ;\wait
  then, wait until F_WAIT2.Bit2=1               ;/
  F_WAIT2=00000000h                             ;-write disable or so
```
During the write operation one can (probably?) not read data (nor opcodes) from
FLASH memory, so the above code must be executed either in RAM, or in BIOS ROM
(see SWI 03h, SWI 0Fh, SWI 10h).<br/>

#### 06000300h - F\_SN\_LO - Serial Number LSBs
#### 06000302h - F\_SN\_HI - Serial Number MSBs
#### 06000308h - F\_CAL - Calibration value for LCD
```
  0-15  Data
```
This seems to be an additional "header" region of the FLASH memory
(additionally to the 128K of data). The F\_SN registers contain a serial number
or so (purpose unknown, maybe intended as some kind of an "IP" address for more
complex infrared network applications), the two LO/HI registers must be read by
separate 16bit LDRH opcodes (not by a single 32bit LDR opcode). The F\_CAL
register contains a 6bit calibration value for LCD\_CAL (contrast or so?).<br/>
Although only the above 3 halfwords are used by the BIOS, the "header" is
unlike to be 6 bytes in size, probably there are whatever number of additional
"header" locations at 06000300h and up...?<br/>
Note: Metal Gear Solid Integral uses F\_SN as some kind of copy protection (the
game refuses to run and displays "No copy" if F\_SN is different as when the
pocketstation file was initially created).<br/>

#### F\_BANK\_VAL and F\_BANK\_FLG Notes
Observe that the physical\_bank number (p) is used as array index, and that the
virtual bank number (v) is stored in that location, ie. table[p]=v, which is
unlike as one may have expected it (eg. on a 80386 CPU it'd be vice-versa:
table[v]=p).<br/>
Due to the table[p]=v assignment, a physical block cannot be mirrored to
multiple virtual blocks, instead, multiple physical blocks can be mapped to the
same virtual block (unknown what happens in that case, maybe the data becomes
ANDed together).<br/>



##   Pocketstation IO Communication Ports
#### 0C000000h - COM\_MODE - Com Mode
```
  0     Data Output Enable  (0=None/HighZ, 1=Output Data Bits)
  1     /ACK Output Level   (0=None/HighZ, 1=Output LOW)
  2     Unknown (should be set when expecting a NEW command...?)
  3-31  Unknown (should be zero)
```

#### 0C000008h - COM\_DATA - Com RX/TX Data
```
  0-7   Data (Write: to be transmitted to PSX, Read: been received from PSX)
  8-31  Unknown
```

#### 0C000004h - COM\_STAT1 - Com Status Register 1 (Bit1=Error)
```
  0     Unknown
  1     Error flag or so (0=Okay, 1=Error)
  2-31  Unknown
```
Seems to indicate whatever error (maybe /SEL disabled during transfer, or
timeout, or parity error or something else?) in bit1. Meaning of the other bits
is unknown. Aside from checking the error flag, the kernel does issue a dummy
read at the end of each transfer, maybe to acknowledge something, maybe the
hardware simply resets the error bit after reading (although the kernel doesn't
handle the bit like so when receiving the 1st command byte).<br/>
Aside from the above error flag, one should check if INT\_INPUT.11 becomes zero
during transfer (which indicates undocking).<br/>

#### 0C000014h - COM\_STAT2 - Com Status Register 2 (Bit0=Ready)
```
  0     Ready flag (0=Busy, 1=Ready) (when 8bits have been transferred)
  1-31  Unknown
```

#### 0C000010h - COM\_CTRL1 - Com Control Register 1
```
  0     Unknown (should be set AT BEGIN OF A NEW command...?)
  1     Unknown (0=Disable something, 1=Enable something)
  2-31  Unknown (should be zero)
```
Used values are:<br/>
```
  00000000h = unknown?  disable
  00000002h = unknown?  enable
  00000003h = unknown?  at BEGIN of a new command
```
When doing the enable thing, Bit1 should be set to 0-then-1...? Bit0 might
enable the data shift register... and bit1 might be a master enable and master
acknowledge for the COM interrupt... or something else?<br/>

#### 0C000018h - COM\_CTRL2 - Com Control Register 2
```
  0     Unknown (should be set, probably starts or acknowledges something)
  1     Unknown (should be set when expecting a NEW command...?)
  2-31  Unknown (should be zero)
```
Used values are:<br/>
```
  00000001h = unknown?  used before AND after each byte-transfer
  00000003h = unknown?  used after LAST byte of command (and when init/reset)
```
Maybe that two bits acknowledge the ready/error bits?<br/>

#### INT\_INPUT.6  FIQ (!) COM    for the COM\_registers?      (via /SEL Pin?)
```
  (via FIQ vector, not IRQ vector)
```

#### INT\_INPUT.11 IRQ Docked ("IOP")  (0=Undocked, 1=Docked to PSX)
Probably senses the voltage on the cartridge slots VCC Pin. Becomes zero when
Undocked (and probably also when the PSX is switched off).<br/>
The Kernel uses IRQ-11 for BOTH sensing docking and undocking, ie. as if the
IRQ would be triggered on both 0-to-1 and 1-to-0 transistions... though maybe
that feature just relies on switch-bounce. For the same reason (switch bounce),
the IRQ-11 handler performs a delay before it checks the new INT\_INPUT.11
setting (ie. the delay skips the unstable switch bound period, and allows the
signal to stabilize).<br/>

#### IOP\_START/IOP\_STOP.Bit1
The BIOS adjusts this bit somehow in relation to communication. Unknown
when/why/how it must be used. For details on IOP\_START/IOP\_STOP see Power
Control chapter.<br/>

#### Opcode E6000010h (The Undefined Instruction) - Write chr(r0) to TTY
This opcode is used by the SN Systems emulator to write chr(r0) to a TTY style
text window. r0 can be ASCII characters 20h and up, or 0Ah for CRLF. Using that
opcode is a not too good idea because the default BIOS undef instruction
handler simply runs into an endless loop, so games that are using it (eg.
Break-Thru by Jason) won't work on real hardware. That, unless the game would
change the undef instruction vector at [04h] in Kernel RAM, either replacing it
by a MOVS R15,R14 opcode (ignore exception and return to next opcode), or by
adding exception handling that outputs the character via IR or via whatever
cable connection. Observe that an uninitialized FUNC3 accidently destroys
[04h], so first init FUNC3 handler via SWI 17h, before trying to change [04h],
moreover, mind that SWI 05h may reset FUNC3, causing the problem to reappear.<br/>
Altogether, it'd be MUCH more stable to write TTY characters to an unused I/O
port... only problem is that it's still unknown which I/O ports are unused...
ie. which do neither trap data aborts, nor do mirror to existing ports...?<br/>



##   Pocketstation IO Power Control
#### 0B000000h - CLK\_MODE - Clock control (CPU and Timer Speed) (R/W)
```
  0-3  Clock Ratio (01h..08h, see below) (usually 7 = 3.99MHz)    (R/W)
  4    Clock Change State (0=Busy, 1=Ready)                       (Read-only)
  5-15 ?
```
Allows to change the CPU clock (and Timer clock, which is usually one half of
the CPU clock, or less, depending on the Timer Divider). Possible values are:<br/>
```
  00h = hangs hardware    ;-don't use
  01h = 0.063488 MHz      ;\
  02h = 0.126976 MHz      ;
  03h = 0.253952 MHz      ; 31*8000h / 1,2,4,8,16
  04h = 0.507904 MHz      ;
  05h = 1.015808 MHz      ;/
  06h = 1.998848 MHz      ;\
  07h = 3.997696 MHz      ; 61*8000h * 1,2,4
  08h = 7.995392 MHz      ;/
  09h..0Fh = same as 08h  ;-aliases
```
Before changing CLK\_MODE, F\_WAIT1 and F\_WAIT2 should be adjusted accordingly
(see there for details). Note that many memory regions have waitstates, the
full CPU speed can be reached mainly with code/data in WRAM.<br/>
For emulator authors: Note that some Pocketstation software will expect bit 4 of CLK\_MODE to go from 0 to 1 rather than just polling it until it's 1. For this reason, emulating bit 4 as always being 1 can very likely break.<br/>

#### 0B000004h - CLK\_STOP - Clock stop (Sleep Mode)
Stops the CPU until an interrupt occurs. The pocketstation doesn't have a
power-switch nor standby button, the closest thing to switch "power off" is to
enter sleep mode. Software should do that when the user hasn't pressed buttons
for 1-2 seconds (that, only in handheld mode, not when docked to the PSX; where
it's using the PSX power supply instead of the battery).<br/>
```
  0    Stop Clock (1=Stop)
  1-15 ?
```
Wakeup is usually done by IRQ-0 (Fire Button) and IRQ-11 (Docking). If alarm is
enabled, then the GUI also enables IRQ-9 (RTC), and compares RTC\_TIME against
the alarm setting each time when it wakes up.<br/>
Before writing to CLK\_STOP, one should do:<br/>
```
  DAC_CTRL=0                         ;\disable sound
  IOP_STOP=20h                       ;/
  LCD_MODE=0                         ;-disable video
  IRDA=whatever                      ;-disable infrared (if it was used)
  BATT_CTRL=BATT_CTRL AND FFFFFFFCh  ;-do whatever
  INT_MASK_SET=801h                  ;-enable Docking/Fire wakeup interrupts
```
The GUI uses CLK\_STOP only for Standby purposes (not for waiting for its 30Hz
"frame rate" timer 0 interrupt; maybe that isn't possible, ie. probably
CLK\_STOP does completely disable the system clock, and thus does stop
Timer0-2...?)<br/>

#### 0D800000h - IOP\_CTRL - Configures whatever...? (R/W)
```
  0-3  Probably Direction for IOP_DATA bit0..3 (0=Input, 1=Output)
  4-31 Unknown/Unused (seems to be always zero)
```
Unknown. Set to 0000000Fh by BIOS upon reset. Aside from that, the BIOS does
never use that register.<br/>

#### 0D800004h - IOP\_STAT (R) - Read Current bits? -- No, seems to be always 0
#### 0D800004h - IOP\_STOP (W) - Set IOP\_DATA Bits
#### 0D800008h - IOP\_START (W) - Clear IOP\_DATA Bits
These two ports are probably accessing a single register, writing "1" bits to
IOP\_STOP sets bits in that register, and writing "1" bits to IOP\_START clears
bits... or vice-versa...? Writing "0" bits to either port seems to leave that
bits unchanged. The meaning of most bits is still unknown:<br/>
```
  0    Unknown, STARTED by Kernel upon reset
  1    Red LED, Communication related (START=Whatever, STOP=Whatelse) (?)
  2    Unknown, STARTED by Kernel upon reset
  3    Unknown, STARTED by Kernel upon reset
  4    Never STARTED nor STOPPED by BIOS (maybe an INPUT, read via IOP_DATA)
  5    Sound Enable (START=On, STOP=Off)
  6    Unknown, STOPPED by Kernel upon reset
  7-31 Unknown, never STARTED nor STOPPED by BIOS
```
Aside from Bit1, it's probably not neccessary to change the unknown bits...?<br/>
Sound is usually disabled by setting IOP\_STOP=00000020h. IOP\_STAT is rarely
used. Although, one piece of code in the BIOS disables sound by setting
IOP\_STOP=IOP\_STAT OR 00000020h, that is probably nonsense, probably intended to
keep bits stopped if they are already stopped (which would happen anyways),
however, the strange code implies that reading from 0D800004h returns the
current status of the register, and that the bits in that register seem to be
0=Started, and 1=Stopped...?<br/>

#### 0D80000Ch - IOP\_DATA (R)
```
  0    ?
  1    Red LED (0=On, 1=Off)
  2    ?
  3    ?
  4    Seems to be always 1 (maybe Infrared input?)
  5-31 Unknown/Unused (seems to be always zero)
```
Unknown. Not used by the BIOS. Reportedly this register is 0010h if IR
Connection...? This register is read by Rewrite ID, and by Harvest Moon. Maybe
bit4 doesn't mean \<if\> IR connection exist, but rather \<contains\>
the received IR data level...?<br/>

#### 0D800020h - BATT\_CTRL - Battery Monitor Control?
Unknown. Somehow battery saving related. Upon reset, and upon leaving sleep
mode, the BIOS does set BATT\_CTRL=00000000h. Before entering sleep mode, it
does set BATT\_CTRL=BATT\_CTRL AND FFFFFFFCh, whereas, assuming that BATT\_CTRL
was 00000000h, ANDing it with FFFFFFFCh would simply leave it unchanged...
unless the hardware (or maybe a game) sets some bits in BATT\_CTRL to nonzero
values...?<br/>

#### Battery Low Interrupt
```
  INT_INPUT.10    IRQ     Battery Low     (0=Normal, 1=Battery Low)
```
Can be used to sense if the battery is low, if so, one may disable sound output
and/or reduce the CPU speed to increase the remaining battery lifetime. Unknown
how long the battery lasts, and how much the lifetime is affected by audio,
video, infrared, cpu speed, and sleep mode...?<br/>
The pocketstation can be also powered through the VCC pin (ie. when docked to
the PSX, then it's working even if the battery is empty; or even without
battery).<br/>



