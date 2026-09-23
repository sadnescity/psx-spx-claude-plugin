---
name: bios-irq-threads-timer
description: "PSX BIOS kernel functions: interrupt/exception handling, events, threads, timers, joypad, GPU, memory allocation, memcpy/memset, string functions, printf. Use when calling BIOS functions for IRQ, events, threading, memory management, or string operations."
---

##   BIOS Interrupt/Exception Handling
The Playstation's Kernel uses an uncredible inefficient and unstable exception
handler; which may have been believed to be very powerful and flexible.<br/>

#### Inefficiency
For a maximum of slowness, it does always save and restore all CPU registers
(including such that aren't used in the exception handler). It does then go
through a list of installed interrupt handlers - and executes ALL of them. For
example, a Timer0 IRQ is first passed to the Cdrom and Vblank handlers (which
must reject it, no thanks), before it does eventually reach the Timer0 handler.<br/>

#### Unstable IRQ Handling
A fundamental mistake in the exception handler is that it doesn't memorize the
incoming IRQ flags. So the various interrupt handlers must check Port 1F801070h
one after each other. That means, if a high priority handler has rejected IRQ
processing (because the desired IRQ flag wasn't set at that time), then a lower
priority handler may process it (assuming that the IRQ flag got set in the
meantime), and, in worst case it may even acknowledge it (so the high priority
handler does never receive it).<br/>
To avoid such problems, there should be only ONE handler installed for each IRQ
source. However, that isn't always possible because the Kernel automatically
installs some predefined handlers. Most noteworthy, the totally bugged
DefaultInterruptHandlers is always installed (and cannot be removed), so it
does randomly trigger Events. Fortunately, it does not acknowledge the IRQs
(unless SetIrqAutoAck was used to enable that fatal behaviour).<br/>

#### B(18h) - ResetEntryInt()
Applies the default "Exit" structure (which consists of a pointer to
ReturnFromException, and the Kernel's exception stacktop (minus 4, for whatever
reason), and zeroes for the R16..R23,R28,R30 registers. Returns the address of
that structure.<br/>
See HookEntryInt for details.<br/>

#### B(19h) - HookEntryInt(addr)
addr points to a structure (with same format as for the setjmp function):<br/>
```
  00h 4    r31/ra,pc ;usually ptr to ReturnFromException function
  04h 4    r28/sp    ;usually exception stacktop, minus 4, for whatever reason
  08h 4    r30/fp    ;usually 0
  0Ch 4x8  r16..r23  ;usually 0
  2Ch 4    r28/gp    ;usually 0
```
The hook function is executed only if the ExceptionHandler has been fully
executed (after processing an IRQ, many interrupt handlers are calling
ReturnFromException to abort further exception handling, and thus do skip the
hook function). Once when the hook function has finished, it should execute
ReturnFromException. The hook function is called with r2=1 (that is important
if the hook address was recorded with setjmp, where it "returns" to the
setjmp caller, with r2 as "return value").<br/>

#### Priority Chains
The Kernel's exception handler has four priority chains, each may contain one
or more Interrupt or Exception handlers. The default handlers are:<br/>
```
  Prio Chain Content
  0    CdromDmaIrq, CdromIoIrq, SyscallException
  1    CardSpecificIrq, VblankIrq, Timer2Irq, Timer1Irq, Timer0Irq
  2    PadCardIrq
  3    DefInt
```
The exception handler calls all handlers, starting with the first element in
the priority 0 chain (ie. usually CdromDmaIrq). The separate handlers must
check if they want to process the IRQ (eg. CdromDmaIrq would process only CDROM
DMA IRQs, but not joypad IRQs or so). If it has processed and acknowledged the
IRQ, then the handler may execute ReturnFromException, which causes the
handlers of lower priority to be skipped (if there are still other
unacknowledge IRQs pending, then the hardware will re-enter the exception
handler as soon as the RFE opcode in ReturnFromException does re-enable
interrupts).<br/>

#### C(02h) - SysEnqIntRP(priority,struc)  ;bugged, use with care
Inserts a new element in the specified priority chain. The new element is
inserted at the begin of the chain, so (within that priority chain) the new
element has highest priority.<br/>
```
  00h 4  pointer to next element    (0=none)  ;this pointer is inserted by BIOS
  04h 4  pointer to SECOND function (0=none)  ;executed if func1 returns r2<>0
  08h 4  pointer to FIRST  function (0=none)  ;executed first
  0Ch 4  Not used (usually zero)
```
BUG: SysDeqIntRP can remove only the first element in the chain (see there for
details), so adding new chain elements may cause OTHER functions to be unable
to remove their chain elements. The BIOS seems to be occassionally
adding/removing the "CardSpecificIrq" and "PadCardIrq" (with priority 1 and 2),
so using that priorities may cause the BIOS to be unable to remove that IRQ
handlers. Using priority 0 and 3 should work (as long as the software takes
care to remove only the newest elements) (but there should be no conflicts with
the BIOS which does never remove priority 0 and 3 elements) (leaving apart that
DequeueCdIntr and _96_remove try to remove priority 0 elements, but that
functions won't work anyways; due to the same bug).<br/>

#### C(03h) - SysDeqIntRP(priority,struc)  ;bugged, use with care
Removes the specified element from the specified priority chain.<br/>
BUG: The function tries to search the whole chain (and to remove the element if
it finds it). However, it does only check the first element properly, and,
thereafter it reads a garbage value from an uninitialized stack location, and
acts more or less unpredictable. So, it can remove only the first element in
the chain, ie. it should be called only if you are SURE that there's no newer
element in the chain, and only if you are SURE that the element IS in the
chain.<br/>

#### SYS(01h) - EnterCriticalSection()  ;syscall with r4=01h
Disables interrupts by clearing SR (cop0r12) Bit 2 and 10 (of which, Bit2 gets
copied to Bit0 once when returning from the syscall exception). Returns 1 if
both bits were set, returns 0 if one or both of the bits were already zero.<br/>

#### SYS(02h) - ExitCriticalSection()   ;syscall with r4=02h
Enables interrupts by set SR (cop0r12) Bit 2 and 10 (of which, Bit2 gets copied
to Bit0 once when returning from the syscall exception). There's no return
value (all registers except SR and K0 are unchanged).<br/>

#### C(0Dh) - SetIrqAutoAck(irq,flag)
Specifies if the DefaultInterruptHandler shall automatically acknowledge IRQs.
The "irq" paramter is the number of the interrupt, ie. 00h..0Ah = IRQ0..IRQ10.
The "flag" value should be 0 to disable AutoAck, or non-zero to enable AutoAck.
By default, AutoAck is disabled for all IRQs.<br/>
Mind that the DefaultInterruptHandler is totally bugged. Especially the AutoAck
feature doesn't work very well: It may cause higher priority handlers to miss
their IRQ, and it may even cause the DefaultInterruptHandler to miss its own
IRQs.<br/>

#### C(06h) - ExceptionHandler()
The C(06h) vector points to the exception handler, ie. to the function that is
invoked from the 4 opcodes at address 80000080h, that opcodes jump directly to
the exception handler, so patching the C(06h) vector has no effect.<br/>
Reading the C(06h) entry can be used to let a custom 80000080h handler pass
control back to the default handler (that, by a "direct" jump, not by the usual
"MOV R9,06h / CALL 0C0h" method, which would destroy main programs R9
register).<br/>
Also, reading C(06h) may be useful for patching the exception handler (which
contains a bunch of NOP opcodes, which seem to be intended to insert additional
opcodes, such like debugger exception handling) (Note: some of that NOPs are
reserved for Memory Card IRQ handling).<br/>
BUG: Early BIOS versions did try to examine a copy of cop0r13 in r2 register,
but did forgot cop0r13 to r2 (so they examined garbage), this was fixed in
newer BIOS versions, additionally, most commercial games still include patches
for compatibility with the old BIOS.<br/>

#### B(17h) - ReturnFromException()
Restores the CPU registers (R1-R31,HI,LO,SR,PC) (except R26/K0) from the
current TCB. This function is usually executed automatically at the end of the
ExceptionHandler, however, functions in the exception chain may call
ReturnFromException to return immediately, without processing chain elements of
lower priority.<br/>

#### C(00h) - EnqueueTimerAndVblankIrqs(priority) ;used with prio=1
#### C(01h) - EnqueueSyscallHandler(priority) ;used with prio=0
#### C(0Ch) - InitDefInt(priority) ;used with prio=3
Internally used to add some default IRQ and Exception handlers.<br/>

#### No Nested Exceptions
The Kernel doesn't support nested exceptions, that would require a decreasing
exception stack, however, the kernel saves the incoming CPU registers in the
current TCB, and an exception stack with fixed start address for internal
push/pop during exception handling. So, nesting would overwrite these values.
Do not enable IRQs, and don't trap other exceptions (like break or syscall
opcodes, or memory or overlow errors) during exception handling.<br/>
Note: The execption stack has a fixed size of 1000h bytes (and is located
somewhere in the first 64Kbytes of memory).<br/>



##   BIOS Event Functions
#### B(08h) - OpenEvent(class, spec, mode, func)
Adds an event structure to the event table.<br/>
```
     class,spec - triggers if BOTH values match
     mode - (1000h=execute function/stay busy, 2000h=no func/mark ready)
     func - Address of callback function (0=None) (used only when mode=1000h)
  out: R2 = Event descriptor (F1000000h and up), or FFFFFFFFh if failed
```
Opens an event, should be called within a critical section. The return value is
used to identify the event to the other event functions. A list of event
classes, specs and modes is at the end of this section. Initially, the event is
disabled.<br/>
Note: The desired max number of events can be specified in the SYSTEM.CNF boot
file (the default is "EVENT = 10" (which is a HEX number, ie. 16 decimal; of
which 5 events are internally used by the BIOS for CDROM functions, so, of the
16 events, only 11 events are available to the game). A bigger amount of events
will slowdown the DeliverEvent function (which always scans all EvCBs, even if
all events are disabled).<br/>

#### B(09h) - CloseEvent(event) - releases event from the event table
Always returns 1 (even if the event handle is unused or invalid).<br/>

#### B(0Ch) - EnableEvent(event) - Turns on event handling for specified event
Always returns 1 (even if the event handle is unused or invalid).<br/>

#### B(0Dh) - DisableEvent(event) - Turns off event handling for specified event
Always returns 1 (even if the event handle is unused or invalid).<br/>

#### B(0Ah) - WaitEvent(event)
Returns 0 if the event is disabled. Otherwise hangs in a loop until the event
becomes ready, and returns 1 once when it is ready (and automatically switches
the event back to busy status). Callback events (mode=1000h) do never set the
ready flag (and thus WaitEvent would hang forever).<br/>
The main program simply hangs during the wait, so when using multiple threads,
it may be more recommended to create an own waitloop that checks TestEvent, and
to call ChangeTh when the event is busy.<br/>
BUG: The return value is unstable (sometimes accidently returns 0=disabled if
the event status changes from not-ready to ready shortly after the function
call).<br/>

#### B(0Bh) - TestEvent(event)
Returns 0 if the event is busy or disabled. Otherwise, when it is ready,
returns 1 (and automatically switches the event back to busy status). Callback
events (mode=1000h) do never set the ready flag.<br/>

#### B(07h) - DeliverEvent(class, spec)
This function is usually called by the kernel, it triggers all events that are
enabled/busy, and that have the specified class and spec values. Depending on
the mode, either the callback function is called (mode=1000h), or the event is
marked as enabled/ready (mode=2000h).<br/>

#### B(20h) - UnDeliverEvent(class, spec)
This function is usually called by the kernel, undelivers all events that are
enabled/ready, and that have mode=2000h, and that have the specified class and
spec values. Undeliver means that the events are marked as enabled/busy.<br/>

#### C(04h) - get\_free\_EvCB\_slot()
A subfunction for OpenEvent.<br/>

#### Event Classes
File Events:<br/>
```
  0000000xh memory card (for file handle fd=x)
```
Hardware Events:<br/>
```
  F0000001h IRQ0  VBLANK
  F0000002h IRQ1  GPU
  F0000003h IRQ2  CDROM Decoder
  F0000004h IRQ3  DMA controller
  F0000005h IRQ4  RTC0 (timer0)
  F0000006h IRQ5/IRQ6 RTC1 (timer1 or timer2)
  F0000007h N/A   Not used (this should be timer2)
  F0000008h IRQ7  Controller (joypad/memcard)
  F0000009h IRQ9  SPU
  F000000Ah IRQ10 PIO ;uh, does the PIO have an IRQ signal? (IRQ10 is joypad)
  F000000Bh IRQ8  SIO
  F0000010h Exception ;CPU crashed (BRK,BadSyscall,Overflow,MemoryError, etc.)
  F0000011h memory card (lower level BIOS functions)
  F0000012h memory card (not used by BIOS; maybe used by Sony's devkit?)
  F0000013h memory card (not used by BIOS; maybe used by Sony's devkit?)
```
Event Events:<br/>
```
  F1xxxxxxh event (not used by BIOS; maybe used by Sony's devkit?)
```
Root Counter Events (Timers and Vblank):<br/>
```
  F2000000h Root counter 0 (Dotclock)                    (hardware timer)
  F2000001h Root counter 1 (horizontal retrace?)         (hardware timer)
  F2000002h Root counter 2 (one-eighth of system clock)  (hardware timer)
  F2000003h Root counter 3 (vertical retrace?) (this is a software timer)
```
User Events:<br/>
```
  F3xxxxxxh user (not used by BIOS; maybe used by games and/or Sony's devkit?)
```
BIOS Events (including such that have nothing to do with BIOS):<br/>
```
  F4000001h memory card (higher level BIOS functions)
  F4000002h libmath (not used by BIOS; maybe used by Sony's devkit?)
```
Thread Events:<br/>
```
  FFxxxxxxh thread (not used by BIOS; maybe used by Sony's devkit?)
```

#### Event Specs
```
  0001h counter becomes zero
  0002h interrupted
  0004h end of i/o
  0008h file was closed
  0010h command acknowledged
  0020h command completed
  0040h data ready
  0080h data end
  0100h time out
  0200h unknown command
  0400h end of read buffer
  0800h end of write buffer
  1000h general interrupt
  2000h new device
  4000h system call instruction ;SYS(04h..FFFFFFFFh)
  8000h error happened
  8001h previous write error happened
  0301h domain error in libmath
  0302h range error in libmath
```

#### Event modes
```
  1000h Execute callback function, and stay busy (do NOT mark event as ready)
  2000h Do NOT execute callback function, and mark event as ready
```



##   BIOS Event Summary
Below is a list of all events (class,spec values) that are delivered and/or
undelivered by the BIOS in one way or another. The BIOS does internally open
five events for cdrom (class=F0000003h with spec=10h,20h,40h,80h,8000h). The
various other class/spec's are only delivered by the BIOS (but not received by
the BIOS) (ie. a game may open/enable memory card events to receive
notifications from the BIOS).<br/>

#### CDROM Events
```
  F0000003h,10h  cdrom DMA finished (all sectors finished)
  F0000003h,20h  cdrom ?
  F0000003h,40h  cdrom dead feature (delivered only by unused functions)
  F0000003h,80h  cdrom INT4 (reached end of disk)
  F0000003h,100h         n/a ?  ;undelivered, but not opened, nor delivered
  F0000003h,200h                ;undelivered, but not opened
  F0000003h,8000h
```

#### Memory Card - Higher Level File/Device Events
```
  0000000xh,4     card file handle (x=fd) done okay
  F4000001h,4     card done okay (len=0)
  F4000001h,100h  card err busy  ;A(A9h)
  F4000001h,2000h card err eject ;A(AAh) or unformatted (bad "MC" id)
  F4000001h,8000h card err write ;A(A8h) or A(AEh) or general error
```

#### Memory Card - Lower Level Hardware I/O Events
```
  F0000011h,4      finished okay
  F0000011h,100h   err busy
  F0000011h,200h     n/a ?
  F0000011h,2000h  err
  F0000011h,8000h  err
  F0000011h,8001h  err (this one is NOT undelivered!)
```

#### Timer/Vblank Events
```
  F2000000h,2   Timer0 (IRQ4)
  F2000001h,2   Timer1 (IRQ5)
  F2000002h,2   Timer2 (IRQ6)
  F2000003h,2   Vblank (IRQ0) (unstable since IRQ0 is also used for joypad)
```

#### Default IRQ Handler Events (very unstable, don't use)
```
  F0000001h,1000h ;IRQ0  (VBLANK)
  F0000002h,1000h ;IRQ1  (GPU)
  F0000003h,1000h ;IRQ2  (CDROM)
  F0000004h,1000h ;IRQ3  (DMA)
  F0000005h,1000h ;IRQ4  (TMR0)
  F0000006h,1000h ;IRQ5  (TMR1)
  F0000006h,1000h ;IRQ6  (TMR2) (accidently uses same event as TMR1)
  F0000008h,1000h ;IRQ7  (joypad/memcard)
  F0000009h,1000h ;IRQ9  (SPU)
  F000000Ah,1000h ;IRQ10 (Joypad and PIO)
  F000000Bh,1000h ;IRQ8  (SIO)
```

#### Unresolved Exception Events
```
  F0000010h,1000h unknown exception ;neither IRQ nor SYSCALL
  F0000010h,4000h unknown syscall   ;syscall(04h..FFFFFFFFh)
```



##   BIOS Thread Functions
#### B(0Eh) - OpenTh(reg\_PC,reg\_SP\_FP,reg\_GP)
Searches a free TCB, marks it as used, and stores the inital program counter
(PC), global pointer (GP aka R28), stack pointer (SP aka R29), and frame
pointer (FP aka R30) (using the same value for SP and FP). All other registers
are left uninitialized (eg. may contain values from an older closed thread,
that includes the SR register, see note).<br/>
The return value is the new thread handle (in range FF000000h..FF000003h,
assuming that 4 TCBs are allocated) or FFFFFFFFh if there's no free TCB. The
function returns to the old current thread, use "ChangeTh" to switch to the
new thread.<br/>
Note: The desired max number of TCBs can be specified in the SYSTEM.CNF boot
file (the default is "TCB = 4", one initially used for the boot executable,
plus 3 free threads).<br/>

#### BUG - Unitialized SR Register
OpenTh does NOT initialize the SR register (cop0r12) of the new thread.
Upon powerup, the bootcode zerofills the TCB memory (so, the SR of new threads
will be initially zero; ie. Kernel Mode, IRQ's disabled, and COP2 disabled).
However, when closing/reopening threads, the SR register will have the value of
the old closed thread (so it may get started with IRQs enabled, and, in worst
case, if the old thread should have switched to User Mode, even without access
to KSEG0, KSEG1 memory).<br/>
Or, ACTUALLY, the memory is NOT zerofilled on powerup... so SR is total random?<br/>

#### B(0Fh) - CloseTh(handle)
Marks the TCB for the specified thread as unused. The function can be used for
any threads, including for the current thread.<br/>
Closing the current thread doesn't terminate the current thread, so it may
cause problems once when opening a new thread, however, it should be stable to
execute the sequence "DisableInterrupts, CloseCurrentThread,
ChangeOtherThread".<br/>
The return value is always 1 (even if the handle was already closed).<br/>

#### B(10h) - ChangeTh(handle)
Pauses the current thread, and activates the selected new thread (or crashes if
the specified handle was unused or invalid).<br/>
The return value is always 1 (stored in the R2 entry of the TCB of the old
thread, so the return value will be received once when changing back to the old
thread).<br/>
Note: The BIOS doesn't automatically switch from one thread to another. So, all
other threads remain paused until the current thread uses ChangeTh to pass
control to another thread.<br/>
Each thread is having it's own CPU registers (R1..R31,HI,LO,SR,PC), the
registers are stored in the TCB of the old thread, and restored when switching
back to that thread. Mind that other registers (I/O Ports or GTE registers
aren't stored automatically, so, when needed, they need to be pushed/popped by
software before/after ChangeTh).<br/>

#### C(05h) - get\_free\_TCB\_slot()
Subfunction for OpenTh, returns the number of the first free TCB (usually
in range 0..3) or FFFFFFFFh if there's no free TCB.<br/>

#### SYS(03h) ChangeThreadSubFunction(addr) ;syscall with r4=03h, r5=addr
Subfunction for ChangeTh, R5 contains the address of the new TCB, just like
all exceptions, the syscall exception is saving the CPU registers in the
current TCB, but does then apply the new TCB as current TCB, and so, it does
then enter the new thread when returning from the exception.<br/>



##   BIOS Timer Functions
#### Timers (aka Root Counters)
The three hardware timers aren't internally used by any BIOS functions, so they
can be freely used by the game, either via below functions, or via direct I/O
access.<br/>

#### Vblank
Some of the below functions are allowing to use Vblank IRQs as a fourth
"timer". However, Vblank IRQs are internally used by the BIOS for handling
joypad and memory card accesses. One could theoretically use two separate
Vblank IRQ handlers, one for joypad, and one as "timer", but the BIOS is much
too unstable for such "shared" IRQ handling (it may occassionally miss one of
the two handlers).<br/>
So, although Vblank IRQs are most important for games, the PSX BIOS doesn't
actually allow to use them for purposes other than joypad access. A possible
workaround is to examine the status byte in one of the joypad buffers (ie. the
InitPAD2(buf1,22h,buf2,22h) buffers). Eg. a wait\_for\_vblank function could look
like so: set buf1[0]=55h, then wait until buf1[0]=00h or buf1[0]=FFh.<br/>

#### B(02h) - init\_timer(t,reload,flags)
When t=0..2, resets the old timer mode by setting [1F801104h+t\*16]=0000h,
applies the reload value by [1F801108h+t\*16]=reload, computes the new mode:<br/>
```
  if flags.bit4=0 then mode=0048h else mode=0049h
  if flags.bit0=0 then mode=mode OR 100h
  if flags.bit12=1 then mode=mode OR 10h
```
and applies it by setting [1F801104h+t\*16]=mode, and returns 1. Does nothing
and returns zero for t\>2.<br/>

#### B(03h) - get\_timer(t)
Reads the current timer value: Returns halfword[1F801100h+t\*16] for t=0..2.
Does nothing and returns zero for t\>2.<br/>

#### B(04h) - enable\_timer\_irq(t)
#### B(05h) - disable\_timer\_irq(t)
Enables/disables timer or vblank interrupt enable bits in [1F801074h], bit4,5,6
for t=0,1,2, or bit0 for t=3, or random/garbage bits for t\>3. The enable
function returns 1 for t=0..2, and 0 for t=3. The disable function returns
always 1.<br/>

#### B(06h) - restart\_timer(t)
Sets the current timer value to zero: Sets [1F801100h+t\*16]=0000h and returns 1
for t=0..2. Does nothing and returns zero for t\>2.<br/>

#### C(0Ah) - ChangeClearRCnt(t,flag) ;root counter (aka timer)
Selects what the kernel's timer/vblank IRQ handlers shall do after they have
processed an IRQ (t=0..2: timer 0..2, or t=3: vblank) (flag=0: do nothing; or
flag=1: automatically acknowledge the IRQ and immediately return from
exception). The function returns the old (previous) flag value.<br/>



##   BIOS Joypad Functions
#### Pad Input
Joypads should be initialized via InitPAD2(buf1,22h,buf2,22h), and StartPAD2().
The main program can read the pad data from the buf1/buf2 addresses (including
Status, ID1, button states, and any kind of analogue inputs). For more info on
ID1, Buttons and analogue inputs, see<br/>
[Controllers and Memory Cards](../controllers-digital-analog/SKILL.md)<br/>
Note: The BIOS doesn't include any functions for sending custom data to the
pads (such like for controlling rumble motors).<br/>

#### B(12h) - InitPAD2(buf1, siz1, buf2, siz2)
Memorizes the desired buf1/buf2 addresses, zerofills the buffers by using the
siz1/siz2 buffer size values (which should be 22h bytes each). And does some
initialization on the PadCardIrq element (but doesn't enqueue it, that must be
done by a following call to StartPAD2), and does set the "pad\_enable\_flag", that
flag can be also set/cleared via InitCARD2(pad\_enable), where it selects if the
Pads are kept handled together with Memory Cards. buf1/buf2 are having the
following format:<br/>
```
  00h      Status (00h=okay, FFh=timeout/wrong ID2)
  01h      ID1    (eg. 41h=digital_pad, 73h=analogue_pad, 12h=mouse, etc.)
  02h..21h Data   (max 16 halfwords, depending on lower 4bit of ID1)
```
Note: InitPAD2 does initially zerofill the buffers, so, until the first IRQ is
processed, the initial status is 00h=okay, with buttons=0000h (all buttons
pressed), to fix that situation, change the two status bytes to FFh after
calling InitPAD2 (or alternately, reject ID1=00h).<br/>
Once when the PadCardIrq is enqueued via StartPAD2, and while "pad\_enable\_flag"
is set, the data for (both) Pad1 and Pad2 is read on Vblank interrupts, and
stored in the buffers, the IRQ handler stores up to 22h bytes in the buffer
(regardless of the siz1/siz2 values) (eg. a Multitap adaptor uses all 22h
bytes).<br/>

#### B(13h) - StartPAD2()
Should be used after InitPAD2. Enqueues the PadCardIrq handler, and does
additionally initialize some flags.<br/>

#### B(14h) - StopPAD2()
Dequeues the PadCardIrq handler. Note that this handler is also used for memory
cards, so it'll "stop" cards, too.<br/>

#### B(15h) - PAD\_init2(type, button\_dest, unused, unused)
This is an extremely bizarre and restrictive function - don't use! The function
fails unless type is 20000000h or 20000001h (the type value has no other
function). The function uses "buf1/buf2" addresses that are located somewhere
"hidden" within the BIOS variables region, the only way to read from that
internal buffers is to use the ugly "PAD_dr()" function. For
some strange reason it FFh-fills buf1/buf2, and does then call
InitPAD2(buf1,22h,buf2,22) (which does immediately 00h-fill the previously
FFh-filled buffers), and does then call StartPAD2().<br/>
Finally, it does memorize the "button\_dest" address (see
PAD_dr() for details on that value). The two unused parameters
have no function, however, they are internally written back to the stack
locations reserved for parameter 2 and 3, ie. at [SP+08h] and [SP+0Ch] on the
caller's stack, so the function MUST be called with all four parameters
allocated on stack. Return value is 2 (or 0 if type was disliked).<br/>

#### B(16h) - PAD\_dr()
This is a very ugly function, using the internal "buf1/buf2" values from
"PAD_init2" and the "button\_dest" value that was passed to that
function.<br/>
If "button\_dest" is non-zero, then this function is automatically called by the
PadCardIrq handler, and stores it's return value at [button\_dest] (where it may
be read by the main program). If "button\_dest" is zero, then it isn't called
automatically, and it \<can\> be called manually (with return value in R2),
however, it does additionally write the return value to [button\_dest], ie. to
[00000000h] in this case, destroying that memory location.<br/>
The return value itself is useless garbage: The lower 16bit contain the pad1
buttons, the upper 16bit the pad2 buttons, of which, both values have reversed
byte-order (ie. the first button byte in upper 8bit). The function works only
with controller IDs 41h (digital joypad) and 23h (nonstandard device). For
ID=23h, the halfword is ORed with 07C7h, and bit6,7 are then cleared if the
analogue inputs are greater than 10h. For ID=41h the data is left intact. Any
other ID values, or disconnected joypads, cause the halfword to be set to FFFFh
(same as when no buttons are pressed), that includes newer analogue pads
(unless they are switched to "digital" mode).<br/>



##   BIOS GPU Functions
#### A(48h) - SendGP1Command(gp1cmd)
Writes [1F801814h]=gp1cmd. There's no return value (r2 is left unchanged).<br/>

#### A(49h) - GPU\_cw(gp0cmd)      ;send GP0 command word
Calls gpu\_sync(), and does then write [1F801810h]=gp0cmd. Returns the return
value from the gpu\_sync() call.<br/>

#### A(4Ah) - GPU\_cwp(src,num) ;send GP0 command word and parameter words
Calls gpu\_sync(), and does then copy "num" words from [src and up] to
[1F801810h], src should usually point to a command word, followed by num-1
parameter words. Transfer is done by software (without DMA). Always returns 0.<br/>

#### A(4Bh) - send\_gpu\_linked\_list(src)
Transfer an OT via DMA. Calls gpu\_sync(), and does then write
[1F801814h]=4000002h, [1F8010F4h]=0, [1F8010F0h]=[1F8010F0h] OR 800h,
[1F8010A0h]=src, [1F8010A4h]=0, [1F8010A8h]=1000401h. The function does
additionally output a bunch of TTY status messages via printf. The function
doesn't wait until the DMA is completed. There's no return value.<br/>

#### A(4Ch) - gpu\_abort\_dma()
Writes [1F8010A8h]=401h, [1F801814h]=4000000h, [1F801814h]=2000000h,
[1F801814h]=1000000h. Ie. stops GPU DMA, and issues GP1(4), GP1(2), GP1(1).
Returns 1F801814h, ie. the I/O address.<br/>

#### A(4Dh) - GetGPUStatus()
Reads [1F801814h] and returns that value.<br/>

#### A(46h) - GPU\_dw(Xdst,Ydst,Xsiz,Ysiz,src)
Waits until GPUSTAT.Bit26 is set (unlike gpu\_sync, which waits for Bit28), and
does then [1F801810h]=A0000000h, [1F801810h]=YdstXdst, [1F801810h]=YsizXsiz,
and finally transfers "N" words from [src and up] to [1F801810h], where "N" is
"Xsiz\*Ysiz/2". The data is transferred by software (without DMA) (by code
executed in the uncached BIOS region with high waitstates, so the data transfer
is very SLOW).<br/>
Caution: If "Xsiz\*Ysiz" is odd, then the last halfword is NOT transferred, so
the GPU stays waiting for the last data value.<br/>
Returns [SP+04h]=Ydst, [SP+08h]=Xsiz, [SP+0Ch]=Ysiz, [SP+10h]=src+N\*4, and
R2=src=N\*4.<br/>

#### A(47h) - gpu\_send\_dma(Xdst,Ydst,Xsiz,Ysiz,src)
Calls gpu\_sync(), writes [1F801810h]=A0000000h, [1F801814h]=4000002h,
[1F8010F0h]=[1F8010F0h] OR 800h, [1F8010A0h]=src, [1F8010A4h]=N\*10000h+10h
(where N="Xsiz\*Ysiz/32"), [1F8010A8h]=1000201h.<br/>
Caution: If "Xsiz\*Ysiz" is not a multiple of 32, then the last halfword(s) are
NOT transferred, so the GPU stays waiting for that values.<br/>
Returns R2=1F801810h, and [SP+04h]=Ydst, [SP+08h]=Xsiz, [SP+0Ch]=Ysiz.<br/>

#### A(4Eh) - gpu\_sync()
If DMA is off (when GPUSTAT.Bit29-30 are zero): Waits until GPUSTAT.Bit28=1 (or
until timeout).<br/>
If DMA is on: Waits until D2\_CHCR.Bit24=0 (or until timeout), and does then
wait until GPUSTAT.Bit28=1 (without timeout, ie. may hang forever), and does
then turn off DMA via GP1(04h).<br/>
Returns 0 (or -1 in case of timeout, however, the timeout values are very big,
so it may take a LOT of seconds before it returns).<br/>



##   BIOS Memory Allocation
#### A(33h) - malloc(size)
Allocates size bytes on the heap, and returns the memory handle (aka the
address of the allocated memory block). The address of the block is guaranteed
to by aligned to 4-byte memory boundaries. Size is rounded up to a multiple of
4 bytes. The address may be in KUSEG, KSEG0, or KSEG1, depending on the address
passed to InitHeap.<br/>
Caution: The BIOS (tries to) initialize the heap size to 0 bytes (actually it
accidently overwrites that initial setting by garbage during relocation), so
any call to malloc will fail, unless InitHeap has been used to initialize the
address/size of the heap.<br/>

#### A(34h) - free(buf)
Deallocates the memory block. There's no return value, and no error checking.
The function simply sets [buf-4]=[buf-4] OR 00000001h, so if buf is an invalid
handle it may destroy memory at [buf-4], or trigger a memory exception (for
example, when buf=0).<br/>

#### A(37h) - calloc(sizx, sizy)     ;SLOW!
Allocates xsiz\*ysiz bytes by calling malloc(xsiz\*ysiz), and, unlike malloc, it
does additionally zerofill the memory via SLOW "bzero" function. Returns the
address of the memory block (or zero if failed).<br/>

#### A(38h) - realloc(old\_buf, new\_size)   ;SLOW!
If "old\_buf" is zero, executes malloc(new\_size), and returns r2=new\_buf (or
0=failed). Else, if "new\_size" is zero, executes free(old\_buf), and returns
r2=garbage. Else, executes malloc(new\_size), bcopy(old\_buf,new\_buf,new\_size),
and free(old\_buf), and returns r2=new\_buf (or 0=failed).<br/>
Caution: The bcopy function is SLOW, and realloc does accidently copy
"new\_size" bytes from old\_buf, so, if the old\_size was smaller than new\_size
then it'll copy whatever garbage data - in worst case, if it exceeds the top of
the 2MB RAM region, it may crash with a locked memory exception, although
that'd happen only if SetMem(2) was used to restrict RAM to 2MBs.<br/>

#### A(39h) - InitHeap(addr, size)
Initializes the address and size of the heap - the BIOS does not automatically
do this, so, before using the heap, InitHeap must be called by software.
Usually, the heap would be memory region between the end of the boot
executable, and the bottom of the executable's stack. InitHeap can be also used
to deallocate all memory handles (eg. when a new exe file has been loaded, it
may use it to deallocate all old memory).<br/>
The heap is used only by malloc/realloc/calloc/free, and by the "qsort"
function.<br/>

#### B(00h) - alloc\_kernel\_memory(size)
#### B(01h) - free\_kernel\_memory(buf)
Same as malloc/free, but, instead of the heap, manages the 8kbyte control block
memory at A000E000h..A000FFFFh. This region is used by the kernel to allocate
ExCBs (4x08h bytes), EvCBs (N\*1Ch bytes), TCBs (N\*0C0h bytes), and the process
control block (1x04h bytes). Unlike the heap, the BIOS does automatically
initialize this memory region via SysInitMemory(addr,size), and does
autimatically allocate the above data (where the number of EvCBs and TCBs is as
specified in the SYSTEM.CNF file). Note: FCBs and DCBs are located elsewhere,
at fixed locations in the kernel variables area.<br/>

#### Scratchpad Note
The kernel doesn't include any allocation functions for the scratchpad (nor do
any kernel functions use that memory area), so the executable can freely use
the "fast" memory at 1F800000h..1F8003FFh.<br/>

#### A(9Fh) - SetMem(megabytes)
Changes the effective RAM size (2 or 8 megabytes) by manipulating port
1F801060h, and additionally stores the size in megabytes in RAM at [00000060h].<br/>
Note: The BIOS bootcode accidently sets the RAM value to 2MB (which is the
correct physical memory size), but initializes the I/O port to 8MB (which
mirrors the physical 2MB within that 8MB region), so the initial values don't
match up with each other.<br/>
Caution: Applying the correct size of 2MB may cause the "realloc" function to
crash (that function may accidently access memory above 2MB).<br/>



##   BIOS Memory Fill/Copy/Compare (SLOW)
Like most A(NNh) functions, below functions are executed in uncached BIOS ROM,
the ROM has very high waitstates, and the 32bit opcodes are squeezed through an
8bit bus. Moreover, below functions are restricted to process the data
byte-by-byte. So, they are very-very-very slow, don't even think about using
them.<br/>
Of course, that applies also for most other BIOS functions. But it's becoming
most obvious for these small functions; memcpy takes circa 160 cycles per byte
(reasonable would be less than 4 cycles), and bzero takes circa 105 cycles per
byte (reasonable would be less than 1 cycles).<br/>

#### A(2Ah) - memcpy(dst, src, len)
Copies len bytes from [src..src+len-1] to [dst..dst+len-1]. Refuses to copy any
data when dst=00000000h or when len\>7FFFFFFFh. The return value is always
the incoming "dst" value.<br/>

#### A(2Bh) - memset(dst, fillbyte, len)
Fills len bytes at [dst..dst+len-1] with the fillbyte value. Refuses to fill
memory when dst=00000000h or when len\>7FFFFFFFh. The return value is the
incoming "dst" value (or zero, when len=0 or len\>7FFFFFFFh).<br/>

#### A(2Ch) - memmove(dst, src, len) - bugged
Same as memcpy, but (attempts) to support overlapping src/dst regions, by using
a backwards transfer when src\<dst (and, for some reason, only when
dst\>=src+len).<br/>
BUG: The backwards variant accidently transfers len+1 bytes from [src+len..src]
down to [dst+len..dst].<br/>

#### A(2Dh) - memcmp(src1, src2, len) - bugged
Compares len bytes at [src1..src1+len-1] with [src2..src2+len-1], and
(attempts) to return the difference between the first mismatching bytes, ie.
[src1+N]-[src2+N], or 0 if there are no mismatches. Refuses to compare data
when src1 or src2 is 00000000h, and returns 0 in that case.<br/>
BUG: Accidently returns the difference between the bytes AFTER the first
mismatching bytes, ie. [src1+N+1]-[src2+N+1].<br/>
That means that a return value of 0 can mean absolutely anything: That the
memory blocks are identical, or that a mismatch has been found (but that the
NEXT byte after the mismatch does match), or that the function has failed (due
to src1 or src2 being 00000000h).<br/>

#### A(2Eh) - memchr(src, scanbyte, len)
Scans [src..src+len-1] for the first occurence of scanbyte. Refuses to scan any
data when src=00000000h or when len\>7FFFFFFFh. Returns the address of that
first occurence, or 0 if the scanbyte wasn't found.<br/>

#### A(27h) - bcopy(src, dst, len)
Same as "memcpy", but with "src" and "dst" exchanged. That is, the first
parameter is "src", the refuse occurs when "src" is 00000000h, and, returns the
incoming "src" value (whilst "memcpy" uses "dst" in that places).<br/>

#### A(28h) - bzero(dst, len)
Same as memset, but uses 00h as fixed fillbyte value.<br/>

#### A(29h) - bcmp(ptr1, ptr2, len) - bugged
Same as "memcmp", with exactly the same bugs.<br/>



##   BIOS String Functions
#### A(15h) - strcat(dst, src)
Appends src to the end of dst. Searches the ending 00h byte in dst, and copies
src to that address, up to including the ending 00h byte in src. Returns the
incoming dst value. Refuses to do anything if src or dst is 00000000h (and
returns 0 in that case).<br/>

#### A(16h) - strncat(dst, src, maxlen)
Same as "strcat", but clipped to "MaxSrc=(min(0,maxlen)+1)" characters, ie. the
total length is max "length(dst)+min(0,maxlen)+1". If src is longer or equal to
"MaxSrc", then only the first "MaxSrc" chars are copied (with the last byte
being replaced by 00h). If src is shorter, then everything up to the ending 00h
byte gets copied, but without additional padding (unlike as in "strncpy").<br/>

#### A(17h) - strcmp(str1, str2)
Compares the strings up to including ending 00h byte. Returns 0 if they are
identical, or otherwise [str1+N]-[str2+N], where N is the location of the first
mismatch, the two bytes are sign-expanded to 32bits before doing the
subtraction. The function rejects str1/str2 values of 00000000h (and returns
0=both are zero, -1=only str1 is zero, and +1=only str2 is zero).<br/>

#### A(18h) - strncmp(str1, str2, maxlen)
Same as "strcmp" but stops after comparing "maxlen" characters (and returns 0
if they did match). If the strings are shorter, then comparision stops at the
ending 00h byte (exactly as for strcmp).<br/>

#### A(19h) - strcpy(dst, src)
Copies data from src to dst, up to including the ending 00h byte. Refuses to
copy anything if src or dst is 00000000h. Returns the incoming dst address (or
0 if copy was refused).<br/>

#### A(1Ah) - strncpy(dst, src, maxlen)
Same as "strcpy", but clipped to "maxlen" characters. If src is longer or equal
to maxlen, then only the first "maxlen" chars are copied (but without appending
an ending 00h byte to dst). If src is shorter, then the remaining bytes in dst
are padded with 00h bytes.<br/>

#### A(1Bh) - strlen(src)
Returns the length of the string up to excluding the ending 00h byte (or 0 when
src is 00000000h).<br/>

#### A(1Ch) - index(src, char)
#### A(1Dh) - rindex(src, char)
#### A(1Eh) - strchr(src, char)  ;exactly the same as "index"
#### A(1Fh) - strrchr(src, char) ;exactly the same as "rindex"
Scans for the first (index) or last (rindex) occurence of char in the string.
Returns the memory address of that occurence (or 0 if there's no occurence, or
if src is 00000000h). Char may be 00h (returns the end address of the string).
Note that, despite of the function names, the return value is always a memory
address, NOT an index value relative to src.<br/>

#### A(20h) - strpbrk(src, list)
Scans for the first occurence of a character that is contained in the list. The
list contains whatever desired characters, terminated by 00h.<br/>
Returns the address of that occurence, or 0 if there was none. BUG: If there
was no occurence, it returns 0 only if src[0]=00h, and otherwise returns the
incoming "src" value (which is the SAME return value as when a occurence did
occur on 1st character).<br/>

#### A(21h) - strspn(src, list)
#### A(22h) - strcspn(src, list)
Scans for the first occurence of a character that is (strspn), or that isn't
(strcspn) contained in the list. The list contains whatever desired characters,
terminated by 00h.<br/>
Returns the index (relative to src) of that occurence. If there was no
occurence, then it returns the length of src. That silly return values do not
actually indicate if an occurence has been found or not (unless one checks for
[src+index]=00h or so).<br/>
\*\*\*<br/>
"The strcspn() function shall compute the length (in bytes) of the maximum
initial segment of the string pointed to by s1 which consists entirely of bytes
not from the string pointed to by s2."<br/>
"The strspn() function shall compute the length (in bytes) of the maximum
initial segment of the string pointed to by s1 which consists entirely of bytes
from the string pointed to by s2."<br/>
\*\*\*<br/>
Hmmmm, that'd be vice-versa?<br/>

#### A(23h) - strtok(src, list) ;first call
#### A(23h) - strtok(0, list) ;further call(s)
Used to split a string into fragments, list contains a list of characters that
are to be treated as separators, terminated by 00h.<br/>
The first call copies the incoming string to a buffer in the BIOS variables
area (the buffer size is 100h bytes, so the string should be max 255 bytes
long, plus the ending 00h byte, otherwise the function destroys other BIOS
variables), it does then search the first fragment, starting at the begin of
the buffer. Further calls (with src=00000000h) are searching further fragments,
starting at the buffer address from the previous call. The internal buffer is
used only for strtok, so its contents (and the returned string fragments)
remain intact until a new first call to strtok takes place.<br/>
The separate fragments are processed by searching the first separator, starting
at the current buffer address, the separator is then replaced by a 00h byte,
and the old buffer address is returned to the caller. Moreover, the function
tries to skip all continously following separators, until reaching a
non-separator, and does memorize that address for the next call (due to that
skipping further calls won't return empty fragments, the first call may do so
though). That skipping seems to be bugged, if list contains two or more
different characters, then additional separators aren't skipped.<br/>
```
  ",,TEXT,,,END" with list=","  returns "", "TEXT", "END"
  ",,TEXT,,,END" with list=",." returns "", "", "TEXT", "", "", "END"
```
Once when there are no more fragments, then 00000000h is returned.<br/>

#### A(24h) - strstr(str, substr) - buggy
Scans for the first occurence of substr in the string. Returns the memory
address of that occurence (or 0 if it was unable to find an occurence).<br/>
BUG: After rejecting incomplete matches, the function doesn't fallback to the
old str address plus 1, but does rather continue at the current str address.
Eg. it doesn't find substr="aab" in str="aaab" (in that example, it does merely
realize that "aab"\<\>"aaa" and then that "aab"\<\>"b").<br/>



