---
name: memory-cards
description: "PSX Memory Cards: read/write command protocol (81h/52h/57h), data format (16KB, 15 blocks, directory, icon frames), save file structure, memory card image formats. Use when working with memory card I/O, save file management, or card image conversion."
---

##   Memory Card Read/Write Commands
#### Reading Data from Memory Card
```
  Send Reply Comment
  81h  N/A   Memory card address
  52h  FLAG  Send Read Command (ASCII "R"), Receive FLAG Byte
  00h  5Ah   Receive Memory Card ID1
  00h  5Dh   Receive Memory Card ID2
  MSB  (00h) Send Address MSB  ;\sector number (0..3FFh)
  LSB  (pre) Send Address LSB  ;/
  00h  5Ch   Receive Command Acknowledge 1  ;<-- late /ACK after this byte-pair
  00h  5Dh   Receive Command Acknowledge 2
  00h  MSB   Receive Confirmed Address MSB
  00h  LSB   Receive Confirmed Address LSB
  00h  ...   Receive Data Sector (128 bytes)
  00h  CHK   Receive Checksum (MSB xor LSB xor Data bytes)
  00h  47h   Receive Memory End Byte (should be always 47h="G"=Good for Read)
```
Non-sony cards additionally send eight 5Ch bytes after the end flag.<br/>
When sending an invalid sector number, original Sony memory cards respond with
FFFFh as Confirmed Address (and do then abort the transfer without sending any
data, checksum, or end flag), third-party memory cards typically respond with
the sector number ANDed with 3FFh (and transfer the data for that adjusted
sector number).<br/>

#### Writing Data to Memory Card
```
  Send Reply Comment
  81h  N/A   Memory card address
  57h  FLAG  Send Write Command (ASCII "W"), Receive FLAG Byte
  00h  5Ah   Receive Memory Card ID1
  00h  5Dh   Receive Memory Card ID2
  MSB  (00h) Send Address MSB  ;\sector number (0..3FFh)
  LSB  (pre) Send Address LSB  ;/
  ...  (pre) Send Data Sector (128 bytes)
  CHK  (pre) Send Checksum (MSB xor LSB xor Data bytes)
  00h  5Ch   Receive Command Acknowledge 1
  00h  5Dh   Receive Command Acknowledge 2
  00h  4xh   Receive Memory End Byte (47h=Good, 4Eh=BadChecksum, FFh=BadSector)
```

#### Get Memory Card ID Command
```
  Send Reply Comment
  81h  N/A   Memory card address
  53h  FLAG  Send Get ID Command (ASCII "S"), Receive FLAG Byte
  00h  5Ah   Receive Memory Card ID1
  00h  5Dh   Receive Memory Card ID2
  00h  5Ch   Receive Command Acknowledge 1
  00h  5Dh   Receive Command Acknowledge 2
  00h  04h   Receive 04h
  00h  00h   Receive 00h
  00h  00h   Receive 00h
  00h  80h   Receive 80h
```
This command is supported only by original Sony memory cards. Not sure if all
sony cards are responding with the same values, and what meaning they have,
might be number of sectors (0400h) and sector size (0080h) or whatever.<br/>

#### Invalid Commands
```
  Send Reply Comment
  81h  N/A   Memory card address
  xxh  FLAG  Send Invalid Command (anything else than "R", "W", or "S")
```
Transfer aborts immediately after the faulty command byte, or, occasionally
after one more byte (with response FFh to that extra byte).<br/>

#### FLAG Byte
The initial value of the FLAG byte on power-up (and when re-inserting the
memory card) is 08h.<br/>
Bit3=1 is indicating that the directory wasn't read yet (allowing to sense
memory card changes). For some strange reason, bit3 is NOT reset when reading
from the card, but rather when writing to it. To reset the flag, games are
usually issuing a dummy write to sector number 003Fh, more or less
unneccessarily stressing the lifetime of that sector.<br/>
Bit2=1 seems to be intended to indicate write errors, however, the write
command seems to be always finishing without setting that bit, instead, the
error flag may get set on the NEXT command.<br/>
Note: Some (not all) non-sony cards also have Bit5 of the FLAG byte set.<br/>

#### Timings
IRQ7 is usually triggered circa 1500 cycles after sending a byte (counted from
the begin of the first bit), except, the last byte doesn't trigger IRQ7, and,
after the 7th byte of the Read command, an additional delay of circa 31000
cycles occurs before IRQ7 gets triggered (that strange extra delay occurs only
on original Sony cards, not on cards from other manufacturers).<br/>
There seems to be no extra delays in the Write command, as it seems, the data
is written on the fly, and one doesn't need to do any write-busy handling...
although, theoretically, the write shouldn't start until verifying the
checksum... so it can't be done on the fly at all...?<br/>

