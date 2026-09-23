---
name: controllers-special
description: "PSX controllers advanced: configuration commands (enter/exit config mode), vibration/rumble, DualShock2 analog buttons, special controllers (dance mat, fishing, keyboard, DVD remote). Use when working with controller configuration, rumble, or special input devices."
---

##   Controllers - Configuration Commands
Some controllers can be switched from Normal Mode to Config Mode. The Config
Mode was invented for activating the 2nd rumble motor in SCPH-1200 analog
joypads. Additionally, the Config commands can switch between analog/digital
inputs (without needing to manually press the Analog button), activate more
analog inputs (on Dualshock2), and read some type/status bytes.<br/>

#### Normal Mode
```
  42h "B" Read Buttons (and analog inputs when in analog mode)
  43h "C" Enter/Exit Configuration Mode (stay normal, or enter)
```
Transfer length in Normal Mode is 5 bytes (Digital mode), or 9 bytes (Analog
mode), or up to 21 bytes (Dualshock2).<br/>

#### Configuration Mode
```
  40h "@" Unused, or Dualshock2: Get/Set ButtonAttr?
  41h "A" Unused, or Dualshock2: Get Reply Capabilities
  42h "B" Read Buttons AND analog inputs (even when in digital mode)
  43h "C" Enter/Exit Configuration Mode (stay config, or exit)
  44h "D" Set LED State (analog mode on/off)
  45h "E" Get LED State (and Type/constants)
  46h "F" Get Variable Response A (depending on incoming bit)
  47h "G" Get whatever values (response HiZ F3h 5Ah 00h 00h 02h 00h 01h 00h)
  48h "H" Unknown (response HiZ F3h 5Ah 00h 00h 00h 00h 01h 00h)
  49h "I" Unused
  4Ah "J" Unused
  4Bh "K" Unused
  4Ch "L" Get Variable Response B (depending on incoming bit)
  4Dh "M" Get/Set RumbleProtocol
  4Eh "N" Unused
  4Fh "O" Unused, or Dualshock2: Set ReplyProtocol
```
Transfer length in Config Mode is always 9 bytes.<br/>

#### Normal Mode - Command 42h "B" - Read Buttons (and analog inputs when enabled)
```
  Send  01h 42h 00h xx  yy  (00h 00h 00h 00h) (...)
  Reply HiZ id  5Ah buttons ( analog-inputs ) (dualshock2 buttons...)
```
The normal read command, see Standard Controller chapter for details on buttons
and analog inputs. The xx/yy bytes have effect only if rumble is unlocked; use
Command 43h to enter config mode, and Command 4Dh to unlock rumble. Command 4Dh
has billions of combinations, among others allowing to unlock only one of the
two motors, and to exchange the xx/yy bytes, however, with the default values,
xx/yy are assigned like so:<br/>
```
  yy.bit0-7 ---> Left/Large Motor M1 (analog slow/fast) (00h=stop, FFh=fastest)
  xx.bit0   ---> Right/small Motor M2 (digital on/off)  (0=off, 1=on)
```
The Left/Large motor starts spinning at circa min=50h..60h, and, once when
started keeps spinning downto circa min=38h. The exact motor start boundary
depends on the current position of the weight (if it's at the "falling" side,
then gravity helps starting), and also depends on external movements (eg. it
helps if the user or the other rumble motor is shaking the controller), and may
also vary from controller to controller, and may also depend on the room
temperature, dirty or worn-out mechanics, etc.<br/>