##   BIOS Number/String/Character Conversion
#### A(0Eh) - abs(val)
#### A(0Fh) - labs(val)  ;exactly same as "abs"
Returns the absolute value (if val\<0 then R2=-val, else R2=val).<br/>

#### A(0Ah) - todigit(char)
Takes the incoming character, ANDed with FFh, and returns 0..9 for characters
"0..9" and 10..35 for "A..Z" or "a..z", or 0098967Fh (9,999,999 decimal) for
any other 7bit characters, or garbage for characters 80h..FFh.<br/>

#### A(25h) - toupper(char)
#### A(26h) - tolower(char)
Returns the incoming character, ANDed with FFh, with letters "A..Z" converted
to uppercase/lowercase format accordingly. Works only for char 00h..7Fh (some
characters in range 80h..FFh are left unchanged, others are randomly "adjusted"
by adding/subtracting 20h, and by sign-expanding the result to 32bits).<br/>

#### A(0Dh) - strtol(src, src\_end, base)
Converts a string to a number. The function skips any leading "blank"
characters (that are, 09h..0Dh, and 20h) (ie. TAB, CR, LF, SPC, and some
others) (some characters in range 80h..FFh are accidently treated as "blank",
too).<br/>
The incoming base value should be in range 2..11, although the function does
also accept the buggy values in range of 12..36 (for values other than 2..36 it
defaults to decimal/base10). The used numeric digits are "0..9" and "A..Z" (or
less when base is smaller than 36).<br/>
The string may have a negative sign prefix "-" (negates the result) (a "+" is
NOT recognized; and will be treated as the end of the string). Additionally,
the string may contain prefixes "0b" (binary/base2), "0x" (hex/base16), or "o"
(octal/base8) (only "o", not "0o"), allowing to override the incoming "base"
value.<br/>
BUG: Incoming base values greater than 11 don't work due to the prefix feature
(eg. base=16 with string "0b11" will be treated as 11 binary, and base=36 with
string "o55" will be treated as 55 octal) (the only workaround would be to
add/remove leading "0" characters, ie. "b11" or "00b11" or "0o55" would work
okay).<br/>
Finally, the function initializes result=0, and does then process the digits as
"result=result\*base+digit" (without any overflow checks) unless/until it
reaches an unknown digit (or when digit\>=base) (ie. the string may end with
00h, or with any other unexpected characters).<br/>
The function accepts both uppercase and lowercase characters (both as prefixes,
and as numeric digits). The function returns R2=result, and
[src\_end]=end\_address (ie. usually the address of the ending 00h byte; or of
any other unexpected end-byte). If src points to 00000000h, then the function
returns r2=0, and leaves [src\_end] unchanged.<br/>

