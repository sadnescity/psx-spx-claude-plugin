---
name: cdrom-file-exe-tim
description: "PSX file formats - executables and textures: PSX-EXE header and SYSTEM.CNF, CPE/SYM debug formats, TIM texture format (4/8/15/24-bit, CLUT), TGA, PCX, other bitmap formats. Use when working with PSX executables, TIM textures, or image file formats."
---

#   CDROM File Formats
#### Official PSX File Formats
[CDROM File Official Sony File Formats](cdromfileformats.md#cdrom-file-official-sony-file-formats)<br/>

#### Executables
[CDROM File Playstation EXE and SYSTEM.CNF](cdromfileformats.md#cdrom-file-playstation-exe-and-systemcnf)<br/>
[CDROM File PsyQ .CPE Files (Debug Executables)](cdromfileformats.md#cdrom-file-psyq-cpe-files-debug-executables)<br/>
[CDROM File PsyQ .SYM Files (Debug Information)](cdromfileformats.md#cdrom-file-psyq-sym-files-debug-information)<br/>

#### Video Files
[CDROM File Video Texture Image TIM/PXL/CLT (Sony)](cdromfileformats.md#cdrom-file-video-texture-image-timpxlclt-sony)<br/>
[CDROM File Video Texture/Bitmap (Other)](cdromfileformats.md#cdrom-file-video-texturebitmap-other)<br/>
[CDROM File Video 2D Graphics CEL/BGD/TSQ/ANM/SDF (Sony)](cdromfileformats.md#cdrom-file-video-2d-graphics-celbgdtsqanmsdf-sony)<br/>
[CDROM File Video 3D Graphics TMD/PMD/TOD/HMD/RSD (Sony)](cdromfileformats.md#cdrom-file-video-3d-graphics-tmdpmdtodhmdrsd-sony)<br/>
[CDROM File Video STR Streaming and BS Picture Compression (Sony)](cdromfileformats.md#cdrom-file-video-str-streaming-and-bs-picture-compression-sony)<br/>

#### Audio Files
[CDROM File Audio Single Samples VAG (Sony)](cdromfileformats.md#cdrom-file-audio-single-samples-vag-sony)<br/>
[CDROM File Audio Sample Sets VAB and VH/VB (Sony)](cdromfileformats.md#cdrom-file-audio-sample-sets-vab-and-vhvb-sony)<br/>
[CDROM File Audio Sequences SEQ/SEP (Sony)](cdromfileformats.md#cdrom-file-audio-sequences-seqsep-sony)<br/>
[CDROM File Audio Other Formats](cdromfileformats.md#cdrom-file-audio-other-formats)<br/>
[CDROM File Audio Streaming XA-ADPCM](cdromfileformats.md#cdrom-file-audio-streaming-xa-adpcm)<br/>
[CDROM File Audio CD-DA Tracks](cdromfileformats.md#cdrom-file-audio-cd-da-tracks)<br/>

#### Virtual Filesystem Archives
PSX titles are quite often using virtual filesystems, with numerous custom file
archive formats.<br/>
[CDROM File Archives with Filename](cdromfileformats.md#cdrom-file-archives-with-filename)<br/>
[CDROM File Archives with Offset and Size](cdromfileformats.md#cdrom-file-archives-with-offset-and-size)<br/>
[CDROM File Archives with Offset](cdromfileformats.md#cdrom-file-archives-with-offset)<br/>
[CDROM File Archives with Size](cdromfileformats.md#cdrom-file-archives-with-size)<br/>
[CDROM File Archives with Chunks](cdromfileformats.md#cdrom-file-archives-with-chunks)<br/>
[CDROM File Archives with Folders](cdromfileformats.md#cdrom-file-archives-with-folders)<br/>
[CDROM File Archives in Hidden Sectors](cdromfileformats.md#cdrom-file-archives-in-hidden-sectors)<br/>
More misc stuff...<br/>
[CDROM File Archive HED/DAT/BNS/STR (Ape Escape)](cdromfileformats.md#cdrom-file-archive-heddatbnsstr-ape-escape)<br/>
[CDROM File Archive WAD.WAD, BIG.BIN, JESTERS.PKG (Crash/Herc/Pandemonium)](cdromfileformats.md#cdrom-file-archive-wadwad-bigbin-jesterspkg-crashhercpandemonium)<br/>
[CDROM File Archive BIGFILE.BIG (Gex)](cdromfileformats.md#cdrom-file-archive-bigfilebig-gex)<br/>
[CDROM File Archive BIGFILE.DAT (Gex - Enter the Gecko)](cdromfileformats.md#cdrom-file-archive-bigfiledat-gex-enter-the-gecko)<br/>
[CDROM File Archive FF9 DB (Final Fantasy IX)](cdromfileformats.md#cdrom-file-archive-ff9-db-final-fantasy-ix)<br/>
[CDROM File Archive Ace Combat 2 and 3](cdromfileformats.md#cdrom-file-archive-ace-combat-2-and-3)<br/>
[CDROM File Archive NSD/NSF (Crash Bandicoot 1-3)](cdromfileformats.md#cdrom-file-archive-nsdnsf-crash-bandicoot-1-3)<br/>
[CDROM File Archive STAGE.DIR and *.DAT (Metal Gear Solid)](cdromfileformats.md#cdrom-file-archive-stagedir-and-dat-metal-gear-solid)<br/>
[CDROM File Archive DRACULA.DAT (Dracula)](cdromfileformats.md#cdrom-file-archive-draculadat-dracula)<br/>
[CDROM File Archive Croc 1 (DIR, WAD, etc.)](cdromfileformats.md#cdrom-file-archive-croc-1-dir-wad-etc)<br/>
[CDROM File Archive Croc 2 (DIR, WAD, etc.)](cdromfileformats.md#cdrom-file-archive-croc-2-dir-wad-etc)<br/>
[CDROM File Archive Headerless Archives](cdromfileformats.md#cdrom-file-archive-headerless-archives)<br/>
Using archives can avoid issues with the PSX's poorly implemented ISO
filesystem: The PSX kernel supports max 800h bytes per directory, and lacks
proper caching for most recently accessed directories (additionally, some
archives can load the whole file/directory tree from continous sectors, which
could be difficult in ISO filesystems).<br/>

#### Compression
[CDROM File Compression](cdromfileformats.md#cdrom-file-compression)<br/>

#### Misc
[CDROM File XYZ and Dummy/Null Files](cdromfileformats.md#cdrom-file-xyz-and-dummynull-files)<br/>

#### General CDROM Disk Images
[CDROM Disk Images CCD/IMG/SUB (CloneCD)](cdromfileformats.md#cdrom-disk-images-ccdimgsub-clonecd)<br/>
[CDROM Disk Images CDI (DiscJuggler)](cdromfileformats.md#cdrom-disk-images-cdi-discjuggler)<br/>
[CDROM Disk Images CUE/BIN/CDT (Cdrwin)](cdromfileformats.md#cdrom-disk-images-cuebincdt-cdrwin)<br/>
[CDROM Disk Images MDS/MDF (Alcohol 120%)](cdromfileformats.md#cdrom-disk-images-mdsmdf-alcohol-120)<br/>
[CDROM Disk Images NRG (Nero)](cdromfileformats.md#cdrom-disk-images-nrg-nero)<br/>
[CDROM Disk Image/Containers CDZ](cdromfileformats.md#cdrom-disk-imagecontainers-cdz)<br/>
[CDROM Disk Image/Containers ECM](cdromfileformats.md#cdrom-disk-imagecontainers-ecm)<br/>
[CDROM Subchannel Images](cdromfileformats.md#cdrom-subchannel-images)<br/>
[CDROM Disk Images Other Formats](cdromfileformats.md#cdrom-disk-images-other-formats)<br/>

#### FILENAME.EXT
The BIOS seems to support only (max) 8-letter filenames with 3-letter
extension, typically all uppercase, eg. "FILENAME.EXT". Eventually, once when
the executable has started, some programs might install drivers for long
filenames(?)<br/>

The PSX uses the standard CDROM ISO9660 filesystem without any encryption (ie.
you can put an original PSX CDROM into a DOS/Windows computer, and view the
content of the files in text or hex editors without problems).<br/>

#### Note
MagDemoNN is short for "Official U.S. Playstation Magazine Demo Disc NN"<br/>



##   CDROM File Official Sony File Formats
#### Official Sony File Formats
<https://psx.arthus.net/sdk/Psy-Q/DOCS/Devrefs/Filefrmt.pdf> - Sony 1998<br/>
```
  File Formats
    (c) 1998 Sony Computer Entertainment Inc.
    Publication date: November 1998
  Chapter 1: Streaming Audio and Video Data
    STR: Streaming (Movie) Data                               1-3
    BS: MDEC Bitstream Data                                   1-8
    XA: CD-ROM Voice Data                                     1-31
  Chapter 2: 3D Graphics
    RSD: 3D Model Data [RSD,PLY,MAT,GRP,MSH,PVT,COD,MOT,OGP]  2-3
    TMD: Modeling Data for OS Library                         2-24
    PMD: High-Speed Modeling Data                             2-35
    TOD: Animation Data                                       2-40
    HMD: Hierarchical 3D Model, Animation and Other Data      2-49
  Chapter 3: 2D Graphics
    TIM: Screen Image Data                                    3-3
    SDF: Sprite Editor Project File                           3-8
    PXL: Pixel Image Data                                     3-11
    CLT: Palette Data                                         3-14
    ANM: Animation Information                                3-16
    TSQ: Animation Time Sequence                              3-22
    CEL: Cell Data                                            3-23
    BGD: BG Map Data                                          3-27
  Chapter 4: Sound
    SEQ: PS Sequence Data                                     4-3
    SEP: PS Multi-Track Sequence Data                         4-3
    VAG: PS Single Waveform Data                              4-5
    VAB: PS Sound Source Data [VAB and VH/VB]                 4-5
    DA: CD-DA Data                                            4-7
  Chapter 5: PDA and Memory Card
    FAT: Memory Card File System Specification                5-3
```
Most games are using their own custom file formats. However, VAG, VAB/VH(VB,
STR/XA, and TIM are quite popular (because they are matched to the PSX
low-level data encoding). Obviously, EXE is also very common (although not
included in the above document).<br/>



##   CDROM File Playstation EXE and SYSTEM.CNF
#### SYSTEM.CNF
Contains boot info in ASCII/TXT format, similar to the CONFIG.SYS or
AUTOEXEC.BAT files for MSDOS. A typical SYSTEM.CNF would look like so:<br/>
```
  BOOT = cdrom:\abcd_123.45;1 arg ;boot exe (drive:\path\name.ext;version)
  TCB = 4                         ;HEX (=4 decimal)   ;max number of threads
  EVENT = 10                      ;HEX (=16 decimal)  ;max number of events
  STACK = 801FFF00                ;HEX (=memtop-256)
```
The first line specifies the executable to load, from the "cdrom:" drive, "\"
root directory, filename "abcd\_123.45" (case-insensitive, the real name in the
disk directory would be uppercase, ie. "ABCD\_123.45"), and, finally ";1" is the
file's version number (a rather strange ISO-filesystem specific feature) (the
version number should be usually/always 1). Additionally, "arg" may contain an
optional 128-byte command line argument string, which is copied to address
00000180h, where it may be interpreted by the executable (most or all games
don't use that feature).<br/>
Each line in the file should be terminated by 0Dh,0Ah characters... not sure if
it's also working with only 0Dh, or only 0Ah...?<br/>

#### ABCD\_123.45
This is a normal executable (exactly as for the .EXE files, described below),
however, the filename/extension is taken from the game code (the "ABCD-12345"
text that is printed on the CD cover), but, with the minus replaced by an
underscore, and due to the 8-letter filename limit, the last two characters are
stored in the extension region.<br/>
That "XXXX\_NNN.NN" naming convention seems to apply for all official licensed
PSX games. Wild Arms does unconventionally have the file in a separate folder,
"EXE\SCUS\_946.06".<br/>

#### PSX.EXE (Boot-Executable) (default filename when SYSTEM.CNF doesn't exist)
#### XXXX\_NNN.NN (Boot-Executable) (with filename as specified in SYSTEM.CNF)
#### FILENAME.EXE (General-Purpose Executable)
PSX executables are having an 800h-byte header, followed by the code/data.<br/>
```
  000h-007h ASCII ID "PS-X EXE"
  008h-00Fh Zerofilled
  010h      Initial PC                   (usually 80010000h, or higher)
  014h      Initial GP/R28               (usually 0)
  018h      Destination Address in RAM   (usually 80010000h, or higher)
  01Ch      Filesize (must be N*800h)    (excluding 800h-byte header)
  020h      Data section Start Address   (usually 0)
  024h      Data Section Size in bytes   (usually 0)
  028h      BSS section Start Address    (usually 0) (when below Size=None)
  02Ch      BSS section Size in bytes    (usually 0) (0=None)
  030h      Initial SP/R29 & FP/R30 Base (usually 801FFFF0h) (or 0=None)
  034h      Initial SP/R29 & FP/R30 Offs (usually 0, added to above Base)
  038h-04Bh Reserved for A(43h) Function (should be zerofilled in exefile)
  04Ch-xxxh ASCII marker
             "Sony Computer Entertainment Inc. for Japan area"
             "Sony Computer Entertainment Inc. for Europe area"
             "Sony Computer Entertainment Inc. for North America area"
             (or often zerofilled in some homebrew files)
             (the BIOS doesn't verify this string, and boots fine without it)
  xxxh-7FFh Zerofilled
  800h...   Code/Data                  (loaded to entry[018h] and up)
```
The code/data is simply loaded to the specified destination address, ie. unlike
as in MSDOS .EXE files, there is no relocation info in the header.<br/>
Note: In bootfiles, SP is usually 801FFFF0h (ie. not 801FFF00h as in
system.cnf). When SP is 0, the unmodified caller's stack is used. In most cases
(except when manually calling DoExecute), the stack values in the exeheader
seem to be ignored though (eg. replaced by the SYSTEM.CNF value).<br/>
The memfill region is zerofilled by a "relative" fast word-by-word fill (so
address and size must be multiples of 4) (despite of the word-by-word filling,
still it's SLOW because the memfill executes in uncached slow ROM).<br/>
The reserved region at [038h-04Bh] is internally used by the BIOS to memorize
the caller's RA,SP,R30,R28,R16 registers (for some bizarre reason, this
information is saved in the exe header, rather than on the caller's stack).<br/>
Additionally to the initial PC,R28,SP,R30 values that are contained in the
header, two parameter values are passed to the executable (in R4 and R5
registers) (however, usually that values are simply R4=1 and R5=0).<br/>
Like normal functions, the executable can return control to the caller by
jumping to the incoming RA address (provided that it hasn't destroyed the stack
or other important memory locations, and that it has pushed/popped all
registers) (returning works only for non-boot executables; if the boot
executable returns to the BIOS, then the BIOS will simply lockup itself by
calling the "SystemErrorBootOrDiskFailure" function.<br/>

#### Relocatable EXE
Fade to Black (CINE.EXR) contains ID "PS-X EXR" (instead "PS-X EXE") and string
"PSX Relocable File - Delphine Software Int.", this is supposedly some custom
relocatable exe file (unsupported by the PSX kernel).<br/>

#### MSDOS.EXE and WINDOWS.EXE Files
Some PSX discs contain DOS or Windows .EXE files (with "MZ" headers), eg.
devkit leftovers, or demos/gimmicks.<br/>



##   CDROM File PsyQ .CPE Files (Debug Executables)
#### Fileheader
```
  00h 4   File ID (01455043h aka "CPE",01h)
```

#### Chunk 00h: End of File
```
  00h 1   Chunk ID (00h)
```

#### Chunk 01h: Load Data
```
  00h 1   Chunk ID (01h)
  01h 4   Address (usually 80010000h and up)
  05h 4   Size (LEN)
  09h LEN Data (binary EXE code/data)
```
Theoretically, this could contain the whole EXE body in a single chunk.
However, the PsyQ files are usually containing hundreds of small chunks (with
each function and each data item in a separate chunk). For converting CPE to
EXE, use "ExeOffset = (CpeAddress AND 1FFFFFFFh)-10000h+800h".<br/>

#### Chunk 02h: Run Address (whatever, optional, usually not used in CPE files)
```
  00h 1   Chunk ID (02h)
  01h 4   Address
```
Unknown what this is. It's not the entrypoint (which is set via chunk 03h).
Maybe intended to change the default load address (usually 80010000h)?<br/>

#### Chunk 03h: Set Value 32bit (LEN=4) (used for entrypoint)
#### Chunk 04h: Set Value 16bit (LEN=2) (unused)
#### Chunk 05h: Set Value 8bit  (LEN=1) (unused)
#### Chunk 06h: Set Value 24bit (LEN=3) (unused)
```
  00h 1   Chunk ID (03h..06h)
  01h 2   Register (usually 0090h=Initial PC, aka Entrypoint)
  03h LEN Value (8bit..32bit)
```

#### Chunk 07h: Select Workspace (whatever, optional, usually not used in CPE)
```
  00h 1   Chunk ID (07h)
  01h 4   Workspace number (usually 00000000h)
```

#### Chunk 08h: Select Unit (whatever, usually first chunk in CPE file)
```
  00h 1   Chunk ID (08h)
  01h 1   Unit (usually 00h)
```

#### Example from LameGuy's sample.cpe:
```
  0000h 4    File ID ("CPE",01h)
  0004h 2    Select Unit 0            (08h,00h)
  0006h 7    Set Entrypoint 8001731Ch (03h,0090h,8001731Ch)
  000Dh 0Dh  Load   (01h,800195F8h,00000004h,0,0,0,0)
  001Ah ..   Load   (01h,80010000h,0000002Bh,...)
  004Eh ..   Load   (01h,8001065Ch,00000120h,...)
  0177h ...  Load   (01h,8001077Ch,0000012Ch,...)
  02ACh ...  Load   (01h,800108A8h,000000A4h,...)
  ...   ...  Load   (...)
  98F4h ...  Load   (01h,800195F0h,00000008h,...)
  9905h 1    End    (00h)
```



##   CDROM File PsyQ .SYM Files (Debug Information)
PsyQ .SYM Files contain debug info, usually bundled with PsyQ .MAP and Psy .CPE
files. Those files are generated by PsyQ tools, which appear to be still in use
for homebrew PSX titles.<br/>
The files are occassionally also found on PSX CDROMs:<br/>
```
  Legacy of Kain PAL version (\DEGUG\NTSC\KAIN2.SYM+MAP+CPE)
  RC Revenge (\RELEASE.SYM)
  Twisted Metal: Small Brawl (MagDemo54: TMSB\TM.SYM)
  Jackie Chan Stuntmaster (GAME_REL.SYM+CPE)
  SnoCross Championship Racing (MagDemo37: SNOCROSS\SNOW.TOC\SNOW.MAP)
  Sled Storm (MagDemo24: DEBUG\MAIN.MAP)
  E.T. Interplanetary Mission (MagDemo54: MEGA\MEGA.CSH\* has SYM+CPE+MAP)
```

#### Fileheader .SYM
```
  00h 4  File ID ("MND",01h)
  04h 4  Whatever (0,0,0,0)    ;TOMB5: 0,02h,0,0
  08h .. Chunks (see below)
```

#### Symbol Chunks

##### Chunk 01h: Symbol (Immediate, eg. memsize, or membase)
##### Chunk 02h: Symbol (Function Address for Internal &amp; External Functions)
##### Chunk 05h: Symbol (?)
##### Chunk 06h: Symbol (?)
```
  00h 4   Address/Value
  04h 1   Chunk ID (01h/02h/05h/06h)
  05h 1   Symbol Length (LEN)
  06h LEN Symbol (eg. "VSync")
```

#### Source Code Line Chunks

##### Chunk 80h: Source Code Line Numbers: Address for 1 Line
```
  00h 4   Address (for 1 line, starting at current line)
  04h 1   Chunk ID (80h)
```

##### Chunk 82h: Source Code Line Numbers: Address for N Lines (8bit)
```
  00h 4   Address (for N lines, starting at current line)
  04h 1   Chunk ID (82h)
  05h 1   Number of Lines (00h=None, or 02h and up?)
```

##### Chunk 84h: Source Code Line Numbers: Address for NN Lines (16bit)
```
  00h 4   Address (for N lines, starting at current line)
  04h 1   Chunk ID (84h)
  05h 2   Number of Lines (?)
```

##### Chunk 86h: Source Code Line Numbers: Address for Line NNN (32bit?)
```
  00h 4   Address (for 1 line, starting at newly assigned current line)
  04h 1   Chunk ID (84h)
  05h 4   Absolute Line Number (rather than number of lines) (?)
```

##### Chunk 88h: Source Code Line Numbers: Start with Filename
```
  00h 4   Address (start address)
  04h 1   Chunk ID (88h=Filename)
  05h 4   First Line Number (after comments/definitions) (32bit?)
  09h 1   Filename Length (LEN)
  0Ah LEN Filename (eg. "C:\path\main.c")
```

##### Chunk 8Ah: Source Code Line Numbers: End of Source Code
```
  00h 4   Address (end address)
  04h 1   Chunk ID (8Ah)
```

#### Internal Function Chunks

##### Chunk 8Ch: Internal Function: Start with Filename
```
  00h 4    Address
  04h 1    Chunk ID (8Ch)
  05h 4    Whatever (1Eh,00h,20h,00h)  ;or 1Eh,00h,18h,00h
  09h 4    Whatever (00h,00h,1Fh,00h)
  0Dh 4    Whatever (00h,00h,00h,C0h)
  11h 4    Whatever (FCh,FFh,FFh,FFh)  ;mask? neg.offset?
  15h 4    Whatever (10h,00h,00h,00h)  <-- line number (32bit?)
  19h 1    Filename Length (LEN1)
  1Ah LEN1 Filename (eg. "C:\path\main.c")
  xxh 1    Symbol Length (LEN2)
  xxh LEN2 Symbol (eg. "VSync")
```

##### Chunk 8Eh: Internal Function: End of Function (end of chunk 8Ch)
```
  00h 4   Address
  04h 1   Chunk ID (8Eh)
  05h 4   Line Number                 <-- line number (32bit?)
```

##### Chunk 90h: Internal Function:Whatever90h... first instruction in main func?
##### Chunk 92h: Internal Function:Whatever92h... last instruction in main func?
Maybe line numbers? Or end of definitions for incoming parameters?<br/>
```
  00h 4   Address
  04h 1   Chunk ID (90h/92h)
  05h 4   Whatever (1Fh,00h,00h,00h)  <-- line number relative to main.start?
```

#### Class/Type Chunks

##### Chunk 94h: Type/Symbol (Simple Types?)
```
  00h 4   Offset (when used within a structure, or stack-N, or otherwise zero)
  04h 1   Chunk ID (94h)
  05h 2   Class (000Dh=Type.alias, 000Ah=Address, 0001h=Stack, 0002h=Addr)
  07h 2   Type (XX = 8bit,16bit,signed,etc.?)
  09h 4   Zero, or Size in Bytes (for "memblocks")
  0xh 1   Symbol Name Length (LEN)
  0xh LEN Symbol Name (eg. "size_t")
```

##### Chunk 96h: Type/Symbol (Complex Structures/Arrays?)
```
  00h 4   Offset (when used within a structure, otherwise zero)
  04h 1   Chunk ID (96h)
  05h 2   Class (02h=Array,08h=RefToStruct,0Dh=DefineAlias,66h=StructEnd)
  07h 2   Type (0xh=Small, 3xh=WithArrayStuff?) (same/similar as in chunk 94h)
  09h 4     Struct Size in Bytes
  0Dh 2     Array Dimensions (DIM) (0=none) ;eg. [3][4] --> 0002h
  0Fh DIM*4 Array Entries per Dimension     ;eg. [3][4] --> 00000003h,00000004h
  xxh 1     Internal Fake Name Length (LEN1) (0=none)
  xxh LEN1  Internal Fake Name  (eg. ".1fake")
  xxh 1     Symbol Name Length (LEN2)
  xxh LEN2  Symbol Name (eg. "r")
```

#### Class/Type Values

##### Class definition (in chunk 94h) (and somewhat same/similar in chunk 96h)
(looks same/similar as C\_xxx class values in COFF files!)<br/>
```
  0001h = Local variable              (with Offset = negative stack offset)
  0002h = Global variable or Function (with Offset = address)
  0008h = Item in Structure           (with Offser = offset within struct)
  0009h = Incoming Function param     (with Offset = index; 0,4,8,etc.)
  000Ah = Type address / struc start? (with Offset = zero)
  000Dh = Type alias                  (with Offset = zero)
```

##### Type definition (in chunk 94h/96h)
(maybe lower 4bit=type, and next 4bit=usage/variant?)<br/>
(looks same/similar as T\_xxx type values in COFF files!)<br/>
```
  0000h =
  0001h =
  0002h =
  0003h =                (16bit signed?)
  0004h = int            (32bit signed?)
  0005h =
  0006h =
  0007h =
  0008h = (address)      (32bit unsigned?) (with Definition=000Ah)
  0009h =
  000Ah =
  000Bh =
  000Ch = u_char         (8bit unsigned?)
  000Dh = u_short,ushort (16bit unsigned?)
  000Eh = u_int          (32bit unsigned?)
  000Fh = u_long         (64bit unsigned?) (or rather SAME as above?)
  0021h = function with 0 params, and/or return="nothing"?
  0024h = main function with 2 params, and/or return="int"?
  0052h = argv           (string maybe?)
  0038h = GsOT           (huh?)
  00F8h = GsOT_TAG       (huh?)
  00FCh = PACKET         (huh?)
  ??    = float,bool,string,ptr,packet,(un-)signed8/16/32/64bit,etc
  ??    = custom type/struct (using value 000xh plus "fake" name, or so?)
```

#### .MAP File

##### PsyQ .MAP File
The .SYM file is usually bundled with a .MAP file, which is containing a
summary of the symbolic info as ASCII text (but without info on line numbers or
data types). For example:<br/>
```
    Start     Stop   Length      Obj Group            Section name
 80010000 80012D5B 00002D5C 80010000 text             .rdata
 80012D5C 800C8417 000B56BC 80012D5C text             .text
 800C8418 800CDAB7 000056A0 800C8418 text             .data
 800CDAB8 800CFB63 000020AC 800CDAB8 text             .sdata
 800CFB64 800D5C07 000060A4 800CFB64 bss              .sbss
 800D5C08 800DD33F 00007738 800D5C08 bss              .bss
```

```
  Address  Names alphabetically
 800CFE80 ACE_amount
 800CFB94 AIMenu
 800CDE5C AXIS_LENGTH
 8005E28C AddClippedTri
 8005DFEC AddVertex
 ...
```

```
  Address  Names in address order
 00000000 _cinemax_obj
 00000000 _cinemax_header_org
 00000000 _cinemax_org
 00000000 _mcardx_sbss_size
 00000000 _mcardx_org
 ...
```



##   CDROM File Video Texture Image TIM/PXL/CLT (Sony)
TIM/PXL/CLT are standard formats from Sony's devkit. TIM is used by many PSX
games.<br/>
```
  .TIM   contains Pixel data, and (optional) CLUT data  ;-all in one file
  .PXL   contains Pixel data only                       ;\in two separate files
  .CLT   contains CLUT data only (if any)               ;/
```

#### TIM Format
```
  000h 1  File ID  (always 10h=TIM)
  001h 1  Version  (always 00h)
  002h 2  Reserved (always 0000h) (or 1 or 2 for Compressed TIM, see below)
  004h 4  Flags (bit0-2=Type; see below, bit3=HasCLUT, bit4-31=Reserved/zero)
  ...  .. Data Section for CLUT (Palette), only exists if Flags.bit3=1, HasCLUT
  ...  .. Data Section for Pixels (Bitmap/Texture)
```
The Type in Flags.bit0-2 can be 0=4bpp, 1=8bpp, 2=16bpp, 3=24bpp, 4=Mixed.<br/>
NFL Blitz 2000 (MagDemo26: B2000\DATA\ARTD\_G.BIN) does additionally use Type
5=8bit.<br/>
The Type value value is only a hint on how to view the Pixel data (the data is
copied to VRAM regardless of the type; 4=Mixed is meant to indicate that the
data contains different types, eg. both 4bpp &amp; 8bpp textures).<br/>
Type 3=24bpp is quite rare, but does exist (eg. Colony Wars (MagDemo02:
CWARS\GAME.RSC\DEMO.TIM).<br/>

#### The format of the CLUT and Pixel Data Section(s) is:
```
  000h 4  Size of Data Section (Xsiz*2*Ysiz+0Ch)  ;maybe rounded to 4-byte?
  004h 4  Destination Coord    (YyyyXxxxh)  ;Xpos counted in halfwords
  008h 4  Width+Height         (YsizXsizh)  ;Xsiz counted in halfwords
  00Ch .. VRAM Data (to be DMAed to frame buffer)
```
Note: Above is usually a multiple of 4 bytes, but not always:<br/>
Shadow Madness (MagDemo18: SHADOW\DATA\ANDY\LOADSAVE\\*.TIM) contains TIM
bitmaps with 27x27 or 39x51 halfwords; those files have odd section size &
odd total filesize. Gran Turismo 2 (GT2.VOL\arcade\arc\_other.tim\0000) also has
odd size. Unknown if the CLUT can also have odd size (which would misalign the
following Bitmap section).<br/>
Bust A Groove (MagDemo18: BUSTGR\_A\G\_COMMON.DFS\0005) has 0x0 pixel Bitmaps
(with CLUT data).<br/>

#### PXL/CLT Format
PXL/CLT is very rare. And oddly, with swapped ID values (official specs say
11h=PXL, 12h=CLT, but the existing games do use 11h=CLT, 12h=PXL).<br/>
Used by Granstream Saga (MagDemo10 GS\\*)<br/>
Used by Bloody Roar 1 (MagDemo06: BL\\*)<br/>
Used by Bloody Roar 2 (MagDemo22: ASC,CMN,EFT,LON,SND,ST5,STU\\*)<br/>

#### CLT Format
```
  000h 1  File ID  ( 11h=CLT) (although Sony's doc says 12h)
  001h 1  Version  ( 00h)
  002h 2  Reserved (always 0000h)
  004h 4  Flags (bit0-1=Type=2; bit2-31=Reserved/zero)
  ...  .. Data Section for CLUT (Palette)
```
The .CLT Type should be always 2 (meant to indicate 16bit CLUT entries).<br/>

#### PXL Format
```
  000h 1  File ID  (always 12h=PXL) (although Sony's doc says 11h)
  001h 1  Version  (always 00h)
  002h 2  Reserved (always 0000h)
  004h 4  Flags (bit0-?=Type; see below, bit?-31=Reserved/zero)
  ...  .. Data Section for Pixels (Bitmap/Texture)
```
This does probably support the same 5 types as in .TIMs (though official Sony
docs claim the .PXL type to be only 1bit wide, but netherless claim that PXL
can be 4bpp, 8bpp, or 16bpp).<br/>

#### Compressed TIMs
Ape Escape (Sony 1999) is using a customized TIM format with 4bpp compression:<br/>
[CDROM File Compression TIM-RLE4/RLE8](cdromfileformats.md#cdrom-file-compression-tim-rle4rle8)<br/>
Other than that, TIMs can be compressed via generic compression functions (like
LZSS, GZIP), or via bitmap dedicated compression formats (like BS, JPG, GIF).<br/>

#### Malformed Files

##### Malformed TIMs in BIGFILE.DAT
```
  Used by Legacy of Kain: Soul Reaver (eg. BIGFILE.DAT\folder04h\file13h)
  Used by Gex - Enter the Gecko (eg. BIGFILE.DAT\file0Fh\LZcompressed)
```
Malformed TIMs contain texture data preceeded by a dummy 14h-byte TIM header
with following constant values:<br/>
```
  10 00 00 00  02 00 00 00  04 00 08 00  00 02 00 00  00 02 00 02  ;<-- this
  10 00 00 00  02 00 00 00  04 00 08 00  00 00 00 00  00 02 00 02  ;<-- or this
```
The malformed entries include:<br/>
```
  [04h]=Type should indicated the color depth, but it's always 02h=16bpp.
  [08h]=Width*2*Height+0Ch should be 8000Ch, but malformed is 80004h.
  Total filesize should be 80014h, but Gecko files are often MUCH smaller.
```
Also, destination yloc should be 0..1FFh, but PSX "Lemmings &amp; Oh No! More
Lemmings" (FILES\GFX\\*.TIM) has yloc=200h (that game also has vandalized .BMP
headers with 2-byte alignment padding after ID "BM", whilst pretending that
those extra bytes aren't there in data offset and total size entries).<br/>

##### Oversized TIMs
```
  Used by Pong (MagDemo24: LES02020\*\*.TIM)
```
Has 200x200h pix, but section size (and filesize) are +2 bigger than that:<br/>
```
  10 00 00 00 02 00 00 00 0E 00 08 00 C0 01 00 00 00 02 00 02  ;Pong *.TIM
  10 00 00 00 02 00 00 00 0E 00 07 00 00 02 00 00 C0 01 00 02  ;Pong WORLD.TIM
  10 00 00 00 02 00 00 00 0E 80 03 00 00 02 00 01 C0 01 00 01  ;Pong ZONE*.TIM
```

##### Miscomputed Section Size
NBA Basketball 2000 (MagDemo28: FOXBB\TIM\\*.TIM) has TIMs with section size
"0Ch+Xsiz\*Ysiz" instead of "0Ch+Xsiz\*2\*Ysiz".<br/>

##### NonTIMs in Bloody Roar 1 and 2
```
  Bloody Roar 1 (CMN\INIT.DAT\000Eh)
  Bloody Roar 2 (CMN\SE00.DAT, CMD\SEL00.DAT\0030h and CMN\VS\VS.DAT\0000h)
```
This looks somehow TIM-inspired, but has ID=13h.<br/>
```
  13 00 00 00 02 00 00 00 0C 20 00 00 00 00 F8 01 00 01 10 00  ;Bloody Roar 1
  13 00 00 00 02 00 00 00 0C 20 00 00 00 00 00 00 00 01 10 00  ;Bloody Roar 2
```

##### Other uncommon/malformed TIM variants
And, Heart of Darkness has a TIM with Size entry set to Xsiz\*2\*Ysiz+0Eh
(instead of +0Ch) (that malformed TIM is found inside of the RNC compressed
IMAGES\US.TIM file).<br/>
Also, NFL Gameday '99 (MagDemo17: GAMEDAY\PHOTOS.FIL) contains a TIM cropped to
800h-byte size (containing only the upper quarter of the photo).<br/>
Also, not directly malformed, but uncommon: Final Fantasy IX contains 14h-byte
0x0 pixel TIMs (eg. FF9.IMG\dir04\file0046\1B-0000\04-0001).<br/>
Klonoa (MagDemo08: KLONOA\FILE.IDX\3\2\0..1) has 0x0pix TIM (plus palette).<br/>

##### Malformed CLTs
```
  Used by Secret of Mana, WM\WEFF\*.CLT
```
ID is 10h=TIM, Flags=10101009h (should be ID=12h, Flags=02h).<br/>



##   CDROM File Video Texture/Bitmap (Other)
Apart from Sony's TIM (and PXL/CLT) format, there are a bunch of other
texture/bitmap formats:<br/>

#### Compressed Bitmaps
```
  .BS used by several games (and also in most .STR videos)
  .GIF used by Lightspan Online Connection CD
  .JPG used by Lightspan Online Connection CD
  .BMP with RLE4 used by Lightspan Online Connection CD (MONOFONT, PROPFONT)
  .BMP with RLE8+Delta also used by Online Connection CD (PROPFONT\ARIA6.BMP)
  .PCX with RLE used by Jampack Vol. 1 (MDK\CD.HED\*.pcx)
```

#### Uncompressed Bitmaps
```
  .BMP
  .BMP used by Mat Hoffman's Pro BMX (MagDemo39: BMX\BMXCD.HED\*)
  .BMP used by Mat Hoffman's Pro BMX (MagDemo48: MHPB\BMXCD.HED\*)
  .BMP used by Thrasher: Skate and Destroy (MagDemo27: SKATE\ASSETS\*.ZAL)
  .BMP used by Dave Mirra Freestyle BMX (MagDemo36,46: BMX\ASSETS\*.ZAL)
  .VRM .IMG .TEX .TIM .RAW .256 .COL .4B .15B .R16 .TPG - raw VRAM data
  "SC" memory card icons
```

#### Targa TGA and Paintbrush PCX
[CDROM File Video Texture/Bitmap (TGA)](cdromfileformats.md#cdrom-file-video-texturebitmap-tga)<br/>
[CDROM File Video Texture/Bitmap (PCX)](cdromfileformats.md#cdrom-file-video-texturebitmap-pcx)<br/>

#### PSI bitmap - Power Spike (MagDemo43: POWER\GAME.IDX\\*.BIZ\\*.PSI)
```
  000h 10h   Name 1 ("FILENAME.BMP", zeropadded)
  010h 10h   Name 2 ("FILENAME.PSI", zeropadded)
  020h 4     Bits per pixel (usually 4, 8, or 16)
  024h 2     Bitmap VRAM Dest.X ?
  026h 2     Bitmap VRAM Dest.Y ?
  028h 2     Bitmap Width in pixels
  02Ah 2     Bitmap Height in pixels
  02Ch 2     Palette VRAM Dest.X ?   ;\zero for 16bpp
  02Eh 2     Palette VRAM Dest.Y ?   ;/
  030h 2     Bitmap Width in Halfwords (PixelWidth*bpp/16)
  032h 2     Palette Size in Halfwords (0, 10h, 100h for 16bpp,4npp,8bpp)
  034h 4     Maybe Bitmap present flag (always 1)
  038h 4     Maybe Palette present flag (0=16bpp, 1=4bpp/8bpp)
  03Ch ..    Bitmap pixels
  ...  ..    Palette (if any, for 4bpp: 16x16bit, for 8bpp: 256x16bit)
```

#### JumpStart Wildlife Safari Field Trip (MagDemo52: DEMO\DATA.DAT\\*.DAT+\*.PSX)
This game does use two different (but nearly identical) bitmap formats (with
either palette or bitmap data stored first).<br/>
```
  000h 4     Total Filesize (Width*Height+20Ch)
  004h 2     Bitmap Width
  006h 2     Bitmap Height
  008h 4     Unknown, always 1 (maybe 1=8bpp?)
 In .DAT files (512x192 or 256x64 pix), palette first:
  00Ch 200h  Palette data
  20Ch ..    Bitmap data
 In .PSX files (64x64 pix), bitmap first:
  00Ch ..    Bitmap data
  ...  200h  Palette data
```
To detect the "palette first" format, check for these conditions(s):<br/>
```
  Filename extension is ".DAT"
  Bitmap Width<>Height (non-square)
  [00Ch..20Bh] has AllMSBs>=80h, and SomeLSBs<80h
```
Note: The bitmaps are vertically mirrored (starting with bottom-most scanline).<br/>

#### WxH Bitmap (Width\*Height)
Used by Alone in the Dark The New Nightmare (FAT.BIN\BOOK,DOC,INTRO,MENU\\*)<br/>
Used by Rayman (RAY\JUN,MON,MUS\\*) (but seems to contain map data, not pixels)<br/>
```
  000h 2   Width  (W)   ;\usually 320x240 (or 512x240 or 80x13)
  002h 2   Height (H)   ;/
  004h ..  Bitmap 16bpp (W*H*2 bytes)
```

#### RAWP Bitmap
Used by Championship Motocross (MagDemo25: SMX\RESHAD.BIN\\*) ("RAWP")<br/>
```
  000h 4     ID "RAWP" (this variant has BIG-ENDIAN width/height!)
  004h 2     Width  (usually 280h=640pix or 140h=320pix) (big-endian!!!)
  006h 2     Height (usually 1E0h=480pix or F0h=240pix)  (big-endian!!!)
  008h ..    Bitmap data, 16bpp (width*height*2 bytes)
```

#### XYWH Bitmap/Palette (X,Y,Width\*Height) (.BIT and .CLT)
Used by CART World Series (MagDemo04: CART\\*.BIT and \*.BIN\\*)<br/>
Used by NFL Gameday '98 (MagDemo04: GAMEDAY\BUILD\GRBA.FIL\\*)<br/>
Used by NFL Gameday '99 (MagDemo17: GAMEDAY\\*.BIT and \*.FIL\\*)<br/>
Used by NFL Gameday 2000 (MagDemo27: GAMEDAY\\*.BIT)<br/>
Used by NCAA Gamebreaker '98 (MagDemo05: GBREAKER\\*.BIT and UFLA.BIN\\*)<br/>
Used by NCAA Gamebreaker 2000 (MagDemo27: GBREAKER\\*.BIT and \*.FIL\\*)<br/>
Used by Twisted Metal 4 (MagDemo30: TM4DATA\\*.MR,\*.IMG\\*.bit,\*.clt)<br/>
```
  000h 2   VRAM.X             (X) (0..3FFh)
  002h 2   VRAM.X             (Y) (0..1FFh)
  004h 2   Width in halfwords (W) (1..400h)
  006h 2   Height             (H) (1..200h)
  008h ..  Bitmap or Palette data (W*H*2 bytes)
```

#### Doom (PSXDOOM\ABIN\PSXDOOM.WAD\\*\\*)
```
  000h 2     Hotspot X (signed) (usually 0)
  002h 2     Hotspot Y (signed) (usually 0)
  004h 2     Width in bytes
  006h 2     Height
  008h ..    Bitmap 8bpp (Width*Height bytes)
```
Most files have Hotspot X=0,Y=0, WAD\LOADING has X=FF80h,Y=FF8Ah, and WAD\S\\*
has X=0..Width, Y=0..Height+1Ah (eg. S\BKEY\*, S\BFG\*, S\PISFA0 have large Y).<br/>
The files do not contain any palette info... maybe 2800h-byte PLAYPAL does
contain the palette(s)?<br/>

#### Lemmings &amp; Oh No! More Lemmings (FILES\GFX\\*.BOB, FILES\SMLMAPS\\*.BOB)
```
  000h 2       Width
  002h 2       Height
  004h 100h*3  Palette 24bit RGB888
  304h ..      Bitmap 8bpp (Width*Height bytes)
  ..   (1700h) Unknown (only in SMLMAPS\*.BOB, not in GFX\*.BOB)
```
Apart from .BOB, the FILES\GFX folder also has vandalized .BMP (with ID
"BM",00h,00h) and corrupted .TIM (with VRAM.Y=200h).<br/>

#### Perfect Assassin (DATA.JFS\DATA\\*.BM)
```
  000h 4      Format 1 (0=8bpp, 1=16bpp)
  004h 4      Format 2 (1=8bpp, 2=16bpp)
  008h 4      Width in pixels
  00Ch 4      Height in pixels
  010h ..     Bitmap Data
  ...  (300h) Palette 18bit RGB666 (R,G,B range 00h..3Fh) (only if format 8bpp)
```

#### One (DIRFILE.BIN\\*.VCF)
```
  000h 4     Unknown (always 1)
  004h 4     Unknown (always 8)
  008h 4     Unknown (always 2) (maybe 2=16bpp?)
  00Ch 4     Width in pixels (3Ah, 140h, or 280h)
  010h 4     Height          (3Ah, or F0h)
  014h ..    Bitmap 16bpp (Width*Height*2 bytes)
```

#### One (DIRFILE.BIN\\*.VCK and DIRFILE.BIN\w\*\sect\*.bin\TEXTURE  001)
```
  000h 2     Number if Files (N)
  002h 2     Number of VRAM.Slots (less or equal than Number of Files)
  004h 4     ID "BLK0"
  008h N*10h File List
  ...  ..    1st File Bitmap
  ...  ..    1st File Palette (20h/200h/0 bytes for 4bpp/8bpp/16bpp)
  ...  ..    2nd File Bitmap
  ...  ..    2nd File Palette (only if PaletteID=FileNo=1)
  ...  ..    3rd File Bitmap
  ...  ..    3rd File Palette (only if PaletteID=FileNo=2)
  ...  ..    etc.
```
File List entries:<br/>
```
  000h 2     VRAM.X in halfwords (0..1Fh, +bit15=Blank)  ;\within current
  002h 2     VRAM.Y              (0..3Fh)                ;/VRAM.Slot
  004h 2     Width in pixels (max 80h/40h/20h for 4bpp/8bpp/16bpp)
  006h 2     Height          (max 40h)
  008h 2     VRAM.Slot       (0,1,2,3,...,NumSlots-1)
  00Ah 2     Unknown         (0,1,2,4 in *.vck, 4 in sect*.bin)
  00Ch 2     Color Depth     (0=4bpp, 1=8bpp, 2=16bpp)
  00Eh 2     Palette ID      (0..FileNo-1=Old, FileNo=New, FFFFh=None/16bpp)
  NumFiles-1, or ID of already used palette)
```
Note: VRAM.Slots are 20h\*40h halfwords.<br/>
Bitmaps can either have newly defined palettes (when PaletteID=FileNo), or
re-use previously defined "old" palettes (when PaletteID\<FileNo).<br/>
The Blank flag allows to define a blank region (for whatever purpose), the file
doesn't contain any bitmap/palette data for such blank regions.<br/>

#### BMR Bitmaps
These are 16bpp bitmaps, stored either in uncompressed .BMR files, or in
compressed .RLE files:<br/>
[CDROM File Compression RLE_16](cdromfileformats.md#cdrom-file-compression-rle_16)<br/>
```
  Apocalypse (MagDemo16: APOC\CD.HED\*.RLE and *.BMR)
  Spider-Man 1 older version (MagDemo31: SPIDEY\CD.HED\*.RLE)
  Spider-Man 1 newer version (MagDemo40: SPIDEY\CD.HED\*.RLE and .BMR)
  Spider-Man 2 (MagDemo50: HARNESS\CD.HED\*.RLE)
  Tony Hawk's Pro Skater (MagDemo22: PROSKATE\CD.HED\*.BMR)
```
The width/height for known filesizes are:<br/>
```
  33408h bytes --> 512x205pix, 16bpp (Apocalypse warning.rle)
  3C008h bytes --> 512x240pix, 16bpp (most common)
  96008h bytes --> 640x480pix, 16bpp (tony hawk's pro skater)
```
Most of the older BMR files (in Apocalypse) have valid 8-byte headers:<br/>
```
  000h 2     Unknown (FFA0h) (ID for files with valid headers?)
  002h 2     Dest.Y (usually 0) (11h=(240-205)/2 in Apocalypse warning.rle)
  004h 2     Width  (usually 200h=512pix)
  006h 2     Height (usually F0h=240pix) (CDh=205pix in Apocalypse warning.rle)
  008h ..    Bitmap data, 16bpp (width*height*2 bytes)
```
Most or all newer BMR files (in Apocalypse "loadlogo.rle", and in all files in
Spider-Man 1, Spider-Man-2, Tony Hawk's Pro Skater) have the 8-byte header
replaced by unused 8-byte at end of file:<br/>
```
  000h ..    Bitmap data, 16bpp (width*height*2 bytes)
  ..   8     Unused (garbage or extra pixels, not transferred to VRAM)
```
BUG: The bitmaps in all .BMR files (both with/without header) are distorted:
The last 4-byte (rightmost 2pix) of each scanline should be actually located at
the begin of the scanline, and the last scanline is shifted by an odd amount of
bytes (resulting in nonsense 16bpp pixel colors); Spider-Man is actually
displaying the bitmap in that distorted form (although it does mask off some
glitches: one of the two bad rightmost pixels is replaced by a bad black
leftmost pixel, and glitches in upper/lower lines aren't visible on 224-line
NTSC screens).<br/>

#### Croc 1 (retail: \*.IMG) (retail only, not in MagDemo02 demo version)
#### Croc 2 (MagDemo22: CROC2\CROCII.DIR\\*.IMG)
#### Disney's The Emperor's New Groove (MagDemo39: ENG\KINGDOM.DIR\\*.IMG)
#### Disney's Aladdin in Nasira's Rev. (MagDemo46: ALADDIN\ALADDIN.DIR\\*.IMG)
Contains raw 16bpp bitmaps, with following sizes:<br/>
```
  25800h bytes = 12C00h pixels (320x240)  ;Croc 1 (retail version)
  3C000h bytes = 1E000h pixels (512x240)
  96000h bytes = 4B000h pixels (640x480)
```
Note: The .IMG format is about same as .BMR files (but without the 8-byte
header, and without distorted scanlines).<br/>

#### Mat Hoffman's Pro BMX (MagDemo39: BMX\FE.WAD+STR\\*.BIN) (Activision)
#### Mat Hoffman's Pro BMX (MagDemo48: MHPB\FE.WAD+STR\\*.BIN) (Shaba/Activision)
```
  000h 2     Bits per pixel (4 or 8)
  002h 2     Bitmap Width in pixels
  004h 2     Bitmap Height in pixels
  006h 2     Zero
  008h N*2   Palette (with N=(1 SHL bpp))
  ...  ..    Bitmap (with Width*Height*bpp/8 bytes)
  ...  (..)  Zeropadding to 4-byte boundary (old version only)
```
The trailing alignment padding exists only in old demo version (eg. size of
78x49x8bpp "coreypp.bin" is old=10F8h, new=10F6h).<br/>

#### E.T. Interplanetary Mission (MagDemo54: MEGA\MEGA.CSH\\*)
```
  000h 2     Type (0=4bpp, 1=8bpp, 2=16bpp)
  002h 2     Unknown (usually 0000h, or sometimes CCCCh)
  004h 2     Bitmap Width in pixels
  006h 2     Bitmap Height in pixels
  008h 200h  Palette (always 200h-byte, even for 4bpp or 16bpp)
  208h ..    Bitmap (Width*Height*bpp/8 bytes)
```
Palette is 00h-or-CCh-padded when 4bpp, or CCh-filled when 16bpp.<br/>
Note: Some files contain two or more such bitmaps (of same or different sizes)
badged together.<br/>

#### EA Sports: Madden NFL '98 (MagDemo02: TIBURON\\*.DAT\\*)
#### EA Sports: Madden NFL 2000 (MagDemo27: MADN00\\*.DAT\\*)
#### EA Sports: Madden NFL 2001 (MagDemo39: MADN01\\*.DAT\\*)
This format is used in various EA Sports Madden .DAT archives, it contains
standard TIMs with extra Headers/Footers.<br/>
```
  000h 4     Offset to TIM (1Ch) (Hdr size)    (1Ch)               ;\
  004h 4     Offset to Footer    (Hdr+TIM size)(123Ch,1A3Ch,1830h) ;
  008h 2     Bitmap Width in pixels      (40h or 60h or 30h)       ;
  00Ah 2     Bitmap Height in pixels     (40h)                     ;
  00Ch 4     Unknown, always 01h         (01h)                     ; Header
  010h 4     Unknown, always 23h         (23h)                     ; 1Ch bytes
  014h 2     Unknown, always 0101h       (101h)                    ;
  016h 1     Bitmap Width in pixels      (40h or 60h or 30h)       ;
  017h 1     Bitmap Height in pixels     (40h)                     ;
  018h 4     Unknown, always 00h         (0)                       ;/
  01Ch ..    TIM (Texture, can be 4bpp, 8bpp, 16bpp)               ;-TIM
  ...  4     Unknown, always C0000222h   (C0000222h)               ;\
  ...  2     Unknown, always 0001h       (0001h)                   ;
  ...  1     Bitmap Width in pixels      (40h or 60h or 30h)       ; Footer
  ...  1     Bitmap Height in pixels     (40h)                     ; 12h bytes
  ...  4     Unknown, always 78000000h   (78000000h)               ;
  ...  6     Unknown                     (0,0,80h,0,0,0)           ;/
```
Purpose is unknown; the 8bit Width/Height entries might be TexCoords.<br/>
The PORTRAITS.DAT archives are a special case:<br/>
```
  Madden NFL '98 (MagDemo02: TIBURON\PORTRAIT.DAT) (48x64, 16bpp)
  Madden NFL 2000 (MagDemo27: MADN00\PORTRAIT.DAT) (96x64, 8bpp plus palette)
  Madden NFL 2001 (MagDemo39: MADN01\PORTRAIT.DAT) (64x64, 8bpp plus palette)
```
Those PORTRAITS.DAT don't have any archive header, instead they do contain
several images in the above format, each one zeropadded to 2000h-byte size.<br/>

#### 989 Sports: NHL Faceoff '99 (MagDemo17: FO99\\*.KGB\\*.TEX)
#### 989 Sports: NHL Faceoff 2000 (MagDemo28: FO2000\\*.TEX)
#### 989 Sports: NCAA Final Four 2000 (MagDemo30: FF00\\*.TEX)
```
  000h 0Ch  ID "TEX PSX ",01h,00h,00h,00h    ;used in 989 Sports games
  00Ch 4    Number of Textures
  010h 4    Total Filesize
  014h 4    Common Palette Size    (0=200h, 1=None, 2=20h)
  018h (..) Common Palette, if any (0,20h,200h bytes)
  ...  ..   Texture(s)
 Texture format:
  000h 10h  Filename (eg. "light1", max 16 chars, zeropadded if shorter)
  010h 4    Width in pixels  (eg. 40h)
  014h 4    Height           (eg. 20h or 40h)
  018h 4    Unknown          (always 0)
  01Ch 4    Number of Colors (eg. 10h, 20h or 100h)
  020h ..   Bitmap (4bpp when NumColors<=10h, 8bpp when NumColors>10h)
  ...  (..) Palette (NumColors*2 bytes, only present if Common Palette=None)
```
The .TEX files may be in ISO folders, KGB archives, DOTLESS archives. And, some
are stored in headerless .DAT/.CAT archives (which start with ID "TEX PSX ",
but seem to have further files appended thereafter).<br/>

#### Electronic Arts .PSH (SHPP)
FIFA - Road to World Cup 98 (with chunk C0h/C1h = RefPack compression)<br/>
NCAA March Madness 2000 (MagDemo32: MM2K\\*.PSH)<br/>
Need for Speed 3 Hot Pursuit (\*.PSH, ZLOAD\*.QPS\RefPack.PSH)<br/>
ReBoot (DATA\\*.PSH) (with chunk 6Bh)<br/>
Sled Storm (MagDemo24: DEBUG,ART,ART2,ART3,SOUND\\*.PSH) (with Comment, Mipmap)<br/>
WCW Mayhem (MagDemo28: WCWDEMO\\*.BIG\\*.PSH) (with chunk C0h/C1h = RefPack)<br/>
```
  000h 4    ID "SHPP"
  004h 4    Total Filesize (or Filesize-0Ch, eg. FIFA'98 ZLEG*.PSH)
  008h 4    Number of Textures (N)
  00Ch 4    ID "GIMX"
  010h N*8  File List
  ...  ..   Data (each File contains a Bitmap chunk, and Palette chunk, if any)
 File List entries:
  000h 4    Name (ascii) (Mipmaps use the same name for each mipmap level)
  004h 4    Offset from begin of archive to first Chunk of file
  Caution: Most PSH files do have the above offsets sorted in increasing order,
  but some have UNSORTED offsets, eg. Sled Storm (MagDemo24: ART3\LOAD1.PSH),
  so one cannot easily compute sizes as NextOffset-CurrOffset.
  Note: Mipmap textures consist of two files with same name and different
  resolution, eg. in Sled Storm (MagDemo24: ART\WORLD0x.PSH)
 Bitmap Chunk:
  000h 1    Chunk Type (40h=PSX/4bpp, 41h=PSX/8bpp, 42h=PSX/16bpp)
  001h 3    Offset from current chunk to next chunk (000000h=None)
  004h 2    Bitmap Width in pixels (can be odd, pad lines to 2-byte boundary)
  006h 2    Bitmap Height
  008h 2    Center X   (whatever that is)
  00Ah 2    Center Y   (whatever that is)
  00Ch 2    Position X (whatever that is, plus bit12-15=flags?)
  00Eh 2    Position Y (whatever that is, plus bit12-15=flags?)
  010h ..   Bitmap data (each scanline is padded to 2-byte boundary)
  ...  ..   Padding to 8-byte boundary
 Compressed Bitmap Chunk:
  000h 1    Chunk Type (C0h=PSX/4bpp, C1h=PSX/8bpp, and probably C2h=PSX/16bpp)
  001h 0Fh  Same as in Chunk 40h/41h/42h (see there)
  010h ..   Compressed Bitmap data (usually/always with Method=10FBh)
  ...  ..   Padding to 8-byte boundary
 Palette Chunk (if any) (only for 4bpp/8bpp bitmaps, not for 16bpp):
  000h 1    Chunk Type (23h=PSX/Palette)
  001h 3    Offset from current chunk to next chunk (000000h=None)
  004h 2    Palette Width in halfwords (10h or 100h)
  006h 2    Palette Height             (1)
  008h 2    Unknown (usually same as Width) (or 80D0h or 9240h)
  00Ah 2    Unknown (usually 0000h)         (or 0001h or 0002h)
  00Ch 2    Unknown (usually 0000h)
  00Eh 2    Unknown (usually 00F0h)
  010h ..   Palette data (16bit per color)
  Note: The odd 80D0h,0001h values occur in Sled Storm ART\WORKD00.PSH\TBR1)
 Unknown Chunk (eg. ReBoot (DATA\AREA15.PSH\sp*))
  000h 1    Chunk Type (6Bh)
  001h 3    Offset from current chunk to next chunk (000000h=None)
  004h 8    Unknown (2C,00,00,3C,03,00,00,00)
  00Ch -    For whatever reason, there is no 8-byte padding here
 Comment Chunk (eg. Sled Storm (MagDemo24: ART\WORLD0x.PSH))
  000h 1    Chunk Type (6Fh=PSX/Comment)
  001h 3    Offset from current chunk to next chunk (000000h=None)
  004h ..   Comment ("Saved in Photoshop Plugin made by PEE00751@...",00h)
  ...  ..   Zeropadding to 8-byte boundary
 Unknown Chunk (eg. Sled Storm (MagDemo24: ART\WORLD09.PSH\ADAA))
  000h 1    Chunk Type (7Ch)
  001h 3    Offset from current chunk to next chunk (000000h=None)
  004h 2Ch  Unknown (reportedly Hot spot / Pix region, but differs on PSX?)
```
The whole .PSH file or the bitmap chunks can be compressed:<br/>
[CDROM File Compression EA Methods](cdromfileformats.md#cdrom-file-compression-ea-methods)<br/>
Variants of the .PSH format are also used on PC, PS2, PSP, XBOX (with other
Chunk Types for other texture/palette formats, and for optional extra data).
For details, see: <http://wiki.xentax.com/index.php/EA_SSH_FSH_Image>


#### Destruction Derby Raw (MagDemo35: DDRAW\\*.PCK,\*.FNT,\*.SPR)
This format can contain one single Bitmap, or a font with several small
character bitmaps.<br/>
```
  000h 2     ID "BC"                                        ;\
  002h 1     Color Depth (1=4bpp, 2=8bpp, 4=16bpp)          ; Header
  003h 1     Type        (40h=Bitmap, C0h=Font)             ;/
  ...  (2)   Palette Unknown (0 or 1)                       ;\only if Bitmap
  ...  (2)   Palette Unknown (1)                            ; 4bpp or 8bpp
  ...  (..)  Palette data (20h or 200h bytes for 4bpp/8bpp) ;/
  ...  2     Bitmap Number of Bitmaps-1 (N-1)               ;\
  ...  2     Bitmap Width in pixels                         ;
  ...  2     Bitmap Height in pixels                        ; Bitmap(s)
  ...  N*1   Bitmap Tilenumbers (eg. "ABCDEFG..." for Fonts);
  ...  N*1   Bitmap Proportional Font widths? (0xh or FFh)  ;
  ...  N*BMP Bitmap(s) for all characters                   ;/
  ...  (20h) Palette Data (20h bytes for 4bpp)              ;-only if Font/4bpp
```
All bitmap scanlines are padded to 2-byte boundary, eg. needed for:<br/>
```
  INGAME1\BOWL2.PTH\SPRITES.PTH\ST.SPR    30x10x4bpp: 15 --> 16 bytes/line
  INGAME1\BOWL2.PTH\SPRITES.PTH\STOPW.SPR 75x40x4bpp: 37.5 --> 38 bytes/line
```
The BC files are usually compressed (either in PCK file, or in the compressed
DAT portion of a PTH+DAT archive).<br/>

#### Cool Boarders 2 (MagDemo02: CB2\DATA\*\\*.FBD)
```
  000h 2    ID ("FB")                                ;\File Header
  002h 2    Always 1 (version? 4bpp? num entries?)   ;/
  004h 2    Palette VRAM Dest X (eg. 300h)           ;\
  006h 2    Palette VRAM Dest Y (eg. 1CCh,1EDh,1FFh) ; Palette Header
  008h 2    Palette Width in halfwords (eg. 100h)    ; (all zero when unused)
  00Ah 2    Palette Height (eg. 1 or 0Dh)            ;/
  00Ch 2    Bitmap VRAM Dest X (eg. 140h or 200h)    ;\
  00Eh 2    Bitmap VRAM Dest Y (eg. 0 or 100h)       ; Bitmap Header
  010h 2    Bitmap Width in halfwords                ;
  012h 2    Bitmap Height                            ;/
  ...  ..   Palette Data (if any)                    ;-Palette Data
  ...  ..   Bitmap Data                              ;-Bitmap Data
```
The bitmap data seems to be 4bpp and/or 8bpp, but it's hard to know the correct
palette (some files have more than 16 or 256 palette colors, or don't have any
palette at all).<br/>



##   CDROM File Video Texture/Bitmap (TGA)
#### Targa TGA
```
  000h 1   Image ID Size (00h..FFh, usually 0=None)      ;0
  001h 1   Palette Present Flag (0=None, 1=Present)      ;0            iv=1
  002h 1   Data Type code (0,1,2,3,9,10,11,32,33)        ;NEBULA=2     iv=1
  003h 2   Palette First Color (usually 0)               ;0            iv=0
  005h 2   Palette Number of Colors (usually 100h)       ;0            iv=100h
  007h 1   Palette Bits per Color (16,24,32, usually 24) ;0            iv=18h
  008h 2   Bitmap X origin (usually 0)                   ;0
  00Ah 2   Bitmap Y origin (usually 0)                   ;0
  00Ch 2   Bitmap Width                                  ;NEBULA=20h LOGO=142h
  00Eh 2   Bitmap Height                                 ;NEBULA=20h
  010h 1   Bitmap Bits per Pixel (8,16,24,32 exist?)     ;NEBULA=18h   iv=8
  011h 1   Image Descriptor (usually 0)                  ;0
  012h ..  Image ID Data (if any, len=[00h], usually 0=None)
  ...  ..  Palette
  ...  ..  Bitmap
  ...  1Ah Footer (8x00h, "TRUEVISION-XFILE.", 00h) (not present in iview)
```
Data Type [02h]:<br/>
```
  00h = No image data included  ;-Unknown purpose
  01h = Color-mapped image      ;\
  02h = RGB image               ; Uncompressed
  03h = Black and white image   ;/
  09h = Color-mapped image      ;\Runlength
  0Ah = RGB image               ;/
  0Bh = Black and white image   ;-Unknown compression method
  20h = Color-mapped image      ;-Huffman+Delta+Runlength
  21h = Color-mapped image      ;-Huffman+Delta+Runlength+FourPassQuadTree
```
The official specs do list the above 9 types, but do describe only 4 types in
detail (type 01h,02h,09h,0Ah).<br/>
```
  Type 01h and 09h lack details on supported bits per pixel (8bpp with 100h
    colors does exist; unknown if less (or more) than 8bpp are supported,
    and if so, in which bit order.
  Type 02h and 0Ah are more or less well documented.
  Type 03h has unknown bit-order, also unknown if/how it differs from type
    01h with 1bpp.
  Type 0Bh, 20h, 21h lack any details on the compression method.
```
TGA's are used by a couple of PSX games/demos (all uncompressed):<br/>
```
  16bpp: Tomb Raider 2 (MagDemo01: TOMBRAID\*.RAW)
  24bpp: Tomb Raider 2 (MagDemo05: TOMB2\*.TGA)
  24bpp: Colony Wars Venegance (MagDemo14: CWV\GAME.RSC\NEBULA*.TGA, *SKY.TGA)
  24bpp: Colony Wars Red Sun (MagDemo31: CWREDSUN\GAME.RSC\000A\*)
  16bpp: Colony Wars Venegance (MagDemo14: CWV\GAME.RSC\LOGO.DAT)
  16bpp: X-Men: Mutant Academy (MagDemo50: XMEN2\*)
  16bpp: Disney's Tarzan (MagDemo42: TARZAN\*)
  8bpp+Wrong8bitAttr: SnoCross Championship Racing (MagDemo37: SNOCROSS\*.TGA)
  16bpp+WrongYflip: SnoCross Championship Racing (MagDemo37: SNOCROSS\*.TGA)
```
For whatever reason, TGA is still in use on newer consoles:<br/>
```
  32bpp: 3DS AR Games (RomFS:\i_ar\tex\hm*.lz77
```



##   CDROM File Video Texture/Bitmap (PCX)
#### PC Paintbrush .PCX files (ZSoft)
Default extension is .PCX (some tools did use .PCX for the "main" image, and
.PCC for smaller snippets that were clipped/cropped/copied from from a large
image).<br/>
```
  000h 1    File ID (always 0Ah=PCX/ZSoft)
  001h 1    Version (0,2,3,4,5)
  002h 1    Compression (always 01h=RLE) (or inofficial: 00h=Uncompressed)
  003h 1    Bits per Pixel (per Plane) (1, 2, 4, or 8)
  004h 2    Window X1   ;\
  006h 2    Window Y1   ; Width  = X2+1-X1
  008h 2    Window X2   ; Height = Y2+1-Y1
  00Ah 2    Window Y2   ;/
  00Ch 2    Horizontal Resolution in DPI  ;\often square, but can be also zero,
  00Eh 2    Vertical Resolution in DPI    ;/or screen size, or other values
  010h 30h  EGA/VGA Palette (16 colors, 3-byte per color = R,G,B) (or garbage)
  010h 1    CGA: Bit7-4=Background Color (supposedly IRGB1111 ?)
  013h 1    CGA: Bit7:0=Color,1=Mono,Bit6:0=Yellow,1=White,Bit5:0=Dim,1=Bright
  014h 1    Paintbrush IV: New CGA Color1 Green  ;\weird new way to encode CGA
  015h 1    Paintbrush IV: New CGA Color1 Red    ;/palette in these two bytes
  040h 1    Reserved (00h) (but is 96h in animals.pcx)
  041h 1    Number of color planes (1=Palette, 3=RGB, or 4=RGBI)
  042h 2    Bytes per Line (per plane) (must be N*2) (=(Width*Bits+15)/16*2)
  044h 2    PaletteInfo? (0000h/xxxxh=Normal, 0001h=Color/BW, 0002h=Grayscale)
  046h 2    Horizontal screen size in pixels  ;\New fields, found only
  048h 2    Vertical screen size in pixels    ;/in Paintbrush IV/IV Plus
  04Ah 36h  Reserved (zerofilled) (or garbage in older files, custom in MGS)
  080h ..   Bitmap data (RLE compressed)
  ...  1    VGA Palette ID (0Ch=256 colors)                      ;\when 8bpp
  ..   300h VGA Palette (256 colors, 3-byte per color  = R,G,B)  ;/
```
Decoding PCX files is quite a hardcore exercise due to a vast amount of
versions, revisions, corner cases, incomplete &amp; bugged specifications, and
inofficial third-party glitches.<br/>

#### PCX Versions
```
  00h = Version 2.5 whatever ancient stuff
  02h = Version 2.8 with custom 16-color palette
  03h = Version 2.8 without palette (uses fixed CGA/EGA palette)
  04h = Version ?.? without palette (uses fixed CGA/EGA palette)
  05h = Version 3.0 with custom 16-color or 256-color palette or truecolor
```
NOTE: Version[01h]=05h with PaletteInfo[44h]=0001h..0002h is Paintbrush IV?<br/>

#### Known PCX Color Depths
```
  planes=1, bits=1  P1        ;1bit, HGC 2 color (iview and paint shop pro 2)
  planes=1, bits=2  P2        ;2bit, CGA 4 color (with old/new palette info)
  planes=3, bits=1  RGB111    ;3bit, EGA 8 color (official samples)  ;\version
  planes=4, bits=1  IRGB1111  ;4bit, EGA 16 color (paint shop pro 2) ;/03h..04h
  planes=1, bits=4  P4        ;4bit, BMP 16 color (iview)
  planes=1, bits=8  P8        ;8bit, VGA 256 color palette
  planes=1, bits=8  I8        ;8bit, VGA 256 level grayscale (gmarbles.pcx)
  planes=3, bits=8  BGR888    ;24bit, truecolor (this is official 24bit format)
 ;planes=1, bits=24 BGR888 ?  ;24bit, reportedly exists? poor compression
 ;planes=4, bits=4  ABGR4444  ;16bit, wikipedia-myth? unlikely to exist
 ;planes=4, bits=8  ABGR8888  ;32bit, truecolor+alpha (used in abydos.dcx\*)
```

#### Width and Height
These are normally calculated as so:<br/>
```
  Width  = X2+1-X1      ;width for normal files
  Height = Y2+1-Y1      ;height for normal files
```
However, a few PCX files do accidentally want them to be calculated as so:<br/>
```
  Width  = X2-X1        ;width for bugged files
  Height = Y2-Y1        ;height for bugged files
```
Files with bugged width can be (sometimes) detected as so:<br/>
```
  (Width*Bits+15)/16*2) > BytesPerLine
```
Files with bugged height can be detected during decompression:<br/>
```
  BeginOfLastScanline >= Filesize (or Filesize-301h for files with palette)
```
Bugged sample files are SAMPLE.DCX, marbles.pcx and gmarbles.pcx. RLE
decompression may crash when not taking care of such files.<br/>

#### Color Planes and Palettes
The official ZSoft PCX specs are - wrongly - describing planes as:<br/>
```
  plane0 = red         ;\
  plane1 = green       ; this is WRONG, NONSENSE, does NOT exist
  plane2 = blue        ;
  plane3 = intensity   ;/
```
The 8-color and 16-color EGA images are actually using plane0,1,2,(3) as
bit0,1,2,(3) of the EGA color number; which implies plane0=blue (ie. red/blue
are opposite of the ZSoft document).<br/>
The truecolor and truecolor+alpha formats have plane0..2=red,green,blue (as
described by ZSoft), but they don't have any intensity plane (a few files are
using plane3=alpha).<br/>

#### Mono 2-Color Palette
This format was intended for 640x200pix 2-color CGA graphics, it's also common
for higher resolution FAX or print images. The general rule for these files is
to use this colors:<br/>
```
  color0=black
  color1=white
```
There are rumours that color1 could be changed to any of the 16 CGA colors
(supposedly via [10h].bit7-4, but most older &amp; newer 2-color files have
that byte set to 00h, so one would end up with black-on-black).<br/>
Some newer 2-color files contain RGB palette entries [10h]=000000h,
[13h]=FFFFFFh (and [16h..3Fh]=00h-filled or FFh-filled).<br/>
Iview does often display 2-color images with color1=dark green (somewhat
mysteriously; it's doing that even for files that don't contain any CGA color
numbers or RGB palette values that could qualify as dark green).<br/>

#### 4-Color Palettes
This format was intended for 320x200pix 4-color CGA graphics, and the palette
is closely bound to colors available in CGA graphics modes. Color0 is defined
in [10h], and Color1-3 were originally defined in [13h], and later in
[14h,15h]:<br/>
```
  color0=[10h].bit7-4  ;(Color0 IRGB)  ;CGA Port 3D9h.bit3-0 (usually 0=black)
  bright=[13h].bit5                    ;CGA Port 3D9h.bit4    ;\
  palette=[13h].bit6                   ;CGA Port 3D9h.bit5    ; old method
  if [13h].bit7 then palette=2         ;CGA Port 3D8h.bit2    ;/
  if [01h]=05h and [44h]=0001h then                           ;\new "smart"
    if [14h]>200 or [15h]>200 then bright=1, else bright=0    ; method used in
    if [14h]>[15h] then palette=0 else palette=1              :/Paintbrush IV
  if palette=0 and bright=0 then color1..3=02h,04h,06h  ;\green-red-yellow
  if palette=0 and bright=1 then color1..3=0Ah,0Ch,0Eh  ;/
  if palette=1 and bright=0 then color1..3=03h,05h,07h  ;\cyan-magenta-white
  if palette=1 and bright=1 then color1..3=0Bh,0Dh,0Fh  ;/
  if palette=2 and bright=0 then color1..3=03h,04h,07h  ;\cyan-red-white
  if palette=2 and bright=1 then color1..3=0Bh,0Ch,0Fh  ;/
```
Palette=2 uses some undocumented CGA glitch, it was somewhat intended to output
grayscale by disabling color burst on CGA hardware with analog composite
output, but actually most or all CGA hardware is having digital 4bit IRGB
output, which outputs cyan-red-white.<br/>
The new "smart" method is apparently trying to detect if [13h-1Bh] contains RGB
values with Color1=Green or Cyan, and to select the corresponding CGA palette;
unfortunately such PCX files are merely setting [14h,15h] to match up with the
"smart" formula, without actually storing valid RGB values in [13h-1Bh].<br/>

#### 8-Color and 16-Color, with fixed EGA Palettes (version=03h or 04h)
These images have 3 or 4 planes. Plane0-3 correspond to bit0-3 of the EGA color
numbers (ie. blue=plane0, green=plane1, red=plane2, and either intensity=plane3
for 16-color, or intensity=0 for 8-color images).<br/>
Some 8-Color sample images (with version=03h and 04h) can be found bundled with
PC Paintbrush Plus 1.22 for Windows. A 16-color sample called WINSCR.PCX can be
found elsewhere in internet.<br/>
Caution 1: Official ZSoft specs are wrongly claiming plane0=red and
plane2=blue; this is wrong (although Paint Shop Pro 2 is actually implementing
it that way) (whilst MS Paint for Win95b can properly display them) (most other
tools are trying to read a palette from [10h..3Fh], which is usually garbage
filled in version=03h..04h).<br/>
Caution 2: The standard EGA palette is used for version=03h..04h (many docs
claim it to be used for version=03h only).<br/>

#### 16-Color, with custom EGA/VGA Palettes (version=02h or 05h)
These can have 1 plane with 4 bits, or 4 planes with 1 bit. Header[10h..3Fh]
contains a custom 16-color RGB palette with 3x8bit per R,G,B.<br/>
Classic VGA hardware did only use the upper 6bit of the 8bit values.<br/>
Classic EGA hardware did only use the upper 2bit of the 8bit values (that, only
when having a special EGA monitor with support for more than 16 colors).<br/>

#### 256-Color VGA Palettes (version=05h)
These have 1 plane with 8 bits. And a 256-color RGB palette with 3x8bit per
R,G,B appended at end of file.<br/>
The appended 256-color palette should normally exist only in 256-color images,
some PCX tools are reportedly always appending the extra palette to all
version=05h files (even for 2-color files).<br/>

#### 256-Level Grayscale Images (version=05h and [44h]=0002h)
The most obvious and reliable way is to use a palette with grayscale RGB
values. However, Paintbrush IV is explicetly implementing (or ignoring?) an
obscure grayscale format with following settings:<br/>
```
  [01h]=version=05h, and [44h]=0002h=grayscale
```
That settings are used in a file called gmarbles.pcx (which does contain a
256-color RGB palette with gray RGB values, ie. one can simply ignore the
special settings, and display it as normal 256-color image).<br/>

#### Default 16-color CGA/EGA Palettes
```
  Color  Name                     IRGB1111 RGB222 RGB888   Windows
  00h    dark black               0000     000    000000   000000
  01h    dark blue                0001     002    0000AA   000080
  02h    dark green               0010     020    00AA00   008000
  03h    dark cyan                0011     022    00AAAA   008080
  04h    dark red                 0100     200    AA0000   800000
  05h    dark magenta             0101     202    AA00AA   800080
  06h    dark yellow (brown)      0110     210!!  AA5500!! 808000
  07h    dark white (light gray)  0111     222    AAAAAA   C0C0C0!!
  08h    bright black (dark gray) 1000     111    555555   808080!!
  09h    bright blue              1001     113    5555FF   0000FF
  0Ah    bright green             1010     131    55FF55   00FF00
  0Bh    bright cyan              1011     133    55FFFF   00FFFF
  0Ch    bright red               1100     311    FF5555   FF0000
  0Dh    bright magenta           1101     313    FF55FF   FF00FF
  0Eh    bright yellow            1110     331    FFFF55   FFFF00
  0Fh    bright white             1111     333    FFFFFF   FFFFFF
```
Some notes on number of colors:<br/>
```
 CGA supports 16 colors in text mode (but only max 4 colors in graphics mode).
 EGA supports the same 16 colors as CGA in both text and graphics mode.
 EGA-with-special-EGA-monitor supports 64 colors (but only max 16 at once).
 VGA supports much colors (but can mimmick CGA/EGA colors, or similar colors)
```
CGA is using a 4pin IRGB1111 signal for up to 16 colors in text mode (max 4
colors in graphics mode), and CGA monitors contain some circuitry to convert
"dark yellow" to "brown" (though cheap CGA clones may display it as "dark
yellow").<br/>
EGA can display CGA colors (with all 16 colors in graphics mode).
EGA-with-special-EGA-monitor uses 6pin RGB222 signals for up to 64 colors (but
not more than 16 colors at once).<br/>
Windows is also using those 16 standard colors (when not having any VGA driver
installed, and also in 256-color VGA mode, in the latter case the 16 standard
colors are held to always available (even if different tasks are trying to
simultanously display different images with different palettes).<br/>
However, Windows has dropped brown, and uses non-pastelized bright colors.<br/>

#### PCX files in PSX games
```
  .PCX with RLE used by Jampack Vol. 1 (MDK\CD.HED\*.pcx)
  .PCX with RLE used by Hot Wheels Extreme Racing (MagDemo52: US_01293\MISC\*)
  .PCX with RLE used by Metal Gear Solid (slightly corrupted PCX files)
```

#### PCX files in PSX Metal Gear Solid (MGS)
MGS is storing some extra data at [4Ah..57h] (roughly resembling the info in
TIM files).<br/>
```
  04Ah 2    Custom MGS ID (always 3039h)
  04Ch 2    Display Mode? (08h/18h=4bit, 09h/19h=8bit)
  04Eh 2    Bitmap X-coordinate in VRAM (reportedly "divided by 2" ???)
  050h 2    Bitmap Y-coordinate in VRAM
  052h 2    Palette X-coordinate in VRAM
  054h 2    Palette Y-coordinate in VRAM
  056h 2    Palette number of actually used colors (can be less than 16/256)
  058h 28h  Reserved (zerofilled)
  080h ..   Bitmap data (RLE compressed)
  ...  1    VGA Palette ID (0Ch=256 colors)                      ;\when 8bpp
  ..   300h VGA Palette (256 colors, 3-byte per color  = R,G,B)  ;/
  ..   ..   Padding to 4-byte boundary, ie. palette isn't at filesize-301h !!!
```
MGS has filesize padded to 4-byte boundary. That is causing problems for files
with 256-color palette: The official way to find the palette is to stepback
301h bytes from end of file, which won't work with padding. To find the MGS
palette, one must decompress the whole bitmap, and then expect the 301h-byte
palette to be located after the compressed data.<br/>
As an extra oddity, MGS uses non-square ultra-high DPI values.<br/>

#### DCX Archives
DCX archives contain multiple PCX files (eg. multi-page FAX documents). The
standard format is as so:<br/>
```
  0000h 4     ID (3ADE68B1h) (987654321 decimal)
  0004h 4000h File List (32bit offsets) (max 1023 files, plus 0=End of List)
  1004h ..    File Data area (PCX files)
```
However, some files have the first PCX at offset 1000h (ie. the list is only
3FFCh bytes tall). Reportedly there are also files that start with yet smaller
offsets (for saving space when the file list contains fewer entries).<br/>
The PCX filesize is next-curr offset (or total-curr for last file).<br/>

#### References
<https://www.fileformat.info/format/pcx/egff.htm>




