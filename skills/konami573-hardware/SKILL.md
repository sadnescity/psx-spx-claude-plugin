---
name: konami573-hardware
description: "Konami System 573 arcade hardware: differences from PS1, register map (flash ROM, RTC, ATAPI, DIP switches, watchdog), JVS interface, I/O board variants (analog, digital, fishing, gun, DDR). Use when working with System 573 arcade hardware."
---


# Konami System 573

The System 573 is a PlayStation-based system used in a number of Konami arcade
games from the late 90s and early 2000s, most notably Dance Dance Revolution and
other titles from the Bemani series of rhythm games.

- [Differences vs. PS1](#differences-vs-ps1)
- [Register map](#register-map)
- [JVS interface](#jvs-interface)
- [I/O boards](#io-boards)
- [Security cartridges](../konami573-security-io/SKILL.md#security-cartridges)
- [External modules](../konami573-security-io/SKILL.md#external-modules)
- [BIOS](../konami573-security-io/SKILL.md#bios)
- [Bootleg mod boards](../konami573-security-io/SKILL.md#bootleg-mod-boards)
- [Game-specific information](../konami573-security-io/SKILL.md#game-specific-information)
- [Notes](../konami573-security-io/SKILL.md#notes)
- [Pinouts](../konami573-security-io/SKILL.md#pinouts)
- [Credits, sources and links](../konami573-security-io/SKILL.md#credits-sources-and-links)

This document is currently work-in-progress. Here is an incomplete list of
things the authors believe need more research:

- The BIOS and games are notoriously picky about ATAPI drives due to Konami's
  libraries not always respecting timings and polling registers in the way
  suggested by the specifications. Such issues shall be documented more in
  detail.
- The `GE765-PWB(B)A` and `PWB0000073070` I/O boards have been fully and
  partially reverse engineered respectively, but documentation for them is
  missing.
- The `GN845-PWB(B)` DDR stage PCB's communication protocol is largely unknown.
  More tests need to be done on real hardware and its CPLD shall be dumped if
  possible.
- The protocol used by the 573 to communicate with the `PWB0000100991` network
  PCB has been reversed, however very little about the PCB's own hardware and
  software stack is otherwise known.
- Some revisions of the main board have two resistor footprints next to the
  Konami ASIC, one labeled `FJ` and the other `SH`. Only one of them is
  populated; it presumably sets or clears a bit in one of the ASIC input ports.
  Given the labels it may be related to the manufacturer of the onboard flash
  memory (Fujitsu or Sharp), however even boards fitted with Sharp chips come
  with the `FJ` resistor populated. Moreover, all known games identify the chips
  by probing their JEDEC ID.

## Differences vs. PS1

### Main changes

- **Main RAM is 4 MB** instead of 2 MB and **VRAM is 2 MB** instead of 1 MB. SPU
  RAM is still 512 KB.
- **The CD-ROM drive is completely different**. While the PS1's drive is fully
  integrated into the motherboard and uses a custom protocol, the 573 employs a
  standard ATAPI drive. It can thus boot from burned CD-Rs or even CD-RWs just
  fine (as long as the drive itself is capable of reading them in the first
  place), with no modifications needed to the stock hardware. There is no
  provision for playing XA-ADPCM, however CD-DA playback through the drive's own
  audio output (fed into the 573 motherboard via a 4-pin audio cable) is
  supported and used by some games.
- **The SIO0 bus for controllers and memory cards is unused**. It is broken out
  to a connector, however no known I/O board uses it. Some games supported PS1
  controllers and memory cards through an adapter connected over JVS (see the
  external modules section).
- **The "parallel I/O" expansion port is replaced by 2 PCMCIA slots**. These
  slots are wired in parallel and mapped at the same address as the internal
  flash through bank switching. They are fairly limited though as they only
  support 16-bit bus accesses (i.e. `/CE1` and `/CE2` are tied together, even
  though the CPU actually exposes them as separate signals!), have no DMA and
  don't expose the PCMCIA I/O and configuration space (`/IORD` and `/IOWR` are
  not connected at all). This makes them incompatible with CF cards and most
  PCMCIA devices.

### Additional hardware

- **Audio and video outputs**: unlike the PS1, which outputs composite, S-video
  and RGB, the 573 only outputs RGB with C-sync through the JAMMA connector and
  a DB15 port compliant with the JVS specification (same pinout as VGA but not
  directly compatible, as VGA normally runs at higher resolutions and uses
  separate H/V sync pins). A built-in 15 watt stereo speaker amplifier is also
  provided for cabinets that lack their own sound system.
- **JAMMA interface and built-in I/O ports**: the 573 provides multiple digital
  and analog ports for interfacing with arcade cabinet controls. Depending on
  the I/O board the system came with, these signals might be broken out through
  connectors on the system's case.
- **Internal 16 MB flash memory**: the 573's BIOS is capable of booting either
  from the CD drive or from an array of flash memory chips soldered to the
  motherboard, which are also memory mapped. Most Konami games are designed to
  run from flash: when attempting to run them from CD without also having them
  installed, the executable on the disc will erase the flash and install the
  game before starting. Most games still require the CD, in some cases a
  different one, to be kept in the drive after installation as they use it for
  music playback or to stream additional data.
- **PCMCIA memory card**: some games shipped with additional flash memory in the
  form of one or more 16 or 32 MB PCMCIA cards. Note that these are "linear"
  memory mapped flash cards without any built-in controller, not CF or
  ATA-compatible cards. See the BIOS section for more details on why CF cards
  are not supported.
- **RTC and battery-backed 8 KB RAM**: used by games to store settings, save
  data and installation info (possibly including serial numbers). Unfortunately
  the RTC chip is one of those all-in-one things with a battery sealed inside,
  soldered directly to the motherboard.
- **JVS host**: allows connection of multiple daisy chained peripherals using
  the standardized JVS protocol, based on a serial (RS-485) bus. The JVS port on
  the 573 was only ever "officially" used for the PS1 memory card reader module,
  however some games seem to support JVS I/O boards and input devices in
  addition to the built-in JAMMA connector.
- **Security cartridge**: optionally installed on the 573's side, contains a
  password protected EEPROM that holds factory pre-programmed data as well as
  keys generated during game installation, plus in some case a 64-bit serial
  number ROM. Security cartridges were bundled with most game discs as a way to
  prevent copying, as the discs themselves had no other protection of any kind.
  The CPU's serial port (SIO1) is also wired to the security cartridge slot.

## Register map

All standard PS1 registers, with the exception of the CD-ROM drive's, are
present and accessible. System 573-specific hardware is mapped into the DEV0
region at `0x1f000000`. IRQ10 and DMA5, normally reserved for the expansion bus
(and lightguns) on a regular PS1, are used to access the ATAPI drive, while IRQ2
and DMA3 go unused.

**NOTE**: DEV0 must be configured prior to accessing any of these registers. The
configuration value written by Konami's code to the DEV0 delay/size register at
`0x1f801008` is `0x24173f47`. Afterwards, *all* bus writes shall be 16 or 32
bits wide. The behavior of 8-bit writes is undefined, but 8-bit reads work as
intended.

| Address range           | Description                                            |
| :---------------------- | :----------------------------------------------------- |
| `0x1f000000-0x1f3fffff` | Bank switched, can be mapped to flash or PCMCIA slots  |
| `0x1f400000-0x1f40000f` | [Konami ASIC registers](#konami-asic-registers)        |
| `0x1f480000-0x1f48000f` | [IDE register bank 0](#ide-registers)                  |
| `0x1f4c0000-0x1f4c000f` | [IDE register bank 1](#ide-registers)                  |
| `0x1f620000-0x1f623fff` | [RTC registers](#rtc-registers) and battery-backed RAM |
| `0x1f640000-0x1f6400ff` | [I/O board registers](#io-boards)                      |
| `0x1f500000-0x1f6a0001` | [Other registers](#other-registers)                    |

### Konami ASIC registers

Registers in the `0x1f400000-0x1f40000f` region are handled by the Konami 056879
I/O ASIC, consisting of a single 8-bit output port and at least six 16-bit input
ports. The same chip was used in other Konami arcade boards of the time.

#### `0x1f400000` (ASIC register 0): **ADC** / **Coin counters** / **Audio control**

| Bits | RW | Description                                   |
| ---: | :- | :-------------------------------------------- |
|    0 | W  | Data input to ADC (`DI`)                      |
|    1 | W  | Chip select to ADC (`/CS`)                    |
|    2 | W  | Data clock to ADC (`CLK`)                     |
|    3 | W  | Coin counter 1 (1 = energize counter coil)    |
|    4 | W  | Coin counter 2 (1 = energize counter coil)    |
|    5 | W  | Built-in audio amplifier enable (0 = muted)   |
|    6 | W  | External audio input enable (0 = muted)       |
|    7 | W  | SPU DAC output enable (0 = muted)             |
|    8 | W  | JVS MCU reset output (0 = pull reset low)     |
| 9-15 |    | _Unused_                                      |

The ADC chip is an ADC0834 from TI, which uses a proprietary SPI-like protocol.
Its four inputs are wired to the `ANALOG` connector on the 573 motherboard.
Refer to the ADC083x datasheet for details on how to bitbang the protocol.

Mechanical coin counters are incremented by games whenever a coin is inserted by
setting bit 3 or 4 for a fraction of a second and then clearing them. Bit 5
controls whether the onboard audio amp is enabled but does not affect the RCA
line level outputs, which are always enabled. Setting bit 5 has no effect
immediately as the amplifier takes about a second to turn on.

Bit 6 is used by games to mute audio from the CD-ROM drive or digital I/O board.
However, testing on real hardware seems to suggest it is actually some sort of
attenuation control, as the audio is still audible (albeit at a very low volume)
when the bit is cleared. Note that some games, such as GuitarFreaks, break the
CD/MP3 output to separate jacks on the front I/O panel rather than routing it
through the motherboard, making bit 6 meaningless.

Bit 8 resets the JVS MCU. Since the reset pin is active-low, resetting is done
by writing 0, waiting at least 10 H8 clock cycles (the BIOS waits 2 hblanks)
and writing 1 again. Resetting the MCU will clear `JVSDRDY` but not `JVSIRDY`.
As the 056879 ASIC's output register is only 8 bits wide, bit 8 is actually
handled by a discrete flip-flop on the motherboard.

Unknown what reading from this port does.

#### `0x1f400004` (ASIC register 2): **DIP switches** / **JVS status** / **Security cartridge**

| Bits  | RW | Description                             |
| ----: | :- | :-------------------------------------- |
|   0-3 | R  | DIP switch 1-4 status (0 = on, 1 = off) |
|   4-5 | R  | Current JVS MCU status code             |
|   6-7 | R  | Current JVS MCU error code              |
|  8-15 | R  | `I0-I7` from security cartridge         |

The MCU status code can be one of the following values:

| Code | Description                                                     |
| ---: | :-------------------------------------------------------------- |
|    0 | Waiting for the 573 to read or write the first word of a packet |
|    1 | Busy (sending a packet or waiting for a response)               |
|    2 | Waiting for the 573 to finish reading or writing a packet       |
|    3 | _Unused_                                                        |

The MCU error code can be one of the following values:

| Code | Description                                                      |
| ---: | :--------------------------------------------------------------- |
|    0 | _Unused_                                                         |
|    1 | Packet written by the 573 has an invalid checksum                |
|    2 | Packet written by the 573 does not start with a `0xe0` sync byte |
|    3 | No error                                                         |

Once an error is reported, the MCU will enter an endless loop and become
unresponsive. In order to clear the error the MCU must be reset using bit 8 in
register `0x1f400000`.

The highest 8 bits read from this register are the current state of the security
cartridge's `I0-I7` pins. See the security cartridge section for an explanation
of what each bit is wired to. Unknown whether reading from this register will
clear the `IRDY` flag, if previously set by the cartridge.

Bit 3 (DIP switch 4) is used by the BIOS to determine whether to boot from
flash. If set, the BIOS will attempt to search for a valid executable on the
internal flash and both PCMCIA cards prior to falling back to the CD-ROM.

#### `0x1f400006` (ASIC register 3): **Misc. inputs**

| Bits  | RW | Description                                   |
| ----: | :- | :-------------------------------------------- |
|     0 | R  | Data output from ADC (`DO`)                   |
|     1 | R  | SAR status from ADC (`SARS`)                  |
|     2 | R  | From `IO0` on security cartridge              |
|     3 | R  | Sense input from JVS port                     |
|     4 | R  | `JVSIRDY` status from JVS MCU                 |
|     5 | R  | `JVSDRDY` status from JVS MCU                 |
|     6 | R  | `IRDY` status from security cartridge         |
|     7 | R  | `DRDY` status from security cartridge         |
|     8 | R  | Coin switch input 1 (0 = coin being inserted) |
|     9 | R  | Coin switch input 2 (0 = coin being inserted) |
|    10 | R  | PCMCIA card 1 insertion (0 = card present)    |
|    11 | R  | PCMCIA card 2 insertion (0 = card present)    |
|    12 | R  | Service button (JAMMA pin R, 0 = pressed)     |
| 13-15 |    | Unused?                                       |

See the security cartridge section for more details about `IRDY` and  `DRDY`. In
order for bit 2 to be valid, `IO0` should be set as an input by clearing the
respective bit in register `0x1f500000`.

#### `0x1f400008` (ASIC register 4): **JAMMA controls**

| Bits | RW | Description                            |
| ---: | :- | :------------------------------------- |
|    0 | R  | Player 2 joystick left (JAMMA pin X)   |
|    1 | R  | Player 2 joystick right (JAMMA pin Y)  |
|    2 | R  | Player 2 joystick up (JAMMA pin V)     |
|    3 | R  | Player 2 joystick down (JAMMA pin W)   |
|    4 | R  | Player 2 button 1 (JAMMA pin Z)        |
|    5 | R  | Player 2 button 2 (JAMMA pin a)        |
|    6 | R  | Player 2 button 3 (JAMMA pin b)        |
|    7 | R  | Player 2 start button (JAMMA pin U)    |
|    8 | R  | Player 1 joystick left (JAMMA pin 20)  |
|    9 | R  | Player 1 joystick right (JAMMA pin 21) |
|   10 | R  | Player 1 joystick up (JAMMA pin 18)    |
|   11 | R  | Player 1 joystick down (JAMMA pin 19)  |
|   12 | R  | Player 1 button 1 (JAMMA pin 22)       |
|   13 | R  | Player 1 button 2 (JAMMA pin 23)       |
|   14 | R  | Player 1 button 3 (JAMMA pin 24)       |
|   15 | R  | Player 1 start button (JAMMA pin 17)   |

As buttons are active-low (wired between JAMMA pins and ground), all bits are 0
when a button is pressed and 1 otherwise. The BIOS and games often read from
this register and discard the result as a way of (inefficiently) flush the CPU's
write queue.

#### `0x1f40000a` (ASIC register 5): **Data from JVS MCU**

| Bits | RW | Description                |
| ---: | :- | :------------------------- |
| 0-15 | R  | Current data word from MCU |

This register is only valid when the `JVSIRDY` flag is set. After reading, a
dummy write to `0x1f520000` shall be issued to clear `JVSIRDY`. If the MCU has
more data available, it will update the register and set the flag again.

#### `0x1f40000c` (ASIC register 6): **JAMMA controls** / **External inputs**

| Bits  | RW | Description                             |
| ----: | :- | :-------------------------------------- |
|   0-7 |    | Unused?                                 |
|     8 | R  | Player 1 button 4 (JAMMA pin 25)        |
|     9 | R  | Player 1 button 5 (JAMMA pin 26)        |
|    10 | R  | Test button (built-in and JAMMA pin 15) |
|    11 | R  | Player 1 button 6                       |
| 12-15 |    | Unused?                                 |

As buttons are active-low (wired between JAMMA pins and ground), all bits are 0
when a button is pressed and 1 otherwise.

The signals for buttons 4 and 5 are wired in parallel to both JAMMA and the
`EXT-IN` connector, while button 6 can only be connected through `EXT-IN` and is
usually unused.

#### `0x1f40000e` (ASIC register 7): **JAMMA controls** / **External inputs**

| Bits  | RW | Description                             |
| ----: | :- | :-------------------------------------- |
|   0-7 |    | Unused?                                 |
|     8 | R  | Player 2 button 4 (JAMMA pin c)         |
|     9 | R  | Player 2 button 5 (JAMMA pin d)         |
|    10 |    | Main RAM layout type (0 = new, 1 = old) |
|    11 | R  | Player 2 button 6                       |
| 12-15 |    | Unused?                                 |

As buttons are active-low (wired between JAMMA pins and ground), all bits are 0
when a button is pressed and 1 otherwise.

The signals for buttons 4 and 5 are wired in parallel to both JAMMA and the
`EXT-IN` connector, while button 6 can only be connected through `EXT-IN` and is
usually unused.

Bit 10 is probed by the 700B01 BIOS kernel to determine how to configure the
main RAM controller. If cleared, the configuration register at `0x1f801060` is
set to `0x4788`, otherwise it is set to `0x0c80`. This check was introduced
alongside revision D of the main board, which features alternate footprints for
two 2 MB chips in place of eight 512 KB ones.

### IDE registers

The IDE interface consists of a 16-bit parallel data bus with a 3-bit address
bus and two bank select pins (`/CS0` and `/CS1`), giving a total of sixteen
16-bit registers of which only nine are typically used. On the 573 the two IDE
banks are mapped to two separate memory regions at `0x1f480000` and `0x1f4c0000`
respectively. The IDE interrupt pin is routed into IRQ10 through the CPLD, while
all other signals on the 40-pin connector (DMA handshaking lines, status pins,
etc.) go unused.

Most 573 games, with the exception of those that run entirely from the internal
flash or PCMCIA cards, expect an ATAPI CD-ROM drive to be always connected and
configured as the primary (master) drive. Connecting an additional ATA hard
drive, CF card, IDE-to-SATA bridge or other device configured as secondary will
not interfere with the BIOS or games, thus homebrew games and apps can leverage
such a drive to store data separately from the currently installed game.

Note that IDE and ATAPI give slightly different meanings to each register. Refer
to the ATA and ATAPI specifications for more details.

#### `0x1f480000` (IDE bank 0, address 0): **Data**

| Bits | RW | Description                 |
| ---: | :- | :-------------------------- |
| 0-15 | RW | Current packet or data word |

Data transfers can also be performed through DMA. See below for details.

#### `0x1f480002` (IDE bank 0, address 1): **Error** / **Features**

When read:

| Bits | RW | Description (ATA)                 | RW | Description (ATAPI)           |
| ---: | :- | :-------------------------------- | :- | :---------------------------- |
|    0 |    | _Reserved_                        | R  | Illegal length flag (`ILI`)   |
|    1 | R  | No media flag (`NM`)              | R  | End of media flag (`EOM`)     |
|    2 | R  | Command aborted flag (`ABRT`)     | R  | Command aborted flag (`ABRT`) |
|    3 | R  | Media change request flag (`MCR`) |    | _Reserved_                    |
|    4 | R  | Address not found flag (`IDNF`)   | R  | SCSI sense key bit 0          |
|    5 | R  | Media changed flag (`MC`)         | R  | SCSI sense key bit 1          |
|    6 | R  | Uncorrectable error flag (`UNC`)  | R  | SCSI sense key bit 2          |
|    7 | R  | DMA CRC error flag (`ICRC`)       | R  | SCSI sense key bit 3          |
| 8-15 |    | _Unused_                          |    | _Unused_                      |

When written:

| Bits | RW | Description (ATA)                       | RW | Description (ATAPI)                              |
| ---: | :- | :-------------------------------------- | :- | :----------------------------------------------- |
|    0 | W  | Command-specific feature index or flags | W  | Use overlapped mode for next command (`OVL`)     |
|    1 | W  | Command-specific feature index or flags | W  | Transfer data for next command using DMA (`DMA`) |
|  2-7 | W  | Command-specific feature index or flags | W  | _Reserved_ (should be 0)                         |
| 8-15 |    | _Unused_                                |    | _Unused_                                         |

#### `0x1f480004` (IDE bank 0, address 2): **Sector count**

| Bits | RW | Description (ATA)              | RW | Description (ATAPI)                                            |
| ---: | :- | :----------------------------- | :- | :------------------------------------------------------------- |
|    0 | W  | Transfer sector count bit 0    | R  | Pending transfer type (`C/D`, 0 = data, 1 = command)           |
|    1 | W  | Transfer sector count bit 1    | R  | Pending transfer direction (`I/O`, 0 = to device, 1 = to host) |
|    2 | W  | Transfer sector count bit 2    | R  | Pending transfer bus release flag (`REL`)                      |
|  3-7 | W  | Transfer sector count bits 3-7 | RW | Current command tag                                            |
| 8-15 |    | _Unused_                       |    | _Unused_                                                       |

In ATA 48-bit LBA mode, bits 8-15 of the number of sectors to transfer must be
written to this register first, followed by bits 0-7.

In ATA CHS or 28-bit LBA mode, setting this register to 0 will cause 256 sectors
to be transferred.

#### `0x1f480006` (IDE bank 0, address 3): **Sector number**

| Bits | RW | Description (ATA)                | RW | Description (ATAPI) |
| ---: | :- | :------------------------------- | :- | :------------------ |
|  0-7 | W  | CHS sector index or LBA bits 0-7 |    | _Unused_            |
| 8-15 |    | _Unused_                         |    | _Unused_            |

In ATA 48-bit LBA mode, bits 24-31 of the target LBA must be written to this
register first, followed by bits 0-7.

#### `0x1f480008` (IDE bank 0, address 4): **Cylinder number low**

| Bits | RW | Description (ATA)                            | RW | Description (ATAPI)          |
| ---: | :- | :------------------------------------------- | :- | :--------------------------- |
|  0-7 | RW | CHS cylinder index bits 0-7 or LBA bits 8-15 | RW | Transfer chunk size bits 0-7 |
| 8-15 |    | _Unused_                                     |    | _Unused_                     |

In ATA 48-bit LBA mode, bits 32-39 of the target LBA must be written to this
register first, followed by bits 8-15.

When reset, ATAPI drives will set this register to `0x14`.

#### `0x1f48000a` (IDE bank 0, address 5): **Cylinder number high**

| Bits | RW | Description (ATA)                              | RW | Description (ATAPI)           |
| ---: | :- | :--------------------------------------------- | :- | :---------------------------- |
|  0-7 | RW | CHS cylinder index bits 8-15 or LBA bits 16-23 | RW | Transfer chunk size bits 8-15 |
| 8-15 |    | _Unused_                                       |    | _Unused_                      |

In ATA 48-bit LBA mode, bits 40-47 of the target LBA must be written to this
register first, followed by bits 16-23.

When reset, ATAPI drives will set this register to `0xeb`.

#### `0x1f48000c` (IDE bank 0, address 6): **Head number** / **Drive select**

| Bits | RW | Description (ATA)                         | RW | Description (ATAPI)                       |
| ---: | :- | :---------------------------------------- | :- | :---------------------------------------- |
|  0-3 | W  | CHS head index or 28-bit LBA bits 24-27   |    | _Reserved_ (should be 0)                  |
|    4 | RW | Drive select (0 = primary, 1 = secondary) | RW | Drive select (0 = primary, 1 = secondary) |
|    5 |    | _Reserved_ (should be 1?)                 |    | _Reserved_ (should be 1?)                 |
|    6 | W  | Sector addressing mode (0 = CHS, 1 = LBA) |    | _Reserved_ (should be 0)                  |
|    7 |    | _Reserved_ (should be 1?)                 |    | _Reserved_ (should be 1?)                 |
| 8-15 |    | _Unused_                                  |    | _Unused_                                  |

Bits 0-3 are not used in ATA 48-bit LBA mode.

#### `0x1f48000e` (IDE bank 0, address 7): **Status** / **Command**

When read:

| Bits | RW | Description (ATA)              | RW | Description (ATAPI)              |
| ---: | :- | :----------------------------- | :- | :------------------------------- |
|    0 | R  | Error flag (`ERR`)             | R  | Check condition flag (`CHK`)     |
|    1 |    | _Reserved_                     |    | _Reserved_                       |
|    2 |    | _Reserved_                     |    | _Reserved_                       |
|    3 | R  | Data request flag (`DRQ`)      | R  | Data request flag (`DRQ`)        |
|    4 | R  | Drive write error flag (`DWE`) | R  | Overlapped service flag (`SERV`) |
|    5 | R  | Drive fault flag (`DF`)        | R  | Drive fault flag (`DF`)          |
|    6 | R  | Drive ready flag (`DRDY`)      | R  | Drive ready flag (`DRDY`)        |
|    7 | R  | Drive busy flag (`BSY`)        | R  | Drive busy flag (`BSY`)          |
| 8-15 |    | _Unused_                       |    | _Unused_                         |

When written:

| Bits | RW | Description   |
| ---: | :- | :------------ |
|  0-7 | W  | Command index |
| 8-15 |    | _Unused_      |

In order to issue a command, the features, sector, cylinder and head registers
must be set up appropriately before writing the command ID to this register.
Refer to the ATA specification for a list of available commands and their
parameters.

`DRDY` is set by the drive when it is ready to execute an ATA command. Note that
ATAPI drives will *not* set `DRDY` initially, while still accepting ATAPI
commands, in order to prevent misdetection as a hard drive. Before sending any
command, a polling loop shall be used to wait until `BSY` is cleared.

`DRQ` is set when the drive is waiting for data to be read or written. Depending
on the drive and command, an interrupt may also be fired when `DRQ` goes high
after a command is issued. `ERR`/`CHK` is set if the last command executed
resulted in an error; in that case the error register will contain more
information about the cause of the error.

Reading from this register will acknowledge any pending drive interrupt and
deassert IRQ10. Note that, as with all PS1 interrupts, IRQ10 must additionally
be acknowledged at the interrupt controller side in order for it to fire again.

#### `0x1f4c000c` (IDE bank 1, address 6): **Alternate status**

Read-only mirror of the status register at `0x1f48000e` that returns the same
flags, but does not acknowledge any pending IRQ when read.

#### IDE DMA and quirks

DMA channel 5, normally reserved for the expansion port on a PS1, can be used to
transfer data to/from the IDE bus... with some caveats. The "correct" way to
connect an IDE drive to the PS1's DMA controller would to be to wire up `DMARQ`
and `/DMACK` from the drive directly to the respective pins on the CPU, allowing
the DMA controller to synchronize transfers to the drive's internal buffer in
chunked mode.

However, Konami being Konami, they did not do this on the 573. IDE drives will
instead interpret DMA reads or writes as a burst of regular ("PIO", as defined
in the ATA specification) CPU-issued reads or writes. As such, the drive shall
be configured for PIO data transfers rather than DMA using the "set features"
ATA command, and bits 9-10 in the `DMA5_CHCR` register shall be cleared to put
the channel in manual synchronization mode. The `DRQ` bit in the status register
must also be polled manually prior to starting a transfer, to ensure the drive
is ready for it.

### RTC registers

The RTC is an ST M48T58. This chip behaves like an 8 KB 8-bit static RAM, wired
to the lower 8 bits of the 16-bit data bus. It must thus be accessed by
performing 16-bit bus accesses and ignoring/masking out the upper 8 bits (as
with IDE control registers).

The first 8184 bytes are mapped to the `0x1f620000-0x1f623fef` region and are
simply battery-backed SRAM, which will retain its contents across power cycles
as long as the RTC's battery is not dead. The last 8 bytes are used as clock and
control registers.

The values of the clock registers are buffered: they are stored in intermediate
registers rather than being read from or written to the clock counters directly.
Bits 6 and 7 in the control register at `0x1f623ff0` are used to control
transfers between the registers and clock counters. All clock values are
returned in BCD format.

#### `0x1f623ff0` (M48T58 register `0x1ff8`): **Calibration** / **Control**

| Bits | RW | Buffered | Description                                             |
| ---: | :- | :------- | :------------------------------------------------------ |
|  0-4 | RW | Unknown  | Calibration offset (0-31), adjusts oscillator frequency |
|    5 | RW | Unknown  | Sign bit for calibration offset (1 = positive)          |
|    6 | W  | No       | Read mutex (1 = prevent buffered register updates)      |
|    7 | W  | No       | Write mutex and trigger                                 |
| 8-15 |    |          | _Unused_                                                |

The values of all buffered clock registers are updated automatically. Setting
bit 6 will disable this behavior while keeping the counters running, allowing
for the registers to be read reliably without the RTC updating them at the same
time. The bit shall be cleared after reading the registers.

Setting bit 7 will also halt buffered register updates, so that they can be
overwritten manually with new values. Clearing it afterwards will result in the
registers' values being copied back to the clock counters.

#### `0x1f623ff2` (M48T58 register `0x1ff9`): **Seconds** / **Stop**

| Bits | RW | Buffered | Description                                     |
| ---: | :- | :------- | :---------------------------------------------- |
|  0-3 | RW | Yes      | Second units (0-9)                              |
|  4-6 | RW | Yes      | Second tens (0-5)                               |
|    7 | RW | Unknown  | Stop flag (0 = clock paused, 1 = clock running) |
| 8-15 |    |          | _Unused_                                        |

#### `0x1f623ff4` (M48T58 register `0x1ffa`): **Minute**

| Bits | RW | Buffered | Description            |
| ---: | :- | :------- | :--------------------- |
|  0-3 | RW | Yes      | Minute units (0-9)     |
|  4-6 | RW | Yes      | Minute tens (0-5)      |
|    7 |    |          | _Reserved_ (must be 0) |
| 8-15 |    |          | _Unused_               |

#### `0x1f623ff6` (M48T58 register `0x1ffb`): **Hour**

| Bits | RW | Buffered | Description                          |
| ---: | :- | :------- | :----------------------------------- |
|  0-3 | RW | Yes      | Hour units (0-9, or 0-3 if tens = 2) |
|  4-5 | RW | Yes      | Hour tens (0-2)                      |
|  6-7 |    |          | _Reserved_ (must be 0)               |
| 8-15 |    |          | _Unused_                             |

Hours are always returned in 24-hour format, as there is no way to switch to
12-hour format.

#### `0x1f623ff8` (M48T58 register `0x1ffc`): **Day of week** / **Century**

| Bits | RW | Buffered | Description                                |
| ---: | :- | :------- | :----------------------------------------- |
|  0-2 | RW | Yes      | Day of week (1-7)                          |
|    3 |    |          | _Reserved_ (must be 0)                     |
|    4 | RW | Yes      | Century flag                               |
|    5 | RW | Unknown  | Century flag toggling enable (1 = enabled) |
|    6 | RW | Unknown  | Enable 512 Hz clock signal output on pin 1 |
|    7 |    |          | _Reserved_ (must be 0)                     |
| 8-15 |    |          | _Unused_                                   |

The day of week register is a free-running counter incremented alongside the day
counter. There is no logic for calculating the day of the week, so it must be
updated manually when setting the time. Konami games use 1 as Sunday, 2 as
Monday and so on.

Bit 4 is a single-bit "counter" that gets toggled each time the year counter
overflows. It can be frozen by clearing bit 5. Konami games do not use the
century flag, as they interpret any year counter value in 70-99 range as
1970-1999 and all other values as a year after 2000.

#### `0x1f623ffa` (M48T58 register `0x1ffd`): **Day of month** / **Battery state**

| Bits | RW | Buffered | Description                                          |
| ---: | :- | :------- | :--------------------------------------------------- |
|  0-3 | RW | Yes      | Day of month units (range depends on tens and month) |
|  4-5 | RW | Yes      | Day of month tens (range depends on month)           |
|    6 | R  | No       | Low battery flag (1 = battery voltage is below 2.5V) |
|    7 | RW | Unknown  | Battery monitoring enable (1 = enabled)              |
| 8-15 |    |          | _Unused_                                             |

Bit 6 is updated when the system is power cycled, if bit 7 has previously been
set.

#### `0x1f623ffc` (M48T58 register `0x1ffe`): **Month**

| Bits | RW | Buffered | Description                           |
| ---: | :- | :------- | :------------------------------------ |
|  0-3 | RW | Yes      | Month units (1-9, or 0-2 if tens = 1) |
|    4 | RW | Yes      | Month tens (0-1)                      |
|  5-7 |    |          | _Reserved_ (must be 0)                |
| 8-15 |    |          | _Unused_                              |

#### `0x1f623ffe` (M48T58 register `0x1fff`): **Year**

| Bits | RW | Buffered | Description      |
| ---: | :- | :------- | :--------------- |
|  0-3 | RW | Yes      | Year units (0-9) |
|  4-7 | RW | Yes      | Year tens (0-9)  |
| 8-15 |    |          | _Unused_         |

The year counter covers a full century, going from 00 to 99. On each overflow
the century flag in the day of week register is toggled.

### Other registers

These registers are implemented almost entirely using 74-series logic and the
XC9536 CPLD on the main board.

#### `0x1f500000`: **Bank switch** / **Security cartridge**

| Bits | RW | Description                                              |
| ---: | :- | :------------------------------------------------------- |
|  0-5 | W  | Bank number (0-47, see below)                            |
|    6 | W  | `IO0` direction on security cartridge (0 = input/high-z) |
|    7 |    | Unknown (goes into CPLD)                                 |
| 8-15 |    | _Unused_                                                 |

Bit 6 controls whether `IO0` on the security cartridge is an input or an output.
If set, `IO0` will output the same logic level as `D0`, otherwise the pin will
be floating. Bits 0-5 are used to switch the device mapped to the 4 MB
`0x1f000000-0x1f3fffff` region:

| Bank  | Mapped to                             |
| ----: | :------------------------------------ |
|     0 | Internal flash 1 (chips `31M`, `27M`) |
|     1 | Internal flash 2 (chips `31L`, `27L`) |
|     2 | Internal flash 3 (chips `31J`, `27J`) |
|     3 | Internal flash 4 (chips `31H`, `27H`) |
|  4-15 | _Unused_                              |
| 16-31 | PCMCIA card slot 1                    |
| 32-47 | PCMCIA card slot 2                    |
| 48-63 | _Unused_                              |

#### `0x1f520000`: **`JVSIRDY` clear**

| Bits | RW | Description |
| ---: | :- | :---------- |
| 0-15 |    | _Unused_    |

This register is a dummy write-only port that clears the `JVSIRDY` flag when any
value is written to it. The flag is set by the JVS MCU whenever a new data word
is available for reading from `0x1f40000a`.

#### `0x1f560000`: **IDE reset control**

| Bits | RW | Description                           |
| ---: | :- | :------------------------------------ |
|    0 | W  | Reset pin output (0 = pull reset low) |
| 1-15 |    | _Unused_                              |

Since the IDE reset pin is active-low, a reset is performed by writing 0 to this
register, then waiting a few milliseconds and writing 1 again. Note that the IDE
specification also defines a way to "soft-reset" devices (e.g. to abort
execution of a command) using the `SRST` bit in the device control register.

#### `0x1f5c0000`: **Watchdog clear**

| Bits | RW | Description |
| ---: | :- | :---------- |
| 0-15 |    | _Unused_    |

This register is a dummy write-only port that clears the watchdog timer embedded
in the Konami 058232 power-on reset and coin counter driver chip when any value
is written to it. The BIOS and games write to this port roughly once per frame.

If the watchdog is not cleared at least every 350-400 ms, it will pull the
system's reset line low for about 50 ms in order to force a reboot. The watchdog
can be disabled without affecting power-on reset by placing a jumper on `S86`
(see the pinouts section).

#### `0x1f600000`: **External outputs**

| Bits | RW | Description                           |
| ---: | :- | :------------------------------------ |
|  0-7 | W  | To `OUT0-OUT7` on `EXT-OUT` connector |
| 8-15 |    | _Unused_                              |

The lower 8 bits written to this register are latched on pins `OUT0-OUT7` of the
external output connector (see the pinouts section). This connector is used by
some games to control cabinet lights without using an I/O board.

#### `0x1f680000`: **Data to JVS MCU**

| Bits | RW | Description      |
| ---: | :- | :--------------- |
| 0-15 | W  | Data word to MCU |

In order to prevent overruns, this register shall only be accessed when
`JVSDRDY` is cleared. Writing to it will set `JVSDRDY`.

#### `0x1f6a0000`: **Security cartridge outputs**

| Bits | RW | Description                      |
| ---: | :- | :------------------------------- |
|  0-7 | W  | To `D0-D7` on security cartridge |
| 8-15 |    | _Unused_                         |

The lower 8 bits written to this register are latched on pins `D0-D7` of the
cartridge slot. See the security cartridge section for an explanation of what
each pin is wired to. Bit 0 additionally controls the `IO0` pin when configured
as an output through the bank switch register. Writing to this register will set
the `DRDY` flag, which can then be cleared by the cartridge.

## JVS interface

The System 573 is equipped with a JVS host interface, allowing for connection of
I/O modules, controllers and other devices that implement the JVS protocol
commonly used in arcade cabinets.

JVS uses a single RS-485 bus running at 115200 bits per second, shared by all
devices. The standard JVS connector is a single USB-A port, with the data lines
used as the RS-485 differential pair and the `VBUS` pin as a sensing line (see
the JVS specification for details). JVS devices typically have a full size USB-B
port for connection to the host, plus optionally another USB-A port for daisy
chaining additional devices. The RS-485 bus needs to be terminated; some boards
will automatically insert a termination resistor when connected as the last node
in a daisy chain.

### Packet format

A JVS packet can be up to 258 bytes long and is made up of the following fields:

| Byte | Description                                                    |
| ---: | :------------------------------------------------------------- |
|    0 | Synchronization byte, must be `0xe0`                           |
|    1 | Destination address                                            |
|    2 | Length (number of payload bytes including checksum)            |
|   3- | Payload                                                        |
|      | Checksum (sum of address, length and payload bytes modulo 256) |

**NOTE**: when a JVS packet is sent over the RS-485 bus, any `0xd0` or `0xe0`
byte other than the synchronization byte must be escaped as `0xd0 0xcf` or
`0xd0 0xdf` respectively, in order to allow downstream devices to reliably
determine the end of a packet. On the 573, the JVS MCU handles escaping outbound
packets and unescaping inbound packets automatically. The escaping process does
*not* update the length field to reflect the escaped length of the packet.

Refer to the JVS specification for details on the contents of standard and
vendor-specific payloads.

### MCU communication protocol

The system's JVS interface is managed by a dedicated H8/3644 microcontroller,
interfaced through two 16-bit latches and handshaking lines (in a similar way to
the 8-bit ports on the security cartridge slot). The MCU's firmware is stored in
OTP ROM and consists of a simple loop that buffers the data written by the 573,
sends it, waits for a response to be received and lets the 573 read it.

In order to perform a JVS transaction the 573 must:

1.  Reset the MCU through register `0x1f400000`, clear `JVSIRDY` by writing to
    `0x1f520000` then wait for the status and error codes in register
    `0x1f400004` to be set to 0 and 3 respectively.
2.  Write the packet two bytes at a time to `0x1f680000`, waiting for `JVSDRDY`
    to go low before each write. Words are little endian, so for instance the
    first word of a packet with destination address `0x01` would be `0x01e0`. If
    the total length of the packet is odd, the last byte shall still be written
    as a word (with the upper byte zeroed out).
3.  Wait for the status code to become 1. At this point the MCU will send the
    packet and wait for a response from a device on the bus.
4.  Wait for the status code to become 0, signalling a valid response has been
    received and can be read out. A timeout should be implemented here, as the
    MCU will wait for a response indefinitely even if no device is present. The
    MCU has no concept of a broadcast, so this also applies to the JVS reset
    command: nothing on the bus answers a reset, so the MCU blocks on it forever
    and `JVSDRDY` never drops again. The status and error codes read 1 and 3
    throughout - busy, no error - and no further packet will be written out. The
    only way out is resetting the MCU through bit 8 of `0x1f400000`.
5.  Read the packet, again two bytes at a time, from `0x1f40000a`, waiting for
    `JVSIRDY` to go high before each read and clearing it by writing to
    `0x1f520000` after each read. The status code will be set to 2 after the
    first word is read and back to 0 once no more data is available to read.

The MCU does not allow for non-JVS packets to be sent as it validates the sync
byte, checksum and uses the length field to determine packet length. Responses
cannot be received without sending a packet first either. The MCU will also
insert a 200 µs minimum delay between the last byte of a received packet and the
first byte of the next packet.

## I/O boards

The System 573 was designed to be expanded with game-specific hardware using I/O
expansion boards mounted on top of the main board, and/or custom security
cartridges. I/O boards have access to the 16-bit system bus and are accessible
through the `0x1f640000-0x1f6400ff` region.

- [Analog I/O board (`GX700-PWB(F)`)](#analog-io-board-gx700-pwbf)
- [Digital I/O board (`GX894-PWB(B)A`)](#digital-io-board-gx894-pwbba)
- [Alternate analog I/O board (`GX700-PWB(K)`)](#alternate-analog-io-board-gx700-pwbk)
- [Fishing controller I/O board (`GE765-PWB(B)A`)](#fishing-controller-io-board-ge765-pwbba)
- [DDR Karaoke Mix I/O board (`GX921-PWB(B)`)](#ddr-karaoke-mix-io-board-gx921-pwbb)
- [GunMania I/O board (`PWB0000073070`)](#gunmania-io-board-pwb0000073070)
- [Hypothetical debugging board](#hypothetical-debugging-board)

### Analog I/O board (`GX700-PWB(F)`)

Used in early Bemani games such as DDR 1stMIX and 2ndMIX, as well as some
non-Bemani games. The name is misleading as the board does not deal with any
analog signals whatsoever; the name was given retroactively to distinguish it
from the digital I/O board. It provides up to 28 optoisolated open-drain outputs
typically used to control cabinet lights, split across 4 banks:

- **Bank A** (`CN33`): 8 outputs (A0-A7)
- **Bank B** (`CN34`): 8 outputs (B0-B7)
- **Bank C** (`CN35`): 8 outputs (C0-C7)
- **Bank D** (`CN36`): 4 outputs (D0-D3)

Some games shipped with partially populated analog I/O boards, thus not all
banks may be available. See the game-specific information section for details on
how lights are wired up on each cabinet type.

#### `0x1f640080`: **Bank A**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
|    0 | W  | Output A1 (0 = grounded, 1 = high-z) |
|    1 | W  | Output A3 (0 = grounded, 1 = high-z) |
|    2 | W  | Output A5 (0 = grounded, 1 = high-z) |
|    3 | W  | Output A7 (0 = grounded, 1 = high-z) |
|    4 | W  | Output A6 (0 = grounded, 1 = high-z) |
|    5 | W  | Output A4 (0 = grounded, 1 = high-z) |
|    6 | W  | Output A2 (0 = grounded, 1 = high-z) |
|    7 | W  | Output A0 (0 = grounded, 1 = high-z) |
| 8-15 |    | _Unused_                             |

#### `0x1f640088`: **Bank B**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
|    0 | W  | Output B1 (0 = grounded, 1 = high-z) |
|    1 | W  | Output B3 (0 = grounded, 1 = high-z) |
|    2 | W  | Output B5 (0 = grounded, 1 = high-z) |
|    3 | W  | Output B7 (0 = grounded, 1 = high-z) |
|    4 | W  | Output B6 (0 = grounded, 1 = high-z) |
|    5 | W  | Output B4 (0 = grounded, 1 = high-z) |
|    6 | W  | Output B2 (0 = grounded, 1 = high-z) |
|    7 | W  | Output B0 (0 = grounded, 1 = high-z) |
| 8-15 |    | _Unused_                             |

#### `0x1f640090`: **Bank C**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
|    0 | W  | Output C1 (0 = grounded, 1 = high-z) |
|    1 | W  | Output C3 (0 = grounded, 1 = high-z) |
|    2 | W  | Output C5 (0 = grounded, 1 = high-z) |
|    3 | W  | Output C7 (0 = grounded, 1 = high-z) |
|    4 | W  | Output C6 (0 = grounded, 1 = high-z) |
|    5 | W  | Output C4 (0 = grounded, 1 = high-z) |
|    6 | W  | Output C2 (0 = grounded, 1 = high-z) |
|    7 | W  | Output C0 (0 = grounded, 1 = high-z) |
| 8-15 |    | _Unused_                             |

#### `0x1f640098`: **Bank D**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
|    0 | W  | Output D3 (0 = grounded, 1 = high-z) |
|    1 | W  | Output D2 (0 = grounded, 1 = high-z) |
|    2 | W  | Output D1 (0 = grounded, 1 = high-z) |
|    3 | W  | Output D0 (0 = grounded, 1 = high-z) |
| 4-15 |    | _Unused_                             |

### Digital I/O board (`GX894-PWB(B)A`)

Used by later Bemani games, such as DDR from Solo onwards. This board features
the same 28 isolated open-drain outputs as the analog I/O board, plus a Xilinx
XCS40XL Spartan-XL FPGA and a Micronas MAS3507D audio decoder ASIC used to play
encrypted MP3 files. The FPGA has 24 MB of dedicated DRAM into which the files
are preloaded on startup, then decrypted on the fly and fed to the decoder. The
board also features 128 KB of SRAM used as a cache, RS-232 and ARCnet
transceivers for communication with other hardware and a DS2401 serial number
chip, used to prevent usage of the same security cartridge on more than one 573.

The vast majority of the registers provided by this board (including some but
not all light outputs) are handled by its FPGA, which requires a configuration
bitstream to be uploaded to it in order to work. Registers in the
`0x1f6400f0-0x1f6400ff` region are handled by a CPLD and are functional even if
no bitstream is loaded. There are several known versions of Konami's bitstream:

| SHA-1 (41337 bytes, LSB first)             | First used by                          |
| :----------------------------------------- | :------------------------------------- |
| `32d455a25eb26fe4e4b577cb0f0e3bebd0f82959` | Dance Dance Revolution Solo Bass Mix   |
| `a53b8906de95c34b6e3f053bd7488c888bc904b6` | Dance Dance Revolution 3rdMIX          |
| `5d27c84e812f71401f940621f79c5c6114192895` | GuitarFreaks 2ndMIX                    |
| `450b12627b7eacd3ea3f8b0b7a16589a13010c41` | Mambo a Go-Go                          |
| `53d0c1e3f6ae042d7d45ce889b79a12f1be5eabd` | Martial Beat e-Amusement               |
| `d1d0f123bbb9d5abfefbd556c366f9ded0779e41` | Martial Beat (leftover file 1, unused) |
| `f354619fe1a80cabe0b774784181b3bfeff0a3e9` | Martial Beat (leftover file 2, unused) |

The DDR and Mambo bitstreams all implement the same registers (listed below) and
seem to only differ in the MP3 decryption algorithm, while the unused Martial
Beat bitstreams seem to behave in a completely different way.

Homebrew software may also load custom bitstreams developed using the Xilinx ISE
4.2 toolchain (the last version to support Spartan-XL parts). The following
custom bitstreams are known to exist so far:

| SHA-1 (41337 bytes, LSB first)             | First used by               |
| :----------------------------------------- | :-------------------------- |
| `9d5acaae61f03f4d71831ebdb013af6189802ed2` | 573in1 1.0.0                |
| `e9212e9ff24fa876158f510e3c17649a110f60a4` | 573in1 (development branch) |

#### `0x1f640080` (FPGA, all bitstreams): **Magic number**

| Bits | RW | Description                                                                   |
| ---: | :- | :---------------------------------------------------------------------------- |
| 0-15 | R  | Magic number (`0x1234` for Konami bitstreams, `0x573f` for 573in1 bitstreams) |

This register is checked by some versions of Konami's digital I/O board driver
to make sure the bitstream was properly loaded.

#### `0x1f640082` (FPGA, 573in1 bitstream): **Configuration**

| Bits | RW | Description                                                                                 |
| ---: | :- | :------------------------------------------------------------------------------------------ |
|  0-7 | R  | Bitstream version (currently `0x02`)                                                        |
|    8 | RW | MP3 looping enable (1 = continue playing from start address when end address is reached)    |
|    9 | RW | Automatically clear DAC sample counter registers when starting MP3 playback (1 = clear)     |
|   10 | RW | Automatically clear register `0x1f6400cc` when DAC sample counter delta is read (1 = clear) |
|   11 | RW | Automatically disable sample counter if cleared while MP3 playback is stopped (1 = disable) |
|   12 | RW | Primary MP3 descrambler key (0 = `key1`, 1 = scrambled XOR of `key1` and `key2`)            |
|   13 | RW | Secondary MP3 descrambler key (0 = none, 1 = scrambled counter initialized from `key3`)     |
|   14 | RW | MP3 data feeder endianness (0 = read bits 15-8 then 7-0, 1 = read bits 7-0 then 15-8)       |
|   15 | RW | Swap bits 14 and 15 of `key1` when mutating it (1 = swap)                                   |

Custom register only implemented by the 573in1 bitstream, in order to allow for
emulation of quirks present in different versions of Konami's bitstreams as well
as control some additional features.

Bits 9-11 tune the behavior of the DAC sample counter registers (`0x1f6400ca`,
`0x1f6400cc` and `0x1f6400cf`). Setting all of them will make the registers
replicate the behavior of those provided by the DDR 3rdMIX bitstream onwards,
while clearing them will bring them closer to the earlier DDR Solo Bass Mix
bitstream's behavior.

Bits 12, 13 and 15 control the MP3 decryption algorithm. All of them shall be
set to decrypt MP3 files from DDR 3rdMIX onwards (scrambled with `key1`, `key2`
and `key3`) or cleared to play DDR Solo Bass Mix files (scrambled with `key1`
only). Bit 14 controls which byte of each 16-bit word in DRAM is fed to the
MAS3507D first and should be cleared for encrypted MP3 playback.

The 573in1 bitstream's descrambler can be configured to play unencrypted data by
performing the following steps:

- clear bits 12, 13 and 15;
- set bit 14 (encrypted MP3s are byte swapped as part of the scrambling process
  but an unencrypted file will have to be swapped during playback);
- clear `key1` by writing zero to register `0x1f6400a8`, which will render the
  decryption step a no-op.

#### `0x1f640090` (FPGA, all bitstreams): **Network board address**

#### `0x1f640092` (FPGA, all bitstreams): **Unknown (network related)**

#### `0x1f6400a0` (FPGA, all bitstreams): **MP3 data start address high**

#### `0x1f6400a2` (FPGA, all bitstreams): **MP3 data start address low**

#### `0x1f6400a4` (FPGA, all bitstreams): **MP3 data end address high**

#### `0x1f6400a6` (FPGA, all bitstreams): **MP3 data end address low**

#### `0x1f6400a8` (FPGA, all bitstreams): **MP3 frame counter** / **Descrambler key 1**

When read:

| Bits | RW | Description                                                     |
| ---: | :- | :-------------------------------------------------------------- |
| 0-15 | R  | Current MP3 frame count (number of MAS3507D `PI4` rising edges) |

When written:

| Bits | RW | Description          |
| ---: | :- | :------------------- |
| 0-15 | W  | Initial `key1` value |

The frame counter is only active when bit 15 in register `0x1f6400ae` is set.
Note that the MAS3507D also has an internal frame counter readable through I2C,
independent of this register.

#### `0x1f6400aa` (FPGA, all bitstreams): **MP3 playback status**

When read:

| Bits | RW | Description                               |
| ---: | :- | :---------------------------------------- |
| 0-11 |    | _Unused_                                  |
|   12 | R  | MAS3507D MP3 data request flag (`PI19`)   |
|   13 | R  | MAS3507D MP3 error flag (`PI8`)           |
|   14 | R  | MAS3507D MP3 frame sync flag (`PI4`)      |
|   15 | R  | MAS3507D master clock ready flag (`WRDY`) |

When written:

| Bits  | RW | Description                                     |
| ----: | :- | :---------------------------------------------- |
|  0-11 |    | _Unused_                                        |
|    12 | W  | MAS3507D chip reset (`/POR`, 0 = pull low)      |
|    13 | W  | MAS3507D PIO chip select (`/PCS`, 0 = pull low) |
| 14-15 |    | _Unused_                                        |

During normal operation the reset input should be high and the PIO chip select
low. Setting the chip select high will result in the MAS3507D tristating `PI19`,
`PI8` and `PI4`.

#### `0x1f6400ac` (FPGA, all bitstreams): **MAS3507D I2C**

| Bits  | RW | Description                         |
| ----: | :- | :---------------------------------- |
|  0-11 |    | _Unused_                            |
|    12 | RW | MAS3507D `SDA` (write 0 = pull low) |
|    13 | RW | MAS3507D `SCL` (write 0 = pull low) |
| 14-15 | RW | _Unused_                            |

Due to the MAS3507D relying heavily on I2C clock stretching (pulling `SCL` low
to request the host to wait), both `SDA` and `SCL` are bidirectional open-drain
signals.

#### `0x1f6400ae` (FPGA, all bitstreams): **MP3 data feeder control**

| Bits  | RW | Description                                                |
| ----: | :- | :--------------------------------------------------------- |
|  0-11 |    | _Unused_                                                   |
|    12 | R  | Current playback status (0 = paused, 1 = playing)          |
|    13 | W  | Playback enable (0 = disabled/ignore bit 14, 1 = enabled)  |
|    14 | W  | Playback control (0 = pause, 1 = play)                     |
|    15 | W  | MP3 frame counter enable (0 = disabled/reset, 1 = enabled) |

Data is only fed to the MAS3507D when both bits 13 and 14 are set. Bit 12 is a
read-only copy of bit 14 and remains set if playback is stopped by clearing bit
13 only.

Bit 15 controls whether to increment register `0x1f6400a8` each time a rising
edge is detected on the MAS3507D's `PI4` (frame sync) pin. The counter is
automatically reset to zero when this bit is cleared.

#### `0x1f6400b0` (FPGA, all bitstreams): **DRAM write address high**

#### `0x1f6400b2` (FPGA, all bitstreams): **DRAM write address low**

#### `0x1f6400b4` (FPGA, all bitstreams): **DRAM data**

| Bits | RW | Description       |
| ---: | :- | :---------------- |
| 0-15 | RW | Current data word |

**NOTE**: on some bitstream versions, all registers in the
`0x1f6400b0-0x1f6400bf` region seem to mirror this register when read (possibly
due to incomplete address decoding), however only a read from `0x1f6400b4` will
increment the current read pointer and kick off prefetching of the next word.

#### `0x1f6400b6` (FPGA, all bitstreams): **DRAM read address high**

#### `0x1f6400b8` (FPGA, all bitstreams): **DRAM read address low**

#### `0x1f6400ba` (FPGA, all bitstreams): **Unknown**

#### `0x1f6400c0` (FPGA, all bitstreams): **Network data**

#### `0x1f6400c2` (FPGA, all bitstreams): **Network TX FIFO length**

#### `0x1f6400c4` (FPGA, all bitstreams): **Network RX FIFO length**

#### `0x1f6400c6` (FPGA, all bitstreams): **Unknown**

Seems to return `0x7654` on startup.

#### `0x1f6400c8` (FPGA, all bitstreams): **Unknown (network related)**

Seems to also return `0x7654` on startup.

#### `0x1f6400ca` (FPGA, all bitstreams except Solo): **DAC sample counter high**

#### `0x1f6400cc` (FPGA, all bitstreams): **DAC sample counter low**

#### `0x1f6400ce` (FPGA, all bitstreams): **DAC sample counter delta**

#### `0x1f6400e0` (FPGA, all bitstreams): **Bank A**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
| 0-11 |    | _Unused_                             |
|   12 | W  | Output A4 (0 = grounded, 1 = high-z) |
|   13 | W  | Output A5 (0 = grounded, 1 = high-z) |
|   14 | W  | Output A6 (0 = grounded, 1 = high-z) |
|   15 | W  | Output A7 (0 = grounded, 1 = high-z) |

#### `0x1f6400e2` (FPGA, all bitstreams): **Bank A**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
| 0-11 |    | _Unused_                             |
|   12 | W  | Output A0 (0 = grounded, 1 = high-z) |
|   13 | W  | Output A1 (0 = grounded, 1 = high-z) |
|   14 | W  | Output A2 (0 = grounded, 1 = high-z) |
|   15 | W  | Output A3 (0 = grounded, 1 = high-z) |

#### `0x1f6400e4` (FPGA, all bitstreams): **Bank B**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
| 0-11 |    | _Unused_                             |
|   12 | W  | Output B4 (0 = grounded, 1 = high-z) |
|   13 | W  | Output B5 (0 = grounded, 1 = high-z) |
|   14 | W  | Output B6 (0 = grounded, 1 = high-z) |
|   15 | W  | Output B7 (0 = grounded, 1 = high-z) |

#### `0x1f6400e6` (FPGA, all bitstreams): **Bank D**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
| 0-11 |    | _Unused_                             |
|   12 | W  | Output D0 (0 = grounded, 1 = high-z) |
|   13 | W  | Output D1 (0 = grounded, 1 = high-z) |
|   14 | W  | Output D2 (0 = grounded, 1 = high-z) |
|   15 | W  | Output D3 (0 = grounded, 1 = high-z) |

#### `0x1f6400e8` (FPGA, all bitstreams): **Internal logic reset**

| Bits | RW | Description                                                  |
| ---: | :- | :----------------------------------------------------------- |
| 0-11 |    | _Unused_                                                     |
|   12 | W  | Unknown reset (0 = reset)                                    |
|   13 | W  | Reset MP3 feeder and master clock divider to DAC (0 = reset) |
|   14 | W  | Unknown reset (0 = reset)                                    |
|   15 | W  | Unknown reset (0 = reset)                                    |

Konami's code writes `0xf000`, followed by `0x0000`, a delay and `0xf000` again,
to this register after uploading the bitstream.

#### `0x1f6400ea` (FPGA, all bitstreams): **Descrambler key 2**

| Bits | RW | Description          |
| ---: | :- | :------------------- |
| 0-15 | W  | Initial `key2` value |

#### `0x1f6400ec` (FPGA, all bitstreams): **Descrambler key 3**

| Bits | RW | Description          |
| ---: | :- | :------------------- |
|  0-7 | W  | Initial `key3` value |
| 8-15 |    | _Unused_             |

#### `0x1f6400ee` (FPGA, all bitstreams): **1-wire bus**

When read:

| Bits  | RW | Description               |
| ----: | :- | :------------------------ |
|   0-7 |    | _Unused_                  |
|     8 | R  | DS2433 1-wire bus readout |
|  9-11 |    | _Unused_                  |
|    12 | R  | DS2401 1-wire bus readout |
| 13-15 |    | _Unused_                  |

When written:

| Bits  | RW | Description                                            |
| ----: | :- | :----------------------------------------------------- |
|   0-7 |    | _Unused_                                               |
|     8 | W  | Drive DS2433 1-wire bus low (1 = pull low, 0 = high-z) |
|  9-11 |    | _Unused_                                               |
|    12 | W  | Drive DS2401 1-wire bus low (1 = pull low, 0 = high-z) |
| 13-15 |    | _Unused_                                               |

In addition to the DS2401 the board has an unpopulated footprint for a DS2433
1-wire EEPROM, connected to a separate FPGA pin.

#### `0x1f6400f0` (CPLD): **Unknown (unused?)**

Konami's code does not write to this CPLD register.

#### `0x1f6400f2` (CPLD): **Unknown (unused?)**

Konami's code does not write to this CPLD register.

#### `0x1f6400f4` (CPLD): **DAC reset**

| Bits | RW | Description                         |
| ---: | :- | :---------------------------------- |
| 0-14 |    | _Unused_                            |
|   15 | W  | Audio DAC reset/disable (0 = reset) |

Konami's code uses this register to mute the DAC during FPGA and MAS3507D
initialization.

#### `0x1f6400f6` (CPLD): **FPGA status and control**

When read:

| Bits | RW | Description                      |
| ---: | :- | :------------------------------- |
| 0-11 |    | _Unused_                         |
|   12 | R  | Possibly `/INIT` from FPGA       |
|   13 | R  | Possibly `DONE` from FPGA        |
|   14 | R  | Board identification? (always 1) |
|   15 | R  | Board identification? (always 0) |

**NOTE**: all registers in the `0x1f6400f0-0x1f6400ff` region seem to return the
same value as this register when read, possibly due to incomplete address
decoding in the CPLD. Konami's driver only ever reads from this register and
treats all other CPLD registers as write-only.

When written:

| Bits | RW | Description                 |
| ---: | :- | :-------------------------- |
| 0-11 |    | _Unused_                    |
|   12 | W  | Possibly `/INIT` to FPGA    |
|   13 | W  | Possibly `DONE` to FPGA     |
|   14 | W  | Possibly `/PROGRAM` to FPGA |
|   15 | W  | Unused? (always 1)          |

This register is only written to 3 times when resetting the FPGA prior to
loading the bitstream. The values written are `0x8000` first, then `0xc000` and
finally `0xf000`.

#### `0x1f6400f8` (CPLD): **FPGA bitstream upload**

| Bits | RW | Description             |
| ---: | :- | :---------------------- |
| 0-14 |    | _Unused_                |
|   15 | W  | Bit to send to the FPGA |

Bits written to this register are sent to the FPGA's configuration interface
(`DIN` and `CCLK` pins, see the XCS40XL datasheet). There is no separate bit to
control the `CCLK` pin as clocking is handled automatically. The FPGA is wired
to boot in "slave serial" mode and wait for a bitstream to be loaded by the 573
through this port.

All known games load the bitstream from an array embedded in the executable or a
file on the internal flash (usually named `data/fpga/fpga_mp3.bin`), then write
its contents to this port LSB first and monitor the FPGA status register. The
bitstream is always 330696 bits (41337 bytes) long as per the XCS40XL datasheet.

#### `0x1f6400fa` (CPLD): **Bank C**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
| 0-11 |    | _Unused_                             |
|   12 | W  | Output C0 (0 = grounded, 1 = high-z) |
|   13 | W  | Output C1 (0 = grounded, 1 = high-z) |
|   14 | W  | Output C2 (0 = grounded, 1 = high-z) |
|   15 | W  | Output C3 (0 = grounded, 1 = high-z) |

#### `0x1f6400fc` (CPLD): **Bank C**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
| 0-11 |    | _Unused_                             |
|   12 | W  | Output C4 (0 = grounded, 1 = high-z) |
|   13 | W  | Output C5 (0 = grounded, 1 = high-z) |
|   14 | W  | Output C6 (0 = grounded, 1 = high-z) |
|   15 | W  | Output C7 (0 = grounded, 1 = high-z) |

#### `0x1f6400fe` (CPLD): **Bank B**

| Bits | RW | Description                          |
| ---: | :- | :----------------------------------- |
| 0-11 |    | _Unused_                             |
|   12 | W  | Output B0 (0 = grounded, 1 = high-z) |
|   13 | W  | Output B1 (0 = grounded, 1 = high-z) |
|   14 | W  | Output B2 (0 = grounded, 1 = high-z) |
|   15 | W  | Output B3 (0 = grounded, 1 = high-z) |

### Alternate analog I/O board (`GX700-PWB(K)`)

Used by Kick &amp; Kick. Has several optocouplers, plus a DS2401 serial number
chip and several unpopulated footprints.

This board is currently undocumented.

### Fishing controller I/O board (`GE765-PWB(B)A`)

Used by the Fisherman's Bait series. Uses an NEC uPD4701 mouse/trackball chip to
track motion of the fishing reel's rotary encoders and contains PWM drivers for
the feedback motors. Along with the analog I/O board, it is the only known board
that does *not* have a DS2401.

This board is currently undocumented.

### DDR Karaoke Mix I/O board (`GX921-PWB(B)`)

Used by DDR Karaoke Mix 1 and 2. Similarly to the digital I/O board, this board
features several optoisolated light outputs, an ARCnet PHY and a DS2401 serial
number chip. It also has composite video inputs and outputs, a video encoder to
convert the 573's native RGB output to composite and additional circuitry to
superimpose it onto the video feed from an external karaoke machine. An onboard
PC16552 UART is provided to communicate with the machine (the security cartridge
also exposes SIO1).

This board is currently undocumented.

### GunMania I/O board (`PWB0000073070`)

Used by GunMania and GunMania Zone Plus. Contains an RGB to S-video converter
which drives the cabinet's projector, several motor drivers, optoisolators, a
PC16552 UART and a DS2401 serial number chip. A DB25 connector on the side of
the board is used to interface to the resistive matrix used to detect bullet
shots.

This board is currently undocumented.

### Hypothetical debugging board

There is no proof whatsoever of this board having ever existed, but the BIOS and
some games attempt to access the hardware on it. It seems to contain at least a
Fujitsu MB89371 UART and a 7-segment display, although these may have actually
been on two separate boards (or built into a prototype board used by Konami
during development).

The MB89371 does not have a publicly available datasheet.

#### `0x1f640000`: **UART data**

#### `0x1f640002`: **UART control**

#### `0x1f640004`: **UART baud rate select**

#### `0x1f640006`: **UART mode**

#### `0x1f640010`: **7-segment display**

| Bits | RW | Description                    |
| ---: | :- | :----------------------------- |
|    0 | W  | Right digit segment G (0 = on) |
|    1 | W  | Right digit segment F (0 = on) |
|    2 | W  | Right digit segment E (0 = on) |
|    3 | W  | Right digit segment D (0 = on) |
|    4 | W  | Right digit segment C (0 = on) |
|    5 | W  | Right digit segment B (0 = on) |
|    6 | W  | Right digit segment A (0 = on) |
|    7 |    | _Unused_                       |
|    8 | W  | Left digit segment G (0 = on)  |
|    9 | W  | Left digit segment F (0 = on)  |
|   10 | W  | Left digit segment E (0 = on)  |
|   11 | W  | Left digit segment D (0 = on)  |
|   12 | W  | Left digit segment C (0 = on)  |
|   13 | W  | Left digit segment B (0 = on)  |
|   14 | W  | Left digit segment A (0 = on)  |
|   15 |    | _Unused_                       |

Used by the BIOS kernel while booting (in a similar way to the standard PS1
kernel, which uses register `0x1f802041` instead) as well as the shell and some
games. This may have been meant to be a POST display integrated into the 573
main board at some point.