#### A(0Ch) - strtoul(src, src\_end, base)
Same as "strtol" except that it doesn't recognize the "-" sign prefix (ie.
works only for unsigned numbers).<br/>

#### A(10h) - atoi(src)
#### A(11h) - atol(src)  ;exactly same as "atoi" (but slightly slower)
Same as "strtol", except that it doesn't return the string end address in
[src\_end], and except that it defaults to base=10, but still supports prefixes,
allowing to use base2,8,16. CAUTION: For some super bizarre reason, this
function treats "0" (a leading ZERO digit) as OCTAL prefix (unlike strtol,
which uses the "o" letter as octal prefix) (the "0x" and "0b" prefixes are
working as usually).<br/>

#### A(12h) - atob(src, num\_dst)
Calls "strtol(str,src\_end,10)", and does then exchange the two return values
(ie. sets R2=[src\_end], and [num\_dst]=value\_32bit).<br/>

#### A(0Bh) - atof(src) ;USES (ABSENT) COP1 FPU !!!
#### A(32h) - strtod(src, src\_end) ;USES (ABSENT) COP1 FPU !!!
These functions are intended to convert strings to floating point numbers,
however, the functions are accidently compiled for MIPS processors with COP1
floating point unit (which is not installed in the PSX, nor does the BIOS
support a COP1 software emulation), so calling these functions will produce a
coprocessor exception, causing the PSX to lockup via A(40h)
SystemErrorUnresolvedException.<br/>

