---
name: bios-file-cd-memcard
description: "PSX BIOS kernel functions: file I/O (open/read/write/close), CDROM access, memory card read/write, function tables (A/B/C), BIOS memory map. Use when calling BIOS functions for file or storage access."
---

#   Kernel (BIOS)
[BIOS Overview](#bios-overview)<br/>
[BIOS Memory Map](#bios-memory-map)<br/>
[BIOS Function Summary](#bios-function-summary)<br/>
[BIOS File Functions](#bios-file-functions)<br/>
[BIOS File Execute and Flush Cache](#bios-file-execute-and-flush-cache)<br/>
[BIOS CDROM Functions](#bios-cdrom-functions)<br/>
[BIOS Memory Card Functions](#bios-memory-card-functions)<br/>
[BIOS Interrupt/Exception Handling](../bios-irq-threads-timer/SKILL.md#bios-interruptexception-handling)<br/>
[BIOS Event Functions](../bios-irq-threads-timer/SKILL.md#bios-event-functions)<br/>
[BIOS Event Summary](../bios-irq-threads-timer/SKILL.md#bios-event-summary)<br/>
[BIOS Thread Functions](../bios-irq-threads-timer/SKILL.md#bios-thread-functions)<br/>
[BIOS Timer Functions](../bios-irq-threads-timer/SKILL.md#bios-timer-functions)<br/>
[BIOS Joypad Functions](../bios-irq-threads-timer/SKILL.md#bios-joypad-functions)<br/>
[BIOS GPU Functions](../bios-irq-threads-timer/SKILL.md#bios-gpu-functions)<br/>
[BIOS Memory Allocation](../bios-irq-threads-timer/SKILL.md#bios-memory-allocation)<br/>
[BIOS Memory Fill/Copy/Compare (SLOW)](../bios-irq-threads-timer/SKILL.md#bios-memory-fillcopycompare-slow)<br/>
[BIOS String Functions](../bios-irq-threads-timer/SKILL.md#bios-string-functions)<br/>
[BIOS Number/String/Character Conversion](../bios-irq-threads-timer/SKILL.md#bios-numberstringcharacter-conversion)<br/>
[BIOS Misc Functions](../bios-irq-threads-timer/SKILL.md#bios-misc-functions)<br/>
[BIOS Internal Boot Functions](../bios-boot-internals/SKILL.md#bios-internal-boot-functions)<br/>
[BIOS More Internal Functions](../bios-boot-internals/SKILL.md#bios-more-internal-functions)<br/>
[BIOS PC File Server](../bios-boot-internals/SKILL.md#bios-pc-file-server)<br/>
[BIOS TTY Console (std_io)](../bios-boot-internals/SKILL.md#bios-tty-console-std_io)<br/>
[BIOS Character Sets](../bios-boot-internals/SKILL.md#bios-character-sets)<br/>
[BIOS Control Blocks](../bios-boot-internals/SKILL.md#bios-control-blocks)<br/>
[BIOS Versions](../bios-boot-internals/SKILL.md#bios-versions)<br/>
[BIOS Patches](../bios-boot-internals/SKILL.md#bios-patches)<br/>



##   BIOS Overview
#### BIOS CDROM Boot
The main purpose of the BIOS is to boot games from CDROM, unfortunately, before
doing that, it displays the Sony intro. It's also doing some copy protection
and region checks, and refuses to boot unlicensed games, or illegal copies, or
games for other regions.<br/>

#### BIOS Bootmenu
The bootmenu shows up when starting the Playstation without CDROM inserted. The
menu allows to play Audio CDs, and to erase or copy game positions on Memory
Cards.<br/>

#### BIOS Functions
The BIOS contains a number of more or less useful, and probably more or less
inefficient functions that can be used by software.<br/>
No idea if it's easy to take full control of the CPU, ie. to do all hardware
access and interrupt handling by software, without using the BIOS at all?<br/>
Eventually the BIOS functions for accessing the CDROM drive are important, not
sure how complicated/compatible it'd be to access the CDROM drive directly via
I/O ports... among others, there might be different drives used in different
versions of the Playstation, which aren't fully compatible with each other?<br/>

#### BIOS Memory
The BIOS occupies 512Kbyte ROM with 8bit address bus (so the BIOS ROM is rather
slow, for faster execution, portions of it are relocated to the first 64K of
RAM). For some very strange reason, the original PSX BIOS executes all ROM
functions in uncached ROM, which is incredible slow (nocash BIOS uses cached
ROM, which does work without problems).<br/>
The first 64Kbyte of the 2Mbyte Main RAM are reserved for the BIOS (containing
exception handlers, jump tables, other data, and relocated code). That reserved
region does unfortunately include the "valuable" first 32Kbytes (valuable
because that memory could be accessed directly via [R0+immediate], without
needing to use R1..R31 as base register).<br/>



##   BIOS Memory Map
#### BIOS ROM Map (512Kbytes)
```
  BFC00000h Kernel Part 1  (code/data executed in uncached ROM)
  BFC10000h Kernel Part 2  (code/data relocated to cached RAM)
  BFC18000h Intro/Bootmenu (code/data decompressed and relocated to RAM)
  BFC64000h Character Sets
```

#### BIOS ROM Header/Footer
```
  BFC00100h Kernel BCD date  (YYYYMMDDh)
  BFC00104h Console Type     (see Port 1F802030h, Secondary IRQ10 Controller)
  BFC00108h Kernel Maker/Version Strings (separated by one or more 00h bytes)
  BFC7FF32h GUI Version/Copyright Strings (if any) (separated by one 00h byte)
```

#### BIOS RAM Map (1st 64Kbytes of RAM) (fixed addresses mainly in 1st 500h bytes)
```
  00000000h 10h    Garbage Area (see notes below)
  00000010h 30h    Unused/reserved
  00000040h 20h    COP0 debug-break vector (not used by Kernel) (in KSEG0)
  00000060h 4      RAM Size (in megabytes) (2 or 8)
  00000064h 4      Unknown (set to 00000000h)
  00000068h 4      Unknown (set to 000000FFh)
  0000006Ch 14h    Unused/reserved
  00000080h 10h    Exception vector (actually in KSEG0, ie. at 80000080h)
  00000090h 10h    Unused/reserved
  000000A0h 10h    A(nnh) Function Vector
  000000B0h 10h    B(nnh) Function Vector
  000000C0h 10h    C(nnh) Function Vector
  000000D0h 30h    Unused/reserved
  00000100h 58h    Table of Tables (BIOS Control Blocks) (see below)
  00000158h 28h    Unused/reserved
  00000180h 80h    Command line argument from SYSTEM.CNF; BOOT = fname argument
  00000200h 300h   A(nnh) Jump Table
  00000500h ...    Kernel Code/Data (relocated from ROM)
  0000Cxxxh ...    Unused/reserved
  0000DF80h 80h    Used for BIOS Patches (ie. used by games, not used by BIOS)
  0000DFFCh 4      Response value from Intro/Bootmenu
  0000E000h 2000h  Kernel Memory; ExCBs, EvCBs, and TCBs allocated via B(00h)
```

#### User Memory (not used by Kernel)
```
  00010000h ...    Begin of User RAM (Exefile, Data, Heap, Stack, etc.)
  001FFF00h ...    Default Stacktop (usually in KSEG0)
  1F800000h 400h   Scratchpad (Data-Cache mis-used as Fast RAM)
```

#### Table of Tables (see BIOS Control Blocks for details)
Each table entry consists of two 32bit values; containing the base address, and
total size (in bytes) of the corresponding control blocks.<br/>
```
  00000100h  ExCB Exception Chain Entrypoints (addr=var, size=4*08h)
  00000108h  PCB  Process Control Block       (addr=var, size=1*04h)
  00000110h  TCB  Thread Control Blocks       (addr=var, size=N*C0h)
  00000118h  -    Unused/reserved
  00000120h  EvCB Event Control Blocks        (addr=var, size=N*1Ch)
  00000128h  -    Unused/reserved
  00000130h  -    Unused/reserved
  00000138h  -    Unused/reserved
  00000140h  FCB  File Control Blocks         (addr=fixed, size=10h*2Ch)
  00000148h  -    Unused/reserved
  00000150h  DCB  Device Control Blocks       (addr=fixed, size=0Ah*50h)
```
File handles (fd=00h..0Fh) can be simply converted as fcb=[140h]+fd\*2Ch.<br/>
Event handles (event=F10000xxh) as evcb=[120h]+(event AND FFFFh)\*1Ch.<br/>

#### Garbage Area at Address 00000000h
The first some bytes of memory address 00000000h aren't actually used by the
Kernel, except for storing some garbage at that locations. However, this
garbage is actually important for bugged games like R-Types and Fade to Black
(ie. games that do read from address 00000000h due to using uninitialized
pointers).<br/>
Initially, the garbage area is containing a copy of the 16-byte exception
handler at address 80h, but the first 4-bytes are typically smashed (set to
00000003h from some useless dummy writes in some useless CDROM delays). Ie. the
16-bytes should have these values:<br/>
```
  [00000000h]=3C1A0000h  ;<-- but overwritten by 00000003h after soon
  [00000004h]=275A0C80h  ;<-- or 275A0C50h (in older BIOS)
  [00000008h]=03400008h
  [0000000Ch]=00000000h
```
For R-Types, the halfword at [0] must non-zero (else the game will do a DMA to
address 0, and thereby destroy kernel memory). Fade to Black does several
garbage reads from [0..9], a wrong byte value at [5] can cause the game to
crash with an invalid memory access exception upon memory card access.<br/>



##   BIOS Function Summary
#### Parameters, Registers, Stack
Argument(s) are passed in R4,R5,R6,R7,[SP+10h],[SP+14h],etc.<br/>
Caution: When calling a sub-function with N parameters, the caller MUST always
allocate N words on the stack, and, although the first four parameters are
passed in registers rather than on stack, the sub-function is allowed to
use/destroy these words at [SP+0..N\*4-1].<br/>
BIOS Functions (and custom callback functions) are allowed to destroy registers
R1-R15, R24-R25, R31 (RA), and HI/LO. Registers R16-R23, R29 (SP), and R30 (FP)
must be left unchanged (if the function uses that registers, then it must
push/pop them). R26 (K0) is reserved for exception handler and should be
usually not used by other functions. R27 (K1) and R28 (GP) are left more or
less unused by the BIOS, so one can more or less freely use them for whatever
purpose.<br/>
The return value (if any) is stored in R2 register.<br/>

#### A-Functions (Call 00A0h with function number in R9 Register)
```
  A(00h) or B(32h) open(filename,accessmode)
  A(01h) or B(33h) lseek(fd,offset,seektype)
  A(02h) or B(34h) read(fd,dst,length)
  A(03h) or B(35h) write(fd,src,length)
  A(04h) or B(36h) close(fd)
  A(05h) or B(37h) ioctl(fd,cmd,arg)
  A(06h) or B(38h) exit(exitcode)
  A(07h) or B(39h) isatty(fd)
  A(08h) or B(3Ah) getc(fd)
  A(09h) or B(3Bh) putc(char,fd)
  A(0Ah) todigit(char)
  A(0Bh) atof(src)     ;Does NOT work - uses (ABSENT) cop1 !!!
  A(0Ch) strtoul(src,src_end,base)
  A(0Dh) strtol(src,src_end,base)
  A(0Eh) abs(val)
  A(0Fh) labs(val)
  A(10h) atoi(src)
  A(11h) atol(src)
  A(12h) atob(src,num_dst)
  A(13h) setjmp(buf)
  A(14h) longjmp(buf,param)
  A(15h) strcat(dst,src)
  A(16h) strncat(dst,src,maxlen)
  A(17h) strcmp(str1,str2)
  A(18h) strncmp(str1,str2,maxlen)
  A(19h) strcpy(dst,src)
  A(1Ah) strncpy(dst,src,maxlen)
  A(1Bh) strlen(src)
  A(1Ch) index(src,char)
  A(1Dh) rindex(src,char)
  A(1Eh) strchr(src,char)  ;exactly the same as "index"
  A(1Fh) strrchr(src,char) ;exactly the same as "rindex"
  A(20h) strpbrk(src,list)
  A(21h) strspn(src,list)
  A(22h) strcspn(src,list)
  A(23h) strtok(src,list)  ;use strtok(0,list) in further calls
  A(24h) strstr(str,substr)       ;Bugged
  A(25h) toupper(char)
  A(26h) tolower(char)
  A(27h) bcopy(src,dst,len)
  A(28h) bzero(dst,len)
  A(29h) bcmp(ptr1,ptr2,len)      ;Bugged
  A(2Ah) memcpy(dst,src,len)
  A(2Bh) memset(dst,fillbyte,len)
  A(2Ch) memmove(dst,src,len)     ;Bugged
  A(2Dh) memcmp(src1,src2,len)    ;Bugged
  A(2Eh) memchr(src,scanbyte,len)
  A(2Fh) rand()
  A(30h) srand(seed)
  A(31h) qsort(base,nel,width,callback)
  A(32h) strtod(src,src_end) ;Does NOT work - uses (ABSENT) cop1 !!!
  A(33h) malloc(size)
  A(34h) free(buf)
  A(35h) lsearch(key,base,nel,width,callback)
  A(36h) bsearch(key,base,nel,width,callback)
  A(37h) calloc(sizx,sizy)            ;SLOW!
  A(38h) realloc(old_buf,new_siz)     ;SLOW!
  A(39h) InitHeap(addr,size)
  A(3Ah) _exit(exitcode)
  A(3Bh) or B(3Ch) getchar()
  A(3Ch) or B(3Dh) putchar(char)
  A(3Dh) or B(3Eh) gets(dst)
  A(3Eh) or B(3Fh) puts(src)
  A(3Fh) printf(txt,param1,param2,etc.)
  A(40h) SystemErrorUnresolvedException()
  A(41h) LoadTest(filename,headerbuf)
  A(42h) Load(filename,headerbuf)
  A(43h) Exec(headerbuf,param1,param2)
  A(44h) FlushCache()
  A(45h) init_a0_b0_c0_vectors
  A(46h) GPU_dw(Xdst,Ydst,Xsiz,Ysiz,src)
  A(47h) gpu_send_dma(Xdst,Ydst,Xsiz,Ysiz,src)
  A(48h) SendGP1Command(gp1cmd)
  A(49h) GPU_cw(gp0cmd)   ;send GP0 command word
  A(4Ah) GPU_cwp(src,num) ;send GP0 command word and parameter words
  A(4Bh) send_gpu_linked_list(src)
  A(4Ch) gpu_abort_dma()
  A(4Dh) GetGPUStatus()
  A(4Eh) gpu_sync()
  A(4Fh) SystemError
  A(50h) SystemError
  A(51h) LoadExec(filename,stackbase,stackoffset)
  A(52h) GetSysSp
  A(53h) SystemError           ;PS2: set_ioabort_handler(src)
  A(54h) or A(71h) _96_init()
  A(55h) or A(70h) _bu_init()
  A(56h) or A(72h) _96_remove()  ;does NOT work due to SysDeqIntRP bug
  A(57h) return 0
  A(58h) return 0
  A(59h) return 0
  A(5Ah) return 0
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
  A(70h) or A(55h) _bu_init()
  A(71h) or A(54h) _96_init()
  A(72h) or A(56h) _96_remove()   ;does NOT work due to SysDeqIntRP bug
  A(73h) return 0
  A(74h) return 0
  A(75h) return 0
  A(76h) return 0
  A(77h) return 0
  A(78h) CdAsyncSeekL(src)
  A(79h) return 0               ;DTL-H: Unknown?
  A(7Ah) return 0               ;DTL-H: Unknown?
  A(7Bh) return 0               ;DTL-H: Unknown?
  A(7Ch) CdAsyncGetStatus(dst)
  A(7Dh) return 0               ;DTL-H: Unknown?
  A(7Eh) CdAsyncReadSector(count,dst,mode)
  A(7Fh) return 0               ;DTL-H: Unknown?
  A(80h) return 0               ;DTL-H: Unknown?
  A(81h) CdAsyncSetMode(mode)
  A(82h) return 0               ;DTL-H: Unknown?
  A(83h) return 0               ;DTL-H: Unknown?
  A(84h) return 0               ;DTL-H: Unknown?
  A(85h) return 0               ;DTL-H: Unknown?, or reportedly, CdStop (?)
  A(86h) return 0               ;DTL-H: Unknown?
  A(87h) return 0               ;DTL-H: Unknown?
  A(88h) return 0               ;DTL-H: Unknown?
  A(89h) return 0               ;DTL-H: Unknown?
  A(8Ah) return 0               ;DTL-H: Unknown?
  A(8Bh) return 0               ;DTL-H: Unknown?
  A(8Ch) return 0               ;DTL-H: Unknown?
  A(8Dh) return 0               ;DTL-H: Unknown?
  A(8Eh) return 0               ;DTL-H: Unknown?
  A(8Fh) return 0               ;DTL-H: Unknown?
  A(90h) CdromIoIrqFunc1()
  A(91h) CdromDmaIrqFunc1()
  A(92h) CdromIoIrqFunc2()
  A(93h) CdromDmaIrqFunc2()
  A(94h) CdromGetInt5errCode(dst1,dst2)
  A(95h) CdInitSubFunc()
  A(96h) AddCDROMDevice()
  A(97h) AddMemCardDevice()     ;DTL-H: SystemError
  A(98h) AddDuartTtyDevice()    ;DTL-H: AddAdconsTtyDevice ;PS2: SystemError
  A(99h) add_nullcon_driver()
  A(9Ah) SystemError            ;DTL-H: AddMessageWindowDevice
  A(9Bh) SystemError            ;DTL-H: AddCdromSimDevice
  A(9Ch) SetConf(num_EvCB,num_TCB,stacktop)
  A(9Dh) GetConf(num_EvCB_dst,num_TCB_dst,stacktop_dst)
  A(9Eh) SetCdromIrqAutoAbort(type,flag)
  A(9Fh) SetMem(megabytes)
```
Below functions A(A0h..B4h) not supported on pre-retail DTL-H2000 devboard:<br/>
```
  A(A0h) _boot()
  A(A1h) SystemError(type,errorcode)
  A(A2h) EnqueueCdIntr()  ;with prio=0 (fixed)
  A(A3h) DequeueCdIntr()  ;does NOT work due to SysDeqIntRP bug
  A(A4h) CdGetLbn(filename) ;get 1st sector number (or garbage when not found)
  A(A5h) CdReadSector(count,sector,buffer)
  A(A6h) CdGetStatus()
  A(A7h) bufs_cb_0()
  A(A8h) bufs_cb_1()
  A(A9h) bufs_cb_2()
  A(AAh) bufs_cb_3()
  A(ABh) _card_info(port)
  A(ACh) _card_load(port)
  A(ADh) _card_auto(flag)
  A(AEh) bufs_cb_4()
  A(AFh) card_write_test(port)  ;CEX-1000: jump_to_00000000h
  A(B0h) return 0               ;CEX-1000: jump_to_00000000h
  A(B1h) return 0               ;CEX-1000: jump_to_00000000h
  A(B2h) ioabort_raw(param)     ;CEX-1000: jump_to_00000000h
  A(B3h) return 0               ;CEX-1000: jump_to_00000000h
  A(B4h) GetSystemInfo(index)   ;CEX-1000: jump_to_00000000h
  A(B5h..BFh) N/A ;jump_to_00000000h
```

#### B-Functions (Call 00B0h with function number in R9 Register)
```
  B(00h) alloc_kernel_memory(size)
  B(01h) free_kernel_memory(buf)
  B(02h) init_timer(t,reload,flags)
  B(03h) get_timer(t)
  B(04h) enable_timer_irq(t)
  B(05h) disable_timer_irq(t)
  B(06h) restart_timer(t)
  B(07h) DeliverEvent(class, spec)
  B(08h) OpenEvent(class,spec,mode,func)
  B(09h) CloseEvent(event)
  B(0Ah) WaitEvent(event)
  B(0Bh) TestEvent(event)
  B(0Ch) EnableEvent(event)
  B(0Dh) DisableEvent(event)
  B(0Eh) OpenTh(reg_PC,reg_SP_FP,reg_GP)
  B(0Fh) CloseTh(handle)
  B(10h) ChangeTh(handle)
  B(11h) jump_to_00000000h
  B(12h) InitPAD2(buf1,siz1,buf2,siz2)
  B(13h) StartPAD2()
  B(14h) StopPAD2()
  B(15h) PAD_init2(type,button_dest,unused,unused)
  B(16h) PAD_dr()
  B(17h) ReturnFromException()
  B(18h) ResetEntryInt()
  B(19h) HookEntryInt(addr)
  B(1Ah) SystemError  ;PS2: return 0
  B(1Bh) SystemError  ;PS2: return 0
  B(1Ch) SystemError  ;PS2: return 0
  B(1Dh) SystemError  ;PS2: return 0
  B(1Eh) SystemError  ;PS2: return 0
  B(1Fh) SystemError  ;PS2: return 0
  B(20h) UnDeliverEvent(class,spec)
  B(21h) SystemError  ;PS2: return 0
  B(22h) SystemError  ;PS2: return 0
  B(23h) SystemError  ;PS2: return 0
  B(24h) jump_to_00000000h
  B(25h) jump_to_00000000h
  B(26h) jump_to_00000000h
  B(27h) jump_to_00000000h
  B(28h) jump_to_00000000h
  B(29h) jump_to_00000000h
  B(2Ah) SystemError  ;PS2: return 0
  B(2Bh) SystemError  ;PS2: return 0
  B(2Ch) jump_to_00000000h
  B(2Dh) jump_to_00000000h
  B(2Eh) jump_to_00000000h
  B(2Fh) jump_to_00000000h
  B(30h) jump_to_00000000h
  B(31h) jump_to_00000000h
  B(32h) or A(00h) open(filename,accessmode)
  B(33h) or A(01h) lseek(fd,offset,seektype)
  B(34h) or A(02h) read(fd,dst,length)
  B(35h) or A(03h) write(fd,src,length)
  B(36h) or A(04h) close(fd)
  B(37h) or A(05h) ioctl(fd,cmd,arg)
  B(38h) or A(06h) exit(exitcode)
  B(39h) or A(07h) isatty(fd)
  B(3Ah) or A(08h) getc(fd)
  B(3Bh) or A(09h) putc(char,fd)
  B(3Ch) or A(3Bh) getchar()
  B(3Dh) or A(3Ch) putchar(char)
  B(3Eh) or A(3Dh) gets(dst)
  B(3Fh) or A(3Eh) puts(src)
  B(40h) cd(name)
  B(41h) format(devicename)
  B(42h) firstfile2(filename,direntry)
  B(43h) nextfile(direntry)
  B(44h) rename(old_filename,new_filename)
  B(45h) erase(filename)
  B(46h) undelete(filename)
  B(47h) AddDrv(device_info)  ;subfunction for AddXxxDevice functions
  B(48h) DelDrv(device_name_lowercase)
  B(49h) PrintInstalledDevices()
```
Below functions B(4Ah..5Dh) not supported on pre-retail DTL-H2000 devboard:<br/>
```
  B(4Ah) InitCARD2(pad_enable)  ;uses/destroys k0/k1 !!!
  B(4Bh) StartCARD2()
  B(4Ch) StopCARD2()
  B(4Dh) _card_info_subfunc(port)  ;subfunction for "_card_info"
  B(4Eh) _card_write(port,sector,src)
  B(4Fh) _card_read(port,sector,dst)
  B(50h) _new_card()
  B(51h) Krom2RawAdd(shiftjis_code)
  B(52h) SystemError  ;PS2: return 0
  B(53h) Krom2Offset(shiftjis_code)
  B(54h) _get_errno()
  B(55h) _get_error(fd)
  B(56h) GetC0Table
  B(57h) GetB0Table
  B(58h) _card_chan()
  B(59h) testdevice(devicename)
  B(5Ah) SystemError  ;PS2: return 0
  B(5Bh) ChangeClearPAD(int)
  B(5Ch) _card_status(slot)
  B(5Dh) _card_wait(slot)
  B(5Eh..FFh) N/A ;jump_to_00000000h    ;CEX-1000: B(5Eh..F6h) only
  B(100h....) N/A ;garbage              ;CEX-1000: B(F7h.....) and up
```

#### C-Functions (Call 00C0h with function number in R9 Register)
```
  C(00h) EnqueueTimerAndVblankIrqs(priority) ;used with prio=1
  C(01h) EnqueueSyscallHandler(priority)     ;used with prio=0
  C(02h) SysEnqIntRP(priority,struc)  ;bugged, use with care
  C(03h) SysDeqIntRP(priority,struc)  ;bugged, use with care
  C(04h) get_free_EvCB_slot()
  C(05h) get_free_TCB_slot()
  C(06h) ExceptionHandler()
  C(07h) InstallExceptionHandlers()  ;destroys/uses k0/k1
  C(08h) SysInitMemory(addr,size)
  C(09h) SysInitKernelVariables()
  C(0Ah) ChangeClearRCnt(t,flag)
  C(0Bh) SystemError  ;PS2: return 0
  C(0Ch) InitDefInt(priority) ;used with prio=3
  C(0Dh) SetIrqAutoAck(irq,flag)
  C(0Eh) return 0               ;DTL-H2000: dev_sio_init
  C(0Fh) return 0               ;DTL-H2000: dev_sio_open
  C(10h) return 0               ;DTL-H2000: dev_sio_in_out
  C(11h) return 0               ;DTL-H2000: dev_sio_ioctl
  C(12h) InstallDevices(ttyflag)
  C(13h) FlushStdInOutPut()
  C(14h) return 0               ;DTL-H2000: SystemError
  C(15h) _cdevinput(circ,char)
  C(16h) _cdevscan()
  C(17h) _circgetc(circ)    ;uses r5 as garbage txt for _ioabort
  C(18h) _circputc(char,circ)
  C(19h) _ioabort(txt1,txt2)
  C(1Ah) set_card_find_mode(mode)  ;0=normal, 1=find deleted files
  C(1Bh) KernelRedirect(ttyflag)   ;PS2: ttyflag=1 causes SystemError
  C(1Ch) AdjustA0Table()
  C(1Dh) get_card_find_mode()
  C(1Eh..7Fh) N/A ;jump_to_00000000h
  C(80h.....) N/A ;mirrors to B(00h.....)
```

#### SYS-Functions (Syscall opcode with function number in R4 aka A0 Register)
```
  SYS(00h) NoFunction()
  SYS(01h) EnterCriticalSection()
  SYS(02h) ExitCriticalSection()
  SYS(03h) ChangeThreadSubFunction(addr) ;syscall with r4=03h, r5=addr
  SYS(04h..FFFFFFFFh) calls DeliverEvent(F0000010h,4000h)
```
The 20bit immediate in the "syscall imm" opcode is unused (should be zero).<br/>

#### BREAK-Functions (Break opcode with function number in opcode's immediate)
BRK opcodes may be used within devkits, however, the standard BIOS simply calls
DeliverEvent(F0000010h,1000h) and SystemError\_A\_40h upon any BRK opcodes (as
well as on any other unresolved exceptions).<br/>
```
  BRK(1C00h) Division by zero (commonly checked/invoked by software)
  BRK(1800h) Division overflow (-80000000h/-1, sometimes checked by software)
```
Below breaks are used in DTL-H2000 BIOS:<br/>
```
  BRK(1h) Whatever lockup or so?
  BRK(101h) PCInit()   Inits the fileserver.
  BRK(102h) PCCreat(filename, fileattributes)
  BRK(103h) PCOpen(filename, accessmode)
  BRK(104h) PCClose(filehandle)
  BRK(105h) PCRead(filehandle, length, memory_destination_address)
  BRK(106h) PCWrite(filehandle, length, memory_source_address)
  BRK(107h) PClSeek(filehandle, file_offset, seekmode)
  BRK(3C400h) User has typed "break" command in debug console
```
The break functions have argument(s) in A1,A2,A3 (ie. unlike normal BIOS
functions not in A0,A1,A2), and TWO return values (in R2, and R3). These
functions require a commercial/homebrew devkit... consisting of a Data Cable
(for accessing the PC's harddisk)... and an Expansion ROM (for handling the
BREAK opcodes)... or so?<br/>



##   BIOS File Functions
#### A(00h) or B(32h) - open(filename, accessmode) - Opens a file for IO
```
  out: V0  File handle (00h..0Fh), or -1 if error.
```
Opens a file on the target device for io. Accessmode is set like this:<br/>
```
  bit0     1=Read  ;\These bits aren't actually used by the BIOS, however, at
  bit1     1=Write ;/least 1 should be set; won't work when all 32bits are zero
  bit2     1=Exit without waiting for incoming data (when TTY buffer empty)
  bit9     0=Open Existing File, 1=Create New file (memory card only)
  bit15    1=Asynchronous mode (memory card only; don't wait for completion)
  bit16-31 Number of memory card blocks for a new file on the memory card
```
The PSX can have a maximum of 16 files open at any time, of which, 2 handles
are always reserved for std\_io, so only 14 handles are available for actual
files. Some functions (cd, testdevice, erase, undelete,
format, firstfile2, rename) are temporarily allocating 1 filehandle
(rename tries to use 2 filehandles, but, it does accidently use only 1
handle, too). So, for example, erase would fail if more than 13 file
handles are opened by the game.<br/>

#### A(01h) or B(33h) - lseek(fd, offset, seektype) - Move the file pointer
```
   seektype 0 = from start of file        (with positive offset)
            1 = from current file pointer (with positive/negative offset)
            2 = Bugs. Should be from end of file.
```
Moves the file pointer the number of bytes in A1, relative to the location
specified by A2. Movement from the eof is incorrect. Also, movement beyond the
end of the file is not checked.<br/>

#### A(02h) or B(34h) - read(fd, dst, length) - Read data from an open file
```
  out: V0  Number of bytes actually read, -1 if failed.
```
Reads the number of bytes from the specified open file. If length is not
specified an error is returned. Read per $0080 bytes from memory card (bu:) and
per $0800 from cdrom (cdrom:).<br/>

#### A(03h) or B(35h) - write(fd, src, length) - Write data to an open file
```
  out: V0  Number of bytes written.
```
Writes the number of bytes to the specified open file. Write to the memory card
per $0080 bytes. Writing to the cdrom returns 0.<br/>

#### A(04h) or B(36h) - close(fd) - Close an open file
Returns r2=fd (or r2=-1 if failed).<br/>

#### A(08h) or B(3Ah) - getc(fd) - read one byte from file
```
  out: R2=character (sign-expanded) or FFFFFFFFh=error
```
Internally redirects to "read(fd,tempbuf,1)". For some strange reason, the
returned character is sign-expanded; so, a return value of FFFFFFFFh could mean
either character FFh, or error.<br/>

#### A(09h) or B(3Bh) - putc(char,fd) - write one byte to file
Observe that "fd" is the 2nd paramter (not the 1st paramter as usually).<br/>
```
  out:  R2=Number of bytes actually written, -1 if failed
```
Internally redirects to "write(fd,tempbuf,1)".<br/>

#### B(40h) - cd(name) - Change the current directory on target device
Changes the current directory on the specified device, which should be "cdrom:"
(memory cards don't support directories). The PSX supports only a current
directory, but NOT a current device (ie. after cd, the directory name may be
ommited from filenames, but the device name must be still included in all
filenames).<br/>
```
  in:  A0  Pointer to new directory path (eg. "cdrom:\path")
```
Returns 1=okay, or 0=failed.<br/>
The function doesn't verify if the directory exists. Caution: For cdrom, the
function does always load the path table from the disk (even if it was already
stored in RAM, so cd is causing useless SLOW read/seek delays).<br/>

#### B(42h) - firstfile2(filename,direntry) - Find first file to match the name
Returns r2=direntry (or r2=0 if no matching files).<br/>
Searches for the first file to match the specified filename; the filename may
contain "?" and "\*" wildcards. "\*" means to ignore ALL following characters;
accordingly one cannot specify any further characters after the "\*" (eg.
"DATA\*" would work, but "\*.DAT" won't work). "?" is meant to ignore a single
character cell. Note: The "?" wildcards (but not "\*") can be used also in all
other file functions; causing the function to use the first matching name (eg.
erase "????" would erase the first matching file, not all matching files).<br/>
Start the name with the device you want to address. (ie. pcdrv:) Different
drives can be accessed as normally by their drive names (a:, c:, huh?) if path
is omitted after the device, the current directory will be used.<br/>
A direntry structure looks like this:<br/>
```
  00h 14h Filename, terminated with 00h
  14h 4   File attribute (always 0 for cdrom) (50h=norm or A0h=del for card)
  18h 4   File size
  1Ch 4   Pointer to next direntry? (not used?)
  20h 4   First Sector Number
  24h 4   Reserved (not used)
```
BUG: If "?" matches the ending 00h byte of a name, then any further characters
in the search expression are ignored (eg. "FILE?.DAT" would match to
"FILE2.DAT", but accidently also to "FILE").<br/>
BUG: For CDROM, the BIOS includes some code that is intended to realize disk
changes during firstfile2/nextfile operations, however, that code is so bugged
that it does rather ensure that the BIOS does NOT realize new disks being
inserted during firstfile2/nextfile.<br/>
BUG: firstfile2/nextfile is internally using a FCB. On the first call to
firstfile2, the BIOS is searching a free FCB, and does apply that as "search
fcb", but it doesn't mark that FCB as allocated, so other file functions may
accidently use the same FCB. Moreover, the BIOS does memorize that "search
fcb", and, even when starting a new search via another call to firstfile2, it
keeps using that FCB for search (without checking if the FCB is still free). A
possible workaround is not to have any files opened during firstfile2/nextfile
operations.<br/>

#### B(43h) - nextfile(direntry) - Searches for the next file to match the name
Returns r2=direntry (or r2=0 if no more matching files).<br/>
Uses the settings of a previous firstfile2/nextfile command.<br/>

#### B(44h) - rename(old\_filename, new\_filename)
Returns 1=okay, or 0=failed.<br/>

#### B(45h) - erase(filename) - Delete a file on target device
Returns 1=okay, or 0=failed.<br/>

#### B(46h) - undelete(filename)
Returns 1=okay, or 0=failed.<br/>

#### B(41h) - format(devicename)
Erases all files on the device (ie. for formatting memory cards).<br/>
Returns 1=okay, or 0=failed.<br/>

#### B(54h) - \_get\_errno()
Indicates the reason of the most recent file function error (open,
lseek, read, write, close, _get_error, ioctl, cd,
testdevice, erase, undelete, format, rename). Use
_get_errno() ONLY if an error has occured (the error code isn't reset to zero
by functions that are passing okay). firstfile2/nextfile do NOT affect
_get_errno(). See below list of File Error Numbers for more info.<br/>

#### B(55h) - \_get\_error(fd)
Basically same as B(54h), but allowing to specify a file handle for which error
information is to be received; accordingly it doesn't work for functions that
do use 'hidden' internal file handles (eg. erase, or unsuccessful
open). Returns FCB[18h], or FFFFFFFFh if the handle is invalid/unused.<br/>

#### A(05h) or B(37h) - ioctl(fd,cmd,arg)
Used only for TTY.<br/>

#### A(07h) or B(39h) - isatty(fd)
Returns bit1 of the file's DCB flags. That bit is set only for Duart/TTY, and
is cleared for Dummy/TTY, Memory Card, and CDROM.<br/>

#### B(59h) - testdevice(devicename)
Whatever. Checks the devicename, and if it's accepted, calls a device specific
function. For the existing devices (cdrom,bu,tty) that specific function simply
returns without doing anything. Maybe other devices (like printers or modems)
would do something more interesting.<br/>

#### File Error Numbers for B(54h) and B(55h)
```
  00h okay (though many successful functions leave old error code unchanged)
  02h file not found
  06h bad device port number (tty2 and up)
  09h invalid or unused file handle
  10h general error (physical I/O error, unformatted, disk changed for old fcb)
  11h file already exists error (create/undelete/rename)
  12h tried to rename a file from one device to another device
  13h unknown device name
  16h sector alignment error, or fpos>=filesize, unknown seektype or ioctl cmd
  18h not enough free file handles
  1Ch not enough free memory card blocks
  FFFFFFFFh invalid or unused file handle passed to B(55h) function
```



##   BIOS File Execute and Flush Cache
#### A(41h) - LoadTest(filename, headerbuf)
Loads the 800h-byte exe file header to an internal sector buffer, and does then
copy bytes [10h..4Bh] of that header to headerbuf[00h..3Bh].<br/>

#### A(42h) - Load(filename, headerbuf)
Same as LoadTest (see there for details), but additionally loads the body
of the executable (using the size and destination address in the file header),
and does call FlushCache. The exe can be then started via Exec (this isn't
done automatically by LoadTest). Unlike "LoadExec", the
"LoadTest/Exec" combination allows to return the new exe file to return
to the old exe file (instead of restarting the boot executable).<br/>
BUG: Uses the unstable FlushCache function (see there for details).<br/>

#### A(43h) - Exec(headerbuf, param1, param2)
Can be used to start a previously loaded executable. The function saves
R16,R28,R30,SP,RA in the reserved region of headerbuf (rather than on stack),
more or less slowly zerofills the memfill region specified in headerbuf, reads
the stack base and offset values and sets SP and FP to base+offset (or leaves
them unchanged if base=0), reads the GP value from headerbuf and sets GP to
that value. Then calls the excecutables entrypoint, with param1 and param2
passed in r4,r5.<br/>
If the executable (should) return, then R16,R28,R30,SP,RA are restored from
headerbuf, and the function returns with r2=1.<br/>

#### A(51h) - LoadExec(filename, stackbase, stackoffset)
This is a rather bizarre function. In short, it does load and execute the
specified file, and thereafter, it (tries to) reload and restart to boot
executable.<br/>
Part1: Takes a copy of the filename, with some adjustments: Everything up to
the first ":" or 00h byte is copied as is (ie. the device name, if it does
exist, or otherwise the whole path\filename.ext;ver), the remaining characters
are copied and converted to uppercase (ie. the path\filename.ext;ver part, or
none if the device name didn't exist), finally, checks if a ";" exists (ie. the
version suffix), if there's none, then it appends ";1" as default version.
CAUTION: The BIOS allocates ONLY 28 bytes on stack for the copy of the
filename, that region is followed by 4 unused bytes, so the maximum length
would be 32 bytes (31 characters plus EOL) (eg.
"device:\pathname\filename.ext;1",00h).<br/>
Part2: Enables IRQs via ExitCriticalSection, memorizes the stack base/offset
values from the previously loaded executable (which should have been the boot
executable, unless LoadExec should have been used in nested fashion),
does then use LoadTest to load the desired file, replaces the stack
base/offset values in its headerbuf by the LoadExec parameter values, and
does then execute it via Exec(headerbuf,1,0).<br/>
Part3: If the exefile returns, or if it couldn't be loaded, then the boot file
is (unsuccessfully) attempted to be reloaded: Enables IRQs via
ExitCriticalSection, loads the boot file via LoadTest, replaces the stack
base/offset values in its headerbuf by the values memorized in Part2 (which
\<should\> be the boot executable's values from SYSTEM.CNF, unless the
nesting stuff occurred), and does then execute the boot file via
Exec(headerbuf,1,0).<br/>
Part4: If the boot file returns, or if it couldn't be loaded, then the function
looks up in a "JMP $" endless loop (normally, returning from the boot exe
causes SystemError("B",38Ch), however, after using
LoadExec, this functionality is replaced by the "JMP $" lockup.<br/>
BUG: Uses the unstable FlushCache function (see there for details).<br/>
BUG: Part3 accidently treats the first 4 characters of the exename as memory
address (causing an invalid memory address exception on address 6F726463h, for
"cdrom:filename.exe").<br/>

#### A(9Ch) - SetConf(num\_EvCB, num\_TCB, stacktop)
Changes the number of EvCBs and TCBs, and the stacktop. These values are usually
initialized from the settings in the SYSTEM.CNF file, so using this function
usually shouldn't ever be required.<br/>
The function deallocates all old ExCBs, EvCBs, TCBs (so all Exception handlers,
Events, and Threads (except the current one) are lost, and all other memory
that may have been allocated via alloc\_kernel\_memory(size) is deallocated, too.
It does then allocate the new control blocks, and enqueue the default handlers.
Despite of the changed stacktop, the current stack pointer is kept intact, and
the function returns to the caller.<br/>

#### A(9Dh) - GetConf(num\_EvCB\_dst, num\_TCB\_dst, stacktop\_dst)
Returns the number of EvCBs, TCBs, and the initial stacktop. There's no return
value in the R2 register, instead, the three 32bit return values are stored at
the specified "dst" addresses.<br/>

#### A(44h) - FlushCache()
Flushes the Code Cache, so opcodes are ensured to be loaded from RAM. This is
required when loading program code via DMA (ie. from CDROM) (the cache
controller apparently doesn't realize changes to RAM that are caused by DMA).
The LoadTest and LoadExec functions are automatically calling
FlushCache (so FlushCache is required only when loading program code via
"read" or via "CdReadSector").<br/>
FlushCache may be also required when relocating or modifying program code by
software (the cache controller doesn't seem to realize modifications to memory
mirrors, eg. patching the exception handler at 80000080h seems to be work
without FlushCache, but patching the same bytes at 00000080h doesn't).<br/>
Note: The PSX doesn't have a Data Cache (or actually, it has, but it's misused
as Fast RAM, mapped to a fixed memory region, and which isn't accessable by
DMA), so FlushCache isn't required for regions that contain data.<br/>
BUG: The FlushCache function contains a handful of opcodes that do use the k0
register without having IRQs disabled at that time, if an IRQ occurs during
those opcodes, then the k0 value gets destroyed by the exception handler,
causing FlushCache to get trapped in an endless loop.<br/>
One workaround would be to disable all IRQs before calling FlushCache, however,
the BIOS does internally call the function without IRQs disabled, that applies
to:<br/>
```
  load_file  A(42h)
  load_exec  A(51h)
  add_device B(47h) (and all "add_xxx_device" functions)
  init_card  B(4Ah)
  and by intro/boot code
```
for load\_file/load\_exec, IRQ2 (cdrom) and IRQ3 (dma) need to be enabled, so the
"disable all IRQs" workaround cannot be used for that functions, however, one
can/should disable as many IRQs as possible, ie. everything except IRQ2/IRQ3,
and all DMA interrupts except DMA3 (cdrom).<br/>

#### Executable Memory Allocation
LoadTest and LoadExec are simply loading the file to the address
specified in the exe file header. There's absolutely no verification whether
that memory is (or isn't) allocated via malloc, or if it is used by the boot
executable, or by the kernel, or if it does contain RAM at all.<br/>
When using the "malloc" function combined with loading exe files, it may be
recommended not to pass all memory to InitHeap (ie. to keep a memory region
being reserved for loading executables).<br/>

#### Note
For more info about EXE files and their headers, see<br/>
[CDROM File Formats](../cdrom-file-exe-tim/SKILL.md)<br/>



##   BIOS CDROM Functions
#### General File Functions
CDROMs are basically accessed via normal file functions, with device name
"cdrom:" (which is an abbreviation for "cdrom0:", anyways, the port number is
ignored).<br/>
[BIOS File Functions](#bios-file-functions)<br/>
[BIOS File Execute and Flush Cache](#bios-file-execute-and-flush-cache)<br/>
Before starting the boot executable, the BIOS automatically calls _96_init(), so
the game doesn't need to do any initializations before using CDROM file
functions.<br/>

#### Absent CD-Audio Support
The Kernel doesn't include any functions for playing Audio tracks. Also,
there's no BIOS function for setting the XA-ADPCM file/channel filter values.
So CD Audio can be used only by directly programming the CDROM I/O ports.<br/>

#### Asynchronous CDROM Access
The normal File functions are always using synchroneous access for CDROM (ie.
the functions do wait until all data is transferred) (unlike as for memory
cards, accessmode.bit15 cannot be used to activate asynchronous cdrom access).<br/>
However, one can read files in asynchrouneous fashion via CdGetLbn,
CdAsyncSeekL, and CdAsyncReadSector. CDROM files are non-fragmented, so they
can be read simply from incrementing sector numbers.<br/>

#### A(A4h) - CdGetLbn(filename)
Returns the first sector number used by the file, or -1 in case of error.<br/>
BUG: The function accidently returns -1 for the first file in the directory
(the first file should be a dummy entry for the current or parent directory or
so, so that bug isn't much of a problem), if the file is not found, then the
function accidently returns garbage (rather than -1).<br/>

#### A(A5h) - CdReadSector(count,sector,buffer)
Reads \<count\> sectors, starting at \<sector\>, and writes data to
\<buffer\>. The read is done in mode=80h (double speed, 800h-bytes per
sector). The function waits until all sectors are transferred, and does then
return the number of sectors (ie. count), or -1 in case of error.<br/>

#### A(A6h) - CdGetStatus()
Retrieves the cdrom status via CdAsyncGetStatus(dst) (see there for details;
especially for cautions on door-open flag). The function waits until the event
indicates completion, and does then return the status byte (or -1 in case of
error).<br/>

#### A(78h) - CdAsyncSeekL(src)
Issues Setloc and SeekL commands. The parameter (src) is a pointer to a 3-byte
sector number (MM,SS,FF) (in BCD format).<br/>
The function returns 0=failed, or 1=okay. Completion is indicated by events
(class=F0000003h, and spec=20h, or 8000h).<br/>

#### A(7Ch) - CdAsyncGetStatus(dst)
Issues a GetStat command. The parameter (dst) is a pointer to a 1-byte location
that receives the status response byte.<br/>
The function returns 0=failed, or 1=okay. Completion is indicated by events
(class=F0000003h, and spec=20h, or 8000h).<br/>
Caution: The command acknowledges the door-open flag, but doesn't automatically
reload the path table (which is required if a new disk is inserted); if the
door-open flag was set, one should call a function that does forcefully load
the path table (like cd).<br/>

#### A(7Eh) - CdAsyncReadSector(count,dst,mode)
Issues SetMode and ReadN (when mode.bit8=0), or ReadS (when mode.bit8=1)
commands. count is the number of sectors to be read, dst is the destination
address in RAM, mode.bit0-7 are passed as parameter to the SetMode command,
mode.bit8 is the ReadN/ReadS flag (as described above). The sector size (for
DMA) depends on the mode value: 918h-bytes (bit4=1, bit5=X), 924h-bytes
(bit4=0, bit5=1), or 800h-bytes (bit4,5=0).<br/>
Before CdAsyncReadSector, the sector number should be set via
CdAsyncSeekL(src).<br/>
The function returns 0=failed, or 1=okay. Completion is indicated by events
(class=F0000003h, and spec=20h, 80h, or 8000h).<br/>

#### A(81h) - CdAsyncSetMode(mode)
Similar to CdAsyncReadSector (see there for details), but issues only the
SetMode command, without any following ReadN/ReadS command.<br/>

#### A(94h) - CdromGetInt5errCode(dst1,dst2)
Returns the first two response bytes from the most recent INT5 error:
[dst1]=status, [dst2]=errorcode. The BIOS doesn't reset these values in case of
successful completion, so the values are quite useless.<br/>

#### A(54h) or A(71h) - \_96\_init()
#### A(56h) or A(72h) - \_96\_remove()  ;does NOT work due to SysDeqIntRP bug
#### A(90h) - CdromIoIrqFunc1()
#### A(91h) - CdromDmaIrqFunc1()
#### A(92h) - CdromIoIrqFunc2()
#### A(93h) - CdromDmaIrqFunc2()
#### A(95h) - CdInitSubFunc()  ;subfunction for _96_init()
#### A(9Eh) - SetCdromIrqAutoAbort(type,flag)
#### A(A2h) - EnqueueCdIntr()  ;with prio=0 (fixed)
#### A(A3h) - DequeueCdIntr()  ;does NOT work due to SysDeqIntRP bug
Internally used CDROM functions for initialization and IRQ handling.<br/>



##   BIOS Memory Card Functions
#### General File Functions
Memory Cards aka Backup Units (bu) are basically accessed via normal file
functions, with device names "bu00:" (Slot 1) and "bu10:" (Slot 2),<br/>
[BIOS File Functions](#bios-file-functions)<br/>
Before using the file functions for memory cards, first call
InitCARD2(pad\_enable), then StartCARD2(), and then \_bu\_init().<br/>

#### File Header, Filesize, and Sector Alignment
The first 100h..200h bytes (2..4 sectors) of the file must contain the title
and icon bitmap(s). For details, see:<br/>
[Memory Card Data Format](../memory-cards/SKILL.md#memory-card-data-format)<br/>
The filesize must be a multiple of 2000h bytes (one block), the maximum size
would be 1E000h bytes (when using all 15 blocks on the memory card). The
filesize must be specified when creating the file (ie. accessmode bit9=1, and
bit16-31=number of blocks). Once when the file is created, the BIOS does NOT
allow to change the filesize (unless by deleting and re-creating the file).<br/>
When reading/writing files, the amount of data must be a multiple of 80h bytes
(one sector), and the file position must be aligned to a 80h-byte boundary,
too. There's no restriction on fragmented files (ie. one may cross 2000h-byte
block boundaries within the file).<br/>

#### Poor Memcard Performance
PSX memory card accesses are typically super-slow. That, not so much because
the hardware would be slow, but rather because of improper inefficent code at
the BIOS side. The original BIOS tries to synchronize memory card accesses with
joypad accesses simply by accessing only one sector per frame (although it
could access circa two sectors). To the worst, the BIOS accesses Slot 1 only on
each second frame, and Slot 2 only each other frame (although in 99% of all
cases only one slot is accessed at once, so the access time drops to 0.5
sectors per frame).<br/>
Moreover, the memory card id, directory, and broken sector list do occupy 26
sectors (although the whole information would fit into 4 or 5 sectors) (a
workaround would be to read only the first some bytes, and to skip the
additional unused bytes - though that'd also mean to skip the checksums which
are unfortunately stored at the end of the sector).<br/>
And, anytime when opening a file (in synchronous mode), the BIOS does
additionally read sector 0 (which is totally useless, and gets especially slow
when opening a bunch of files; eg. when extracting the title/icon from all
available files on the card).<br/>

#### Asynchronous Access
The BIOS supports synchronous and asynchronous memory card access. Synchronous
means that the BIOS function doesn't return until the access has completed
(which means, due to the poor performance, that the function spends about 75%
of the time on inactivity) (except in nocash PSX bios, which has better
performance), whilst asynchronous access means that the BIOS function returns
immediately after invoking the access (which does then continue on interrupt
level, and does return an event when finished).<br/>
The file "read" and "write" functions act asynchronous when accessmode
bit15 is set when opening the file. Additionally, the A(ACh)
\_card\_load(port) function can be used to tell the BIOS to load
the directory entries and broken sector list to its internal RAM buffers (eg.
during the games title screen, so the BIOS doesn't need to load that data once
when the game enters its memory card menu). All other functions like erase
or format always act synchronous. The open/findfirst/findnext
functions do normally complete immediately without accessing the card at all
(unless the directory wasn't yet read; in that case the directory is loading in
synchronous fashion).<br/>
Unfortunately, the asynchronous response doesn't rely on a single callback
event, but rather on a bunch of different events which must be all allocated
and tested by the game (and of which, one event is delivered on completion)
(which one depends on whether function completed okay, or if an error
occurred).<br/>

#### Multitap Support (and Multitap Problems)
The BIOS does have some partial support for accessing more than two memory
cards (via Multitap adaptors). Device/port names "bu01:", "bu02:", "bu03:"
allow to access extra memory carts in slot1 (and "bu11:", "bu12:", "bu13:" in
slot2). Namely, those names will send values 82h, 83h, 84h to the memory card
slot (instead of the normal 81h value).<br/>
However, the BIOS directory\_buffer and broken\_sector\_list do support only two
memory cards (one in slot1 and one in slot2). So, trying to access more memory
cards may cause great data corruption (though there might be a way to get the
BIOS to reload those buffers before accessing a different memory card).<br/>
Aside from that problem, the BIOS functions are very-very-very slow even when
accessing only two memory cards. Trying to use the BIOS to access up to eight
memory cards would be very-extremly-very slow, which would be more annoying
than useful.<br/>

#### B(4Ah) - InitCARD2(pad\_enable)  ;uses/destroys k0/k1 !!!
#### B(4Bh) - StartCARD2()
#### B(4Ch) - StopCARD2()
#### A(55h) or A(70h) - \_bu\_init()

```
  --- Below are some lower level memory card functions ---
```

#### A(ABh) - \_card\_info(port)
#### B(4Dh) - \_card\_info\_subfunc(port)  ;subfunction for "\_card\_info"
Can be used to check if the most recent call to \_card\_write has completed
okay. Issues an incomplete dummy read command (similar to B(4Fh) -
\_card\_read). The read command is aborted once when receiving the status
byte from the memory card (the actual data transfer is skipped).<br/>

#### A(AFh) - card\_write\_test(port)  ;not supported by old CEX-1000 version
Resets the card changed flag. For some strange reason, this flag isn't
automatically reset after reading the flag, instead, the flag is reset upon
sector writes. To do that, this function issues a dummy write to sector 3Fh.<br/>

#### B(50h) - \_new\_card()
Normally any memory card read/write functions fail if the BIOS senses the card
change flag to be set. Calling this function tells the BIOS to ignore the card
change flag on the next read/write operation (the function is internally used
when loading the "MC" ID from sector 0, and when calling the card\_write\_test
function to acknowledge the card change flag).<br/>

#### B(4Eh) - \_card\_write(port,sector,src)
#### B(4Fh) - \_card\_read(port,sector,dst)
Invokes asynchronous reading/writing of a single sector. The function returns
1=okay, or 0=failed (on invalid sector numbers). The actual I/O is done on IRQ
level, completion of the I/O command transmission can be checked, among others,
via get/wait\_card\_status(slot) functions (with slot=port/10h).<br/>
In case of the write function, completion of the \<transmission\> does NOT
mean that the actual \<writing\> has completed, instead, write errors are
indicated upon completion of the \<next sector\> read/write transmission
(or, if there are no further sectors to be accessed; one can use \_card\_info to
verify completion of the last written sector).<br/>
The sector number should be in range of 0..3FFh, for some strange reason,
probably a BUG, the function also accepts sector 400h. The specified sector
number is directly accessed (it is NOT parsed through the broken sector
replacement list).<br/>

#### B(5Ch) - \_card\_status(slot)
#### B(5Dh) - \_card\_wait(slot)
Returns the status of the most recent I/O command, possible values are:<br/>
```
  01h=ready
  02h=busy/read
  04h=busy/write
  08h=busy/info
  11h=failed/timeout (eg. when no cartridge inserted)
  21h=failed/general error
```
\_card\_status returns immediately, \_card\_wait waits until a non-busy
state occurs.<br/>

#### A(A7h) - bufs\_cb\_0()
#### A(A8h) - bufs\_cb\_1()
#### A(A9h) - bufs\_cb\_2()
#### A(AAh) - bufs\_cb\_3()
#### A(AEh) - bufs\_cb\_4()
These five callback functions are internally used by the BIOS, notifying other
BIOS functions about (un-)successful completion of memory card I/O commands.<br/>

#### B(58h) - \_card\_chan()
This is a subfunction for the five bufs\_cb_\_xxx functions (indicating
whether the callback occured for a slot1 or slot2 access).<br/>

#### A(ACh) - \_card\_load(port)
Invokes asynchronous reading of the memory card directory. The function isn't
too useful because the BIOS tends to read the directory automatically in
various places in synchronous mode, so there isn't too much chance to replace
the automatic synchronous reading by asynchronous reading.<br/>

#### A(ADh) - \_card\_auto(flag)
Can be used to enable/disable auto format (0=off, 1=on). The \_bu\_init function
initializes auto format as disabled. If auto format is enabled, then the BIOS
does automatically format memory cards if it has failed to read the "MC" ID
bytes on sector 0. Although potentially useful, activating this feature is
rather destructive (for example, read errors on sector 0 might occur accidently
due to improperly inserted cards with dirty contacts, so it'd be better to
prompt the user whether or not to format the card, rather than doing that
automatically).<br/>

#### C(1Ah) - set\_card\_find\_mode(mode)
#### C(1Dh) - get\_card\_find\_mode()
Allows to get/set the card find mode (0=normal, 1=find deleted files), the mode
setting affects only the firstfile2/nextfile functions. All other file functions
are used fixed mode settings (always mode=0 for open, rename,
erase, and mode=1 for undelete).<br/>