#### Normal Mode - Command 43h "C" - Enter/Exit Configuration Mode
```
  Send  01h 43h 00h xx  00h (zero padded...)   (...)
  Reply HiZ id  5Ah buttons (analog inputs...) (dualshock2 buttons...)
```
When issuing command 43h from inside normal mode, the response is same as for
command 42h (button data) (and analog inputs when in analog mode) (but without
M1 and M2 parameters). While in config mode, the ID bytes are always "F3h 5Ah"
(instead of the normal analog/digital ID bytes).<br/>
```
  xx=00h Stay in Normal mode
  xx=01h Enter Configuration mode
```
Caution: Additionally to activating configuration commands, entering config
mode does also activate a Watchdog Timer which does reset the controller if
there's been no communication for about 1 second or so. The watchdog timer
remains active even when returning to normal mode via Exit Config command. The
reset does disable and lock rumble motors, and switches the controller to
Digital Mode (with LED=off, and analog inputs disabled). To prevent this, be
sure to keep issuing joypad reads even when not needing user input (eg. while
loading data from CDROM).<br/>
Caution 2: A similar reset occurs when the user pushes the Analog button; this
is causing rumble motors to be stopped and locked, and of course, the
analog/digital state gets changed.<br/>
Caution 3: If config commands were used, and the user does then push the analog
button, then the 5Ah-byte gets replaced by 00h (ie. responses change from "HiZ
id 5Ah ..." to "HiZ id 00h ...").<br/>

#### Config Mode - Command 42h "B" - Read Buttons AND analog inputs
```
  Send  01h 42h 00h M2  M1  00h 00h 00h 00h
  Reply HiZ F3h 5Ah buttons  analog-inputs
```
Same as command 42h in normal mode, but with forced analog response (ie. analog
inputs and L3/R3 buttons are returned even in Digital Mode with LED=Off).<br/>

#### Config Mode - Command 43h "C" - Enter/Exit Configuration Mode
```
  Send  01h 43h 00h xx  00h 00h 00h 00h 00h
  Reply HiZ F3h 5Ah 00h 00h 00h 00h 00h 00h
```
Equivalent to command 43h in normal mode, but returning 00h bytes rather than
button data, can be used to return to normal mode.<br/>
```
  xx=00h Enter Normal mode (Exit Configuration mode)
  xx=01h Stay in Configuration mode
```
Back in normal mode, the rumble motors (if they were enabled) can be controlled
with normal command 42h.<br/>

#### Config Mode - Command 44h "D" - Set LED State (analog mode on/off)
```
  Send  01h 44h 00h Led Key 00h 00h 00h 00h
  Reply HiZ F3h 5Ah 00h 00h Err 00h 00h 00h
```
The Led byte can be:<br/>
```
  When Led=00h      --> Digital mode, with LED=Off
  When Led=01h      --> Analog mode, with LED=On/red
  When Led=02h..FFh --> Ignored (and, in case of dualshock2: set Err=FFh)
```
The Key byte can be:<br/>
```
  When Key=00h..02h --> Unlock (allow user to push Analog button)
  When Key=03h      --> Lock (stay in current mode, ignore Analog button)
  When Key=04h..FFh --> Acts same as (Key AND 03h)
```
The Err byte is usually 00h (except, Dualshock2 sets Err=FFh upon Led=02h..FFh;
older PSX/PSone controllers don't do that).<br/>

#### Config Mode - Command 45h "E" - Get LED State (and Type/constants)
```
  Send  01h 45h 00h 00h 00h 00h 00h 00h 00h
  Reply HiZ F3h 5Ah Typ 02h Led 02h 01h 00h
```
Returns two interesting bytes:<br/>
```
  Led: Current LED State (00h=Off, 01h=On/red)
  Typ: Controller Type (01h=PSX/Analog Pad, 03h=PS2/Dualshock2)
```
The other bytes might indicate the number of rumble motors, analog sticks, or
version information, or so.<br/>

#### Config Mode - Command 46h "F" - Get Variable Response A
```
  Send  01h 46h 00h ii  00h 00h 00h 00h 00h
  Reply Hiz F3h 5Ah 00h 00h cc  dd  ee  ff
```
When ii=00h --\> returns cc,dd,ee,ff = 01h,02h,00h,0ah<br/>
When ii=01h --\> returns cc,dd,ee,ff = 01h,01h,01h,14h<br/>
Otherwise --\> returns cc,dd,ee,ff = all zeroes<br/>
Note: This is called PadInfoAct in official docs, ii is the actuator (aka
motor) and the last response byte contains its current drain (10 or 20 units).
Whereas, Sony inisits that controllers should never exceed 60 units (eg. when
having more than 2 joypads connected to multitaps).<br/>

#### Config Mode - Command 47h "G" - Get whatever values
```
  Send  01h 47h 00h 00h 00h 00h 00h 00h 00h
  Reply HiZ F3h 5Ah 00h 00h 02h 00h 01h 00h
```
Purpose unknown.<br/>

#### Config Mode - Command 4Ch "L" - Get Variable Response B
```
  Send  01h 4Ch 00h ii  00h 00h 00h 00h 00h
  Reply Hiz F3h 5Ah 00h 00h 00h dd  00h 00h
```
When ii=00h --\> returns dd=04h.<br/>
When ii=01h --\> returns dd=07h.<br/>
Otherwise --\> returns dd=00h.<br/>

#### Config Mode - Command 48h "H" - Unknown (response HiZ F3h 5Ah 4x00h 01h 00h)
```
  Send  01h 48h 00h ii  00h 00h 00h 00h 00h
  Reply HiZ F3h 5Ah 00h 00h 00h 00h ee  00h
```
When ii=00h..01h --\> returns ee=01h.<br/>
Otherwise --\> returns ee=00h.<br/>
Purpose unknown. The command does not seem to be used by any games.<br/>

#### Config Mode - Command 4Dh "M" - Get/Set RumbleProtocol
[Controllers - Vibration/Rumble Control](#controllers---vibrationrumble-control)<br/>

#### Config Mode - Command 40h "@" Dualshock2: Get/Set ButtonAttr?
#### Config Mode - Command 41h "A" Dualshock2: Get Reply Capabilities
#### Config Mode - Command 4Fh "O" Dualshock2: Set ReplyProtocol
[Controllers - Analog Buttons (Dualshock2)](#controllers---analog-buttons-dualshock2)<br/>

#### Config Mode - Command 49h "I" - Unused
#### Config Mode - Command 4Ah "J" - Unused
#### Config Mode - Command 4Bh "K" - Unused
#### Config Mode - Command 4Eh "N" - Unused
#### Config Mode - Command 40h "@" - Unused (except, used by Dualshock2)
#### Config Mode - Command 41h "A" - Unused (except, used by Dualshock2)
#### Config Mode - Command 4Fh "O" - Unused (except, used by Dualshock2)
```
  Send  01h 4xh 00h 00h 00h 00h 00h 00h 00h
  Reply HiZ F3h 5Ah 00h 00h 00h 00h 00h 00h
```
These commands do return a bunch of 00h bytes. These commands do not seem to be
used by any games (apart from the Dualshock2 commands being used by Dualshock2
games).<br/>

#### Note
Something called "Guitar Hero controller" does reportedly also support Config
commands. Unknown if that thing does have the same inputs & rumble motors
as normal analog PSX joypads, and if it does return special type values.<br/>



##   Controllers - Vibration/Rumble Control
Rumble (aka "Vibration Function") is basically controlled by two previously
unused bytes of the standard controller Read command.<br/>
There are two methods to control the rumble motors, the old method is very
simple (but supports only one motor), the new method envolves a bunch of new
configuration commands (and supports two motors).<br/>
```
  SCPH-1150  DualAnalog Pad with 1 motor                  ;-old rumble method
  SCPH-1200  DualAnalog Pad with 2 motors, PSX-design     ;\new rumble method
  SCPH-110   DualAnalog Pad with 2 motors, PSone-design   ;/
  SCPH-10010 DualAnalog Pad with 2 motors, PS2/Dualshock2 ;-plus analog buttons
  Blaze Scorpion Lightgun with rumble      ;\unknow how to control rumble
  Fishing controllers with rumble          ;/
  SCPH-1180 Analog Pad without rumble      ;\unknow if there're config commands
  SCPH-1110 Analog Stick without rumble    ;/for analog mode (probably not)
```

#### Old Method, one motor, no config commands (SCPH-1150, SCPH-1200, SCPH-110)
The SCPH-1150 doesn't support any special config commands, instead, rumble is
solely done via the normal joypad read command:<br/>
```
  Send  01h 42h 00h xx  yy  (00h 00h 00h 00h)
  Reply HiZ id  5Ah buttons ( analog-inputs )
```
The rumble motor is simply controlled by three bits in the xx/yy bytes:<br/>
```
  xx --> must be 40h..7Fh            (ie. bit7=0, bit6=1) ;\switches motor on
  yy --> must be 01h,03h,...,FDh,FFh (ie. bit0=1)         ;/
```
The motor control is digital on/off (no analog slow/fast), recommended values
would be yyxx=0140h=on, and yyxx=0000h=off.<br/>
LED state is don't care (rumble works with led OFF, RED, and GREEN). In absence
of config commands, the LED can be controlled only manually (via Analog
button), the current LED state is implied in the controller "id" byte.<br/>
For backwards compatibility, the above old method does also work on SCPH-1200
and SCPH-110 (for controlling the right/small motor), alternately those newer
pads can use the config commands (for gaining access to both motors).<br/>

#### New Method, two motors, with config commands (SCPH-1200, SCPH-110)
For using the new rumble method, one must unlock the new rumble mode, for that
purpose Sony has invented a "slightly" overcomplicated protocol with not less
than 16 new commands (the rumble relevant commands are 43h and 4Dh, also,
command 44h may be useful for activating analog inputs by software, and, once
when rumble is unlocked, command 42h is used to control the rumble motors).
Anyways, here's the full command set...<br/>
[Controllers - Configuration Commands](#controllers---configuration-commands)<br/>
And, the rumble-specific config command is described below...<br/>

#### Config Mode - Command 4Dh "M" - Get/Set RumbleProtocol
```
  Send  01h 4Dh 00h aa  bb  cc  dd  ee  ff     ;<-- set NEW aa..ff values
  Reply Hiz F3h 5Ah aa  bb  cc  dd  ee  ff     ;<-- returns OLD aa..ff values
```
Bytes aa,bb,cc,dd,ee,ff control the meaning of the 4th,5th,6th,7th,8th,9th
command byte in the controller read command (Command 42h).<br/>
```
  00h      = Map Right/small Motor (Motor M2) to bit0 of this byte
  01h      = Map Left/Large Motor (Motor M1) to bit0-7 of this byte
  02h..FEh = Unknown (can be mapped, maybe for extra motors/outputs)
  FFh      = Map nothing to this byte
```
In practice, one would usually send either one of these command/values:<br/>
```
  Send  01h 4Dh 00h 00h 01h FFh FFh FFh FFh    ;enable new method (two motors)
  Send  01h 4Dh 00h FFh FFh FFh FFh FFh FFh    ;disable motor control
```
Alternately, one could swap the motors by swapping values in aa/bb. Or one
could map the motors anywhere to cc/dd/ee/ff (this will increase the command
length in digital mode, hence changing digital mode ID from 41h to 42h or 43h).
Or, one could map further rumble motors or other outputs to the six bytes (if
any such controller would exist).<br/>
In the initial state, aa..ff are all FFh, and the controller does then use the
old rumble control method (with only one motor). However, that old method gets
disabled once when having messed with config commands (unknown if/how one can
re-enable the old method by software).<br/>

#### Unknown Dualshock2 Vibration
Dualshock2 does reportedly have "two more levels of vibration", unknown what
that means and if it's used by any PSX or PS2 games... it might refer to the
small motor which usually has only 2 levels (on/off) and might have 4 levels
(fast/med/slow/off) on dualshock2... but, if so, it's unknown how to
control/unlock that feature.<br/>
Also, the PSone controller (SCPH-110) appear to have been released shortly
after Dualshock2, unknown if that means that it might have that feature, too.<br/>

#### Note
Rumble is a potentially annoying feature, so games that do support rumble
should also include an option to disable it.<br/>



##   Controllers - Analog Buttons (Dualshock2)
Dualshock2 has three new commands (40h,41h,4Fh) for configuring analog buttons.
Additionally, Command 45h does return a different type byte for Dualshock2.<br/>
Dualshock2 is a PS2 controller. However, it can be also used with PSX games
(either by connecting the controller to a PSX console, or by playing a PSX game
on a PS2 console).<br/>
The analog button feature is reportedly rarely used by PS2 games (and there
aren't any PSX games known to use it).<br/>

#### Config Mode - Command 40h "@" Dualshock2: Get/Set ButtonAttr?
```
  Send  01h 40h 00h Idx Val 00h 00h 00h 00h  ;<-- Set NEW Val, array[Idx]=Val
  Reply HiZ F3h 5Ah 00h 00h Val 00h 00h 00h  ;<-- Old Val (or FFh when Idx>0Bh)
```
Allows to change twelve 3bit values (with Idx=00h..0Bh, and Val=00h..03h).
Default is Val=02h. Purpose is unknown, the 12 values might be related to the
12 analog buttons, but there is no noticable difference between Val=0,1,2,3.
Maybe it does have some subtle effects on things like...<br/>
```
  Digital button sensitivity, or Analog button sensitivity, or
  Analog button bit-depth/conversion speed, or something else?
```

#### Config Mode - Command 41h "A" Dualshock2: Get Reply Capabilities
```
  Send  01h 41h 00h 00h 00h 00h 00h 00h 00h
  Reply HiZ F3h 5Ah FFh FFh 03h 00h 00h 00h
```
This seems to return a constant bitmask indicating which reply bytes can be
enabled/disabled via Command 4Fh (ie. 3FFFFh = 18 bits).<br/>

#### Config Mode - Command 4Fh "O" Dualshock2: Set ReplyProtocol
```
  Send  01h 41h 00h aa  bb  cc  dd  ee  ff
  Reply HiZ F3h 5Ah 00h 00h 00h 00h 00h 00h
```
This can output some 48bit value (bit0=aa.bit0, bit47=ff.bit7), used to
enable/disable Reply bytes in the controller read command (Command 42h).<br/>
```
  -      HighZ                   (always transferred)      1st byte
  -      ID/Mode/Len             (always transferred)      2nd byte
  -      5Ah                     (always transferred)      3rd byte
  0      LSB of digital buttons  (0=No, 1=Yes)             4th byte
  1      MSB of digital buttons  (0=No, 1=Yes)             5th byte
  2      RightJoyX               (0=No, 1=Yes)             6th byte
  3      RightJoyY               (0=No, 1=Yes)             7th byte
  4      LeftJoyX                (0=No, 1=Yes)             8th byte
  5      LeftJoyY                (0=No, 1=Yes)             9th byte
  6      DPAD Right              (0=No, 1=Yes) button 00h  10th byte
  7      DPAD Left               (0=No, 1=Yes) button 01h  11th byte
  8      DPAD Up                 (0=No, 1=Yes) button 02h  12th byte
  9      DPAD Down               (0=No, 1=Yes) button 03h  13th byte
  10     Button /\               (0=No, 1=Yes) button 04h  14th byte
  11     Button ()               (0=No, 1=Yes) button 05h  15th byte
  12     Button ><               (0=No, 1=Yes) button 06h  16th byte
  13     Button []               (0=No, 1=Yes) button 07h  17th byte
  14     Button L1               (0=No, 1=Yes) button 08h  18th byte
  15     Button R1               (0=No, 1=Yes) button 09h  19th byte
  16     Button L2               (0=No, 1=Yes) button 0Ah  20th byte
  17     Button R2               (0=No, 1=Yes) button 0Bh  21st byte
  18-39  Must be 0 (otherwise command is ignored)
  40-47  Unknown (no effect?)
```
Usually, one would use one of the following command/values:<br/>
```
  Send  01h 41h 00h 03h 00h 00h 00h 00h 00h  Digital buttons
  Send  01h 41h 00h 3Fh 00h 00h 00h 00h 00h  Digital buttons + analog sticks
  Send  01h 41h 00h FFh FFh 03h 00h 00h 00h  Enable all 18 input bytes
```
The transfer order is 1st..21st byte as shown above (unless some bits are
cleared, eg. if bit0-5=0 and bit6=1 then DPAD Right would appear as 4th byte
instead of 10th byte). The command length increases/decreases depening on the
number of enabled bits. The transfer length is always 3+N\*2 bytes (including a
00h padding byte when the number of enabled bits is odd). The analog mode ID
byte changes depending on number of halfwords.<br/>
CAUTION: Sending Command 44h does RESET the Command 4Fh setting (either to
DigitalMode=000003h or AnalogMode=00003Fh; same happens when toggling mode via
Analog button).<br/>

Note: Some Dualshock2 Config Mode commands do occassionally send 00h, 5Ah, or
FFh as last (9th) reply byte (unknown if that is some error/status thing, or
garbage).<br/>

#### Analog Button Sensitivity
The pressure sensors are rather imprecise and results may vary on various
factors, including the pressure angle.<br/>
```
  00h       Button released
  01h..2Fh  Normal (soft) pressure
  30h..FEh  Medium pressure
  FFh       Hard pressure
```
Software can safely distinguish between soft and hard pressure.<br/>
Medium pressure is less predictably: The values do not increase linearily, it's
difficult to apply a specific amount of medium pressure (such like 80h..9Fh),
increasing pressure may sometimes jump from 24h to FFh, completely skipping the
medium range.<br/>
Relying on the medium range might work for accelleration buttons (where the
user could still adjust the pressure when the accelleration is too high or too
low); but it would be very bad practice to assign irreversible actions to
medium pressure (such like Soft=Load, Medium=Save, Hard=Quit).<br/>

#### Digital Button Sensitivity
Digital inputs are converting the analog inputs as so:<br/>
```
  Analog=00h      --> not pressed
  Analog=01h..FFh --> pressed (no matter if soft, medium, or hard pressure)
```
Digital inputs are working even when also having analog input enabled for the
same button.<br/>

#### See also
[https://gist.github.com/scanlime/5042071] - tech (=mentions unknown details)
[https://store.curiousinventor.com/guides/PS2/] - guide (=omits unknown stuff)



##   Controllers - Dance Mats
PSX Dance Mats are essentially normal joypads with uncommonly arranged buttons,
the huge mats are meant to be put on the floor, so the user could step on them.<br/>

#### Dance Mat vs Joypad Compatibility
There are some differences to normal joypads: First of, the L1/L2/R1/R2
shoulder buttons are missing in most variants. And, the mats are allowing to
push Left+Right and Up+Down at once, combinations that aren't mechanically
possible on normal joypads (some dancing games do actually require those
combinations, whilst some joypad games may get confused on them).<br/>

#### Dance Mat Unknown Things
Unknown if the mat was sold in japan, and if so, with which SLPH/SCPH number.<br/>
Unknown if the mat's middle field is also having a button assigned.<br/>
Unknown if the mat is having a special controller ID, or if there are other
ways to detect mats (the mats are said to be compatible with skateboard games,
so the mats are probably identifying themselves as normal digital joypad;
assuming that those skateboard games haven't been specifically designed for
mats).<br/>

#### Dance Mat Games
```
  D.D.R. Dance Dance Revolution 2nd Remix
  (and maybe whatever further games)
```
The mats can be reportedly also used with whatever skateboard games.<br/>

#### Dance Mat Variants
There is the US version (DDR Dance Pad, SLUH-00071), and a slightly different
European version (Official Dance Mat, SLEH-00023: shiny latex style with
perverted colors, and Start/Select arranged differently). The japanese version
(RU017) resembles the US version, but without Triangle/Square symbols drawn in
lower left/right edges.<br/>
And there is a handheld version (with additional L1/L2/R2/R1 buttons; maybe
unlicensed; produced as MINI DDR, and also as Venom Mini Dance Pad).<br/>

```
   US Version (white/black/red/blue)         Handheld Version (blue/gray)
    __________.---------.___________          _____/ MINI  \_____
   |          \         /           |        |      D.D.R.       |
   |  SELECT   '-------'    START   |        |L1 L2 SEL STA R2 R1|
   |------------.------.------------|        | ___    ___    ___ |
   |  .''''.   /        \   .''''.  |        || X |  | ^ |  | O ||
   | |  \/  | |    /\    | | .''. | |        ||___|  |___|  |___||
   | |  /\  | |   /..\   | | '..' | |        | ___   .---.   ___ |
   |  '....'  '.   ||   .'  '....'  |        || < | |Stay | | > ||
   | .-------. .''''''''. .-------. |        ||___| |Cool!| |___||
   |/   /|   .'          '.   |\   \|        | ___   '___'   ___ |
   |   / |-- |            | --| \   |        || []|  | v |  | /\||
   |   \ |-- | Stay Cool! | --| /   |        ||___|  |___|  |___||
   |\   \|   '.          .'   |/   /|        |___________________|
   | '-------' '........' '-------' |
   |  .''''.  .'   ||   '.  .''''.  |        Gothic Dance Mat (black/silver)
   | |  /\  | |   \''/   | | |''| | |         _.----------._
   | | /__\ | |    \/    | | |..| | |        | \ SEL  STA / | This one
   |  '....'   \        /   '....'  |        |  '--------'  | wasn't ever
   '------------'------'------------'        | .----------. | produced,
                                             | |  .''''.  | | as cool as
   European Version (pink/blue/yellow)       | | |  /\  | | | it could have
    __________.---------.___________         | | | /..\ | | | been, the lame
   |          \ SEL STA /           |        | |  '.||.'  | | marketing
   |           '-------'            |        | +----------+ | people didn't
   |----------.----------.----------|        | |  .''''.  | | even think
   |  .''''.  |  .''''.  |  .''''.  |        | | |  /\  | | | about it.
   | |  \/  | | |  /\  | | | .''. | |        | | | /..\ | | |
   | |  /\  | | | /..\ | | | '..' | |        | |  '.||.'  | |
   |  '....'  |  '.||.'  |  '....'  |        | +----------+ |
   |----------+-..    ..-+----------|        | |  .'||'.  | |
   |  .'/|'.  /   ''''   \  .'|\'.  |        | | | \''/ | | |
   | | / |--|/            \|--| \ | |        | | |  \/  | | |
   | | \ |--|\            /|--| / | |        | |  '....'  | |
   |  '.\|.'  \   ....   /  '.|/.'  |        | +----------+ |
   |----------+-''    ''-+----------|        | |  .'||'.  | |
   |  .''''.  |  .'||'.  |  .''''.  |        | | | \''/ | | |
   | |  /\  | | | \''/ | | | |''| | |        | | |  \/  | | |
   | | /__\ | | |  \/  | | | |..| | |        | |  '....'  | |
   |  '....'  |  '....'  |  '....'  |        | '----------' '
   '----------|----------|----------'        '--------------'
```

#### Stay Cool?
Despite of the "Stay Cool!" slogan, the mat wasn't very cool - not at all! It
offered only two steps back-and-forth, and also allowed to do extremly uncool
side-steps. Not to mention that it would melt when dropping a burning cigarette
on it. Stay Away!<br/>



## Controllers - Pop'n Controllers
Controllers used for Konami's Pop'n Music series. At least a few different
versions of the controller (Pop'n Controller, Pop'n Controller 2, larger
arcade-size version, possibly others and in different color variations) have
been released for the PS1 and PS2. Unknown if the controllers released in the
PS2 era have any additional commands not present in the original Pop'n
Controller, but they are supposedly fully compatible with PS1 Pop'n Music games.

Pop'n Controllers report as digital controllers (ID byte 41h), but the left,
right, and down d-pad controls are not connected to any physical buttons and are
always reported as pressed (in the first transferred button byte, bits 5-7 are
always 0). Pop'n Music games check these bits to determine if a Pop'n Controller
is connected and will change the in-game controls accordingly if so.



## Controllers - Taiko Controllers (Tatacon)
Drum controllers made by Namco and used by the Taiko no Tatsujin series on the
PS2 (but compatible with the PS1, even though no PS1 Taiko game was ever made).
These controllers behave like standard digital pads (ID 41h) and contain four
hit sensors mapped to the following buttons:<br/>

| Sensor             | Button     | Bit |
| :----------------- | :--------- | --: |
| Left ka (rim)      | L1         |  10 |
| Right ka (rim)     | R1         |  11 |
| Left don (center)  | D-pad left |   7 |
| Right don (center) | Circle     |  13 |

Dedicated start and select buttons are also present. Unlike Pop'n Controllers,
no additional buttons are hardcoded to be always pressed.<br/>



## Controllers - Densha de Go! / Jet de Go! Controllers
Controllers used for Taito's Densha de Go! and Jet de Go! series. Unknown what
method is being used by Densha de Go! and Jet de Go! games for detecting these
controllers.

- The workings of Densha de Go! PSX controllers have been extensively researched
  in the [ddgo-controller-docs](https://github.com/MarcRiera/ddgo-controller-docs)
  repo.
- The Jet de Go! PSX controller comes in gray and black color. It seems to work
  the same as an analog controller and supports vibration. The steering wheel is
  mapped to the left stick (wheel rotation as horizontal, wheel raise/lower as
  vertical axis). The thrust throttle seems mapped to the right stick Y-axis
  full range (so half throttle matches vertically centered right stick).



##   Controllers - Fishing Controllers
The fishing rods are (next to lightguns) some of the more openly martial
playstation controllers - using the credo that "as long as you aren't using
dynamite: it's okay to kill them cause they don't have any feelings."<br/>

#### PSX Fishing Controller Games
```
  Action Bass (Syscom Entertainment) (1999) (SLPH-00100)
  Bass Landing (ASCII/agetec) (1999) (SLPH-00100, SLUH-00063)
  Bass Rise, Fishing Freaks (Bandai) (1999) (BANC-0001)
  Bass Rise Plus, Fishing Freaks (Bandai) (2000) (BANC-0001, SLPH-00100)
  Breath of Fire IV (Capcom) (SLUH-00063)
  Championship Bass (EA Sports) (2000) (SLUH-00063)
  Fish On! Bass (Pony Canyon) (1999) (BANC-0001, SLPH-00100)
  Fisherman's Bait 2/Exiting Bass2 - Big Ol'Bass(Konami)(SLPH-00100,SLUH-00063)
  Fishing Club: (series with 3 titles) (have "headset-logo" on back?)
  Lake Masters II (1999) (Dazz/Nexus) (SLPH-00100)
  Lake Masters Pro (1999) (Dazz/Nexus) (BANC-0001, SLPH-00100)
  Let's Go Bassfishing!: Bass Tsuri ni Ikou! (Banpresto) (1999) (SLPH-00100)
  Matsukata Hiroki no World Fishing (BPS The Choice) (1999) (SLPH-00100)
  Murakoshi Seikai-Bakuchou Nihon Rettou (Victor) (SLPH-00100)
  Murakoshi Masami-Bakuchou Nippon Rettou:TsuriConEdition (1999) (SLPH-00100)
  Pakuchikou Seabass Fishing (JP, 03/25/99) (Victor) (SLPH-00100)
  Perfect Fishing: Bass Fishing (2000) (Seta) (yellow/green logo)
  Perfect Fishing: Rock Fishing (2000) (Seta) (yellow/green logo)
  Oyaji no Jikan: Nechan, Tsuri Iku De! (2000) (Visit) (BANC-0001, SLPH-00100)
  Reel Fishing II / Fish Eyes II (2000)(Natsume/Victor)(SLPH-00100, SLUH-00063)
  Simple 1500 Series Vol. 29: The Tsuri (2000) (yellow/green logo)
  Suizokukan Project: Fish Hunter e no Michi (1999)(Teichiku)(SLPH-00100)
  Super Bass Fishing (1999) (King) (BANC-0001, SLPH-00100, yellow/green logo)
  Super Black Bass X2 (2000) (Starfish) (SLPH-00100)
  Tsuwadou Keiryuu Mizuumihen (Best Edition)(2000) (ASCII PS1+PS2 controllers?)
  Tsuwadou Seabass Fishing (PlayStation the Best) (1999) (Oz Club) (SLPH-00100)
  Uki Uki Tsuri Tengoku Nagami/Uokami Densetsu Oe (2000) (Teichiku)(SLPH-00100)
  Umi no Nushi Tsuri-Takarajima ni Mukatte (1999)(Victor)(BANC-0001,SLPH-00100)
  Winning Lure (Hori) (2000) (for Hori HPS-97 controller)  AKA HPS-98 ?
```

#### Logos on CD Covers
US Fishing games should have a "SLUH-00063" logo. European Fishing games don't
have any fishing logos; apparently fishing controllers haven't been officially
released/supported in Europe.<br/>
Japanese Fishing games can have a bunch of logos: Usually BANC-0001 or
SLPH-00100 (or both).<br/>
Moreover, some japanese games have a yellow/green fishing logo with japanese
text (found on Perfect Fishing: Bass Fishing, Perfect Fishing: Rock Fishing,
Simple 1500 Series Vol. 29: The Tsuri, Super Bass Fishing) (unknown if that
logo refer to other special hardware, or if it means the "normal" BANC-0001 or
SLPH-00100 controllers.<br/>
And Moreover, some japanese games have some sort of "headset" logos with
japanese text, these seem to have same meaning as SLPH-00100; as indicated by
photos on CD cover of Tsuwadou Keiryuu Mizuumihen (Best Edition) (2000); that
CD cover also has a "headset 2" logo, which seems to mean a newer PS2 variant
of the SLPH-00100.<br/>

#### PSX Fishing Controllers
```
  ASCII Tsuricon SLPH-00100 (also marked with a second serial, ASC-0514TR, on the packaging box)
  ASCII Tsuricon 2 ASC-0521TR2 (has a mode switch with 3 settings. "1" is original Tsuricon mode, "2" is Tsuricon 2 mode. Unknown what the unnumbered mode does)
  Sammy Tsuricon 2 SMY-0506FS (looks to be identical to the ASCII Tsuricon 2)
  Sammy Tsuricon 2+ SMY-0511FS (unknown what the differences between this and the Tsuricon 2 are)
  Agetec Bass Landing Fishing Controller SLUH-00063 (US version of ASCII's SLPH-00100 controller)
  Bandai Fishing Controller BANC-0001 (dark gray/blue) (has less buttons than ASCII/agetec)
  Interact Fission (light gray/blue)(similar to ASCII/agetec, 2 extra buttons?)
  Naki (transparent blue) (looks like a clone of the ASCII/agetec controllers)
  Hori HPS-97/HPS-98 (black/gray) (a fishing rod attached to a plastic fish)
```
Of these, the ASCII/agetec controllers seem to be most popular (and most
commonly supported). The Bandai contoller is also supported by a couple of
games (though the Bandai controller itself seems to be quite rare). The
Interact/Naki controllers are probably just clones of the ASCII/agetec ones.
The Hori controller is quite rare (and with its string and plastic fish, it's
apparently working completely different than the other fishing controllers).<br/>

#### Tech Info (all unknown)
Unknown how to detect fishing controllers.<br/>
Unknown how to read buttons, joystick, crank, motion sensors.<br/>
Unknown how to control rumble/vibration.<br/>
Unknown if/how Bandai differs from ASCII/agetec (aside from less buttons).<br/>
Unknown how the Hori thing works.<br/>

#### ASCII SLPH-00100 / agetec SLUH-00063 (silver)
```
          ___
       __|___|__
     _|         |_     _   __
    | |         | |   | |=|__| <--- crank handle
    | | SEL STA | |   | |
    | |         | |---|  \                         ASCII SLPH-00100
    |  \       /  |---|  /                         agetec SLUH-00063
   /  L1       R1  \  | |  __
  |  L2  .---.  R2  | |_|=|__|
  |     | joy |     |
  |     |stick|     |  <------- analog thumb controlled joystick
  | /\   '---'   >< |
  |   []       ()   |
   \     ASCII     /
    '.___________.'   \___ 10 buttons (SEL,STA,L1,L2,R1,R2,/\,[],(),><)
       \ _____ /
        |     |           Note: many (not all) agetec controllers
        |     |           have the >< and () buttons exchanged
        |     |
        |     |              Aside from the crank/buttons/joystick,
        |     |              the controller reportedly contains:
        |     |              some sort of motion sensors?
        |     |              some kind of rumble/vibration?
        |     |
        '.___.'
           '--...___ cable
```

#### Bandai BANC-0001 (dark gray/blue)
```
          ___
       __|___|__
     _|         |      _   __
    | .---.     |\    | |=|__| <--- crank handle
    || joy |    | |   | |
    ||stick|    | |-#-|  \
    | '---'     | |-#-|  /
   / \          |  \  | |  __
  |   |   ...   |   | |_|=|__|
  |   |  :   :  | ()|
  |   |O :___: O|   |   <--- two buttons: () and ><
  |   |- |___| -| ><|        and some slide switch with I and 0 positions?
  |   |         |   |
   \  |  BANDAI |  /      unknown if the joystick is digital or analog
    '._\_______/_.'
       |       |          unknown if there are motion sensors and/or rumble
       '.     .'
        |     |
        |     |
        |     |
        |     |
        |     |
        |     |
        |     |
        '.___.'
           '--...___ cable
```

#### Hori HPS-97 / HPS-98 (black/gray)
```
              ....----------------O
           .''                     \  HPS-97 (controller bundled with game)
          _:_        \              \ HPS-98 (controller only, for HPS-96 game)
       __|___|__      \ short        \
     _|         |_      elastic       \
    |             |     pole           \
    |             |                     \    <--- string (from pole to
    |     SW?     |     _   __           \        reel inside of fish)
   /               \   | |=|__|           \
  |      .---.      |  | |                 \
  | ( ) | joy |     |--|  \                 \               ___
  |     |stick|     |--|  /                  \             /   /
  | ( )  '---'      |  | |  __                \     ...---''''''--.  /|
  |                 |  |_|=|__| <--- crank     \   '               '/ |
   \    ( ) ( )    /                 handle     '..|                  |.
    '.___________.'                                |__________________| :
       \       /     \                                plastic fish      :
        |     |       joystick,                  (presumable some heavy :
        |     |       four buttons,              stationary thing that  :
        |     |       and a switch?              rests on floor)        :
        |     |                                  (presumably with       :
        |     |                                  motor-driven reel?)    :
        |     |                                                         :
        |     |     the two cables do probably connect                  :
        |     |     to both of the PSX controller slots                 :
        '.___.'                                            cable 2  ---'
           '--...___ cable 1
```

##   Controllers - PS2 DVD Remote
An accessory released by Sony for the PS2, consisting of an infrared remote
control and a receiver dongle that plugs into a controller port. The remote
features all standard controller buttons (including L3/R3) as well as additional
controls for the PS2's DVD player.<br/>
The receiver behaves very differently from any other known device: it does not
respond to any command until a button on the remote is pressed. When a valid IR
code is received it will start accepting commands for about 2000-2500 ms, then
become unresponsive again. It will initially behave as two different devices,
one with address 01h acting like a standard digital controller and the other
with address 61h exposing IR codes as received from the remote.<br/>

#### Command 04h - IR poll (and disable controller mode)
```
  Send Reply Comment
  61h  N/A   IR receiver address
  04h  12h   Receive ID bits 0-7, send command byte
  00h  5Ah   Receive ID bits 8-15
  00h  len   Receive code length (20 for DVD remote, 0 if no button is pressed)
  00h  code  Receive code bits 16-23
  00h  code  Receive code bits 8-15
  00h  code  Receive code bits 0-7
```
Returns the IR code of the currently pressed button and its length in bits, or
000000h if no button is pressed (and the receiver is still responding to
commands). Received codes seem to "stick around" for some time even after the
button has been released; when a button is held down the remote resends its code
every 45 ms, so the receiver presumably keeps returning the same code for about
50 ms as a debouncing measure.<br/>
The code is returned LSB first and MSB aligned, i.e. it should be right-shifted
by (24 - len) bits to obtain the "raw" code as sent by the remote. For
instance:<br/>
```
  Code sent by remote (first bit after preamble to last bit):
    0000 0000 1011 1001 0010
  Code sent by remote (MSB to LSB):
    0100 1001 1101 0000 0000
  Data returned by receiver:
    code[16:23] = 01001001
    code[8:15]  = 11010000
    code[0:7]   = 0000xxxx ; xxxx = (24 - len) bits of padding (all zeroes)
  Reassembled MSB-aligned code (MSB to LSB):
    0100 1001 1101 0000 0000 xxxx
```
The receiver will stop acting like a digital controller and replying to address
01h after this command is sent for the first time. Command 06h can be used to
restore controller functionality (see below), unknown if there is also a
watchdog to automatically restore controller mode if no IR poll commands are
issued.<br/>

#### Command 06h, 03h - Re-enable controller mode
```
  Send Reply Comment
  61h  N/A   IR receiver address
  06h  12h   Receive ID bits 0-7, send command byte 1
  03h  5Ah   Receive ID bits 8-15, send command byte 2
  00h  ?     Receive unknown data, send padding
  00h  ?
  00h  ?
  00h  ?
```

#### Command 0Fh - Unknown
This command exists (the receiver will keep pulling /ACK low) but its purpose is
currently unknown. It could possibly be an alternate poll command that does not
disable controller mode.<br/>

#### IR code format
The DVD remote always emits 20-bit IR codes. The receiver does return the length
of the code, but it's unclear if it can receive codes with lengths other than 20
bits.<br/>
All non-controller buttons on the remote are arranged in an 8x16 button matrix,
shown below (transposed for readability):<br/>

| Col | Row 0  | Row 1    | Row 2  | Row 3    | Row 4 | Row 5   | Row 6    | Row 7 |
| --: | :----- | :------- | :----- | :------- | :---- | :------ | :------- | :---- |
|   0 | 1      |          |        | Previous |       |         | Slow <<  |       |
|   1 | 2      |          |        | Next     |       |         | Slow >>  |       |
|   2 | 3      |          |        | Play     |       |         |          |       |
|   3 | 4      |          |        | Scan <<  |       |         | Subtitle |       |
|   4 | 5      |          |        | Scan >>  |       | Display | Audio    |       |
|   5 | 6      |          |        | Shuffle  |       |         | Angle    |       |
|   6 | 7      |          |        |          |       |         |          |       |
|   7 | 8      |          |        |          |       |         |          |       |
|   8 | 9      |          | Time   | Stop     |       |         |          |       |
|   9 | 0      |          |        | Pause    |       |         |          | Up    |
|  10 |        | Title    | A<->B  |          |       |         |          | Down  |
|  11 | Enter  | DVD Menu |        |          |       |         |          | Left  |
|  12 |        |          | Repeat |          |       |         |          | Right |
|  13 |        |          |        |          |       |         |          |       |
|  14 | Return |          |        |          |       |         |          |       |
|  15 | Clear  | Program  |        |          |       |         |          |       |

Each button in the matrix is assigned a code as follows:<br/>
```
  code = 49D00h OR (row << 4) OR (column) ; sent LSB first

  ; where row = 0..7, column = 0..15
```
Controller buttons are handled separately and assigned different codes:<br/>
```
  code = DAD50h OR (id) ; sent LSB first

  ; where id = 0..15, index of the bit that would normally represent the button
  ; in the bitfield returned by a controller poll command
  ; (i.e. 0=Select, 1=L3, 2=R3, 3=Start, 4=Up, 5=Right, etc.)
```
Arrow buttons are a special case, as they are controller buttons but also have
matrix codes assigned. For those the remote alternates between both codes (see
below).<br/>

#### Low-level IR protocol
The remote emits IR pulses modulated with a 38 kHz carrier, as most remotes do.
Codes are sent as a 2460 µs "preamble" pulse followed by 24 data pulses, each of
which can be either 1250 µs (if the respective bit is 1) or 650 µs (if the
respective bit is 0) long. After each pulse including the preamble, the remote
waits 530 µs before sending the next pulse.<br/>
Every code is always sent at least 3 times in a row (more if the button is held
down but not necessarily a multiple of 3), approximately every 45 ms. For arrow
buttons the matrix code is sent 3 times first, then the respective controller
button code is sent 3 times, then the sequence repeats until the button is
released (with the total number of codes sent always being a multiple of 6 in
this case).<br/>

#### Built-in IR receivers
In later PS2 models, Sony integrated the IR receiver into the console. Assuming
the built-in receivers used the same circuitry as the external dongle, this may
explain its weird behavior: the receiver was likely designed to be wired in
parallel with one of the controller ports, and to be unresponsive until the
remote is actually in use to avoid interfering with another controller plugged
into the same port. Whether or not the integrated receivers are connected this
way has not been confirmed.<br/>
There is a second revision of the DVD remote with power and eject buttons, meant
to be used with the PS2 models that have a built-in receiver. Weirdly enough,
however, it seems to be incompatible with the older receiver dongle.<br/>

##   Controllers - I-Mode Adaptor (Mobile Internet)
The I-Mode Adaptor cable (SCPH-10180) allows to connect an I-mode compatible
mobile phone to the playstation's controller port; granting a mobile internet
connection to japanese games.<br/>

#### PSX Games for I-Mode Adaptor (Japan only)
```
  Doko Demo Issyo (PlayStation the Best release only) (Sony) 2000
  Doko Demo Issyo Deluxe Pack (Bomber eXpress/Sony) 2001
  Hamster Club-I (SLPS-03266) (Jorudan) 2002
  iMode mo Issyo: Dokodemo Issho Tsuika Disc (Bomber/Sony) 2001
  Keitai Eddy (iPC) 2000 (but, phone connects to SIO port on REAR side of PSX?)
  Komocchi (Victor) 2001
  Mobile Tomodachi (Hamster) 2002
  Motto Trump Shiyouyo! i-Mode de Grand Prix (Pure Sound) 2002
  One Piece Mansion (Capcom) 2001 (japanese version only)
```
The supported games should have a I-Mode adaptor logo on the CD cover (the logo
depicts two plugs: the PSX controller plug, and the smaller I-Mode plug).<br/>
Note: "Dragon Quest Monsters 1 & 2" was announced/rumoured to support
I-mode (however, its CD cover doesn't show any I-Mode adapter logo).<br/>

#### Tech Details (all unknown)
Unknown how to detect the thing, and how to do the actual data transfers.<br/>
The cable does contain a 64pin chip, an oscillator, and some smaller components
(inside of the PSX controller port connector).<br/>

#### Hardware Variant
Keitai Eddy seems to have the phone connect to the SIO port (on rear side of
the PSX, at least it's depicted like so on the CD cover). This is apparently
something different than the SCPH-10180 controller-port cable. Unknown what it
is exactly - probably some mobile internet connection too, maybe also using
I-mode, or maybe some other protocol.<br/>



##   Controllers - Keyboards
There isn't any official retail keyboard for PSX, however, there is a shitload
of obscure ways to connect keyboards...<br/>

#### Sony SCPH-2000 PS/2 Keyboard/Mouse Adaptor (prototype/with cable) (undated)
#### Sony SCPH-2000 PS/2 Keyboard/Mouse Adaptor (without cable) (undated)
A PS/2 to PSX controller port adaptor. Maybe for educational Lightspan titles?<br/>
There are two hardware variants of the adaptor:<br/>
```
  Adaptor with short cable to PSX-controller port (and prototype marking)
  Adaptor without cable, directly plugged into controller port (final version?)
```
Unknown ^how to access those adaptors, and unknown if the two versions differ
at software side. There seem to be not much more than a handful of people
owning that adaptors, and none of them seems to know how to use it, or even how
to test if it's working with existing software...<br/>
- Keyboard reading might work with the Online Connection CD.<br/>
- Mouse reading might work with normal mouse compatible PSX games.<br/>

#### Lightspan Online Connection CD Keyboard (1997)
The Online Connection CD is a web browser from the educational Lightspan
series, the CD is extremly rare (there's only one known copy of the disc).<br/>
The thing requires a dial-up modem connected to the serial port (maybe simply
using the same RS232 adaptor as used by Yaroze). User input can be done via
joypad, or optionally, via some external keyboard (or keyboard adaptor)
hardware:<br/>
```
  Send  01h 42h 00h 00h 00h 00h 00h 00h 00h 00h 00h 00h 00h 00h 06h
  Reply HiZ 96h 5Ah num dat dat dat dat dat dat dat dat dat dat dat
```
The num byte indicates number of following scancodes (can be num=FFh, maybe
when no keyboard connected?, or num=00h..0Bh for max 11 bytes, unless the last
some bytes should have other meaning, like status/mouse data or so).<br/>
The keyboard scancodes are in "PS/2 Keyboard Scan Code Set 2" format.<br/>
The binary contains some (unused) code for sending data to the keyboard by
changing the 4th-11th byte, and resuming normal operation by setting 4th and
11th byte back to zero:<br/>
```
  Send  ..  ..  ..  01h xxh FFh FFh FFh FFh FFh 00h ..  ..  ..  ..
  Send  ..  ..  ..  00h ..  ..  ..  ..  ..  ..  00h ..  ..  ..  ..
```
Maybe 4th and 11th byte are number of following bytes, with xxh being some
command, and FFh's just being bogus padding; the xxh looks more like an
incrementing value though.<br/>
Despite of the mouse-based GUI, the browser software doesn't seem to support
mouse hardware (neither via PS/2 mice, nor PSX mice). Instead, the mouse arrow
can be merely moved via joypad's DPAD, or (in a very clumsy fashion) via
keyboard cursor keys.<br/>
Note: The browser uses SysEnqIntRP to install some weird IRQ handler that
forcefully aborts all controller (or memory card) transfers upon Vblank.
Unknown if that's somehow required to bypass bugs in the keyboard hardware. The
feature is kinda dangerous for memory card access (especially with fast memcard
access in nocash kernel, which allows to transfer more than one sector per
frame).<br/>

#### Spectrum Emulator Keyboard Adaptor (v1/serial port) (undated)
Made by Anthony Ball. [http://www.sinistersoft.com/psxkeyboard]

```
  [1F801058h]=00CEh  ;SIO1_MR 8bit, no parity, 2 stop bits (8N2)
  [1F80105Ah]=771Ch  ;SIO1_CR rx enable (plus whatever nonsense bits)
  [1F80105Eh]=006Ch  ;SIO1_BR 19200 bps
  RX   Keyboard Scancode (same ASCII-style as in later versions?)
  CTS  Caps-Lock state
  DSR  Num-Lock state
```

#### Spectrum Emulator Keyboard & Sega Sticks Adaptor (v2/controller port) (2000)
Made by Anthony Ball. [http://www.sinistersoft.com/psxkeyboard]

This adaptor can send pad/stick data,<br/>
```
  Send  01h 42h 00h  0h 0h
  Reply HiZ 41h 5Ah  PadA
```
as well as pad/sticks+keyboard data,<br/>
```
  Send  01h 42h 00h  0h 0h 0h 0h 0h 0h 0h 0h  00h 00h   0h 0h 0h 0h 0h 0h
  Reply HiZ E8h 5Ah  PadA  PadB  PadC  PadD   Ver Lock  Buffer(0..5)
```
The above mode(s) can be switched via ACPI Power/Sleep/Wake keys (on keyboards
that do have such keys).<br/>
```
  Version=1     ; version number
  0  SCROLL          ; scroll lock on
  1  NUM             ; num lock on
  2  CAPS            ; caps lock on
  3  DONETEST        ; keyboard has just done a selftest
  4  EMUA            ; emulation mode a
  5  EMUB            ; emulation mode b
```
For whatever reason, the PS/2 scancodes are translated to ASCII-style scancode
values (with bit7=KeyUp flag):<br/>
```
  01   11 12 13 14  15 16 17 18  19 1A 1B 1C  1D 69 1F
  60 21 22 68 24 25 5E 26 2A 28 29 5F 3D  2D  0B 0E 0F  67 2F 1E 2D
  27  51 57 45 52 54 59 55 49 4F 50 5B 5D 0D  10 61 62  37 38 39
  3B   41 53 44 46 47 48 4A 4B 4C 3A 40 23              34 35 36 2B
  02 5C 5A 58 43 56 42 4E 4D 3C 3E 3F     03     63     31 32 33
  04 05 06           20          07 08 09 0A  65 64 66  30    2E 6A
```
BUG: The thing conflicts with memory cards: It responds to ANY byte with value
01h (it should do so only if the FIRST byte is 01h).<br/>

#### Homebrew PS/2 Keyboard/Mouse Adaptor (undated/from PSone era)
```
  Send  01h 42h 00h 00h 00h 00h 00h
  Reply HiZ 12h 5Ah key flg dx  dy
```
flg:<br/>
```
  bit0-1 = Always 11b (unlike Sony mouse)
  bit2 = Left Mouse Button  (0=Pressed, 1=Released)
  bit3 = Right Mouse Button (0=Pressed, 1=Released)
  bit4-5 = Always 11b (like Sony mouse)
  bit6 = Key Release  (aka F0h prefix) (0=Yes)
  bit7 = Key Extended (aka E0h prefix) (0=Yes)
```
Made by Simon Armstrong. This thing emulates a standard PSX Mouse (and should
thus work with most or all mouse compatible games). Additionally, it's sending
keyboard flags/scancodes via unused mouse button bits.<br/>

#### Runix hardware add-on USB Keyboard/Mouse Adaptor (2001) (PIO extension port)
Runix is a homebrew linux kernel for PSX, it can be considered being the holy
grail of the open source scene because nobody has successfully compiled it in
the past 16 years.<br/>
- USB host controller SL811H driver with keyboard and mouse support;<br/>
- RTC support.<br/>
file: drivers/usb/sl811h.c<br/>

#### TTY Console
The PSX kernel allows to output "printf" debug messages via stdout. In the
opposite direction, it's supporting to receive ASCII user input via
"std\_in\_gets" (there isn't any software actually using that feature though,
except maybe debug consoles like DTL-H2000).<br/>



##   Controllers - Additional Inputs
#### Reset Button
PSX only (not PSone). Reboots the PSX via /RESET signal. Probably including for
forcefully getting through the WHOLE BIOS Intro, making it rather
useless/annoying? No idea if it clears ALL memory during reboot?<br/>

#### CDROM Shell Open
Status bit of the CDROM controller. Can be used to sense if the shell is opened
(and also memorizes if the shell was opened since last check; allowing to sense
possible disk changes).<br/>

#### PocketStation
Memory Card with built-in LCD screen and Buttons (which can be used as
miniature handheld console). However, when it is connected to the PSX, the
buttons are vanishing in the cartridge slot, so the buttons cannot be used as
additional inputs for PSX games.<br/>

#### Serial Port PSX only (not PSone)
With an external adaptor (voltage conversion), the serial port can be used
(among others) to connect a RS232 Serial Mouse. Although, most or all
commercial games with mouse input are probably (?) supporting only Sony's Mouse
(on the controller port) (rather than standard RS232 devices on the serial
port).<br/>

#### TTY Debug Terminal
If present, the external DUART can be used for external keyboard input, at the
BIOS side, this is supported as "std\_in".<br/>



##   Controllers - Misc
#### Standard Controllers
```
  SCPH-1010  digital joypad (with short cable)
  SCPH-1080  digital joypad (with longer cable)
  SCPH-1030  mouse (with short cable)
  SCPH-1090  mouse (with longer cable)
  SCPH-1092  mouse (european?)
  SCPH-1110  analog joystick
  SCPH-1150  analog joypad (with one vibration motor, with red/green led)
  SCPH-1180  analog joypad (without vibration motors, with red/green led)
  SCPH-1200  analog joypad (with two vibration motors) (dualshock)
  SCPH-110   analog joypad (with two vibration motors) (dualshock for psone)
  SCPH-10010 dualshock2 (analog buttons, except L3/R3/Start/Select) (for ps2)
  SCPH-1070  multitap
```

#### Special Controllers
```
  SCPH-4010 VPick (guitar-pick controller) (for Quest for Fame, Stolen Song)
```
SLPH-0001 (nejicon)<br/>
BANDAI "BANC-0002" - 4 Buttons (Triangle, Circle, Cross, Square) (nothing more)<br/>

#### Joystick
```
     __________                     __________
    |          |                   |    ^     |     ^
    | L1    R1 |                   | X <+> O  |    <+> = Digital Stick
     \      ___| <--- L2   [] ---> |___ v    /      v
      |    |     <--- R2   /\ --->     |    |
   ___|    |___________________________|    |___   Not sure if all buttons
  |   |    | SEL STA              =?=  |    |   |  are shown at their
  |   |    |                           |    |   |  correct locations?
  |   |    |_         []   /\         _|    |   |    (drawing is based on
  |  _|     /    L1             R1    \     |_  |    below riddle/lyrics)
  |  \_____/          X     O          \_____/  |
  |   /___\      L2             R2      /___\   |
  |                                             |
  |                                             |
   \___________________________________________/
```

```
 The thumb buttons on the left act as L1 and R1,
    the trigger is L2, the pinky button is R2
 The thumb buttons on the right act as X and O,
    the trigger is Square and the pinky button is Triangle.
 I find this odd as the triggers should've been L1 and R1,
    the pinkies L2 and R2.
 The buttons are redundantly placed on the base as large buttons like what
    you'd see on a fight/arcade stick. Also with Start and Select.
 There is also a physical analog mode switch,
    not a button like on dual shock.
```

#### MX4SIO
The MX4SIO is a homebrew microSD card adapter for the PS2 that plugs into a
memory card slot, taking advantage of the fact that SD cards support an SPI mode
which is more or less compatible with SIO0. The adapter is completely passive
and has the card wired up as follows:<br/>

| uSD pin | Name         | Wired to MC pin |
| ------: | :----------- | :-------------- |
|       1 | `D2`/`NC`    | -               |
|       2 | `D3`/`/CS`   | `/CS`           |
|       3 | `CMD`/`MOSI` | `CMD`/`MOSI`    |
|       4 | `VCC`        | `+3.5V`         |
|       5 | `SCK`        | `SCK`           |
|       6 | `GND`        | `GND`, `/ACK`   |
|       7 | `D0`/`MISO`  | `DAT`/`MISO`    |
|       8 | `D1`/`NC`    | -               |

Unfortunately, this design has a fatal flaw that makes it unusable as-is on the
PS1: /ACK is permanently shorted to ground, taking down the entire controller
bus. However, it should be possible to use the MX4SIO on a PS1 with custom
driver code once the MX4SIO's /ACK pin is masked out with some tape, or if no
other controllers or memory cards are plugged in.<br/>
Note that, as SD cards do not employ the addressing scheme used by standard
controllers and memory cards, the MX4SIO should get its own dedicated /CSn pin
and not share the port with a controller (i.e. if the MX4SIO is plugged in slot
2, then controller port 2 shall be left unused).<br/>