#### Note
On other systems (eg. 8bit computers), "abs/atoi" (integer) and "labs/atol"
(long) may act differently. However, on the Playstation, both use signed 32bit
values.<br/>



##   BIOS Misc Functions
#### A(2Fh) - rand()
Advances the random generator as "x=x\*41C64E6Dh+3039h" (aka plus 12345
decimal), and returns a 15bit random value "R2=(x/10000h) AND 7FFFh".<br/>

#### A(30h) - srand(seed)
Changes the current 32bit value of the random generator.<br/>

#### A(B4h) - GetSystemInfo(index)  ;not supported by old CEX-1000 version
Returns a word, halfword, or string, depending on the selected index value:<br/>
```
  00h      Get Kernel BCD Date       (eg. 19951204h) (YYYYMMDDh)
  01h      Get Kernel Flags or so    (usually/always 000000003h)
  02h      Get Kernel Version String (eg. "CEX-3000/1001/1002 by K.S.",0)
  03h      Get whatever halfword     (usually 0)    ;PS2: returns cop0r15
  04h      Get whatever halfword     (usually 0)
  05h      Get RAM Size in kilobytes (usually 2048) ;=[00000060h] SHL 10
  06h..0Eh Get whatever halfwords    (usually 0,400h,0,200h,0,0,1,1,1)
  0Fh      N/A (returns zero) ;PS2: returns 0000h (effectively = same as zero)
  10h..FFFFFFFFh Not used (returns zero)
```
Note: The Date/Version are referring to the Kernel (in the first half of the
BIOS). The Intro and Bootmenu (in the second half of the BIOS) may have a
different version, there's no function to retrieve info on that portion,
however, a version string for it can be usually found at BFC7FF32h (eg. "System
ROM Version 4.5 05/25/00 E",0) (in many bios versions, the last letter of that
string indicates the region, but not in all versions) (the old SCPH1000 does
not include that version string at all).<br/>