#### Notes
Responses in brackets are don't care, (00h) means usually zero, (pre) means
usually equal to the previous command byte (eg. the response to LSB is MSB).<br/>

Memory cards are reportedly "Flash RAM" which sounds like bullshit, might be
battery backed SRAM, or FRAM, or slower EEPROM or FLASH ROM, or vary from card
to card...?<br/>



##   Memory Card Data Format
#### Data Size
```
  Total Memory 128KB = 131072 bytes = 20000h bytes
  1 Block 8KB = 8192 bytes = 2000h bytes
  1 Frame 128 bytes = 80h bytes
```
The memory is split into 16 blocks (of 8 Kbytes each), and each block is split
into 64 sectors (of 128 bytes each). The first block is used as Directory, the
remaining 15 blocks are containing Files, each file can occupy one or more
blocks.<br/>

#### Header Frame (Block 0, Frame 0)
```
  00h-01h Memory Card ID (ASCII "MC")
  02h-7Eh Unused (zero)
  7Fh     Checksum (all above bytes XORed with each other) (usually 0Eh)
```

#### Directory Frames (Block 0, Frame 1..15)
```
  00h-03h Block Allocation State
            00000051h - In use ;first-or-only block of a file
            00000052h - In use ;middle block of a file (if 3 or more blocks)
            00000053h - In use ;last block of a file   (if 2 or more blocks)
            000000A0h - Free   ;freshly formatted
            000000A1h - Free   ;deleted (first-or-only block of file)
            000000A2h - Free   ;deleted (middle block of file)
            000000A3h - Free   ;deleted (last block of file)
  04h-07h Filesize in bytes (2000h..1E000h; in multiples of 8Kbytes)
  08h-09h Pointer to the NEXT block number (minus 1) used by the file
            (ie. 0..14 for Block Number 1..15) (or FFFFh if last-or-only block)
  0Ah-1Eh Filename in ASCII, terminated by 00h (max 20 chars, plus ending 00h)
  1Fh     Zero (unused)
  20h-7Eh Garbage (usually 00h-filled)
  7Fh     Checksum (all above bytes XORed with each other)
```
Filesize [04h..07h] and Filename [0Ah..1Eh] are stored only in the first
directory entry of a file (ie. with State=51h or A1h), other directory entries
have that bytes zero-filled.<br/>

