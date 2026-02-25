---
name: cdrom-format-sectors
description: "CDROM disk format: physical layout (tracks, sessions, lead-in/out), subchannel data (P-Q-R-W), sector encoding (CIRC, L1/L2 ECC, EDC), scrambling. Use when working with raw sector data, subchannel processing, or error correction."
---

#   CDROM Format
#### General CDROM Disk Format
[CDROM Disk Format](cdromformat.md#cdrom-disk-format)<br/>
[CDROM Subchannels](cdromformat.md#cdrom-subchannels)<br/>
[CDROM Sector Encoding](cdromformat.md#cdrom-sector-encoding)<br/>
[CDROM Scrambling](cdromformat.md#cdrom-scrambling)<br/>
[CDROM XA Subheader, File, Channel, Interleave](cdromformat.md#cdrom-xa-subheader-file-channel-interleave)<br/>
[CDROM XA Audio ADPCM Compression](cdromformat.md#cdrom-xa-audio-adpcm-compression)<br/>
[CDROM ISO Volume Descriptors](cdromformat.md#cdrom-iso-volume-descriptors)<br/>
[CDROM ISO File and Directory Descriptors](cdromformat.md#cdrom-iso-file-and-directory-descriptors)<br/>
[CDROM ISO Misc](cdromformat.md#cdrom-iso-misc)<br/>
[CDROM File Formats](cdromfileformats.md)<br/>
[CDROM Video CDs (VCD)](cdromvideocdsvcd.md)<br/>

#### Playstation CDROM Protection
[CDROM Protection - SCEx Strings](cdromformat.md#cdrom-protection-scex-strings)<br/>
[CDROM Protection - Bypassing it](cdromformat.md#cdrom-protection-bypassing-it)<br/>
[CDROM Protection - Modchips](cdromformat.md#cdrom-protection-modchips)<br/>
[CDROM Protection - Chipless Modchips](cdromformat.md#cdrom-protection-chipless-modchips)<br/>
[CDROM Protection - LibCrypt](cdromformat.md#cdrom-protection-libcrypt)<br/>



##   CDROM Disk Format
#### Overview
The PSX uses a ISO 9660 filesystem, with data stored on CD-XA (Mode2) Sectors.
ISO 9660 is standard for CDROM disks, although newer CDROMs may use extended
filesystems, allowing to use long filenames and lowercase filenames, the PSX
Kernel doesn't support such stuff, and, in fact, it's putting some restrictions
on the ISO standard: it's limiting file names to MSDOS-style 8.3 format, and
it's allowing only a limited number of files and directories per disk.<br/>

#### CDROM Filesystem (ISO 9660 aka ECMA-119)
```
  Originally intended for Mode1 Sectors (but is also used for CD-XA Mode2)
  Supports "FILENAME.EXT;VERSION" filenames (version is usually "1")
  Supports all-uppercase filenames and directory names (0-9, A-Z, underscore)
  For PSX: Max 8-character filenames with max 3-character extensions
  For PSX: Max 8-character directory names, without extension
  For PSX: Max one sector per directory (?)
  For PSX: Max one sector (or less?) per path table (?)
```

#### CDROM Extended Architecture (CD-ROM XA aka CD-XA)
```
  Uses Mode2 Sectors (see Sector Encoding chapter)
  Allows 800h or 914h byte data per sector (with/without error correction)
  Allows to break interleaved data into separate files/channels
  Supports XA-ADPCM compressed audio data
  Stores "CD-XA001" at 400h Primary Volume Descriptor (?)
  Stores 14 extra bytes in System Use area (LEN_SU) of Directory Entries
```

#### Physical Audio/CDROM Disk Format (ISO/IEC 10149 aka ECMA-130)
```
  Defines physical metrics of the CDROM and Audio disks
  Defines Sub-channels and Track.Index and Minute.Second.Fraction numbering
  Defines 14bit-per-byte encoding, and splits sectors into frames
  Defines ECC and EDC (error correction and error detection codes)
```

#### Available Documentation
ISO documents are commercial standards (not available for download), however,
they are based on ECMA standards (which are free for download, however, the
ECMA stuff is in PDF format, so one may treat it as commercial bullshit, too).
CD-ROM XA is commercial only (not available for download), and, CD-XA doesn't
seem to have become very popular outside of the PSX-world, so there's very
little information available, portions of CD-XA are also used in the CD-i
standard (which may be a little better or worse documented).<br/>

#### Stuff
```
  sessions  one or more sessions per disk
  tracks    99 tracks per disk     (01h..99h) (usually only 01h on Data Disks)
  index     99 indices per track   (01h..99h) (rarely used, usually always 01h)
  minutes   74 minutes per disk    (00h..73h) (or more, with some restrictions)
  seconds   60 seconds per minute  (00h..59h)
  sectors   75 sectors per second  (00h..74h)
  frames    98 frames per sector
  bytes     33 bytes per frame (24+1+8 = data + subchannel + error correction)
  bits      14 bits per byte   (256 valid combinations, and many invalid ones)
```

#### Track.Index (stored in subchannel, in BCD format)
Multiple Tracks are usually used only on Audio Disks (one track for each song,
numbered 01h and up), a few Audio Disks may also split Tracks into separate
fragments with different Index values (numbered 01h and up, but most tracks
have only Index 01h). A simple Data Disk would usually contain only one Track
(all sectors marked Track=01h and Index=01h), although some more complex Data
Disks may have multiple Data tracks and/or Audio tracks.<br/>

#### Minute.Second.Sector (stored in subchannel, and in Data sectors, BCD format)
The sectors on CDROMs and CD Audio disks are numbered in Minutes, Seconds, and
1/75 fragments of a second (where a "second" is referring to single-speed
drives, ie. the normal CD Audio playback speed).<br/>
Minute.Second.Sector is stored twice in the subchannel (once the "absolute"
time, and once the "local" time).<br/>
The "absolute" sector number (counted from the begin of the disk) is mainly
relevant for Seek purposes (telling the controller if the drive head is on the
desired location, or if it needs to move the head backwards or forwards).<br/>
The "local" sector number (counted from the begin of the track) is mainly
relevant for Audio Players, allowing to pass the data directly to the
Minute:Second display, without needing to subtract the start address of the
track.<br/>
Data disks are additionally storing the "absolute" values in their Data Areas,
basically that's just the subchannel data duplicated, but more precisely
assigned - the problem with the subchannel data is that the CD Audio standard
seems to lack a clear definition that would assign the begin of the sub-channel
block to the exact begin of a sector; so, when using only the subchannel data,
some Drive Controllers may assign the begin of a new sector to another location
as than other Controllers do, for Audio Disks that isn't too much of a problem,
but for Data Disks it'd be fatal.<br/>

#### Subchannels
Each frame contains 8 subchannel bits (named P,Q,R,S,T,U,V,W). So, a sector
(with 98 frames) contains 98 bits (12.25 bytes) for each subchannel.<br/>
[CDROM Subchannels](cdromformat.md#cdrom-subchannels)<br/>

#### Error Correction
Each Frame contains 8 bytes Error Correction information, which is mainly used
for Audio Disks, but it isn't 100% fail-proof, for that reason, Data Disks are
containing additional Error Correction in the 930h-byte data area (the audio
correction is probably focusing on repairing the MSBs of the 16bit samples, and
gives less priority on the LSBs). Error Correction is some kind of a huge
complex checksum, which allows to detect the location of faulty bytes, and to
fix them.<br/>

#### 930h-Byte Sectors
The "user" area for each sector is 930h bytes (2352 bytes). That region is
combined of the 24-byte data per frame (and excludes the 8-byte audio error
correction info, and the 1-byte subchannel data).<br/>
Most CDROM Controllers are only giving access to this 930h-byte region (ie.
there's no way to read the audio error correction info by software, and only
limited access to the subchannel data, such like allowing to read only the
Q-channel for showing track/minute/second in audio playback mode).<br/>
On Audio disks, the 930h bytes are plain data, on Data disks that bytes are
containing headers, error correction, and usually only 800h bytes user data
(for more info see Sector Encoding chapter).<br/>

#### Sessions
Multi-Sessions are mainly used on CDR's, allowing to append newer data at the
end of the disk at a later time. First of, the old session must contain a flag
indicating that there may be a newer session, telling the CDROM Controller to
search if one such exists (and if that is equally flagged, to search for an
even newer session, and so on until reaching the last and newest session).<br/>
Each session contains a complete new ISO Volume Descriptor, and may
additionally contain new Path Tables, new Directories, and new Files. The
Driver Controller is usually recursing only the Volume Descriptor of the newest
session. However, the various Directory Records of the new session may refer to
old files or old directories from previous sessions, allowing to "import" the
older files, or to "rename" or "delete" them by assigning new names to that
files, or by removing them from the directory.<br/>
The PSX is reportedly not supporting multi-session disks, but that doesn't seem
to be correct, namely, the Setsession command is apparently intended for that
purpose... though not sure if the PSX Kernel is automatically searching the
newest session... otherwise the boot executable in the first session would need
to do that manually by software, and redirect control to the boot executable in
the last session.<br/>



##   CDROM Subchannels
#### Subchannel P
Subchannel P contains some kind of a Pause flag (to indicate muted areas
between Audio Tracks). This subchannel doesn't have any checksum, so the data
cannot be trusted to be intact (unless when sensing a longer stream of
all-one's, or all zero's). Theoretically, the 98 pause bits are somehow
associated to the 98 audio frames (with 24 audio bytes each) of the sector.
However, reportedly, Subchannel P does contain two sync bits, if that is true,
then there'd be only 96 pause flags for 98 audio frames. Strange.<br/>
Note: Another way to indicate "paused" regions is to set Subchannel Q to ADR=1
and Index=00h.<br/>

#### Subchannel Q
contains the following information:<br/>
```
  Bits Expl.
  2    Sub-channel synchronization field
  8    ADR/Control (see below)
  72   Data (content depends on ADR)
  16   CRC-16-CCITT error detection code (big-endian: bytes ordered MSB, LSB)
```
Possible values for the ADR/Control field are:<br/>
```
  Bit0-3 ADR (0=No data, 1..3=see below, 4..0Fh=Reserved)
  Bit4   Audio Preemphasis  (0=No, 1=Yes)      (Audio only, must be 0 for Data)
  Bit5   Digital Copy       (0=Prohibited, 1=Allowed)
  Bit6   Data               (0=Audio, 1=Data)
  Bit7   Four-Channel Audio (0=Stereo, 1=Quad) (Audio only, must be 0 for Data)
```
The 72bit data regions are, depending on the ADR value...<br/>

#### Subchannel Q with ADR=1 during Lead-In -- Table of Contents (TOC)
```
  8    Track number (fixed, must be 00h=Lead-in)
  8    Point (01h..99h or A0h..A2h, see last three bytes for more info)
  24   MSF address (incrementing address within the Lead-in area)
         Note: On some disks, these values are choosen so that the lead-in
         <starts> at 00:00:00, on other disks so that it <ends> at 99:59:74.
  8    Reserved (00h)
```
When Point=01h..99h (Track 1..99) or Point=A2h (Lead-Out):<br/>
```
  24   MSF address (absolute address, start address of the "Point" track)
```
When Point=A0h (First Track Number):<br/>
```
  8    First Track number (BCD)
  8    Disk Type Byte (00h=CD-DA or CD-ROM, 10h=CD-I, 20h=CD-ROM-XA)
  8    Reserved (00h)
```
When Point=A1h (Last Track Number):<br/>
```
  8    Last Track number (BCD)
  16   Reserved (0000h)
```
ADR=1 should exist in 3 consecutive lead-in sectors.<br/>

#### Subchannel Q with ADR=1 in Data region -- Position
```
  8    Track number (01h..99h=Track 1..99)
  8    Index number (00h=Pause, 01h..99h=Index within Track)
  24   Track relative MSF address (decreasing during Pause)
  8    Reserved (00h)
  24   Absolute MSF address
```
ADR=1 is required to exist in at least 9 out of 10 consecutive data sectors.<br/>

#### Subchannel Q with ADR=1 during Lead-Out -- Position
```
  8    Track number (fixed, must be AAh=Lead-Out)
  8    Index number (fixed, must be 01h) (there's no Index=00h in Lead-Out)
  24   Track relative MSF address (increasing, 00:00:00 and up)
  8    Reserved (00h)
  24   Absolute MSF address
```
ADR=1 should exist in 3 consecutive lead-out sectors (and may then be followed
by ADR=5 on multisession disks).<br/>

#### Subchannel Q with ADR=2 -- Catalogue number of the disc (UPC/EAN barcode)
```
  52   EAN-13 barcode number (13-digit BCD)
  12   Reserved (000h)
  8    Absolute Sector number (BCD, 00h..74h) (always 00h during Lead-in)
```
If the first digit of the EAN-13 number is "0", then the remaining digits are a
UPC-A barcode number. Either the 13-digit EAN-13 number, or the 12-digit UPC-A
number should be printed as barcode on the rear-side of the CD package.<br/>
The first some digits contain a country code (EAN only, not UPC), followed by a
manufacturer code, followed by a serial number. The last digit contains a
checksum, which can be calculated as 250 minus the sum of the first 12 digits,
minus twice the sum of each second digit, modulated by 10.<br/>
ADR=2 isn't included on all CDs, and, many CDs do have ADR=2, but the 13 digits
are all zero. Most CDROM drives do not allow to read EAN/UPC numbers.<br/>
If present, ADR=2 should exist in at least 1 out of 100 consecutive sectors.
ADR=2 may occur also in Lead-in.<br/>

#### Subchannel Q with ADR=3 -- ISRC number of the current track
(ISO 3901 and DIN-31-621):<br/>
```
  12   Country Code      (two 6bit characters)   (ASCII minus 30h) ;eg. "US"
  18   Owner Code        (three 6bit characters) (ASCII minus 30h)
  2    Reserved          (zero)
  8    Year of recording (2-digit BCD) ;eg. 82h for 1982
  20   Serial number     (5-digit BCD) ;usually increments by 1 or 10 per track
  4    Reserved          (zero)
  8    Absolute Sector number (BCD, 00h..74h) (always 00h during Lead-in)
```
Most CDROM drives for PC's do not allow to read ISRC numbers (or even worse,
they may accidently return the same ISRC number on every two tracks).<br/>
If present, ADR=3 should exist in at least 1 out of 100 consecutive sectors.
However, reportedly, ADR=3 should not occur in Lead-in.<br/>

#### Subchannel Q with ADR=5 in Lead-in -- Multisession Lead-In Info
When Point=B0h:<br/>
```
  8    Track number (fixed, must be 00h=Lead-in)
  8    POINT = B0h (multi-session disc)
  24   MM:SS:FF = the start time for the next possible session's program area,
       a final session is indicated by FFh:FFh:FFh,
       or when the ADR=5 / Point=B0h is absent.
  8    Number of different Mode-5 pointers present.
  24   MM:SS:FF = the maximum possible start time of the outermost Lead-out
```
When Point=C0h:<br/>
```
  8    Track number (fixed, must be 00h=Lead-in)
  8    POINT = C0h (Identifies a Multisession disc, together with POINT=B0h)
  24   ATIP values from Special Information 1, ID=101
  8    Reserved (must be 00h)
  24   MM:SS:FF = Start time of the first Lead-in area of the disc
```
And, optionally, when Point=C1h:<br/>
```
  8    Track number (fixed, must be 00h=Lead-in)
  8    POINT=C1h
  8x7  Copy of information from A1 point in ATIP
```

#### Subchannel Q with ADR=5 in Lead-Out -- Multisession Lead-Out Info
```
  8    Track number (fixed, must be AAh=Lead-out)
  8    POINT = D1h (Identifies a Multisession lead-out)
  24   Usually zero (or maybe ATIP as in Lead-In with Point=C0h...?)
  8    Seems to be the session number?
  24   MM:SS:FF = Absolute address of the First data sector of the session
```
Present in 3 consequtive sectors (3x ADR=1, 3x ADR=5, 3x ADR=1, 3x ADR=5, etc).<br/>

#### Subchannel Q with ADR=5 in Lead-in -- CDR/CDRW Skip Info (Audio Only)
When Point=01h..40h:<br/>
```
  8    Track number (fixed, must be 00h=Lead-in)
  8    POINT=01h..40h (This identifies a specific playback skip interval)
  24   MM:SS:FF Skip interval stop time in 6 BCD digits
  8    Reserved (must be 00h)
  24   MM:SS:FF Skip interval start time in 6 BCD digits
```
When Point=B1h:<br/>
```
  8    Track number (fixed, must be 00h=Lead-in)
  8    POINT=B1h (Audio only: This identifies the presence of skip intervals)
  8x4  Reserved (must be 00h,00h,00h,00h)
  8    the number of skip interval pointers in POINT=01h..40h
  8    the number of skip track assignments in POINT=B2h..B4h
  8    Reserved (must be 00h)
```
When Point=B2h,B3h,B4h:<br/>
```
  8    Track number (fixed, must be 00h=Lead-in)
  8    POINT=B2h,B3h,B4h (This identifies tracks that should be skipped)
  8    1st Track number to skip upon playback (01h..99h, must be nonzero)
  8    2nd Track number to skip upon playback (01h..99h, or 00h=None)
  8    3rd Track number to skip upon playback (01h..99h, or 00h=None)
  8    Reserved (must be 00h)... unclear... OR... 4th (of 7) skip info's...?
  8    4th Track number to skip upon playback (01h..99h, or 00h=None)
  8    5th Track number to skip upon playback (01h..99h, or 00h=None)
  8    6th Track number to skip upon playback (01h..99h, or 00h=None)
```
Note: Skip intervals are seldom written by recorders and typically ignored by
readers.<br/>

#### Subchannel R..W
Subchannels R..W are usually unused, except for some extended formats:<br/>
```
  CD-TEXT in the Lead-In area (see below)
  CD-TEXT in the Data area    (rarely used)
  CD plus Graphics (CD+G)     (rarely used)
```
Most CDROM drives do not allow to read these subchannels. CD-TEXT was designed
by Sony and Philips in 1997, so it should be found only on (some) newer discs.
Most CD/DVD players don't support it (the only exception is that CD-TEXT seems
to be popular for car hifi equipment). Most record labels don't support
CD-TEXT, even Sony seems to have discontinued it on their own records after
some years (so CD-TEXT is very rare on original disks, however, CDR software
does often allow to write CD-TEXT on CDRs).<br/>

#### Subchannel R..W, when used for CD-TEXT in the Lead-In area
CD-TEXT is stored in the six Subchannels R..W. Of the 12.25 bytes (98 bits) per
subchannel, only 12 bytes are used. Together, all 6 subchannels have a capacity
of 72 bytes (6x12 bytes) per sector. These 72 bytes are divided into four
CD-TEXT fragments (of 18 bytes each). The format of these 18 bytes is:<br/>
```
  00h 1  Header Field ID1: Pack Type Indicator
  01h 1  Header Field ID2: Track Number
  02h 1  Header Field ID3: Sequence Number
  03h 1  Header Field ID4: Block Number and Character Position Indicator
  04h 12 Text/Data Field
  10h 2  CRC-16-CCITT (big-endian) (across bytes 00h..0Fh)
```
ID1 - Pack Type Indicator:<br/>
```
  80h   Titel      (TEXT)
  81h   Performer  (TEXT)
  82h   Songwriter (TEXT)
  83h   Composer   (TEXT)
  84h   Arranger   (TEXT)
  85h   Message    (TEXT)
  86h   Disc ID    (TEXT?)  (content/format/purpose unknown?)
  87h   Genre      (BINARY) (ID codes unknown?)
  88h   TOC        (BINARY) (content/format/purpose unknown?)
  89h   TOC2       (BINARY) (content/format/purpose unknown?)
  8Ah   Reserved for future
  8Bh   Reserved for future
  8Ch   Reserved for future
  8Dh   Reserved for "content provider" aka "closed information"
  8Eh   UPC/EAN and ISRC Codes (TEXT) (content/format/purpose unknown?)
  8Fh   Blocksize (BINARY) (see below)
```
ID2 - Track Number:<br/>
```
  00h       Title/Performer/etc. for the Disc
  01h..63h  Title/Performer/etc. for Track 1..99 (Non-BCD) (Bit7=Extension)
```
ID3 - Sequence Number:<br/>
```
  00h..FFh  Incrementing Number (00h=First 18-byte fragment, 01h=Second, etc.)
```
ID4 - Block Number and Character Position Indicator:<br/>
```
  Bit7      Character Set      (0=8bit, 1=16bit)
  Bit6-4    Block Number       (0..7 = Language number, as set by "Blocksize")
  Bit3-0    Character Position (0..0Eh=Position, 0Fh=Append to prev fragment)
```
Example Data (generated with CDRWIN):<br/>
```
  ID TR SQ CH <------------Text/Data------------> -CRC-  <---Text--->
  80 00 00 00 54 65 73 74 44 69 73 6B 54 69 74 6C E2 22  TestDiskTitl
  80 00 01 0C 65 00 54 65 73 74 54 72 61 63 6B 54 C9 1B  e.TestTrackT
  80 01 02 0A 69 74 6C 65 31 00 54 65 73 74 54 72 40 3A  itle1.TestTr
  80 02 03 06 61 63 6B 54 69 74 6C 65 32 00 00 00 80 E3  ackTitle2...
  81 00 04 00 54 65 73 74 44 69 73 6B 50 65 72 66 03 DF  TestDiskPerf
  81 00 05 0C 6F 72 6D 65 72 00 54 65 73 74 54 72 12 A5  ormer.TestTr
  81 01 06 06 61 63 6B 50 65 72 66 6F 72 6D 65 72 BC 5B  ackPerformer
  81 01 07 0F 31 00 54 65 73 74 54 72 61 63 6B 50 AC 41  1.TestTrackP
  81 02 08 0A 65 72 66 6F 72 6D 65 72 32 00 00 00 64 1A  erformer2...
  8F 00 09 00 01 01 02 00 04 05 00 00 00 00 00 00 6D E2  ............
  8F 01 0A 00 00 00 00 00 00 00 00 03 0B 00 00 00 CD 0C  ............
  8F 02 0B 00 00 00 00 00 09 00 00 00 00 00 00 00 FC 8C  ............
  00   ;<--- for some reason, CDRWIN stores an ending 00h byte in .CDT files
```
Each Text string is terminated by a 00h byte (or 0000h for 16bit character
set). If there's still room in the 12-byte data region, then first characters
for the next Text string (for the next track) are appended after the 00h byte
(if there's no further track, then the remaining bytes should be padded with
00h).<br/>
The "Blocksize" (ID1=8Fh) consists of three packs with 24h bytes of data (first
0Ch bytes stored with ID2=00h, next 0Ch bytes with ID2=01h, and last 0Ch bytes
with ID2=02h):<br/>
```
  00h  1   Character set (00h,01h,80h,81h,82h = see below)
  01h  1   First track number (usually/always 01h)
  02h  1   Last track number (01h..63h)
  03h  1   1bit-cd-text-in-data-area-flag, 7bit-copy-protection-flags
  04h  16  Number of 18-byte packs for ID1=80h..8Fh
  14h  8   Last sequence number of block 0..7 (or 00h=none)
  1Ch  8   Language codes for block 0..7 (definitions are unknown)
```
Character Set values (for ID1=8Fh, ID2=00h, DATA[0]=charset):<br/>
```
  00h ISO 8859-1
  01h ISO 646, ASCII
  80h MS-JIS
  81h Korean character code
  82h Mandarin (standard) Chinese character code
  Other = reserved
```
"In case the same character stings is used for consecutive tracks, character
09h (or 0909h for 16bit charset) may be used to indicate the same as previous
track. It shall not used for the first track."<br/>

#### adjust\_crc\_16\_ccitt(addr\_len)  ;for CD-TEXT and Subchannel Q
```
  lsb=00h, msb=00h      ;-initial value (zero for both CD-TEXT and Sub-Q)
  for i=0 to len-1      ;-len (10h for CD-TEXT, 0Ah for Sub-Q)
    x = [addr+i] xor msb
    x = x xor (x shr 4)
    msb = lsb xor (x shr 3) xor (x shl 4)
    lsb = x xor (x shl 5)
  next i
  [addr+len+0]=msb xor FFh, [addr+len+1]=lsb xor FFh   ;inverted / big-endian
```



##   CDROM Sector Encoding
#### Audio
```
  000h 930h Audio Data (2352 bytes) (LeftLsb,LeftMsb,RightLsb,RightMsb)
```
#### Mode0 (Empty)
```
  000h 0Ch  Sync   (00h,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,00h)
  00Ch 4    Header (Minute,Second,Sector,Mode=00h)
  010h 920h Zerofilled
```
#### Mode1 (Original CDROM)
```
  000h 0Ch  Sync   (00h,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,00h)
  00Ch 4    Header (Minute,Second,Sector,Mode=01h)
  010h 800h Data (2048 bytes)
  810h 4    EDC (checksum across [000h..80Fh])
  814h 8    Zerofilled
  81Ch 114h ECC (error correction codes)
```
#### Mode2/Form1 (CD-XA)
```
  000h 0Ch  Sync   (00h,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,00h)
  00Ch 4    Header (Minute,Second,Sector,Mode=02h)
  010h 4    Sub-Header (File, Channel, Submode AND DFh, Codinginfo)
  014h 4    Copy of Sub-Header
  018h 800h Data (2048 bytes)
  818h 4    EDC (checksum across [010h..817h])
  81Ch 114h ECC (error correction codes)
```
#### Mode2/Form2 (CD-XA)
```
  000h 0Ch  Sync   (00h,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,00h)
  00Ch 4    Header (Minute,Second,Sector,Mode=02h)
  010h 4    Sub-Header (File, Channel, Submode OR 20h, Codinginfo)
  014h 4    Copy of Sub-Header
  018h 914h Data (2324 bytes)
  92Ch 4    EDC (checksum across [010h..92Bh]) (or 00000000h if no EDC)
```

#### encode\_sector
```
  sector[000h]=00h,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,FFh,00h
  sector[00ch]=bcd(adr/75/60)      ;0..7x
  sector[00dh]=bcd(adr/75 MOD 60)  ;0..59
  sector[00eh]=bcd(adr MOD 75)     ;0..74
  sector[00fh]=mode
  if mode=00h then
    sector[010h..92Fh]=zerofilled
  if mode=01h then
    adjust_edc(sector+0, 800h+10h)
    sector[814h..817h]=00h,00h,00h,00h,00h,00h,00h,00h
    calc_p_parity(sector)
    calc_q_parity(sector)
  if mode=02h and form=1
    sector[012h]=sector[012h] AND (NOT 20h)  ;indicate not form2
    sector[014h..017h]=sector[010h..013h]    ;copy of sub-header
    adjust_edc(sector+10h,800h+8)
    push sector[00ch]           ;\temporarily clear header
    sector[00ch]=00000000h      ;/
    calc_p_parity(sector)
    calc_q_parity(sector)
    pop sector[00ch]            ;-restore header
  if mode=02h and form=2
    sector[012h]=sector[012h] OR 20h         ;indicate form2
    sector[014h..017h]=sector[010h..013h]    ;copy of sub-header
    adjust_edc(sector+10h,914h+8)            ;edc is optional for form2
```

#### calc\_parity(sector,offs,len,j0,step1,step2)
```
  src=00ch, dst=81ch+offs, srcmax=dst
  for i=0 to len-1
    base=src, x=0000h, y=0000h
    for j=j0 to 42
      x=x xor GF8_PRODUCT[j,sector[src+0]]
      y=y xor GF8_PRODUCT[j,sector[src+1]]
      src=src+step1, if (step1=2*44) and (src>=srcmax) then src=src-2*1118
    sector[dst+2*len+0]=x AND 0FFh, [dst+0]=x SHR 8
    sector[dst+2*len+1]=y AND 0FFh, [dst+1]=y SHR 8
    dst=dst+2, src=base+step2
```
calc\_p\_parity(sector) = calc\_parity(sector,0,43,19,2\*43,2)<br/>
calc\_q\_parity(sector) = calc\_parity(sector,43\*4,26,0,2\*44,2\*43)<br/>

#### adjust\_edc(addr,len)
```
  x=00000000h
  for i=0 to len-1
    x=x xor byte[addr+i], x=(x shr 8) xor edc_table[x and FFh]
  word[addr+len]=x  ;append EDC value (little endian)
```

#### init\_tables
```
  for i=0 to FFh
    x=i, for j=0 to 7, x=x shr 1, if carry then x=x xor D8018001h
    edc_table[i]=x
  GF8_LOG[00h]=00h, GF8_ILOG[FFh]=00h, x=01h
  for i=00h to FEh
    GF8_LOG[x]=i, GF8_ILOG[i]=x
    x=x SHL 1, if carry8bit then x=x xor 1dh
  for j=0 to 42
    xx=GF8_ILOG[44-j],  yy=subfunc(xx xor 1,19h)
    xx=subfunc(xx,01h), xx=subfunc(xx xor 1,18h)
    xx=GF8_LOG[xx], yy = GF8_LOG[yy]
    GF8_PRODUCT[j,0]=0000h
    for i=01h to FFh
      x=xx+GF8_LOG[i], if x>=255 then x=x-255
      y=yy+GF8_LOG[i], if y>=255 then y=y-255
      GF8_PRODUCT[j,i]=GF8_ILOG[x]+(GF8_ILOG[y] shl 8)
```

#### subfunc(a,b)
```
  if a>0 then
    a=GF8_LOG[a]-b, if a<0 then a=a+255
    a=GF8_ILOG[a]
  return(a)
```



##   CDROM Scrambling
#### Scrambling
Scambling does XOR the data sectors with random values (done to avoid regular
patterns). The scrambling is applied to Data sector bytes[00Ch..92Fh] (not to
CD-DA audio sectors, and not to the leading 12-byte Sync mark in Data sectors).<br/>
The (de-)scrambling is done automatically by the CDROM controller, so disc
images should usually contain unscrambled data (there are some exceptions such
like CD-i discs that have audio and data sectors mixed inside of the same
track; which may confuse the CDROM controller about whether or not to apply
scrambling to which sectors; so one may need to manually XOR the faulty sectors
in the disc image).<br/>
The scrambling pattern is derived from a 15bit polynomial counter (much like a
noise generator in sound chips). The data bits are XORed with the counters low
bit, and the counters lower 2bit are XORed with each other, and shifted in to
the counters upper bit. To compute 8 bits and once, and store them in a
924h-byte table:<br/>
```
  poly=0001h  ;init 15bit polynomial counter
  for i=0 to 924h-1
    scramble_table[i]=poly AND FFh
    poly=(((poly XOR poly/2) AND 0FFh)*80h) XOR (poly/100h)
  next i
```
The resulting table content should be:<br/>
```
  01h,80h,00h,60h,00h,28h,00h,1Eh,80h,08h,60h,06h,A8h,02h,FEh,81h,
  80h,60h,60h,28h,28h,1Eh,9Eh,88h,68h,66h,AEh,AAh,FCh,7Fh,01h,E0h,
  etc.
```
After scrambling, the data is reportedly "shuffled and byte-swapped". Unknown
what shuffling means. And unknown what/where/why byte-swapping is done (it does
reportedly swap each two bytes in the whole(?) 930h-byte (data-?) sector; which
might date back to different conventions for disc images to contain "16bit
audio samples" in big- or little-endian format).<br/>