#### B(56h) - GetC0Table()
#### B(57h) - GetB0Table()
Retrieves the address of the jump lists for B(NNh) and C(NNh) functions,
allowing to patch entries in that lists (however, the BIOS does often jump
directly to the function addresses, rather than indirectly via the list, so
patching may have little effect in such cases). Note: There's no function to
retrieve the address of the A(NNh) jump list, however, that list is
usually/always at 00000200h.<br/>

#### A(31h) - qsort(base, nel, width, callback)
Sorts an array, using a super-slow implementation of the "quick sort"
algorithm. base is the address of the array, nel is the number of elements in
the array, width is the size in bytes of each element, callback is a function
that receives pointers to two elements which need to be compared; callback
should return return zero if the elements are identical, or a positive/negative
number to indicate which element is bigger.<br/>
The qsort function rearranges the contents of the array, ie. depending on the
callback result, it may swap the contents of the two elements, for some bizarre
reason it doesn't swap them directly, but rather stores one of the elements
temporarily on the heap (that means, qsort works only if the heap was
initialized with InitHeap, and only if "width" bytes are free). There's no
return value.<br/>

#### A(35h) - lsearch(key, base, nel, width, callback)
#### A(36h) - bsearch(key, base, nel, width, callback)
Searches an element in an array (key is the pointer to the searched element,
the other parameters are same as for "qsort"). "lsearch" performs a slow linear
search in an unsorted array, by simply comparing one array element after each
other. "bsearch" assumes that the array contains sorted elements (eg. via
qsort), which is allowing to skip some elements, and to jump back and forth in
the array, until it has found the desired element (or the location where it'd
be, if it'd be in the array). Both functions return the address of the element
(or 0 if it wasn't found).<br/>

#### C(19h) - \_ioabort(txt1,txt2)
Displays the two strings on the TTY (in some cases the BIOS does accidently
pass garbage instead of the 2nd string though). And does then execute
_ioabort\_raw(1), see there for more details.<br/>

#### A(B2h) - _ioabort\_raw(param)  ;not supported by old CEX-1000 version
Executes "longjmp(ioabortbuffer,param)". Internally used to recover from
failed I/O operations, param should be nonzero to notify the setjmp caller
that the abort has occurred.<br/>

#### A(13h) - setjmp(buf)
This is a somewhat incomplete implementation of posix's setjmp, by storing the ABI-saved CPU registers in the specified buffer (30h bytes):<br/>
```
  00h 4    r31 (ra) (aka caller's pc)
  04h 4    r29 (sp)
  08h 4    r30 (fp)
  0Ch 4x8  r16..r23
  2Ch 4    r28 (gp)
```
That type of buffer can be used with "_ioabort", "longjmp", and also
"HookEntryInt(addr)".<br/>
The "setjmp" function returns 0 when called directly. However, it may return again -
to the same return address, and the same stack pointer - with another return value (which should be usually
non-zero, to indicate that the state has been restored (eg. \_ioabort passes 1 as
return value).<br/>
Also noteworthy from what a compliant setjmp implementation should be doing
is the absence of saving the state of cop0 and cop2, thus making this slightly
unsuitable for a typical coroutine system implementation.<br/>

#### A(14h) - longjmp(buf, param)
Restores the R16-R23,GP,SP,FP,RA registers from a previously recorded
jmp_buf buffer, and "returns" to that new RA address (rather than to the caller of the
longjmp function). The "param" value is passed as "return value" to the
code at RA, ie. usually to the caller of the original setjmp call. Noteworthy difference
from a conformant longjmp implementation is that the "param" value won't be clamped to 1 if
you pass 0 to it. So since setjmp returns 0 on the first call, the caller of longjmp must take
care that "param" is non-zero, so the callsite of setjmp can make the difference between the first
call and a rollback. See setjmp for further details.<br/>

#### A(53h) - set\_ioabort\_handler(src)  ;PS2 only  ;PSX: SystemError
Normally the _ioabort handler is changed only internally during booting, with
this new function, games can install their own \_ioabort handler. src is pointer
to a 30h-byte "savestate" structure, which will be copied to the actual \_ioabort
structure.<br/>

#### A(06h) or B(38h) - exit(exitcode)
Terminates the program and returns control to the BIOS; which does then lockup
itself via A(3Ah) _exit.<br/>

#### A(A0h) - \_boot()
Performs a warmboot (resets the kernel and reboots from CDROM). Unlike the
normal coldboot procedure, it doesn't display the "\<S\>" and "PS" intro
screens (and doesn't verify the "PS" logo in the ISO System Area), and, doesn't
enter the bootmenu (even if the disk drive is empty, or if it contains an Audio
disk). And, it doesn't reload the SYSTEM.CNF file, so the function works only
if the same disk is still inserted (or another disk with identical SYSTEM.CNF,
such like Disk 2 of the same game).<br/>

#### A(B5h..BFh) B(11h,24h..29h,2Ch..31h,5Eh..FFh) C(1Eh..7Fh) - N/A - Jump 0
These functions jump to address 00000000h. For whatever reason, that address
does usually contain a copy of the exception handler (ie. same as at address
80000080h). However, since there's no return address stored in EPC register,
the functions will likely crash when returning from the exception handler.<br/>

#### A(57h..5Ah,73h..77h,79h..7Bh,7Dh,7Fh..80h,82h..8Fh,B0h..B1h,B3h), and
#### C(0Eh..11h,14h) - N/A - Returns 0
No function. Simply returns with r2=00000000h.<br/>
Reportedly, A(85h) is CdStop, but that seems to be nonsense?<br/>

#### SYS(00h) - NoFunction()
No function. Simply returns without changing any registers or memory locations
(except that, of course, the exception handler destroys k0).<br/>

#### SYS(04h..FFFFFFFFh) - calls DeliverEvent(F0000010h,4000h)
These are syscalls with invalid function number in R4. For whatever reason that
is handled by issuing DeliverEvent(F0000010h,4000h). Thereafter, the syscall
returns to the main program (ie. it doesn't cause a SystemError).<br/>

#### A(3Ah) - \_exit(exitcode)
#### A(40h) - SystemErrorUnresolvedException()
#### A(A1h) - SystemError(type,errorcode) ;type "B"=Boot,"D"=Disk
These are used "SystemError" functions. The functions are repeatedly jumping to
themselves, causing the system to hang. Possibly useful for debugging software
which may hook that functions.<br/>

#### A(4Fh,50h,52h,53h,9Ah,9Bh) B(1Ah..1Fh,21h..23h,2Ah,2Bh,52h,5Ah) C(0Bh) - N/A
These are additional "SystemError" functions, but they are never used. The
functions are repeatedly jumping to themselves, causing the system to hang.<br/>

#### BRK(1C00h) - Division by zero (commonly checked/invoked by software)
#### BRK(1800h) - Division overflow (-80000000h/-1, sometimes checked by software)
The CPU does not generate any exceptions upon divide overflows, because of
that, the Kernel code and many games are commonly checking if the divider is
zero (by software), and, if so, execute a BRK 1C00h opcode. The default BIOS
exception handler doesn't handle BRK exceptions, and does simply redirect them
to SystemErrorUnresolvedException().<br/>