#### Filename Notes
The first some letters of the filename should indicate the game to which the
file belongs, in case of commercial games this is conventionally done like so:
Two character region code:<br/>
```
  "BI"=Japan, "BE"=Europe, "BA"=America
```
followed by 10 character game code,<br/>
```
  in "AAAA-NNNNN" form     ;for Pocketstation executables replace "-" by "P"
```
where the "AAAA" part does imply the region too; (SLPS/SCPS=Japan,
SLUS/SCUS=America, SLES/SCES=Europe) (SCxS=Made by Sony, SLxS=Licensed by
Sony), followed by up to 8 characters,<br/>
```
  "abcdefgh"
```
(which may identify the file if the game uses multiple files; this part often
contains a random string which seems to be allowed to contain any chars in
range of 20h..7Fh, of course it shouldn't contain "?" and "\*" wildcards).<br/>

#### Broken Sector List (Block 0, Frame 16..35)
```
  00h-03h Broken Sector Number (Block*64+Frame) (FFFFFFFFh=None)
  04h-7Eh Garbage (usually 00h-filled) (some cards have [08h..09h]=FFFFh)
  7Fh     Checksum (all above bytes XORed with each other)
```
If Block0/Frame(16+N) indicates that a given sector is broken, then the data
for that sector is stored in Block0/Frame(36+N).<br/>

#### Broken Sector Replacement Data (Block 0, Frame 36..55)
```
  00h-7Fh Data (usually FFh-filled, if there's no broken sector)
```

#### Unused Frames (Block 0, Frame 56..62)
```
  00h-7Fh Unused (usually FFh-filled)
```

#### Write Test Frame (Block 0, Frame 63)
Reportedly "write test". Usually same as Block 0 ("MC", 253 zero-bytes, plus
checksum 0Eh).<br/>

#### Title Frame (Block 1..15, Frame 0) (in first block of file only)
```
  00h-01h  ID (ASCII "SC")
  02h      Icon Display Flag
             11h...Icon has 1 frame  (static) (same image shown forever)
             12h...Icon has 2 frames (animated) (changes every 16 PAL frames)
             13h...Icon has 3 frames (animated) (changes every 11 PAL frames)
            Values other than 11h..13h seem to be treated as corrupted file
            (causing the file not to be listed in the bootmenu)
  03h      Block Number (1-15)  "icon block count"  Uh?
                   (usually 01h or 02h... might be block number within
                   files that occupy 2 or more blocks)
                   (actually, that kind of files seem to HAVE title frames
                   in ALL of their blocks; not only in their FIRST block)
                   (at least SOME seem to have such duplicated title frame,
                   but not all?)
  04h-43h  Title in Shift-JIS format (64 bytes = max 32 characters)
  44h-4Fh  Reserved (00h)
  50h-5Fh  Reserved (00h)  ;<-- this region is used for the Pocketstation
  60h-7Fh  Icon 16 Color Palette Data (each entry is 16bit CLUT)
```
For more info on entries [50h..5Fh], see<br/>
[Pocketstation File Header/Icons](../pocketstation-software/SKILL.md#pocketstation-file-headericons)<br/>

#### Icon Frame(s) (Block 1..15, Frame 1..3) (in first block of file only)
```
  00h-7Fh  Icon Bitmap (16x16 pixels, 4bit color depth)
```
Note: The icons are shown in the BIOS bootmenu (which appears when starting the
PlayStation without a CDROM inserted). The icons are drawn via GP0(2Ch)
command, ie. as Textured four-point polygon, opaque, with texture-blending,
whereas the 24bit blending color is 808080h (so it's quite the same as raw
texture without blending). As semi-transparency is disabled, Palette/CLUT
values can be 0000h=FullyTransparent, or 8000h=SolidBlack (the icons are
usually shown on a black background, so it doesn't make much of a difference).<br/>

#### Data Frame(s) (Block 1..15, Frame N..63; N=excluding any Title/Icon Frames)
```
  00h-7Fh  Data
```
Note: Files that occupy more than one block are having only ONE Title area, and
only one Icon area (in the first sector(s) of their first block), the
additional blocks are using sectors 0..63 for plain data.<br/>

#### Shift-JIS Character Set (16bit) (used in Title Frames)
Can contain japanese or english text, english characters are encoded like so:<br/>
```
  81h,40h      --> SPC
  81h,43h..97h --> punctuation marks
  82h,4Fh..58h --> "0..9"
  82h,60h..79h --> "A..Z"
  82h,81h..9Ah --> "a..z"
```
Titles shorter than 32 characters are padded with 00h-bytes.<br/>
Note: The titles are \<usually\> in 16bit format (even if they consist of
raw english text), however, the BIOS memory card manager does also accept 8bit
characters 20h..7Fh (so, in the 8bit form, the title could be theoretically up
to 64 characters long, but, nethertheless, the BIOS displays only max 32
chars).<br/>
For displaying Titles, the BIOS includes a complete Shift-JIS character set,<br/>
[BIOS Character Sets](../bios-boot-internals/SKILL.md#bios-character-sets)<br/>
Shift-JIS is focused on asian languages, and does NOT include european letters
(eg. such with accent marks). Although the non-japanese PSX BIOSes DO include a
european character set, the BIOS memory card manager DOESN'T seem to translate
any title character codes to that character set region.<br/>



##   Memory Card Images
There are a lot of different ways to get a save from a memory card onto your
PC's hard disk, and these ways sometimes involve sticking some additional
information into a header at the beginning of the file.<br/>

#### Raw Memory Card Images (without header) (ie. usually 128K in size)
```
  SmartLink .PSM,
  WinPSM .PS,
  DataDeck .DDF,
  FPSX .MCR,
  ePSXe .MCD...
```
don't stick any header on the data at all, so you can just read it in and treat
it like a raw memory card.<br/>

All of these headers contain a signature at the top of the file. The three most
common formats and their signatures are:<br/>

```
     Connectix Virtual Game Station format (.MEM): "VgsM", 64 bytes
     PlayStation Magazine format (.PSX): "PSV", 256 bytes
```

some programs will OMIT any blank or unallocated blocks from the end of the
memory card -- if only three save blocks on the card are in use, for example,
saving the other twelve is pointless.<br/>

#### Xploder and Action Replay Files (54 byte header)
```
  00h..14h Filename in ASCII, terminated by 00h (max 20 chars, plus ending 00h)
  15h..35h Title in ASCII, terminated by 00h (max 32 chars, plus ending 00h)
  36h..    File Block(s) (starting with the Title sector)
```
This format contains only a single file (not a whole memory card). The filename
should be the same as used in the Memory Card Directory. The title is more or
less don't care; it may be the SHIFT-JIS title from the Title Sector converted
to ASCII.<br/>

#### .MCS Files (Single Save Format)
MCS files consist of the 128 byte directory frame for the savefile's first block followed by all of that savefile's blocks in linked list order. When importing this format, the directory frame should be parsed for the save filename and the filesize while other fields should be ignored. The rest of the directory frame fields and any extra directory frames, in the case of multi-block saves, should be reconstructed based on the destination memory card.

#### .GME Files (usually 20F40h bytes)
InterAct GME format, produced by the DexDrive.<br/>
```
  000h 12   ASCII String "123-456-STD",00h
  00Ch 4    Usually zerofilled (or meaningless garbage in some files)
  010h 5    Always 00h,00h,01h,00h,01h
  015h 16   Copy of Sector 0..15 byte[00h] ;"M", followed by allocation states
  025h 16   Copy of Sector 0..15 byte[08h] ;00h, followed by next block values
  035h 11   Usually zerofilled (or meaningless garbage in some files)
  040h F00h Fifteen Description Strings (each one 100h bytes, padded with 00h)
  F40h 128K Memory Card Image (128K) (unused sectors 00h or FFh filled)
```
This is a very strange file format, no idea where it comes from. It contains a
F40h bytes header (mainly zerofilled), followed by the whole 128K of FLASH
memory (mainly zerofilled, too, since it usually contains only a small single
executable file).<br/>



##   Memory Card Notes
#### Sony PSX Memory Cards
Sony has manufactured only 128KByte memory cards for PSX, no bigger/smaller
ones.<br/>

#### Sony PS2 Memory Cards
A special case would be PS2 cards, these are bigger, but PS2 cards won't fit
into PSX cards slots (unless when cutting an extra notch in the card edge
connector), a PSX game played on a PS2 console could theoretically access PS2
cards (if it supports the different directory structure on that cards).<br/>

#### Third Party Cards with bigger capacity
Some third party cards contain larger memory chips, however, the PSX
games/kernel are supporting only regular 128Kbyte cards, so the extra memory
can be used only by dividing it into several 128Kbyte memory card images.<br/>
Selecting a different memory card image can be done by a switch or button on
the card, or via joypad key combinations (joypad/card are sharing the same
signals, so the card could watch the traffic on joypad bus, provided that the
MIPS CPU is actually reading the joypad).<br/>

#### Third Party Cards with bigger capacity and Data Compression
Some cards are additionally using data compression to increase the card
capacity, but that techinque is having rather bad reputation and could result
in data loss. For example, if a game has allocated four blocks on the memory
card, then it'll expect to be able to overwrite that four blocks at any time
(without needing to handle "memory card full" errors), however, if the card is
full, and if the newly written data has worse compression ratio, then the card
will be unable to store the new game position (and may have already overwritten
parts of the old game position). As a workaround, such cards may use a LED to
warn users when running low on memory (ideally, there should be always at least
128Kbytes of free memory).<br/>

#### Joytech Smart Card Adaptor
The smart card adaptor plugs into memory card slot, and allows to use special
credit card-shaped memory cards. There don't seem to be any special features,
ie. the hardware setup does just behave like normal PSX memory cards.<br/>

#### Datel VMEM (virtual memory card storage on expansion port)
The Datel/Interact VMEM exists as standalone VMEM cartridge, and some Datel
Cheat Devices do also include the VMEM feature. Either way, the VMEM connects
to expansion port, and contain some large FLASH memory, for storing multiple
memory cards on it. Unknown, how that memory is accessed (maybe it must be
copied to a regular memory card, or maybe they've somehow hooked the Kernel (or
even the hardware signals?) so that games could directly access the VMEM?<br/>

#### Passwords (instead of Memory Cards)
Some older games are using passwords instead of memory cards to allow the user
to continue at certain game positions. That's nice for people without memory
card, but unfortunately many of that games are restricted to it - it'd be more
user friendly to support both passwords, and, optionally, memory cards.<br/>

#### Yaroze Access Cards (DTL-H3020)
The Yaroze Access Card connects to memory card slot, the card resembles regular
memory cards, but it doesn't contain any storage memory. Instead, it does
merely support a very basic Access Card detection command:<br/>
```
  Send Reply Comment
  21h  N/A?  Probably replies HighZ (ie. probably reads FFh)?
  53h  0xh?  Replies unknown 8bit value (upper 4bit are known to be zero)?
```
Ie. when receiving 21h as first byte, it replies by an ACK, and does then
output 0xh as response to the next byte.<br/>
Without the Access Card, the Yaroze Bootdisc will refuse to work (the disc
contains software for transferring data to/from PC, for developing homebrew
games).<br/>

#### Pocketstation (Memory Card with built-in LCD screen and buttons)
[Pocketstation](../pocketstation-hardware/SKILL.md)<br/>
