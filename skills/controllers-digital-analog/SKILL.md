---
name: controllers-digital-analog
description: "PSX controllers: communication protocol (active-low select, clock, data), standard digital/analog pads, mouse, racing controllers, lightguns (GunCon, Justifier), multitap adaptor. Use when working with controller input, pad protocol, or lightgun implementation."
---

#   Controllers and Memory Cards
#### Controllers/Memory Cards
[Controller and Memory Card Overview](controllersandmemorycards.md#controller-and-memory-card-overview)<br/>
[Controller and Memory Card Signals](controllersandmemorycards.md#controller-and-memory-card-signals)<br/>
[Controller and Memory Card Multitap Adaptor](controllersandmemorycards.md#controller-and-memory-card-multitap-adaptor)<br/>

#### Controllers
[Controllers - Communication Sequence](controllersandmemorycards.md#controllers-communication-sequence)<br/>
[Controllers - Standard Digital/Analog Controllers](controllersandmemorycards.md#controllers-standard-digitalanalog-controllers)<br/>
[Controllers - Mouse](controllersandmemorycards.md#controllers-mouse)<br/>
[Controllers - Racing Controllers](controllersandmemorycards.md#controllers-racing-controllers)<br/>
[Controllers - Lightguns](controllersandmemorycards.md#controllers-lightguns)<br/>
[Controllers - Configuration Commands](controllersandmemorycards.md#controllers-configuration-commands)<br/>
[Controllers - Vibration/Rumble Control](controllersandmemorycards.md#controllers-vibrationrumble-control)<br/>
[Controllers - Analog Buttons (Dualshock2)](controllersandmemorycards.md#controllers-analog-buttons-dualshock2)<br/>
[Controllers - Dance Mats](controllersandmemorycards.md#controllers-dance-mats)<br/>
[Controllers - Pop'n Controllers](controllersandmemorycards.md#controllers-popn-controllers)<br/>
[Controllers - Taiko Controllers (Tatacon)](controllersandmemorycards.md#controllers-taiko-controllers-tatacon)<br/>
[Controllers - Densha de Go! / Jet de Go! Controllers](controllersandmemorycards.md#controllers-densha-de-go-jet-de-go-controllers)<br/>
[Controllers - Fishing Controllers](controllersandmemorycards.md#controllers-fishing-controllers)<br/>
[Controllers - PS2 DVD Remote](controllersandmemorycards.md#controllers-ps2-dvd-remote)<br/>
[Controllers - I-Mode Adaptor (Mobile Internet)](controllersandmemorycards.md#controllers-i-mode-adaptor-mobile-internet)<br/>
[Controllers - Additional Inputs](controllersandmemorycards.md#controllers-additional-inputs)<br/>
[Controllers - Misc](controllersandmemorycards.md#controllers-misc)<br/>

#### Memory Cards
[Memory Card Read/Write Commands](controllersandmemorycards.md#memory-card-readwrite-commands)<br/>
[Memory Card Data Format](controllersandmemorycards.md#memory-card-data-format)<br/>
[Memory Card Images](controllersandmemorycards.md#memory-card-images)<br/>
[Memory Card Notes](controllersandmemorycards.md#memory-card-notes)<br/>

#### Pocketstation (Memory Card with built-in LCD screen and buttons)
[Pocketstation](pocketstation.md)<br/>

#### Pinouts
[Pinouts - Controller Ports and Memory-Card Ports](pinouts.md#pinouts-controller-ports-and-memory-card-ports)<br/>



##   Controller and Memory Card Overview
Controllers and memory cards connect to the console using a serial protocol and
are accessed through SIO0 registers:<br/>
[Serial Interfaces (SIO)](serialinterfacessio.md)<br/>
The protocol used is similar to standard SPI, with no start/stop bytes and no
parity (even though SIO0 has support for it). Unlike typical SPI, only one byte
is transferred at a time and a separate wire (/ACK) is used by the device to
signal the PS1 that it is ready to exchange the next byte. For more details see:<br/>
[Controller and Memory Card Signals](controllersandmemorycards.md#controller-and-memory-card-signals)<br/>

#### Device addressing
Each controller port and its respective memory card slot are wired in parallel,
and the /CSn signals select both the controller and the memory card when
asserted. This selection is narrowed down through a simple addressing scheme,
where the first byte sent by the console after asserting /CSn is the address of
the device that shall reply. All devices must keep the DAT line idle before
receiving this byte. Once the address is sent, the device that was addressed
shall pull /ACK low to signal its presence and start exchanging bytes.<br/>
The following addresses are known to be used:<br/>

| Device                               | Address |
| :----------------------------------- | ------: |
| Standard controller                  |   `01h` |
| Yaroze Access Card                   |   `21h` |
| PS2 multitap (incompatible with PS1) |   `21h` |
| PS2 DVD remote receiver              |   `61h` |
| Memory card                          |   `81h` |

#### DSR (/ACK) Controller and Memory Card - Byte Received Interrupt
Gets set after receiving a data byte - that only if an /ACK has been received
from the peripheral (ie. there will be no IRQ if the peripheral fails to send
an /ACK, or if there's no peripheral connected at all).<br/>
```
  Actually, DSR means "more-data-request",
  accordingly, it does NOT get triggered after receiving the LAST byte.
```
I\_STAT.7 is edge triggered (that means it can be acknowledge before or after
acknowledging SIO0\_STAT.9). However, SIO0\_STAT.9 is NOT edge triggered (that
means it CANNOT be acknowledged while the external /IRQ input is still low; ie.
one must first wait until SIO0\_STAT.7=0, and then set SIO0\_CTRL.4=1) (this is
apparently a hardware glitch; note: the LOW duration is circa 100 clock
cycles).<br/>

#### /IRQ10 (/IRQ) Controller - Lightpen Interrupt
Pin 8 on Controller Port. Routed directly to the Interrupt Controller (at
1F80107xh). There are no status/enable bits in the SIO0\_registers (at
1F80104xh).<br/>

#### Plugging and Unplugging Cautions
During plugging and unplugging, the Serial Data line may be dragged LOW for a
moment; this may also affect other connected devices because the same Data line
is shared for all controllers and memory cards (for example, connecting a
joypad in slot 1 may corrupt memory card accesses in slot 2).<br/>
Moreover, the Sony Mouse does power-up with /ACK=LOW, and stays stuck in that
state until it is accessed at least once (by at least sending one 01h byte to
its controller port); this will also affect other devices (as a workaround one
should always access BOTH controller ports; even if a game uses only one
controller, and, code that waits for /ACK=HIGH should use timeouts).<br/>

#### Emulation Note
After sending a byte, the Kernel waits 100 cycles or so, and does THEN
acknowledge any old IRQ7, and does then wait for the new IRQ7. Due to that
bizarre coding, emulators can't trigger IRQ7 immediately within 0 cycles after
sending the byte.<br/>

#### BIOS Functions
Controllers can be probably accessed via InitPad and StartPad functions,<br/>
[BIOS Joypad Functions](kernelbios.md#bios-joypad-functions)<br/>
Memory cards can be accessed by the filesystem (with device names "bu00:"
(slot1) and "bu10:" (slot2) or so). Before using that device names, it seems to
be required to call InitCard, StartCard, and \_bu\_init (?).<br/>

#### Synchronous I/O
The data is transferred in units of bytes, via separate input and output lines.
So, when sending byte, the hardware does simultaneously receive a response
byte.<br/>
One exception is the address byte (which selects either the controller,
or the memory card) until that byte has been sent, neither the controller nor
memory card are selected (and so the first "response" byte should be ignored;
probably containing more or less stable high-z levels).<br/>
The other exception is, when you have send all command bytes, and still want to
receive further data, then you'll need to send dummy command bytes (should be
usually 00h) to receive the response bytes.<br/>



##   Controller and Memory Card Signals
#### Overview
```
        ____                                                              _____
  /CS       \____________________________________________________________/
        ______        ____        ____        ____        ____        _________
  SCK         ||||||||    ||||||||    ||||||||    ||||||||    ||||||||
        ____                                                              _____
  MOSI      '=[ Addr ]====[ Cmd  ]====[ Tap  ]====[Param ]====[Param ]==='

  MISO  ---------------===[ IDlo ]====[ IDhi ]====[ Data ]====[ Data ]===------
        _______________   _________   _________   _________   _________________
  /ACK                 |_|         |_|         |_|         |_|

--- High impedance
=== Any state (don't care)
```

#### Address byte (01h) being sent
```
        ____
  /CS       \__________________________________________________________________
        ______   _   _   _   _   _   _   _   __________________   _   _   _   _
  SCK         |_| |_| |_| |_| |_| |_| |_| |_|                  |_| |_| |_| |_|
        __________                                                  ___
  MOSI          1 |_0___0___0___0___0___0___0____________________0_| 1 |_0___0_
                                                               ____
  MISO  -----------------------------------------------======='  1 |_0___0___0_
        ______________________________________________     ____________________
  /ACK                                                |___|

--- High impedance
=== Any state (don't care)
```

Notes:

- All bytes are sent LSB first.
- The standard baud rate used by the kernel is ~250 kHz. Some controllers and
  memory cards may work with faster rates, but others will not.
- The clock polarity is high-when-idle (sometimes referred to as CPOL=1). Each
  bit is output on a falling clock edge and sampled by the other end on the
  rising clock edge that follows it (CPHA=1).
- The device has to pull /ACK low for at least 2 µs to request the host to
  transfer another byte. Once the last byte of the packet is transferred, the
  device shall no longer pulse /ACK.
- The kernel's controller driver will time out if /ACK is not pulled low by the
  device within 100 µs from the last SCK pulse. It will also ignore /ACK pulses
  sent within the first 2-3 µs (100 cycles) of the last SCK pulse.
- Devices should not respond immediately when /CS is asserted, but should wait
  for the address byte to be sent and only send an /ACK pulse back and start
  replying with data if the address matches.

##   Controller and Memory Card Multitap Adaptor
#### SCPH-1070 (Multitap)
The Multitap is an external adaptor that allows to connect 4 controllers, and 4
memory cards to one controller port. When using two adaptors (one on each
slot), up to 8 controllers and 8 memory cards can be used.<br/>

#### Multitap Controller Access
Normally joypad reading is done by sending this bytes to the pad:<br/>
```
  01 42 00 00 ..   ;normal read
```
And with the multitap, there are even two different ways how to access extra
pads:<br/>
```
  01 42 01 00 ..   ;method 1: receive special ID and data from ALL four pads
  0n 42 00 00 ..   ;method 2: receive data from pad number "n" (1..4)
```
The first method seems to be the more commonly used one (and its special ID is
also good for detecting the multitap); see below for details.<br/>
The second method works more like "normal" reads, among other it's allowing to
transfer more than 4 halfwords per slot (unknown if any existing games are
using that feature).<br/>
The IRQ10 signal (for Konami Lightguns) is simply wired to all four slots via
small resistors (without special logic for activating/deactivating the IRQ on
certain slots).<br/>

#### Multitap Controller Access, Method 1 Details
Below LONG response is activated by sending "01h" as third command byte;
observe that sending that byte does NOT affect the current response. Instead,
it does request that the NEXT command shall return special data, as so:<br/>
```
  Halfword 0      --> Controller ID for MultiTap (5A80h=Multitap)
  Halfword 1..4   --> Player A (Controller ID, Buttons, Analog Inputs, if any)
  Halfword 5..8   --> Player B (Controller ID, Buttons, Analog Inputs, if any)
  Halfword 9..12  --> Player C (Controller ID, Buttons, Analog Inputs, if any)
  Halfword 13..16 --> Player D (Controller ID, Buttons, Analog Inputs, if any)
```
With this method, the Multitap is always sending 4 halfwords per slot (padded
with FFFFh values for devices like Digital Joypads and Mice; which do use less
than 4 halfwords); for empty slots it's padding all 4 halfwords with FFFFh.<br/>
Sending the request is possible ONLY if there is a controller in Slot A (if
controller Slot A is empty then the Slot A access aborts after the FIRST byte,
and it's thus impossible to send the request in the THIRD byte).<br/>
Sending the request works on access to Slot A, trying to send another request
during the LONG response is glitchy (for whatever strange reason); one must
thus REPEATEDLY do TWO accesses: one dummy Slot A access (with the request),
followed by the long Slot A+B+C+D access.<br/>
```
  Previous access had REQ=0 and returned Slot A data ---> returns Slot A data
  Previous access had REQ=0 and returned Slot A-D data -> returns Slot A data
  Previous access had REQ=1 and returned Slot A data ---> returns Slot A-D data
  Previous access had REQ=1 and returned Slot A-D data -> returns garbage
  Previous access had REQ=1 and returned garbage -------> returns Slot A-D data
```
In practice:<br/>
Toggling REQ on/off after each command: Returns responses toggling between
normal Slot A data and long Slot A+B+C+D data.<br/>
Sending REQ=1 in ALL commands: Returns responses toggling between Garbage and
long Slot A+B+C+D data.<br/>
Both of the above is working (one needs only the Slot A+B+C+D part, and it
doesn't matter if the other part is Slot A, or Garbage; as long as the software
is able/aware of ignoring the Garbage). Garbage response means that the
multitap returns ONLY four bytes, like so: Hiz,80h,5Ah,LSB (ie. the leading
HighZ byte, the 5A80h Multitap ID, and the LSB of the Slot A controller ID),
and aborts transfer after that four bytes.<br/>

#### Multitap Memory Card Access
Normally memory card access is done by sending this bytes to the card:<br/>
```
  80 xx .. ..      ;normal access
```
And with the multitap, memory cards can be accessed as so:<br/>
```
  8n xx .. ..      ;access memory card in slot "n" (1..4)
```
That's the way how its done in Silent Hill. Although for the best of confusion,
it doesn't actually work in that game (probably the developer has just linked
in the multitap library, without actually supporting the multitap at higher
program levels).<br/>

#### Multitap Games
```
  Bomberman / Bomberman Party Edition (requires Multitap on Port 2 instead of 1)
  Bomberman World
  Breakout: Off the Wall Fun
  Circuit Breakers
  Crash Team Racing
  FIFA series soccer games
  Frogger
  Hot Shots Golf 2 & 3
  Jigsaw Island: Japan Graffiti / Jigsaw Madness (requires Multitap on Port 2 instead of 1)
  NBA Live (any year) (up to 8 players with two multitaps)
  Need For Speed 3
  Need For Speed 5
  Poy Poy (4 players hitting each other with rocks and trees)
  Running Wild
  S.C.A.R.S. (requires Multitap on Port 2 instead of 1)
  Zen Nippon Pro Wrestling: Ouja no Tamashii (requires Multitap on Port 2 instead of 1)
```
Most Multitap games supporting up to 4 or 5 controllers require the device to be plugged into Port 1, but a small number of games strangely require the device to be plugged into Port 2 instead.<br/>

#### Multitap Versions
```
                   .------.
   SCPH-1070       |      |        SCPH-111
   (gray case)     |      |        (white case)
   (for PSX)       |    D |        (for PSone)
                   |      |                   .----------------.
        cable      |      |        cable     .'   D        C   '.
            ''--.. |    C |         '''--..__|                  |
                  \|      |                  |                  |
  .----------------'      |                  '.   A        B   .'
  |                       |                   '----------------'
  |                       |
  |    A        B        /
  '---------------------'
```
The cable connects to one of the PSX controller ports (which also carries the
memory card signals). The PSX memory card port is left unused (and is blocked
by a small edge on the Multitap's plug).<br/>

#### MultiTap Parsed Controller IDs
Halfword 0 is parsed (by the BIOS) as usually, ie. the LSB is moved to MSB, and
LSB is replaced by status byte (so ID 5A80h becomes 8000h=Multitap/okay, or
xxFFh=bad). Halfwords 1,5,9,13 are NOT parsed (neither by the BIOS nor by the
Multitap hardware), however, some info in the internet is hinting that Sony's
libraries might be parsing these IDs too (so for example 5A41h would become
4100h=DigitalPad/okay, or xxFFh=bad).<br/>

#### Power Supply
The Multitap is powered by the PSX controller port. Unknown if there are any
power supply restrictions (up to eight controllers and eight cards may scratch
some limits, especially when doing things like activating rumble on all
joypads). However, the Multitap hardware itself doesn't do much on supply
restrictions (+3.5V is passed through something; maybe some fuse, loop, or 1
ohm resistor or so) (and +7.5V is passed without any restrictions).<br/>

#### PS2 multitap
Sony made a multitap adapter for the PS2, however it is not compatible with the
PS1 as it plugs into both the controller and memory card ports (which are not
wired in parallel on the PS2). The protocol is also different: rather than
modifying packets it seems to act as a mostly-passive port multiplexer,
accepting switching commands with address 61h. Unknown if the PS2 multitap is
backwards compatible with the SCPH-1070 protocol.<br/>

#### See also
[Pinouts - Component List and Chipset Pin-Outs for Multitap, SCPH-1070](pinouts.md#pinouts-component-list-and-chipset-pin-outs-for-multitap-scph-1070)<br/>



##   Controllers - Communication Sequence
#### Controller Communication Sequence
```
  Send Reply Comment
  01h  Hi-Z  Controller address
  42h  idlo  Receive ID bit0..7 (variable) and Send Read Command (ASCII "B")
  TAP  idhi  Receive ID bit8..15 (usually/always 5Ah)
  MOT  swlo  Receive Digital Switches bit0..7
  MOT  swhi  Receive Digital Switches bit8..15
  --- transfer stops here for digital pad (or analog pad in digital mode) ---
  00h  adc0  Receive Analog Input 0 (if any) (eg. analog joypad or mouse)
  00h  adc1  Receive Analog Input 1 (if any) (eg. analog joypad or mouse)
  --- transfer stops here for analog mouse ----------------------------------
  00h  adc2  Receive Analog Input 2 (if any) (eg. analog joypad)
  00h  adc3  Receive Analog Input 3 (if any) (eg. analog joypad)
  --- transfer stops here for analog pad (in analog mode) -------------------
  --- transfer stops here for nonstandard devices (steering/twist/paddle) ---
```
The TAP byte should be usually zero, unless one wants to activate Multitap
(multi-player mode), for details, see<br/>
[Controller and Memory Card Multitap Adaptor](controllersandmemorycards.md#controller-and-memory-card-multitap-adaptor)<br/>
The two MOT bytes are meant to control the rumble motors (for normal non-rumble
controllers, that bytes should be 00h), however, the MOT bytes have no effect
unless rumble is enabled via config commands, for details, see<br/>
[Controllers - Configuration Commands](controllersandmemorycards.md#controllers-configuration-commands)<br/>
[Controllers - Vibration/Rumble Control](controllersandmemorycards.md#controllers-vibrationrumble-control)<br/>

#### Controller ID (Halfword Number 0)
```
  0-3  Number of following halfwords (01h..0Fh=1..15, or 00h=16 halfwords)
  4-7  Controller Type (or currently selected Controller Mode)
  8-15 Fixed (5Ah)
```
Known 16bit ID values are:<br/>
```
  xx00h=N/A                 (initial buffer value from InitPad BIOS function)
  5A12h=Mouse               (two button mouse)
  5A23h=NegCon              (steering twist/wheel/paddle)
  5A31h=Konami Lightgun     (IRQ10-type)
  5A41h=Digital Pad         (or analog pad/stick in digital mode; LED=Off)
  5A53h=Analog Stick        (or analog pad in "flight mode"; LED=Green)
  5A63h=Namco Lightgun      (Cinch-type)
  5A73h=Analog Pad          (in normal analog mode; LED=Red)
  5A7xh=Dualshock2          (with variable number of inputs enabled)
  5A79h=Dualshock2          (with all analog/digital inputs enabled)
  5A80h=Multitap            (multiplayer adaptor) (when activated)
  5A96h=Keyboard            (rare lightspan keyboard)
  5AE3h=Jogcon              (steering dial)
  5AE8h=Keyboard/Sticks     (rare homebrew keyboard/segasticks adaptor)
  5AF3h=Config Mode         (when in config mode; see rumble command 43h)
  FFFFh=High-Z              (no controller connected, pins floating High-Z)
```
The PS2 DVD remote receiver identifies as either 5A41h (i.e. a digital
controller) when polled using standard controller commands, or 5A12h when using
address 61h to access the IR functionality.<br/>



##   Controllers - Standard Digital/Analog Controllers
```
       ___                      ___           ___                      ___
    __/_L_\__   Analog Pad   __/_R_\__     __/_L_\__  Digital Pad   __/_R_\__
   /    _    \--------------/         \   /    _    \--------------/         \
  |   _| |_   |            |     /\    | |   _| |_   |            |     /\    |
  |  |_ X _|  |SEL      STA|  []    () | |  |_ X _|  |            |  []    () |
  |    |_|  ___   ANALOG   ___   ><    | |    |_|    |  SEL  STA  |     ><    |
  |\______ / L \   LED    / R \ ______/| |\_________/--------------\_________/|
  |       | Joy |--------| Joy |       | |       |                    |       |
  |      / \___/          \___/ \      | |      /                      \      |
   \____/                        \____/   \____/                        \____/
```

#### Standard Controllers
```
  __Halfword 0 (Controller Info)_______________________________________________
  0-15  Controller Info  (5A41h=digital, 5A73h=analog/pad, 5A53h=analog/stick)
  __Halfword 1 (Digital Switches)______________________________________________
  0   Select Button    (0=Pressed, 1=Released)
  1   L3/Joy-button    (0=Pressed, 1=Released/None/Disabled) ;analog mode only
  2   R3/Joy-button    (0=Pressed, 1=Released/None/Disabled) ;analog mode only
  3   Start Button     (0=Pressed, 1=Released)
  4   Joypad Up        (0=Pressed, 1=Released)
  5   Joypad Right     (0=Pressed, 1=Released)
  6   Joypad Down      (0=Pressed, 1=Released)
  7   Joypad Left      (0=Pressed, 1=Released)
  8   L2 Button        (0=Pressed, 1=Released) (Lower-left shoulder)
  9   R2 Button        (0=Pressed, 1=Released) (Lower-right shoulder)
  10  L1 Button        (0=Pressed, 1=Released) (Upper-left shoulder)
  11  R1 Button        (0=Pressed, 1=Released) (Upper-right shoulder)
  12  /\ Button        (0=Pressed, 1=Released) (Triangle, upper button)
  13  () Button        (0=Pressed, 1=Released) (Circle, right button)
  14  >< Button        (0=Pressed, 1=Released) (Cross, lower button)
  15  [] Button        (0=Pressed, 1=Released) (Square, left button)
  __Halfword 2 (Right joystick) (analog pad/stick in analog mode only)_________
  0-7   adc0 RightJoyX (00h=Left, 80h=Center, FFh=Right)
  8-15  adc1 RightJoyY (00h=Up,   80h=Center, FFh=Down)
  __Halfword 3 (Left joystick) (analog pad/stick in analog mode only)__________
  0-7   adc2 LeftJoyX  (00h=Left, 80h=Center, FFh=Right)
  8-15  adc3 LeftJoyY  (00h=Up,   80h=Center, FFh=Down)
  __Further Halfword(s) (Dualshock2 only, and only if enabled)_________________
  0-7   ..   Analog Button (if enabled) (00h=Released, FFh=Max Pressure)
  8-15  ..   Analog Button (if enabled) (00h=Released, FFh=Max Pressure)
  ..    ..   ..
```

#### Analog Mode Note
On power-up, the controllers are in digital mode (with analog inputs disabled).
Analog mode can be (de-)activated manually by pushing the Analog button.
Alternately, analog mode can be (de-)activated by software via rumble
configuration commands (though that's supported only on newer pads; those with
two rumble motors). It is essential that emulators and any third-party hardware have a way of manually toggling analog mode, similar to original analog controllers, as certain games like Gran Turismo 1 will not attempt to enter analog mode on their own, even if they support analog controls and detect an analog controller.<br/>
Since analog pads boot in digital mode and will return the same ID byte as digital controllers, the most common way of distinguishing between the 2 is to send a Dualshock-only command (Typically command 43h - enter/exit config mode) and seeing how the controller responds to it.<br/>
The analog sticks are mechanically restricted to a "circular field of motion"
(most joypads can reach "min/max" values only in "straight" horizontal or
vertical directions, but not in "diagonal" directions).<br/>

#### Analog Joypad Range
```
               ...''''''''''...
       ____ .''________________''._____       ___ 00h
      |  .''                      ''.  |
      |.'                            '.|      ___ 10h
      .'                              '.
     :|                                |:
    : |                                | :    ___ 60h
   .' |            .''''''.            | '.
   :  |          .'        '.          |  :
   :  |          :          :          |  :   ___ 80h
   :  |          :          :          |  :
   :  |          '.        .'          |  :
   '. |            '......'            | .'   ___ A0h
    : |                                | :
     :|                                |:
      '.                              .'      ___ F0h
      |'.                            .'|
      |__'..______________________..'__|      ___ FFh
      .     '..                ..'     .
     00h       '''..........'''       FFh
```

```
   Big Circle   --> Mechanically possible field of motion
   Square Area  --> Digitally visible 8bit field of motion
   Small Circle --> Resting position when releasing the joystick
```
Example min/center/max values for three different pads:<br/>
```
  SCPH-1150          Min=(00,00), Mid: (72..90,79..AC), Max=(FF,FF) at 25'C
  SCPH-1200          Min=(0E,0E), Mid: (6C..8A,75..79), Max=(ED,ED) at 16'C
  SCPH-110           Min=(11,11), Mid: (8A..9F,70..96), Max=(FD,FD) at 16'C
```
Values may vary for other pads and/or different temperatures.<br/>

#### Dual Analog Pad in LED=Green Mode
Basically same as normal analog LED=Red mode, with following differences:<br/>
```
  ID is 5A53h (identifying itself as analog stick) (rather than analog pad)
  Left/right joy-buttons disabled (as for real analog stick, bits are always 1)
  Some buttons are re-arranged: bit9=L1 bit10=[] bit11=/\ bit12=R1 bit15=R2
```
Concerning the button names, the real analog-stick does NOT have re-arranged
buttons (eg. it's L1 button is in bit10), however, concerning the button
locations, the analog stick's buttons are arranged completely differently as on
analog pads (so it might be rather uncomfortable to play analog stick games on
analog pads in LED=Red mode; the LED=Green mode is intended to solve that
problem).<br/>
Might be useful for a few analog-stick games like MechWarrior 2, Ace Combat 2,
Descent Maximum, and Colony Wars. In most other cases the feature is rather
confusing (that's probably why the LED=Green mode wasn't implemented on the
Dual Shock).<br/>

#### See also
[Pinouts - Component List and Chipset Pin-Outs for Digital Joypad, SCPH-1080](pinouts.md#pinouts-component-list-and-chipset-pin-outs-for-digital-joypad-scph-1080)<br/>
[Pinouts - Component List and Chipset Pin-Outs for Analog Joypad, SCPH-1150](pinouts.md#pinouts-component-list-and-chipset-pin-outs-for-analog-joypad-scph-1150)<br/>
[Pinouts - Component List and Chipset Pin-Outs for Analog Joypad, SCPH-1200](pinouts.md#pinouts-component-list-and-chipset-pin-outs-for-analog-joypad-scph-1200)<br/>
[Pinouts - Component List and Chipset Pin-Outs for Analog Joypad, SCPH-110](pinouts.md#pinouts-component-list-and-chipset-pin-outs-for-analog-joypad-scph-110)<br/>



##   Controllers - Mouse
#### Sony Mouse Controller
```
  __Halfword 0 (Controller Info)________________
  0-15  Controller Info  (5A12h=Mouse)
  __Halfword 1 (Mouse Buttons)__________________
  0-7   Not used         (All bits always 1)
  8-9   Unknown          (Seems to be always 0) (maybe SNES-style sensitivity?)
  10    Right Button     (0=Pressed, 1=Released)
  11    Left Button      (0=Pressed, 1=Released)
  12-15 Not used         (All bits always 1)
  __Halfword 2 (Mouse Motion Sensors)___________
  0-7   Horizontal Motion (-80h..+7Fh = Left..Right) (00h=No motion)
  8-15  Vertical Motion   (-80h..+7Fh = Up..Down)    (00h=No motion)
```

#### Sony Mouse Hardware Bug on Power-On
On Power-on (or when newly connecting it), the Sony mouse does draw /ACK to LOW
on power-on, and does then hold /ACK stuck in the LOW position.<br/>
For reference: Normal controllers and memory cards set /ACK=LOW only for around
100 clk cycles, and only after having received a byte from the console.<br/>
The /ACK pin is shared for both controllers and both memory cards, so the stuck
/ACK is also "blocking" all other connected controllers/cards. To release the
stuck /ACK signal: Send a command (at least one 01h byte) to both controller
slots.<br/>

#### Sony Mouse Compatible Games
```
  3D Lemmings
  Alien Resurrection
  Area 51
  Ark of Time
  Atari Anniversary Edition
  Atlantis: The Lost Tales
  Breakout: Off the Wall Fun
  Broken Sword: The Shadow of the Templars
  Broken Sword II: The Smoking Mirror
  Clock Tower: The First Fear
  Clock Tower II: The Struggle Within
  Command & Conquer: Red Alert
  Command & Conquer: Red Alert - Retaliation
  Constructor (Europe)
  Die Hard Trilogy
  Die Hard Trilogy 2: Viva Las Vegas
  Discworld
  Discworld II: Missing Presumed...!?
  Discworld Noir
  Dune 2000
  Final Doom
  Galaxian 3
  Ghoul Panic
  Klaymen Klaymen: Neverhood no Nazon (Japan)
  Lemmings and Oh No! More Lemmings
  Monopoly
  Music 2000
  Myst
  Neorude (Japan)
  Perfect Assassin
  Policenauts (Japan)
  Puchi Carat
  Quake II
  Railroad Tycoon II
  Rescue Shot
  Risk
  Riven: The Sequel to Myst
  RPG Maker
  Sentinel Returns
  SimCity 2000
  Syndicate Wars
  Tempest 2000 (Tempest X3)
  Theme Aquarium (Japan)
  Transport Tycoon
  Warhammer: Dark Omen
  Warzone 2100
  X-COM: Enemy Unknown
  X-COM: Terror from the Deep
  Z
```
Note: There are probably many more mouse compatible games.<br/>
Certain games, mostly FPS games such as Quake II and Doom, have players plug a standard digital/analog pad in port 1
and a mouse in port 2. This way, players can use the mouse for aiming and shooting, while the pad can be used for moving, reloading, and so on.<br/>

#### Sony Mouse Component List
PCB "TD-T41V/\, MITSUMI"<br/>
Component Side:<br/>
```
  1x 3pin   4.00MHz "[M]4000A, 85 2"
  2x 2pin   button (left/right)
  1x 8pin   connector (to cable with shield and 7 wires)
  1x 3pin   "811, T994I"
  2x 3pin   photo transistor (black)  ;\or so, no idea which one is
  2x 2pin   photo diode (transparent) ;/sender and which is sensor
  1x 2pin   electrolyt capacitor 16V, 10uF
```
Solder/SMD Side:<br/>
```
  1x 32pin  "(M), SC442116, FB G22K, JSAA815B"
  1x 14pin  "BA10339F, 817 L67" (Quad Comparator)
  2x 3pin   "LC" (amplifier for photo diodes)
  1x 3pin   "24-" (looks like a dual-diode or so)
  plus many SMD resistors/capacitors
```
Cable:<br/>
```
  PSX.Controller.Pin1 DAT   ---- brown  -- Mouse.Pin4
  PSX.Controller.Pin2 CMD   ---- red    -- Mouse.Pin3
  PSX.Controller.Pin3 +7.5V ---- N/A
  PSX.Controller.Pin4 GND   ---- orange -- Mouse.Pin7 GND (G)
  PSX.Controller.Pin5 +3.5V ---- yellow -- Mouse.Pin1
  PSX.Controller.Pin6 /CSn  ---- green  -- Mouse.Pin5
  PSX.Controller.Pin7 SCK   ---- blue   -- Mouse.Pin2
  PSX.Controller.Pin8 /IRQ  ---- N/A
  PSX.Controller.Pin9 /ACK  ---- purple -- Mouse.Pin6
  PSX.Controller.Shield -------- shield -- Mouse.Pin8 GND (SHIELD)
```

#### PS/2 and USB Mouse Adaptors
Some keyboard adaptors are also including a mouse adaptor feature (either by
simulating normal Sony Mouse controller data, or via more uncommon ways like
using the PSX expansion port).<br/>
[Controllers - Keyboards](controllersandmemorycards.md#controllers-keyboards)<br/>

#### RS232 Mice
Below is some info on RS232 serial mice. That info isn't directly PSX related
as the PSX normally doesn't support those mice.<br/>
With some efforts, one can upgrade the PSX SIO port to support RS232 voltages,
and with such a modded console one could use RS232 mice (in case one wants to
do that).<br/>
The nocash PSX bios can map a RS232 mouse to a spare controller slot (thereby
simulating a Sony mouse), that trick may work with various PSX games.<br/>

#### Standard Serial Mouse
A serial mouse should be read at 1200 bauds, 7 data bits, no parity, 1 stop bit
(7N1) with DTR and RTS on. For best compatibility, the mouse should output 2
stop bits (so it could be alternately also read as 7N2 or 8N1). When the mouse
gets moved, or when a button gets pressed/released, the mouse sends 3 or 4
characters:<br/>
```
  __First Character____________________
  6    First Character Flag (1)
  5    Left Button  (1=Pressed)
  4    Right Button (1=Pressed)
  2-3  Upper 2bit of Vertical Motion
  0-1  Upper 2bit of Horizontal Motion
  __Second Character___________________
  6    Non-first Character Flag (0)
  5-0  Lower 6bit of Horizontal Motion
  __Third Character____________________
  6    Non-first Character Flag (0)
  5-0  Lower 6bit of Vertical Motion
  __Fourth Character (if any)__________
  6    Non-first Character Flag (0)
  5    Middle Button (1=Pressed)
  4    Unused ???
  3-0  Wheel  ???
```
Additionally, the mouse outputs a detection character (when switching RTS (or
DTR?) off and on:<br/>
```
  "M" = Two-Button Mouse (aka "Microsoft" mouse)
  "3" = Three-Button Mouse (aka "Logitech" mouse)
  "Z" = Mouse-Wheel
```
Normally, the detection response consist of a single character (usually "M"),
though some mice have the "M" followed by 11 additional characters of garbage
or version information (these extra characters have bit6=0, so after detection,
one should ignore all characters until receiving the first data character with
bit6=1).<br/>

#### Mouse Systems Serial Mouse (rarely used)
Accessed at 1200 bauds, just like standard serial mouse, but with 8N1 instead
7N1, and with different data bytes.<br/>
```
  __First Byte_________________________
  7-3  First Byte Code (10000b)
  2    Left? Button   (0=Pressed)
  1    Middle? Button (0=Pressed)
  0    Right? Button  (0=Pressed)
  __Second Byte________________________
  7-0  Horizontal Motion (X1)
  __Third Byte_________________________
  7-0  Vertical Motion   (Y1)
  __Fourth Byte________________________
  7-0  Horizontal Motion (X2)
  __Fifth Byte_________________________
  7-0  Vertical Motion   (Y2)
```
The strange duplicated 8bit motion values are usually simply added together,
ie. X=X1+X2 and Y=Y1+Y2, producing 9bit motion values.<br/>

#### Notes
The Sony Mouse connects directly to the PSX controller port. Alternately serial
RS232 mice can be connected to the SIO port (with voltage conversion adaptor)
(most or all commercial games don't support SIO mice, nor does the original
BIOS do so, however, the nocash BIOS maps SIO mice to unused controller slots,
so they can be used even with commercial games; if the game uses BIOS functions
to read controller data).<br/>
Serial Mice (and maybe also the Sony mouse) do return raw mickeys, so effects
like double speed threshold must (should) be implemented by software. Mice are
rather rarely used by PSX games. The game "Perfect Assassin" includes
ultra-crude mouse support, apparently without threshold, and without properly
matching the cursor range to the screen resolution.<br/>



##   Controllers - Racing Controllers
#### neGcon Racing Controller (Twist) (NPC-101/SLPH-00001/SLEH-0003)
```
  __Halfword 0 (Controller Info)_______________________________________________
  0-15  Controller Info  (5A23h=neGcon)
  __Halfword 1 (Digital Switches)______________________________________________
  0-2   Not used       (always 1)       (would be Select, L3, R3 on other pads)
  3     Start Button   (0=Pressed, 1=Released)
  4     Joypad Up      (0=Pressed, 1=Released)
  5     Joypad Right   (0=Pressed, 1=Released)
  6     Joypad Down    (0=Pressed, 1=Released)
  7     Joypad Left    (0=Pressed, 1=Released)
  8-10  Not used       (always 1)       (would be L2, R2, L1 on other pads)
  11    R Button       (0=Pressed, 1=Released) (would be R1 on other pads)
  12    B Button       (0=Pressed, 1=Released) (would be /\ on other pads)
  13    A Button       (0=Pressed, 1=Released) (would be () on other pads)
  14-15 Not used       (always 1)              (would be ><, [] on other pads)
  __Halfword 2 (Right joystick) (analog pad/stick in analog mode only)_________
  0-7   Steering Axis    (00h=Left, 80h=Center, FFh=Right) (or vice-versa?)
  8-15  Analog I button  (00h=Out ... FFh=In)  (Out=released, in=pressed?)
  __Halfword 3 (Left joystick) (analog pad/stick in analog mode only)__________
  0-7   Analog II button (00h=Out ... FFh=In)  (Out=released, in=pressed?)
  8-15  Analog L button  (00h=Out ... FFh=In)  (Out=released, in=pressed?)
```
The Twist controller works like a paddle or steering wheel, but doesn't have a
wheel or knob, instead, it can be twisted: To move into one direction (=maybe
right?), turn its right end away from you (or its left end towards you). For
the opposite direction (=maybe left?), do it vice-versa.<br/>
```
     _____         _  _         _____                              ____
    |__L__\_______/ || \_______/__R__|                            /    \
   /    _   namco   ||   neGcon       \                          /      \
  |   _| |_         ||            B    |                        |       |
  |  |_ X _|    ....||....     II   A  | .... Rotation Axis ... | ...  \|/
  |    |_|          ||            I    |                        |
  |        START    ||                 |                         \
  |       ________  ||  ________       |                          \__\
  |      /        \_||_/        \      |                             /
   \____/                        \____/
```

#### Namco Volume Controller (a paddle with two buttons) (SLPH-00015)
This is a cut-down variant of the neGcon, just a featureless small box. It does
have the same ID value as neGcon (ID=5A23h), but, it excludes most digital, and
all analog buttons.<br/>
```
   _______
  | namco |      Halfword 1 (digital buttons):
  |       |      Bit3  Button A (0=Pressed) (aka neGcon Start button)
  | A   B |      Bit13 Button B (0=Pressed) (aka neGcon A button aka () button)
  |       |      Other bits     (not used, always 1)
  |   _   |      Halfword 2 and 3 (analog inputs):
  |  (_)  |      Steering Axis  (00h..FFh)  (as for neGcon)
  |_______|      Analog I,II,L button values (not used, always 00h)
```

#### SANKYO N.ASUKA aka Nasca Pachinco Handle (SLPH-00007)
Another cut-down variant of the neGcon (with ID=5A23h, too). But, this one
seems to have only one button. Unlike Namco's volume controller it doesn't look
featureless. It looks pretty much as shown in the ascii-arts image below. Seems
to be supported by several irem titles. No idea what exactly it is used for,
it's probably not a sewing machine controller, nor an electronic amboss.<br/>
```
   ____ ____     Halfword 1 (digital buttons):
  |   /   _ \    Bit12 Button   (0=Pressed) (aka neGcon B button aka /\ button)
  |_ /   (_) )   Other bits     (not used, always 1)
  |_|___    /\   Halfword 2 and 3 (analog inputs):
   ____|   |_    Steering Axis  (00h..FFh)  (as for neGcon)
  |__________|   Analog I,II,L button values (not used, always 00h)
```

#### Mad Catz Steering Wheel (SLEH-0006)
A neGcon compatible controller. The Twist-feature has been replaced by a
steering wheel (can be turned by 270 degrees), and the analog I and II buttons
by foot pedals. The analog L button has been replaced by a digital button (ie.
in neGcon mode, the last byte of the controller data can be only either 00h or
FFh). When not using the pedals, the I/II buttons on the wheel can be used
(like L button, they aren't analog though).<br/>
```
        __________________________
       /   ____________________   \    Stick
      /   /                    \   \    ___        Brakes  Gas
     /   (                      )   \  (   )         II     I
    /  I  \                    /  A  \  \ /          ___   ___
   / /\ II \____________MODE__/  B /\ \  |          |   | |   |
  | |  \ L  _                   R /  | | |          |!!!|_|!!!|___
  | |   ) _| |_   MadCatz        (   | |_|_        /|!!!| |!!!|  /
  | |  | |_ X _|                  |  | | | |      / |___| |___| /
  | |  |   |_|                    |  | |  /      / =========== /
  | |   \         SEL STA        /   | | /      / =========== /
   \ \__/ ______________________ \__/ / /      /_____________/
    \____/                      \____/_/
       |___________________________|
```

Unlike the neGon, the controller has Select, \>\< and [] buttons, and a
second set of L/R buttons (at the rear-side of the wheel) (no idea if L1/R1 or
L2/R2 are at front?). Aside from the neGcon mode, the controller can be also
switched to Digital mode (see below for button chart).<br/>

#### MadCatz Dual Force Racing Wheel
Same as above, but with a new Analog mode (additionally to Digital and neGcon
modes). The new mode is for racing games that support only Analog Joypads
(instead of neGcon). Additionally it supports vibration feedback.<br/>

#### MadCatz MC2 Vibration compatible Racing Wheel and Pedals
Same as above, but with a redesigned wheel with rearranged buttons, the digital
pad moved to the center of the wheel, the L/R buttons at the rear-side of the
wheel have been replaced by 2-way butterfly buttons ("pull towards user" acts
as normal, the new "push away from user" function acts as L3/R3).<br/>
```
            ____________________
           /  ________________  \   ___ Stick      Brakes  Gas
          /  /       MC2      \  \ (   )             ___   ___
         /  /__________________\  \ \ /             |   | |   |
        |    A ()    _|_    I ><   | |              |!!!|_|!!!|___
        |   B /\ _    |    _ II [] | |             /|!!!| |!!!|  /
     ___|  L2   / \  STA  / \ R2   |_|_           / |___| |___| /
    /    \     /   | SEL |   \    /    \         / =========== /
   /  ____\    |___|     |___|   /____  \       / =========== /
  /__/     \____________________/     \__\     /_____________/
```

#### MadCatz Button Chart
```
  Mode     Buttons...................... Gas Brake Stick Wheel
  Digital  >< [] () /\ L1 R1 L2 R2 L1 R1 ><  ()    L1/R1 lt/rt
  Analog   >< [] () /\ L1 R1 L2 R2 L3 R3 UP  DN    L1/R1 LT/RT
  Negcon   I  II A  B  L  R  L  R  L  R  I   II    up/dn Twist
```
Whereas, lt/rt/up/dn=Digital Pad, UP/DN=Left Analog Pad Up/Down, LT/RT=Right
Analog Pad Left/Right. Analog mode is supported only by the Dual Force and MC2
versions, L3/R3 only by the MC2 version.<br/>

#### Namco Jogcon (NPC-105/SLEH-0020/SLPH-00126/SLUH-00059)
```
  __Halfword 0 (Controller Info)___________________
  0-15  Controller Info  (5AE3h=Jogcon in Jogcon mode) (ie. not Digital mode)
 halfword1: buttons: same as digital pad
 halfword2:
   0    unknown (uh, this isn't LSB of rotation?)
   1-15 dial rotation (signed offset since last read?) (or absolute position?)
 halfword3:
   0    flag: dial was turned left  (0=no, 1=yes)
   1    flag: dial was turned right (0=no, 1=yes)
   2-15 unknown
```
Rotations of the dial are recognized by an optical sensor (so, unlike
potentiometers, the dial can be freely rotated; by more than 360 degrees). The
dial is also connected to a small motor, giving it a real force-feedback effect
(unlike all other PSX controllers which merely have vibration feedback).
Although that's great, the mechanics are reportedly rather cheap and using the
controller doesn't feel too comfortable. The Jogcon is used only by Ridge Racer
4 for PS1 (and Ridge Racer 5 for PS2), and Breakout - Off the Wall Fun.<br/>
The Mode button probably allows to switch between Jogcon mode and Digital Pad
mode (similar to the Analog button on other pads), not sure if the mode can be
also changed by software via configuration commands...? Unknown how the motor
is controlled; probably somewhat similar to vibration motors, ie. by the M1
and/or M2 bytes, but there must be also a way to select clockwise and
anticlockwise direction)...? The controller does reportedly support config
command 4Dh (same as analog rumble).<br/>
```
       ___       ________       ___
    __/_L_\__   /        \   __/_R_\__
   /    _    \ / LED MODE \-/         \
  |   _| |_   | SEL    STA |     /\    |
  |  |_ X _|  |  ________  |  []    () |
  |    |_|    | /        \ |     ><    |
  |\_________/\/          \/\__ ______/|
  |       |   |   JOGCON   |   |       |
  |       |   |    DIAL    |   |       |
  |       |    \          /    |       |
  |       |     \________/     |       |
  |       |                    |       |
  |       |                    |       |
   \_____/                      \_____/
```



##   Controllers - Lightguns
There are two different types of PSX lightguns (which are incompatible with
each other).<br/>

#### Namco Lightgun (GunCon)
Namco's Cinch-based lightguns are extracting Vsync/Hsync timings from the video
signal (via a cinch adaptor) (so they are working completely independed of
software timings).<br/>
[Controllers - Lightguns - Namco (GunCon)](controllersandmemorycards.md#controllers-lightguns-namco-guncon)<br/>

#### Konami Lightgun (IRQ10)
Konami's IRQ10-based lightguns are using the lightgun input on the controller
slot (which requires IRQ10/timings being properly handled at software side).<br/>
[Controllers - Lightguns - Konami Justifier/Hyperblaster (IRQ10)](controllersandmemorycards.md#controllers-lightguns-konami-justifierhyperblaster-irq10)<br/>
The IRQ10-method is reportedly less accurate (although that may be just due to
bugs at software side).<br/>

#### Third-Party Lightguns
There are also a lot of unlicensed lightguns which are either IRQ10-based, or
Cinch-based, or do support both.<br/>
For example, the Blaze Scorpion supports both IRQ10 and Cinch, and it does
additionally have a rumble/vibration function; though unknown how that rumble
feature is accessed, and which games are supporting it).<br/>

#### Lightgun Games
[Controllers - Lightguns - PSX Lightgun Games](controllersandmemorycards.md#controllers-lightguns-psx-lightgun-games)<br/>

#### Compatibilty Notes (IRQ10 vs Cinch, PAL vs NTSC, Calibration)
Some lightguns are reportedly working only with PAL or only with NTSC games
(unknown which guns, and unknown what is causing problems; the IRQ10 method
should be quite hardware independed, the GunCon variant, too, although
theoretically, some GunCon guns might have problems to extract Vsync/Hsync from
either PAL or NTSC composite signals).<br/>
Lightguns from different manufacturers are reportedly returning slightly
different values, so it would be recommended to include a calibration function
in the game, using at least one calibration point (that would also resolve
different X/Y offsets caused by modifying GP1 display control registers).<br/>
Lightguns are needing to sense light from the cathode ray beam; as such they
won't work on regions of the screen that contain too dark/black graphics.<br/>



##   Controllers - Lightguns - Namco (GunCon)
#### GunCon Cinch-based Lightguns (Namco)
```
  __Halfword 0 (Controller Info)___________________
  0-15  Controller Info  (5A63h=Namco Lightgun; GunCon/Cinch Type)
  __Halfword 1 (Buttons)___________________________
  0-2   Not used              (All bits always 1)
  3     Button A (Left Side)  (0=Pressed, 1=Released) ;aka Joypad Start
  4-12  Not used              (All bits always 1)
  13    Trigger Button        (0=Pressed, 1=Released) ;aka Joypad O-Button
  14    Button B (Right Side) (0=Pressed, 1=Released) ;aka Joypad X-Button
  15    Not used              (All bits always 1)
  __Halfword 2 (X)_________________________________
  0-15  8MHz clks since HSYNC (01h=Error, or 04Dh..1CDh)
  __Halfword 3 (Y)_________________________________
  0-15  Scanlines since VSYNC (05h/0Ah=Error, PAL=20h..127h, NTSC=19h..F8h)
```
Caution: The gun should be read only shortly after begin of VBLANK.<br/>

#### Error/Busy Codes
Coordinates X=0001h, Y=0005h indicates "unexpected light":<br/>
```
  ERROR: Sensed light during VSYNC (eg. from a Bulb or Sunlight).
```
Coordinates X=0001h, Y=000Ah indicates "no light", this can mean either:<br/>
```
  ERROR: no light sensed at all (not aimed at screen, or screen too dark).
  BUSY: no light sensed yet (when trying to read gun during rendering).
```
To avoid the BUSY error, one should read the gun shortly after begin of VBLANK
(ie. AFTER rendering, but still BEFORE vsync). Doing that isn't as simple as
one might think:<br/>
On a NTSC console, time between VBLANK and VSYNC is around 30000 cpu clks,
reading the lightgun (or analog joypads) takes around 15000 cpu clks. So,
reading two controllers within that timeframe may be problematic (and reading
up to eight controllers via multitaps would be absolutely impossible). As a
workaround, one may arrange the read-order to read lightguns at VBLANK (and
joypads at later time). If more than one lightgun is connected, then one may
need to restrict reading to only one (or maybe: max two) guns per frame.<br/>

#### Minimum Brightness
Below are some average minimum brightness values, the gun may be unable to
return position data near/below that limits (especially coordinates close to
left screen border are most fragile). The exact limits may vary from gun to
gun, and will also depend on the TV Set's brightness setting.<br/>
```
  666666h Minimum Gray
  770000h Minimum Blue
  007700h Minimum Green
  000099h Minimum Red
```
The gun does also work with mixed colors (eg. white bold text on black
background works without errors, but the returned coordinates are a bit "jumpy"
in that case; returning the position of the closest white pixels).<br/>
BUG: On a plain RED screen, aiming at Y\>=00F0h, the gun is randomly
returning either Y, or Y-80h (that error occurs in about every 2nd frame, ie.
at 50% chance). It's strange... no idea what is causing that effect.<br/>

#### Coordinates
The coordinates are updated in all frames (as opposed to some lightguns which
do update them only when pulling the trigger).<br/>
The absolute min/max coordinates may vary from TV set to TV set (some may show
a few more pixels than others). The relation of the gun's Screen Coodinates to
VRAM Coordinates does (obviously) depend on where the VRAM is located on the
screen; ie. on the game's GP1(06h) and GP1(07h) settings.<br/>
Vertical coordinates are counted in scanlines (ie. equal to pixels). Horizontal
coordinates are counted in 8MHz units (which would equal a resolution of 385
pixels; which can be, for example, converted to 320 pixel resolution as
X=X\*320/385).<br/>

#### Misinformation (from bugged homebrew source code)
```
  __Halfword 2 (X)_________________________________
  0-7   X-Coordinate  (actual: see X-Offset)             ;\with unspecified
  8-15  X-Offset      (00h: X=X-80, Nonzero: X=X-80+220) ;/dotclock?
  __Halfword 3 (Y)_________________________________
  0-7   Y-Coordinate  (actual: Y=Y-25) (but then, max is only 230, not 263 ?)
  8-15  Pad ID        (uh, what id?) (reportedly too dark/bright error flag?)
```

#### Namco Lightgun Drawing
```
           _-_______________________--_
  ----->  |    namco            \\\\   \    Namco G-Con 45 (light gray) (cinch)
  sensor   |............ .. .....\\\\...|_
          |_ :          :..   _____      _\
            |  O        :__../  )))|    (
             \__________/  |_\____/|     \
               :               :   |      |
               :               :   |      |  NPC-103
         A-Button (Left)   Trigger |      |  SLPH-00034/SLEH-0007/SLUH-00035
         B-Button (Right)          |______|
```

#### See also
[Pinouts - Component List and Chipset Pin-Outs for Namco Lightgun, NPC-103](pinouts.md#pinouts-component-list-and-chipset-pin-outs-for-namco-lightgun-npc-103)<br/>



##   Controllers - Lightguns - Konami Justifier/Hyperblaster (IRQ10)
#### Overall IRQ10-Based Lightgun Access
```
  Send  01h 42h 00h x0h 00h
  Reply HiZ 31h 5Ah buttons
```
The purpose of the "x0h" byte is probably to enable IRQ10 (00h=off, 10h=on),
this would allow to access more than one lightgun (with only one per frame
having the IRQ enabled).<br/>

#### Standard IRQ10-based Lightguns (Konami)
The Controller Data simply consists of the ID and buttons states:<br/>
```
  __Halfword 0 (Controller Info)___________________
  0-15  Controller Info  (5A31h=Konami Lightgun; Timer/IRQ10 type)
  __Halfword 1 (Buttons)
  0-2   Not used                 (All bits always 1)
  3     Start Button (Left Side) (0=Pressed, 1=Released)  ;aka Joypad Start
  4-13  Not used                 (All bits always 1)
  14    Back Button  (Rear End)  (0=Pressed, 1=Released)  ;aka Joypad X-Button
  15    Trigger Button           (0=Pressed, 1=Released)  ;aka Joypad []-Button
```
The coordinates aren't part of the controller data, instead they must be read
from Timer 0 and 1 upon receiving IRQ10 (see IRQ10 Notes below).<br/>

#### Konami Lightgun Drawing
```
     __                 ______ _
   _|__\_______________/  ___ \ \   Konami Justifier/Hyperblaster (light green)
  |   _______________ __ /   \ \ \
  |__|   _ _ _ _     |==|    O| \O\ .... Back Button (Rear End)
     |__:_:_:_:_:__  |___\__ /  ( (
                   |_|  ) \  :   \ \
      Trigger ......  \___/| :...|.|.... Start Button (Left Side)
                           |     | |
                           |     | | SLPH-00013/SLPH-00014/SLEH-0005/SLUH-00017
                          /     _|_|
                          \___--
```

#### Konami IRQ10 Notes
The PSX does have a lightgun input (Pin 8 of the controller), but, Sony did
apparently "forget" to latch the current cathode ray beam coordinates by
hardware when sensing the lightgun signal (quite strange, since that'd be a
simple, inexpensive, and very obvious feature for a gaming console).<br/>
Instead, the lightgun signal triggers IRQ10, and the interrupt handler is
intended to "latch" the coordinates by software (by reading Timer 0 and 1
values, which must configured to be synchronized with the GPU).<br/>
That method requires IRQ handling to be properly implemented in software
(basically, IRQs should not be disabled for longer periods, and DMA transfers
should not block the bus for longer periods). In practice, most programmers
probably don't realize how to do that, to the worst, Sony seems to have
delivered a slightly bugged library (libgun) to developers.<br/>
For details on Timers, see:<br/>
[Timers](timers.md)<br/>
In some consoles, IRQ10 seems to be routed through a Secondary IRQ Controller,
see:<br/>
[EXP2 DTL-H2000 I/O Ports](expansionportpio.md#exp2-dtl-h2000-io-ports)<br/>

#### IRQ10 Priority
For processing IRQ10 as soon as possible, it should be assigned higher priority
than all other IRQs (ie. when using the SysEnqIntRP BIOS function, it should be
the first/newest element in priority chain 0). The libgun stuff assigns an even
higher priority by patching the BIOS exception handler, causing IRQ10 to be
processed shortly before processing the priority chains (the resulting IRQ
priority isn't actually higher as when using 1st element of chain 0; the main
difference is that it skips some time consuming code which pushes registers
R4..R30). For details on that patch, see:<br/>
[BIOS Patches](kernelbios.md#bios-patches)<br/>
Even if IRQ10 has highest priority, execution of (older) other IRQs may cause a
new IRQ10 to be executed delayed (because IRQs are disabled during IRQ
handling), to avoid that problem: Best don't enable any other IRQs except IRQ0
and IRQ10, or, if you need other IRQs, best have them enabled only during
Vblank (there are no scanlines drawn during vblank, so IRQ10 should never
trigger during that period). DMAs might also slow down IRQ execution, so best
use them only during Vblank, too.<br/>

#### IRQ10 Timer Reading
To read the current timer values the IRQ10 handler would be required to be
called \<immediately\> after receiving the IRQ10 signal, which is more or
less impossible; if the main program is trying to read a mul/div/gte result
while the mul/div/gte operation is still busy may stop the CPU for some dozens
of clock cycles, and active DMA transfers or cache hits and misses in the IRQ
handler may cause different timings, moreover, timings may become completely
different if IRQs are disabled (eg. while another IRQ is processed).<br/>
However, IRQ10 does also get triggered in the next some scanlines, so the first
IRQ10 is used only as a notification that the CPU should watch out for further
IRQ10's. Ie. the IRQ10 handler should disable all DMAs, acknowledge IRQ10, and
then enter a waitloop that waits for the IRQ10 bit in I\_STAT to become set
again (or abort if a timeout occurs) and then read the timers, reportedly like
so:<br/>
```
  IF NTSC then X=(Timer0-140)*0.198166, Y=Timer1
  IF PAL  then X=(Timer0-140)*0.196358, Y=Timer1
```
No idea why PAL/NTSC should use different factors, that factors are looking
quite silly/bugged, theoretically, the pixel-to-clock ratio should be the
exactly same for PAL and NTSC...?<br/>
Mind that reading Timer values in Dotclock/Hblank mode is unstable, for Timer1
this can be fixed by the read-retry method, for Timer0 this could be done too,
but one would need to subtract the retry-time to get a correct coordinate;
alternately Timer0 can run at system clock (which doesn't require read-retry),
but it must be then converted to video clock (mul 11, div 7), and then from
video clock to dot clock (eg. div 8 for 320-pixel mode).<br/>
Above can be repeated for the next some scanlines (allowing to take the medium
values as result, and/or to eliminate faulty values which are much bigger or
smaller than the other values). Once when you have collected enough values,
disable IRQ10, so it won't trigger on further scanlines within the current
frame.<br/>

#### IRQ10 Bugs
BUG: The "libgun" library doesn't acknowledge the old IRQ10 \<immediately\>
before waiting for a new IRQ10, so the timer values after sensing the new IRQ10
are somewhat random (especially for the first processed scanline) (the library
allows to read further IRQ10's in further scanlines, which return more stable
results).<br/>
No idea how many times IRQ10 gets typically repeated? Sporting Clays allocates
a buffer for up to 20 scanlines (which would cause pretty much of a slowdown
since the CPU is just waiting during that period) (nethertheless, the game uses
only the first timer values, ie. the bugged libgun-random values).<br/>

Unknown if/how two-player games (with 2 lightguns) are working with the IRQ10
method... if IRQ10 is generated ONLY after pressing the trigger button, then it
may work, unless both players have Trigger pressed at the same time... and,
maybe one can enable/disable the lightguns by whatever commmand being sent to
the controller (presumably that "x0h" byte, see above), so that gun 1 generates
IRQ10 only in each second frame, and gun 2 only in each other frame...?<br/>



##   Controllers - Lightguns - PSX Lightgun Games
#### PSX Lightgun Games
Some games are working only with IRQ10 or only with Cinch, some games support
both methods:<br/>
```
  Area 51 (Mesa Logic/Midway) (IRQ10)
  Crypt Killer (Konami) (IRQ10)
  Die Hard Trilogy 1: (Probe Entertainment) (IRQ10)
  Die Hard Trilogy 2: Viva Las Vegas (n-Space) (IRQ10/Cinch)
  Elemental Gearbolt (Working Designs) (IRQ10/Cinch)
  Extreme Ghostbusters: Ultimate Invasion (LSP) (Cinch)
  Galaxian 3 (Cinch)
  Ghoul Panic (Namco) (Cinch)
  Gunfighter: The Legend of Jesse James (Rebellion) (Cinch)
  Judge Dredd (Gremlin) (Cinch)
  Lethal Enforcers 1-2 (Konami) (IRQ10)
  Maximum Force (Midway) (IRQ10/Cinch)
  Mighty Hits Special (Altron) (EU/JPN) (Cinch)
  Moorhuhn series (Phenomedia) (Cinch)
  Point Blank 1-3 (Namco) (Cinch)
  Project Horned Owl (Sony) (IRQ10)
  Rescue Shot (Namco) (Cinch)
  Resident Evil: Gun Survivor (Capcom) (JPN/PAL versions) (Cinch)
  Silent Hill (IRQ10) ("used for an easter egg")
  Simple 1500 Series Vol.024 - The Gun Shooting (unknown type)
  Simple 1500 Series Vol.063 - The Gun Shooting 2 (unknown type)
  Snatcher (IRQ10)
  Sporting Clays (Charles Doty) (homebrew with buggy source code) (IRQ10/Cinch)
  Star Wars Rebel Assault II (IRQ10)
  Time Crisis, and Time Crisis 2: Project Titan (Namco) (Cinch)
```
Note: The RPG game Dragon Quest Monsters does also contain IRQ10 lightgun code
(though unknown if/when/where the game does use that code).<br/>




