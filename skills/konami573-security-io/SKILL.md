---
name: konami573-security-io
description: "Konami System 573: security cartridges (install, game, network), external modules (multisession/PCMCIA/HDD), BIOS, bootleg mod boards, game-specific technical notes, PCB pinouts. Use when working with System 573 security, BIOS, or game-specific details."
---

## Security cartridges

Most System 573 games use cartridges that plug into the slot on the right side
of the main board as an anti-piracy measure and/or to add game specific I/O
functionality (particularly for games that do not otherwise require any I/O
board). Cartridges typically contain a password protected EEPROM, used to store
game and installation information, and in some cases a DS2401 unique serial
number chip.

- [Electrical interface](#electrical-interface)
- [Cartridge EEPROM types](#cartridge-eeprom-types)
- [EEPROM-less cartridge variants](#eeprom-less-cartridge-variants)
- [X76F041 cartridge variants](#x76f041-cartridge-variants)
- [ZS01 cartridge variants](#zs01-cartridge-variants)
- [Cartridge identifiers](#cartridge-identifiers)

### Electrical interface

All communication with the cartridge is performed through the following means:

- an 8-bit parallel input port (`I0-I7`), readable via register `0x1f400004`;
- a latched 8-bit parallel output port (`D0-D7`), controlled by register
  `0x1f6a0000`;
- a single tristate I/O pin (`IO0`), which can be either configured as a
  floating input or set to output the same logic level as `D0` through register
  `0x1f500000`;
- the CPU's SIO1 interface (`TX`, `RX`, `/RTS`, `/CTS`, `/DTR`, `/DSR`);
- four bus handshaking lines (`IRDY`, `DRDY`, `/IREQ`, `/DACK`).

As all EEPROMs used in cartridges have an I2C interface rather than a parallel
one, `IO0` is used in combination with individual bits of the parallel I/O ports
to bitbang I2C. The SIO1 interface either goes unused or is translated to RS-232
voltage levels and broken out to a connector on the cartridge.

See the pinouts section for more information on the security cartridge slot.

#### Handshaking lines

The cartridge slot carries two status lines *unofficially* known as `IRDY` and
`DRDY` plus two inputs named `/IREQ` and `/DACK`, probably meant for
synchronization with cartridges that would actually use `D0-D7` and `I0-I7` as a
parallel data bus rather than to bitbang serial protocols. No currently known
cartridge uses these pins.

`DRDY` is set whenever the 573 writes to the output port, even if no bits have
actually changed. The cartridge can monitor this signal to know when to read a
byte from the port and then pull `/DACK` low to reset it. To send a byte to the
573 the cartridge can pulse `/IREQ`, which will cause `IRDY` to go high until
the 573 accesses the input port. The 573 can read the status of `IRDY` (as well
as `DRDY`) through the Konami ASIC and wait for it to be set before reading the
next byte.

The cartridge I/O ports can basically be thought of as a single-byte FIFO, with
`DRDY` being the "TX buffer full" flag and `IRDY` the "RX buffer not empty"
flag. The handshaking lines are implemented using a handful of 74LS74 flip
flops.

**NOTE**: the JVS MCU also has its own handshaking lines, `JVSIRDY` and
`JVSDRDY`, which are actually used and work in pretty much the same way. See the
JVS interface section for more information on communicating with the MCU.

#### Note about RTS/CTS

The PS1 CPU's SIO1 UART has hardware flow control and will not transmit data
until CTS is asserted. In order to get around this most cartridges tie CTS to
RTS, allowing it to be controlled in software. Cartridges that use the serial
port (i.e. ones with a network port) have the pins tied together on the PCB,
while other cartridge types usually break them out to a shorted 2-pin jumper.

Some earlier games that do not use SIO1 for networking purposes redirect their
debug logging output to it (by calling the `AddSIO()` function provided by the
Sony SDK) if CTS and RTS are shorted on startup. On later 573 motherboard
revisions, the SIO1 pins are additionally broken out to a separate connector
(`CN24`) and made accessible even when a cartridge without a network port is
inserted.

### Cartridge EEPROM types

Konami's security cartridge driver supports the following EEPROMs:

| Manufacturer     | Chip                                          | "Response to reset" ID    | Capacity  |
| :--------------- | :-------------------------------------------- | :------------------------ | --------: |
| Xicor            | [X76F041](#x76f041-cartridge-variants)        | `19 55 aa 55` (LSB first) | 512 bytes |
| Xicor            | X76F100                                       | `19 00 aa 55` (LSB first) | 112 bytes |
| Konami/Microchip | [ZS01 (PIC16CE625)](#zs01-cartridge-variants) | `5a 53 00 01` (MSB first) | 112 bytes |

**NOTE**: Konami seems to have never manufactured X76F100 cartridges, however
most games that expect an X76F041 can also use the X76F100 interchangeably. ZS01
support was only added in later versions of the driver.

#### ZS01 protocol

The "ZS01" EEPROM (also known as "NS2K001") is actually a PIC16 microcontroller
that mostly replicates the X76F100's functionality, allowing the 573 to store up
to 112 bytes of data protected by a 64-bit password. Unlike the X76F041 and
X76F100, which use plaintext commands, all communication with the ZS01 is
obfuscated using a rudimentary scrambling algorithm. A CRC16 is attached to each
packet and used to detect attempts to tamper with the obfuscation. Attempting to
send too many requests with an invalid CRC16 will cause the ZS01 to self-erase
and reset the password.

A ZS01 transaction can be broken down into the following steps:

1.  The 573 prepares a 12-byte packet to be sent to the ZS01, containing a
    command, address and payload:

    | Bytes | Description                                       |
    | ----: | :------------------------------------------------ |
    |     0 | Command flags                                     |
    |     1 | Address bits 0-7                                  |
    |   2-9 | Payload (data for writes, response key for reads) |
    | 10-11 | CRC16 of bytes 0-9, big endian                    |

    The first byte is a 3-bit bitfield encoding the command and access type:

    | Bits | Description                                    |
    | ---: | :--------------------------------------------- |
    |    0 | Command (0 = write/erase, 1 = read)            |
    |    1 | Address bit 8 (unused, should be 0)            |
    |    2 | Access type (0 = unprivileged, 1 = privileged) |
    |  3-7 | Unused? (should be 0)                          |

    The access type bit specifies whether the command is privileged. Privileged
    commands require the ZS01's current password, while unprivileged commands do
    not.

    The address must be one of the following values:

    | Address     | Length   | Privileged | Description                                |
    | :---------- | -------: | :--------- | :----------------------------------------- |
    | `0x00-0x03` | 32 bytes | No         | Unprivileged data area                     |
    | `0x04-0x0e` | 80 bytes | Yes        | Privileged data area                       |
    | `0xfc`      |  8 bytes | No         | Internal ZS01 serial number                |
    | `0xfd`      |  8 bytes | No         | External DS2401 serial number              |
    | `0xfd`      |  8 bytes | Yes        | Erases data area when written (write-only) |
    | `0xfe`      |  8 bytes | Yes        | Configuration registers                    |
    | `0xff`      |  8 bytes | Yes        | New password (write-only)                  |

    Data is always read or written in aligned 8 byte blocks. Unprivileged areas
    can be read using either a privileged or unprivileged read command, but
    writing to them still requires a privileged write command.

2.  If the command is a read command, a random 8-byte "response key" is
    generated (typically as an MD5 hash of the current time from the RTC) and
    written to the payload field; the ZS01 will later use it to encrypt the
    returned data as a replay attack prevention measure. For write commands, the
    payload field is populated with the 8 bytes to be written.

3.  A CRC16 is calculated over the first 10 bytes of the packet and stored in
    the last 2 bytes in big endian format. The CRC is computed as follows:

    ```c
    #define ZS01_CRC16_POLYNOMIAL 0x1021

    uint16_t zs01_crc16(const uint8_t *data, size_t length) {
        uint16_t crc = 0xffff;

        for (; length; length--) {
            crc ^= *(data++) << 8;

            for (int bit = 8; bit; bit--) {
                uint16_t temp = crc;

                crc <<= 1;
                if (temp & (1 << 15))
                    crc ^= ZS01_CRC16_POLYNOMIAL;
            }
        }

        return (~crc) & 0xffff;
    }
    ```

4.  If the command is privileged, the 573 scrambles the payload field with the
    chip's currently set password, using the following algorithm:

    ```c
    // Note that this state is preserved across calls to zs01_scramble_payload()
    // and must be updated when a response is received (see step 8).
    uint8_t zs01_scrambler_state = 0;

    void zs01_scramble_payload(
        uint8_t *output, const uint8_t *input, size_t length,
        const uint8_t *password
    ) {
        for (; length; length--) {
            int value = *(input++) ^ zs01_scrambler_state;
            value     = (value + password[0]) & 0xff;

            for (int i = 1; i < 8; i++) {
                int add   = password[i] & 0x1f;
                int shift = password[i] >> 5;

                int shifted = value << shift;
                shifted    |= value >> (8 - shift);
                shifted    &= 0xff;

                value = (shifted + add) & 0xff;
            }

            zs01_scrambler_state = value;
            *(output++)          = value;
        }
    }
    ```

    The CRC16 is *not* updated to reflect the new data. This step is skipped for
    unprivileged read commands.

5.  All 12 bytes of the packet are scrambled with a fixed "command key", using
    the following algorithm:

    ```c
    static const uint8_t ZS01_COMMAND_ADD[]   = { 237, 8, 16, 11, 6, 4, 8, 30 };
    static const uint8_t ZS01_COMMAND_SHIFT[] = {   0, 3,  2,  2, 6, 2, 2,  1 };

    void zs01_scramble_packet(
        uint8_t *output, const uint8_t *input, size_t length
    ) {
        // Unlike zs01_scramble_payload(), this state is *not* preserved across
        // calls.
        uint8_t state = 0xff;

        output += length;
        input  += length;

        for (; length; length--) {
            int value = *(--input) ^ state;
            value     = (value + ZS01_COMMAND_ADD[0]) & 0xff;

            for (int i = 1; i < 8; i++) {
                int shifted = value << ZS01_COMMAND_SHIFT[i];
                shifted    |= value >> (8 - ZS01_COMMAND_SHIFT[i]);
                shifted    &= 0xff;

                value = (shifted + ZS01_COMMAND_ADD[i]) & 0xff;
            }

            state       = value;
            *(--output) = value;
        }
    }
    ```

6.  The scrambled packet is sent to the ZS01, which will respond to the first 11
    bytes immediately with an I2C ACK and to the last byte with an ACK after a
    short delay. The 573 then proceeds to read 12 bytes from the ZS01, issuing
    an I2C ACK for each byte received up until the last one.

7.  The 573 uses the response key generated in step 2 to unscramble the packet
    returned by the ZS01. The unscrambling algorithm is the same one used in
    step 5, applied in reverse:

    ```c
    void zs01_unscramble_packet(
        uint8_t *output, const uint8_t *input, size_t length,
        const uint8_t *response_key
    ) {
        uint8_t state = 0xff;

        output += length;
        input  += length;

        for (; length; length--) {
            int value      = *(--input);
            int last_state = state;
            state          = value;

            for (int i = 1; i < 8; i++) {
                int add   = response_key[i] & 0x1f;
                int shift = response_key[i] >> 5;

                int subtracted = (value - add) & 0xff;

                value  = subtracted >> shift;
                value |= subtracted << (8 - shift);
                value &= 0xff;
            }

            value       = (value - response_key[0]) & 0xff;
            *(--output) = value ^ last_state;
        }
    }
    ```

    For write commands, the response key required to unscramble the packet is
    the one sent as part of the last read command issued. For read commands, the
    ZS01 may either use the key provided in the payload field or the one from
    the last read command issued; Konami's code tries unscrambling responses
    with both.

8.  The unscrambled packet will contain the following fields:

    | Bytes | Description                                |
    | ----: | :----------------------------------------- |
    |     0 | Status code (0 = success, 1-5 = error)     |
    |     1 | New payload scrambler state                |
    |   2-9 | Payload (empty for writes, data for reads) |
    | 10-11 | CRC16 of bytes 0-9, big endian             |

    The 573 proceeds to compute the CRC16 of the first 10 bytes. If it does not
    match the one in the packet, it will try unscrambling the packet with a
    different response key (see step 7) before giving up. Otherwise, the global
    `zs01_scrambler_state` variable from step 4 is set to the value of byte 1,
    regardless of whether the status code is zero or not.

    The exact meaning of non-zero status codes is currently unknown.

### EEPROM-less cartridge variants

#### Hyper Bishi Bashi Champ 3-player cartridge (`GX700-PWB(E)`)

This is the only known cartridge type that has no EEPROM (although the PCB does
have an unpopulated X76F041 footprint). It has no plastic case, as it's meant to
be enclosed in the same case as the 573 itself. It has open-drain outputs for
driving up to 12 lights, arranged as 3 banks of 4 outputs each (one bank for
each player's buttons), plus an RS-232 transceiver for SIO1. The following pins
are used:

| Name   | Dir | Usage                                            |
| :----- | :-- | :----------------------------------------------- |
| `TX`   | O   | `TX` to network port (via RS-232 transceiver)    |
| `RX`   | I   | `RX` from network port (via RS-232 transceiver)  |
| `/RTS` | O   | Shorted to `/CTS` to enable SIO1                 |
| `/CTS` | I   | Shorted to `/RTS` to enable SIO1                 |
| `/DSR` | I   | Cartridge insertion detection (grounded)         |
| `D0`   | O   | Updates/latches bank 3 when pulsed               |
| `D1`   | O   | Updates/latches bank 2 when pulsed               |
| `D3`   | O   | Updates/latches bank 1 when pulsed               |
| `D4`   | O   | Data for light output 0 (green button)           |
| `D5`   | O   | Data for light output 1 (blue button)            |
| `D6`   | O   | Data for light output 2 (red button)             |
| `D7`   | O   | Data for light output 3 (start button)           |
| `?`    | O   | `DTR` to network port (via RS-232 transceiver)   |
| `?`    | I   | `DSR` from network port (via RS-232 transceiver) |

This cartridge has three connectors:

- `CN2` (5-pin): RS-232 port. Note that this port is *not* electrically isolated
  and shares its ground with the 573, unlike all other cartridges with an RS-232
  connector.
- `CN3` (16-pin): breaks out the light outputs and the incoming 12V supply from
  `CN4`.
- `CN4` (4-pin): 12V power input, connected through a short cable to `CN17` on
  the 573 main board.

### X76F041 cartridge variants

All X76F041 cartridges use the following pins:

| Name   | Dir | Usage                                                |
| :----- | :-- | :--------------------------------------------------- |
| `/DSR` | I   | Cartridge insertion detection (grounded)             |
| `D0`   | O   | Drives X76F041 I2C `SDA` when `IO0` is set as output |
| `D1`   | O   | X76F041 I2C `SCL`                                    |
| `D2`   | O   | X76F041 chip select (`/CS`)                          |
| `D3`   | O   | X76F041 reset (`RST`)                                |
| `IO0`  | IO  | X76F041 I2C `SDA` readout                            |

X76F041 cartridges equipped with a DS2401 additionally use the following pins:

| Name   | Dir | Usage                                  |
| :----- | :-- | :------------------------------------- |
| `D4`   | O   | Drives 1-wire bus low when pulled high |
| `I6`   | I   | DS2401 1-wire bus readout              |

#### Generic cartridge (`GX700-PWB(D)`)

Rectangular cartridge used by the earliest 573 games and as a separate
installation key for some later games. Contains only the X76F041 EEPROM and no
DS2401, but the PCB has an unpopulated footprint for an unknown 64-pin TQFP
part.

#### Generic cartridge with DS2401 (`GX894-PWB(D)`)

Rectangular cartridge similar to `GX700-PWB(D)` but equipped with a DS2401. The
PCB has two unpopulated SOIC footprints, one of which may possibly be for an
X76F100 or another I2C EEPROM.

#### Early serial port cartridge (`GX896-PWB(A)A`)

Seems to be an older variant of the more common `GX883-PWB(D)` cartridge, with
the same ports but no DS2401. As with the 3-player Bishi Bashi cartridge, it has
no case and is instead meant to sit inside the 573's own case.

| Name   | Dir | Usage                                            |
| :----- | :-- | :----------------------------------------------- |
| `TX`   | O   | `TX` to network port (via RS-232 transceiver)    |
| `RX`   | I   | `RX` from network port (via RS-232 transceiver)  |
| `/RTS` | O   | Shorted to `/CTS` to enable SIO1                 |
| `/CTS` | I   | Shorted to `/RTS` to enable SIO1                 |
| `?`    | O   | `CTRL0` to control port                          |
| `?`    | O   | `CTRL1` to control port                          |
| `?`    | O   | `CTRL2` to control port                          |
| `?`    | O   | `DTR` to network port (via RS-232 transceiver)   |
| `?`    | I   | `DSR` from network port (via RS-232 transceiver) |

This cartridge has two connectors:

- `CN2` (5-pin): electrically isolated RS-232 port. The transceiver is powered
  by an isolated DC-DC module and all signals going from/to the 573 are
  optoisolated.
- `CN3` (6-pin): three 5V logic level signals, used in some cabinets to control
  lights or the speaker amplifier.

#### Serial port cartridge with DS2401 (`GX883-PWB(D)`)

T-shaped cartridge with a DS2401, a "network" (RS-232) port and a "control" or
"amp box" port, commonly used by pre-ZS01 Bemani games. Uses the following pins:

| Name   | Dir | Usage                                            |
| :----- | :-- | :----------------------------------------------- |
| `TX`   | O   | `TX` to network port (via RS-232 transceiver)    |
| `RX`   | I   | `RX` from network port (via RS-232 transceiver)  |
| `/RTS` | O   | Shorted to `/CTS` to enable SIO1                 |
| `/CTS` | I   | Shorted to `/RTS` to enable SIO1                 |
| `?`    | O   | `CTRL0` to control port                          |
| `?`    | O   | `CTRL1` to control port                          |
| `?`    | O   | `CTRL2` to control port                          |
| `?`    | O   | `DTR` to network port (via RS-232 transceiver)   |
| `?`    | I   | `DSR` from network port (via RS-232 transceiver) |

This cartridge has two connectors:

- Network (5-pin, unlabeled on PCB): electrically isolated RS-232 port. The
  transceiver is powered by an isolated DC-DC module and all signals going
  from/to the 573 are optoisolated.
- Control/amp box (6-pin, unlabeled on PCB): three 5V logic level signals, used
  in some cabinets to control lights or the speaker amplifier.

#### PunchMania cartridge (`GX700-PWB(J)`)

T-shaped cartridge used only by PunchMania/Fighting Mania series. Contains an
X76F041, a DS2401 and an ADC0838 used to measure up to 8 analog inputs. The ADC
uses the following pins:

| Name | Dir | Usage                                                 |
| :--- | :-- | :---------------------------------------------------- |
| `D0` | O   | Chip select to ADC (`/CS`), shared with X76F041 `SDA` |
| `D1` | O   | Data clock to ADC (`CLK`), shared with X76F041 `SCL`  |
| `D5` | O   | Data input to ADC (`DI`)                              |
| `I0` | I   | Data output from ADC (`DO`)                           |
| `I1` | I   | SAR status from ADC (`SARS`)                          |

This cartridge has two connectors:

- Unknown (12-pin): analog input connector. As with the ADC built into the 573
  motherboard there seems to be no protection on the inputs, so only voltages in
  0-5V range are accepted.
- `CN4` (10-pin): unknown purpose. Seems to be always unpopulated.

#### Hyper Bishi Bashi Champ 2-player cartridge (`PWB0000068819`)

T-shaped cartridge with open-drain outputs for driving up to 8 lights, arranged
as 2 banks of 4 outputs each. Unlike the `GX700-PWB(E)` 3-player variant, it has
an X76F041 (but no DS2401), lacks the RS-232 port and does not seem to be
designed to be mounted inside the 573. The latches driving the light outputs use
the following pins:

| Name | Dir | Usage                                  |
| :--- | :-- | :------------------------------------- |
| `?`  | O   | Updates/latches bank 1 when pulsed     |
| `?`  | O   | Updates/latches bank 2 when pulsed     |
| `?`  | O   | Data for light output 0 (green button) |
| `?`  | O   | Data for light output 1 (blue button)  |
| `?`  | O   | Data for light output 2 (red button)   |
| `?`  | O   | Data for light output 3 (start button) |

This cartridge has two connectors:

- `CN2` (16-pin): breaks out the light outputs and the incoming 12V supply from
  `CN3`.
- `CN3` (4-pin): 12V power input, presumably connected to the power supply
  externally (i.e. not through the main board).

#### Salary Man Champ cartridge (`PWB0000088954`)

T-shaped cartridge with open-drain outputs for driving up to 8 lights (although
only 6 outputs seem to be populated). Contains an X76F041, a DS2401 and two 4094
shift registers, presumably chained. The shift registers use the following pins:

| Name | Dir | Usage                |
| :--- | :-- | :------------------- |
| `D5` | O   | Shift register clock |
| `D6` | O   | Shift register reset |
| `D7` | O   | Shift register data  |

This cartridge has two connectors:

- Unlabeled (16-pin): breaks out the light outputs and the incoming 12V supply.
- Unlabeled (4-pin): 12V power input, presumably connected to the power supply
  externally (i.e. not through the main board).

### ZS01 cartridge variants

All ZS01 cartridges use the following pins:

| Name   | Dir | Usage                                             |
| :----- | :-- | :------------------------------------------------ |
| `/DSR` | I   | Cartridge insertion detection (grounded)          |
| `D0`   | O   | Drives ZS01 I2C `SDA` when `IO0` is set as output |
| `D1`   | O   | ZS01 I2C `SCL`                                    |
| `D3`   | O   | ZS01 reset                                        |
| `IO0`  | IO  | ZS01 I2C `SDA` readout                            |

All cartridges are fitted with a DS2401, however it is connected to a GPIO pin
on the ZS01 rather than being directly exposed to the 573. The ZS01 additionally
provides its own unique serial number, which seems to be unused by games.

#### Serial port cartridge (`GE949-PWB(D)A`)

ZS01 variant of the `GX883-PWB(D)` cartridge. Uses the following pins:

| Name   | Dir | Usage                                            |
| :----- | :-- | :----------------------------------------------- |
| `TX`   | O   | `TX` to network port (via RS-232 transceiver)    |
| `RX`   | I   | `RX` from network port (via RS-232 transceiver)  |
| `/RTS` | O   | Shorted to `/CTS` to enable SIO1                 |
| `/CTS` | I   | Shorted to `/RTS` to enable SIO1                 |
| `?`    | O   | `CTRL0` to control port                          |
| `?`    | O   | `CTRL1` to control port                          |
| `?`    | O   | `CTRL2` to control port                          |
| `?`    | O   | `DTR` to network port (via RS-232 transceiver)   |
| `?`    | I   | `DSR` from network port (via RS-232 transceiver) |

This cartridge has two connectors:

- Network (5-pin, unlabeled on PCB): electrically isolated RS-232 port. The
  transceiver is powered by an isolated DC-DC module and all signals going
  from/to the 573 are optoisolated.
- Control/amp box (6-pin, unlabeled on PCB): three 5V logic level signals, used
  in some cabinets to control lights or the speaker amplifier.

#### Stripped down serial port cartridge (`GE949-PWB(D)B`)

T-shaped cartridge that uses the same PCB as `GE949-PWB(D)A` but only has the
ZS01, DS2401 and supporting parts are populated. Used by games that do not need
the RS-232 interface.

### Cartridge identifiers

Most games use the security cartride's EEPROM to store, among other data such as
the game code and region, a set of up to four 8-byte identifiers.

#### SID (silicon/serial ID?)

The serial number of the cartridge's DS2401, always present in cartridges that
have one. As per the 1-wire specification it has the following format:

| Bytes | Description                                     |
| ----: | :---------------------------------------------- |
|     0 | 1-wire family code (`0x01` for DS2401)          |
|   1-6 | 48-bit progressive serial number, little endian |
|     7 | CRC8 of bytes 0-6                               |

The CRC is computed as follows:

```c
#define DS2401_CRC8_POLYNOMIAL 0x8c

uint8_t ds2401_crc8(const uint8_t *data, size_t length) {
    uint8_t crc = 0;

    for (; length; length--) {
        uint8_t value = *(data++);

        for (int bit = 8; bit; bit--) {
            uint8_t temp = crc ^ value;

            value >>= 1;
            crc   >>= 1;
            if (temp & 1)
                crc ^= DS2401_CRC8_POLYNOMIAL;
        }
    }

    return crc & 0xff;
}
```

Refer to the DS2401 datasheet and Maxim 1-wire documentation for more details.

#### TID (trace ID)

Seems to be a cartridge-type-agnostic serial number. On cartridges without a
DS2401 the trace ID is assigned by Konami at manufacture time (see the master
calendar section) and has the following format:

| Bytes | Description                                   |
| ----: | :-------------------------------------------- |
|     0 | Trace ID type (`0x81`)                        |
|   1-2 | 16-bit "main" serial number, big endian       |
|   3-6 | 32-bit "sub" serial number, big endian        |
|     7 | Checksum (sum of bytes 0-6 xor'd with `0xff`) |

On cartridges with a DS2401 the trace ID is instead derived from the SID:

| Bytes | Description                                                       |
| ----: | :---------------------------------------------------------------- |
|     0 | Trace ID type (`0x82`)                                            |
|   1-2 | DS2401 serial number hash, big or little endian depending on game |
|   3-6 | _Reserved_ (must be 0)                                            |
|     7 | Checksum (sum of bytes 0-6 xor'd with `0xff`)                     |

The hash is calculated over bytes 1-6 of the SID (excluding the family code and
CRC8) using the following algorithm:

```c
// Note that some games set this to 14 instead of 16.
#define TRACE_ID_HASH_BIT_WIDTH 16

uint16_t trace_id_hash(const uint8_t *data, size_t length) {
    uint16_t hash = 0;

    for (size_t i = 0; i < (length * 8); i += 8) {
        uint8_t value = *(data++);

        for (size_t j = i; j < (i + 8); j++, value >>= 1) {
            if (value & 1)
                hash ^= 1 << (j % TRACE_ID_HASH_BIT_WIDTH);
        }
    }

    return hash;
}
```

#### MID (medium ID?)

Seems to be some kind of cartridge type flag, possibly indicating whether the
cartridge shall be used during or after game installation, or if it was used
when performing a game upgrade and shall no longer be usable to run the game it
initially shipped with.

| Bytes | Description                                       |
| ----: | :------------------------------------------------ |
|     0 | Cartridge type? (always `0x00`, `0x01` or `0x02`) |
|   1-6 | _Reserved_ (must be 0)                            |
|     7 | Checksum (sum of bytes 0-6 xor'd with `0xff`)     |

**NOTE**: `00 00 00 00 00 00 00 00` seems to be a valid MID value, despite
having an otherwise invalid checksum, and to have a different meaning from
`00 00 00 00 00 00 00 ff`.

#### XID (external ID?)

The serial number of the digital I/O board's DS2401, written to the cartridge
during installation by most games that use it in order to prevent reinstallation
on a different system. Has the same format as the SID. On a cartridge that has
not yet been paired to a 573 the XID is set to `00 00 00 00 00 00 00 00`.

When finishing installation or attempting to use a cartridge with a mismatching
XID the game will display the digital I/O board's serial number as an 8-digit
value (`XXXX-YYYY`), generated as follows:

```c
// Some games seem to only use the lower 32 bits of the DS2401's serial number,
// while others use all 48 bits.
size_t xid_to_string_32(char *output, const uint8_t *xid) {
    uint32_t value = 0
        | (xid[1] <<  0)
        | (xid[2] <<  8)
        | (xid[3] << 16)
        | (xid[4] << 24);

    int high = (value / 10000) % 10000;
    int low  = value % 10000;

    return sprintf(output, "%04d-%04d", high, low);
}

size_t xid_to_string_48(char *output, const uint8_t *xid) {
    uint64_t value = 0
        | (xid[1] <<  0)
        | (xid[2] <<  8)
        | (xid[3] << 16)
        | (xid[4] << 24)
        | (xid[5] << 32)
        | (xid[6] << 40);

    int high = (int) ((value / 10000) % 10000);
    int low  = (int) (value % 10000);

    return sprintf(output, "%04d-%04d", high, low);
}
```

Cartridges for games that use the digital I/O board typically come with a blank
label onto which the 8-digit ID can be written by the operator, to help keep
track of which cartridge goes into which system after installation.

Note that games that use other I/O boards with a DS2401, such as Kick &amp; Kick
and DDR Karaoke Mix, do not seem to write those boards' serial numbers to the
cartridge; they are stored in the internal flash memory instead.

## External modules

Over the 573's lifetime Konami introduced several add-ons that extended its
functionality. Unlike the I/O boards, these were external to the 573 unit and
not always mandatory. Not much is currently known about any of these.

### Relay board (`GN845-PWB(A)`)

A relatively simple lamp driver board, controlled by the optoisolated outputs
from the analog or digital I/O board. Commonly mounted in a metal box alongside
audio amplifier boards in most cabinets.

### DDR stage I/O board (`GN845-PWB(B)`)

Sits between the 573 and the sensors in each stage's arrow panels in Dance
Dance Revolution cabinets. It is based on a Xilinx XC9536 CPLD and allows the
573 to check the status of a specific pressure sensor (each panel has 4
sensors, one along each edge), in addition to ensuring DDR games can only be
played with an actual stage rather than just a joystick or buttons wired up to
the 573's JAMMA connector. Konami kept using the same board long after the 573
was discontinued, with the last game to use it being DDR X/X2 (PC based).

Each stage's board communicates with the 573 over 6 wires, of which 4 are the
up/down/left/right signals going to the JAMMA connector and 2 are light outputs
from the I/O board being misused as data and clock lines (see above). The board
initially asserts the right and up signals and waits for the 573 to issue an
initialization command by bitbanging it over the light outputs. Received bits
are acknowledged by the board by echoing them on the right signal and toggling
the up signal.

Once initialization is done the board goes into passthrough mode, asserting the
up/down/left/right signals whenever any of the respective arrow panels' sensors
are pressed. The 573 can issue another command to retrieve the status of each
sensor separately, which is then sent by the board in serialized form over the
right and up signals. DDR games only use this command to display sensor status
in the operator menu, no commands are sent to the board during actual gameplay.

The initialization protocol is currently unknown. The protocol used after
initialization is partially known (see links) but needs to be verified and
documented properly.

### PS1 controller and memory card adapter (`GE885-PWB(A)`)

A ridiculously overengineered JVS board providing support for accessing PS1
controllers and memory cards plugged into ports on the front of the cabinet.
Contains a Toshiba TMPR3904 CPU, a Xilinx XCS10XL Spartan-XL FPGA, 512 KB of RAM
and a 512 KB boot ROM; the ROM is only a small bootloader and the actual
firmware is downloaded from the 573 into RAM. There are also two connectors for
security dongles. Returns the following JVS identifier string:

```
KONAMI CO.,LTD.;White I/O;Ver1.0;White I/O PCB
```

Memory card support became common in later Bemani games, allowing players to
save their scores and play custom charts. GuitarFreaks is the only game known
to support external controllers through this board.

### PunchMania 2 PCMCIA splitter (`PWB0000085445`)

Combines two 32 MB PCMCIA flash cards into the same address space, allowing them
to be accessed as if they were a single 64 MB card. Connects to the 573 through
a cable that plugs into a passive PCMCIA slot adapter. Only used by PunchMania
2.

### e-Amusement network unit (`PWB0000100991`)

Used by some Bemani games, in particular later GuitarFreaks and DrumMania
releases. Provides networking functionality (DHCP and TCP/UDP sockets) as well
as a 10 or 20 GB IDE hard drive for storage of downloaded content. The module
contains a Toshiba TMPR3927 CPU, a Xilinx XC2S100 Spartan-2 FPGA, 16 MB of RAM,
a 512 KB boot ROM and a DP83815 PCI Ethernet MAC. As with the controller and
memory card adapter, the bulk of the firmware seems to be loaded from the 573.
Connects through PCMCIA slot 2, using the same cable and adapter as the
PunchMania PCMCIA splitter.

### Multisession unit (`GXA25-PWB(A)`)

A fairly large box containing a Toshiba TMPR3927 CPU, a Xilinx XC2S200 Spartan-2
FPGA and four (!) hardware MP3 decoders. It comes with up to four daughterboards
installed, each of which hosts a stereo DAC and has RCA jacks for audio input
and output plus a mini-DIN connector for RS-232 communication with a cabinet.
The box also has its own ATAPI CD-ROM drive and power supply.

Its purpose is to enable "session mode" in later Bemani games, which allows for
the same song to be played on multiple games at the same time with the box
playing the backing tracks and routing audio between the machines. It connects
to each cabinet's 573 using RS-232, through the "network" port on the security
cartridge.

### Master calendar

A JVS device used internally by Konami to initialize motherboards and security
cartridges during manufacturing. The exact hardware Konami used is unknown, but
the protocol can be inferred from game code. All games search the JVS bus on
startup and enter a "factory test" mode if any device with the following
identifier string is present:

```
KONAMI CO.,LTD.;Master Calendar;<any value>;<any value>
```

The game will then proceed to request the current date, time, game and region
information from the master calendar, initialize the RTC and program the
security cartridge. The master calendar also returns a unique trace ID (see the
cartridge data formats section) for each 573, used for identification purposes
on cartridges that lack a DS2401.

#### `0x70`: **Get date and time**

#### `0x71`: **Get game region or initialization data**

#### `0x7c, 0x7f, 0x00`: **Get trace ID "main" serial number**

#### `0x7c, 0x80, 0x00`: **Get trace ID "sub" serial number**

#### `0x7d, 0x80, 0x10`: **Get next ID**

#### `0x7e`: **Set DS2401 identifiers**

#### `0x7f`: **Unknown**

#### `0xf0`: **Reset master calendar**

## BIOS

The System 573 BIOS is based on a slightly modified version of Sony's standard
PS1 kernel, plus a custom shell executable.

- [Shell revisions](#shell-revisions)
- [Kernel differences](#kernel-differences)
- [Boot sequence](#boot-sequence)
- [Command-line arguments](#command-line-arguments)
- [JVS MCU test sequence](#jvs-mcu-test-sequence)
- [DVD-ROM support](#dvd-rom-support)
- [Scrapped CF card support](#scrapped-cf-card-support)

### Shell revisions

There seem to be either three or four different versions of the BIOS, all of
which share the same kernel but feature different shells:

| ROM marking | MAME ROM name         | SHA-1                                      | Used by                       |
| :---------- | :-------------------- | :----------------------------------------- | :---------------------------- |
| `700A01`    | `700a01.22g`          | `e1284add4aaddd5337bd7f4e27614460d52b5b48` | Most games                    |
| `700A01`    | `700a01,gchgchmp.22g` | `9aab8c637dd2be84d79007e52f108abe92bf29dd` | Gachagachamp                  |
| `700A01`    |                       |                                            | Unknown (undumped, see below) |
| `700B01`    | `700b01.22g`          | `a2421d0a494892c0e71003c96995ce8f945064dd` | Dancing Stage EuroMIX 2       |

`700A01` is the earliest and most common version. The only difference between
the two known variants of it is that they were linked to slightly different Sony
SDK releases; Konami's own code is identical across the two. There reportedly is
a third variant that shipped on systems that came with the JVS MCU unpopulated
(presumably it would skip the check for it), however no evidence of its
existence has ever been found. The shell is stored in ROM in both variants at
`0xbfc40000`, in the form of a standard PS1 executable (including the header)
that gets loaded at `0x803c0000` by the kernel.

`700B01` has a more complicated structure: it is split up into two separate
executables, one (at `0xbfc28000`, loaded at `0x80010000`) in charge of running
the self-test sequence and the other (at `0xbfc60000`, loaded at `0x80380000`)
handling CD-ROM or flash booting. The overall coding style suggests that it was
developed alongside the installers/launchers used by later Bemani games, but
dropped as the main feature it would have introduced over the `700A01` shell -
CF card support - was broken due to a PCB wiring mistake.

### Kernel differences

The kernel in both the `700A01` and `700B01` shells identifies itself as
`Konami OS by T.H.` with a 1995-09-01 build date. All other Konami PS1-based
arcade boards, with the exception of the Twinkle System, use a kernel with the
same identifier and date (but potentially different code). The kernels used by
other manufacturers' arcade boards also contain the same `T.H.` initials,
possibly hinting at the fact there was a single Sony employee in charge of
providing customized kernels to all arcade system manufacturers.

While the 573's kernel is functionally identical to its retail counterpart
(aside from its lack of support for the PS1's CD-ROM drive), several parts of it
have been slightly tweaked to account for the hardware:

- Most CD-ROM APIs and the ISO9660 filesystem driver seem to have been purged.
- The code to parse `SYSTEM.CNF` and launch the boot executable from the CD-ROM
  has been made inaccessible. The shell handles executable loading and booting
  on its own, without ever returning to the kernel.
- The kernel initializes the EXP1 region and clears the watchdog periodically
  while booting. It does *not* keep clearing it in the background (e.g. from the
  exception handler) once the shell is loaded.
- `700B01` performs a "memory initialization" sequence that fills various RAM
  areas with pseudorandom values (possibly for heap debugging purposes), showing
  `c1` through `c7` on the debugging board's 7-segment display in the process.
- `700B01` reads register `0x1f40000e` to determine which RAM footprints on the
  board are populated, then configures the main RAM controller accordingly.
- The GPU is reset and a series of color bars is displayed while the shell is
  being relocated to RAM. This feature is also present in other non-retail
  kernels such as the DTL-H2000's.
- The shell is launched through a stub that contains a
  `Lisenced by Sony Computer Entertainment Inc.(SCEI)` \[sic\] string, validated
  by the kernel in a similar (but not identical) way to PS1 expansion port ROMs.

### Boot sequence

All variants of the shell are far simpler than their PS1 counterparts, as they
lack any kind of UI (aside from a non-interactive status screen) and have *no*
*copy protection or anti-piracy checks* of any kind. Once loaded by the kernel,
they start by initializing the system bus and proceed to run a hardware
self-test. The outcome of all checks is displayed on screen, with the following
ones being performed:

- `22G`: BIOS ROM integrity check. A checksum is computed and verified against
  the one present in the ROM at `0xbfc7fffc-0xbfc7ffff`;
- `16H`, `16G`, `14H`, `14G`: main RAM read/write test (first row of chips on
  the board, closest to the CPU);
- `12H`, `12G`, `9H`, `9G`: main RAM read/write test (second row of chips on the
  board, closest to the JAMMA connector);
- `4L`, `4P`: VRAM read/write test. This causes the 573 to briefly display
  random pixels as framebuffers are overwritten during the check;
- `10Q`: SPU RAM read/write test;
- `18E`: JVS MCU reset and status check;
- `CDR`: ATAPI CD-ROM drive initialization and executable loading.

**NOTE**: `700A01` shells do not actually test `4P`! The GPU starts up in 1 MB
VRAM mode by default and the shell does not enable the chip select for the
second bank, so the first VRAM chip is tested twice instead. This bug was fixed
in the `700B01` shell, which initializes the GPU correctly.

If any check fails the shell locks up, shows a blinking "HARDWARE ERROR...
RESET" prompt and stops clearing the watchdog after a few seconds, causing the
573 to reboot. Otherwise, the state of DIP switch 4 is checked and the shell
attempts to load an executable from four different sources in the following
order:

- PCMCIA flash card in slot 2 (if inserted and DIP switch 4 is on);
- PCMCIA flash card in slot 1 (if inserted and DIP switch 4 is on);
- Internal flash memory (if DIP switch 4 is on);
- `PSX.EXE` in the root directory of the disc inserted in the CD-ROM drive. The
  drive is only initialized after booting from flash or PCMCIA fails or if DIP
  switch 4 is off, thus the shell will not error out if a drive is not connected
  but a boot executable is present on the flash. Note that the drive must be set
  up as an IDE primary/master device using the appropriate jumpers.

As with Sony's PS1 shell, the 573 shell's ISO9660 filesystem driver only
implements a minimal subset of the specification and may not properly support
non-8.3 file names. It also **only allocates 2 KB for the disc's path table**,
so the total number of directories on the disc must be kept to a minimum in
order to prevent the shell from crashing. Unlike the PS1, however, the 573
ignores `SYSTEM.CNF` completely regardless of whether or not it is present on
the disc; the shell is hardcoded to always load `PSX.EXE`. Homebrew discs can
take advantage of this behavior to provide separate PS1 and 573 executables
instead of detecting the system type at runtime.

If DIP switch 4 is on, the shell expects to find a standard PS1 executable
(including the full 2048-byte header) at offset `0x24` on either the built-in
flash memory or one of the two PCMCIA flash cards, preceded by a CRC32 checksum
of it at offset `0x20`. The CRC is stored in little endian format and is *not*
calculated on the whole executable, but rather only on bytes whose offsets are a
power of two (i.e. on bytes at `0x24 + 0`, `0x24 + 1`, `0x24 + 2`, `0x24 + 4`
and so on). The check is implemented as follows:

```c
#define EXE_CRC32_POLYNOMIAL 0xedb88320 // 0x04c11db7 bit-reversed

uint32_t exe_crc32(const uint8_t *data, size_t length) {
    size_t   offset = 0;
    uint32_t crc    = 0xffffffff;

    while (offset < length) {
        crc ^= data[offset];

        for (int bit = 8; bit; bit--) {
            uint16_t temp = crc;

            crc >>= 1;
            if (temp & 1)
                crc ^= EXE_CRC32_POLYNOMIAL;
        }

        if (offset)
            offset <<= 1;
        else
            offset = 1;
    }

    return ~crc;
}

#define DIP_SWITCH_PTR    ((const uint32_t *) 0x1f400004)
#define EXE_CRC32_PTR     ((const uint32_t *) 0x1f000020)
#define EXE_HEADER_PTR    ((const uint8_t  *) 0x1f000024)
// Offset of the "text section size" field within the executable header
#define EXE_TEXT_SIZE_PTR ((const uint32_t *) 0x1f000040)

bool is_exe_valid(void) {
    if (*DIP_SWITCH_PTR & (1 << 3)) // 1 = DIP switch off
        return false;
    if (memcmp(EXE_HEADER_PTR, "PS-X EXE", 8))
        return false;

    // BUG: the actual size of the executable including the header is
    // (2048 + *EXE_TEXT_SIZE_PTR), however neither the 700A01 nor 700B01 shells
    // take this into account and instead end up ignoring the executable's last
    // 2048 bytes.
    uint32_t crc = exe_crc32(EXE_HEADER_PTR, *EXE_TEXT_SIZE_PTR);

    return (crc == *EXE_DATA_PTR);
}
```

Installing a new game usually involves inserting the installation disc and
turning off DIP switch 4 in order to prevent the shell from booting the game
currently installed on the internal flash.

### Command-line arguments

PS1 executables are generally launched with CPU registers `$a0` and `$a1` set to
zero, in order to make sure programs that interpret them as `argc` and `argv`
respectively will not crash by trying to parse invalid data. The `700A01` shell
follows this convention.

The `700B01` shell, however, does pass two arguments to the executable it loads.
`$a0` is thus set to 2, while `$a1` is set to point to an array containing
pointers to the following strings:

- `boot.rom=700B01`
- `boot.from=<device>`, where `<device>` is one of the following:
  - `flash.0` (internal flash memory)
  - `flash.1` (PCMCIA flash card in slot 1)
  - `flash.2` (PCMCIA flash card in slot 2)
  - `ata.2` (CF card in slot 2)
  - `cdrom`

The launchers used by later Bemani games use these arguments if present to
determine where to load the main game executable from, and fall back to
autodetecting the game's installation location otherwise.

### JVS MCU test sequence

The JVS MCU check is implemented in a different way between the two shell
revisions. While the `700A01` shell simply resets the MCU and validates the
status and error codes, the `700B01` self-test sequence performs 35 (!)
different checks, each validating the codes returned under different conditions.
The following tests are done:

1.  Reset MCU, clear `JVSIRDY`, ensure that:
    - status code = 0
    - error code = 3
    - `JVSIRDY` = 0
    - `JVSDRDY` = 0
    - incoming JVS data = `0x0000`
2.  Reset MCU, write valid dummy packet header (`0x00e0`), ensure that:
    - status code = 2
    - error code = 3
3.  Reset MCU, write invalid dummy packet header (`0x001f`), ensure that:
    - status code = 2
    - error code = 2
4.  Reset MCU, write 16 dummy packets (`0x1fe0`, `0x0004`, `1 << i`, checksum),
    for each packet ensure that:
    - status code = 1
    - error code = 3
5.  Reset MCU, write 16 dummy packets (same as above) with an invalid checksum,
    for each packet ensure that:
    - status code = 1
    - error code = 1

It is currently unclear if any data is actually sent to the JVS bus during step
4, as the shell may reset the MCU it before it starts sending the packet.

### DVD-ROM support

Even though neither of the shell versions was explicitly designed with DVD-ROM
support in mind, it *is* possible to run games from a DVD-ROM thanks to the fact
that the ATAPI commands used by the shell and games to read sectors from the
disc are medium-agnostic. Games that rely on CD-DA playback obviously cannot be
put on a DVD, however all other games (including ones that rely on the digital
I/O board for MP3 playback) will work as long as the disc is formatted as if it
were a typical 573 CD-ROM (ISO9660 with no extensions, no UDF, 8.3 file names
and a path table smaller than 2 KB).

**NOTE**: due to ATAPI incompatibility issues only a very limited number of
DVD-ROM drives will actually be recognized and work properly with the shells and
games. This is unrelated to the DVD format itself and is purely due to the fact
that, unlike CD-ROM drives, most DVD drives were manufactured after the ATAPI
specification got updated in a way that broke the 573's compatibility.

This accidental capability was greatly abused by bootleg Bemani "superdiscs"
that bundled multiple games on a single DVD-ROM and shipped with a modified
installation menu, allowing the user to pick which game to install. Each game on
a superdisc is patched to load its files from a subdirectory rather than from
the DVD's root.

Homebrew 573 software can be distributed as an ISO9660 image larger than 650 MB
meant to be burned to a DVD-R, if sacrificing PS1 compatibility and CD-DA
support is an option. In such case the image shall be distributed as an `.iso`
file with 2048-byte sectors, rather than the typical `.bin` and `.cue` file pair
used for PS1 games with 2352-byte Mode 2 sectors.

### Scrapped CF card support

In addition to booting from "linear" memory mapped PCMCIA flash cards, the
`700B01` shell features a driver for CF cards and a FAT filesystem parser that
allows it to mount a CF card inserted in PCMCIA slot 2 (via a passive
CF-to-PCMCIA adapter), search for a flash card image file and interpret its
contents as if it were an actual flash card, loading the executable directly
from it. Or at least, that *would* allow it to do so, had Konami not screwed up
the wiring of the PCMCIA slots.

CF cards can operate in three different interfacing modes: memory mapped, I/O
mapped and IDE compatibility mode. On the 573 only memory mapped mode is
accessible as the other modes require usage of I/O chip select pins that are not
connected. This mode, however, requires the host to issue 8-bit writes to the
card's 16-bit bus through the use of individual chip select lines for each byte
(`/CE1` and `/CE2`). While the PS1's CPU *does* have separate lower (`/WR0`) and
upper (`/WR1`) byte write strobes that could have been easily adapted to the
appropriate signals, Konami decided to cut this specific corner and shorted
`/CE1` and `/CE2` on each PCMCIA slot together, making it impossible to issue a
single-byte write.

**NOTE**: later revisions of the 573 main board seem to have unpopulated jumpers
next to the PCMCIA slots that can be used to rewire the chip select signals. It
is currently unclear if these jumpers are actually sufficient to enable CF card
booting without any additional hardware or BIOS modifications.

## Bootleg mod boards

It is not uncommon to find 573s fitted with a bootleg BIOS "mod board" in place
of the stock `700A01` or `700B01` mask ROM. These boards used to be bundled
alongside bootleg game CD-ROMs and were apparently required in order to bypass
the "anti-piracy checks" in Konami's BIOS.

Of course, since neither version of the shell has any such checks, the claims
were completely misleading. The actual purpose of these boards was not to tamper
with the BIOS, but rather to piggyback on the system bus and provide a crude
authentication mechanism to the bootleg game, allowing it to verify that it was
indeed running on a 573 equipped with an appropriate mod board. In other words,
**mod boards were actually the bootleggers' implementation of Konami's**
**security cartridge system**, meant to prevent people from simply burning
copies of a bootleg CD-ROM and forcing them to buy bootleg kits from whoever
produced them instead. *Oh the irony.*

The added authentication circuitry will not create any issues with official nor
homebrew software, however most of these boards feature an additional party
trick: *the shell executable is altered to load a differently named executable*,
making bootleg discs unable to boot on a stock 573 and vice versa. The following
names have been found so far in modified BIOS ROMs:

- `QSY.DXD`
- `SSW.BXF`
- `TSV.AXG`
- `GSE.NXX`
- `NSE.GXX`

The following names have been found on unofficial game discs, but are not
confirmed to have ever been used in modified BIOS ROMs:

- `OSE.FXX`
- `QSU.DXH`
- `QSX.DXE`
- `QSZ.DXC`
- `RSU.CXH`
- `RSV.CXG`
- `RSW.CXF`
- `RSZ.CXC`
- `SSX.BXE`
- `SSY.BXD`
- `TSW.AXF`
- `TSX.AXE`
- `TSY.AXD`
- `TSZ.AXC`

Homebrew software should thus place multiple copies of the boot executable on
the CD-ROM to ensure any BIOS, modded or not, can successfully load it. An
interesting side note is that, for any of these names, summing the ASCII codes
of each character will always yield the same result. Presumably bootleggers were
unable to find the code in charge of BIOS ROM checksum validation and found it
easier to just turn the string into random nonsense whose checksum collided with
the original one.

### `DDRTURBO` mod board

Board required by and specific to the DDR Extreme PLUS hack. Unlike all other
currently known boards, this one actually adds new functionality to the system:
the ability to speed up MP3 playback... *by taking the place of the 29.45 MHz*
*main oscillator* on the digital I/O board, which is desoldered and replaced
with a bodge wire. It features three crystal oscillators supplying the following
clocks:

- **29.5 MHz** (0.16% faster than stock, referred to as "Normal Speed" in
  Extreme PLUS)
- **33 MHz** (12.05% faster than stock, referred to as "Speed up 10%" in Extreme
  PLUS)
- **36 MHz** (22.24% faster than stock, referred to as "Speed up 20%" in Extreme
  PLUS)

The board listens for reads from the upper half of BIOS ROM
(`0xbfc40000-0xbfc7ffff`) and latches bits 5-6 of the byte read to determine
which clock to output to the digital I/O board:

| Byte read    | Clock           |
| -----------: | --------------: |
| `0b*00*****` |          33 MHz |
| `0b*01*****` |          36 MHz |
| `0b*10*****` |        29.5 MHz |
| `0b*11*****` | Unknown (none?) |

**NOTE**: kernel code execution while the game is running will *not* affect the
clock as the kernel is contained entirely within the ROM's first half. The
second half is in fact only accessed on startup when relocating the shell
executable to RAM and computing the ROM checksum.

In order to switch clocks, Extreme PLUS always reads from one of the following
addresses:

| Address read | Byte read | Clock    |
| -----------: | --------: | -------: |
| `0xbfc40ebf` |    `0x55` | 29.5 MHz |
| `0xbfc40810` |    `0x00` |   33 MHz |
| `0xbfc41341` |    `0xaa` |   36 MHz |

The board's EPROM holds a copy of the 700A01 BIOS with the last byte of the
checksum at `0xbfc7ffff` modified from `0xf9` to `0x39`. Extreme PLUS uses this
change to detect the mod board and will refuse to run if it is not present. The
padding byte at `0xbfc7fffb` is also changed from `0xff` to `0x3f` in order for
the contents of the ROM to match the new checksum.

## Game-specific information

### Black case I/O connectors

Fisherman's Bait and a few other non-Bemani games use a 573 housed in a black
case with blue front and back panels. Unlike the gray metal cases used by other
games, this case model has no cutouts for removable front and back panels that
hold game-specific connectors and instead has a fixed set of ports exposed:

- **Power**: 2x4 Molex connector that can be used as a power input or output,
  wired to `CN17`.
- **Option 1**: DE9 connector providing four analog inputs, wired to `CN3` on
  the main board.
- **Option 2**: DE9 connector providing six button (digital) inputs, of which
  four are also exposed on the JAMMA connector. Wired to `CN5` on the
  motherboard.
- **Reel connector** (back side): 3x3 Molex connector wired to the
  `GE765-PWB(B)A` fishing controller I/O board. Probably missing on systems that
  that did not come with Fisherman's Bait.

### DDR I/O connectors

Dance Dance Revolution uses a 573 enclosed in a gray metal case, with either an
analog or digital I/O board installed. The front panel has a cutout covered by a
metal plate, which in turn holds the following connectors:

- **1P** (10-pin white, only 7 pins used): connects to the left stage and
  controls arrow lights, in addition to being used for bitbanged communication
  with the stage PCB. Wired to light bank A on the I/O board.
- **2P** (10-pin orange, only 7 pins used): same as above for the right stage.
  Wired to light bank B on the I/O board.
- Unlabeled (10-pin red, only 7 pins used): connects to cabinet button and
  marquee lights. Wired to light bank C.
- Unlabeled (6-pin white, only 2 pins used): controls the inverter that drives
  the neon rings around the speakers. Wired to light bank D.

The back panel has a similar cutout, covered by a plate with holes for the
digital I/O board's RCA networking jacks.

### DDR light mapping

Dance Dance Revolution cabinets (standard 2-player ones, not Solo) have lights
wired up to the analog or digital I/O board as follows:

| Output | Connected to                |
| -----: | :-------------------------- |
|     A0 | Player 1 up arrow           |
|     A1 | Player 1 down arrow         |
|     A2 | Player 1 left arrow         |
|     A3 | Player 1 right arrow        |
|     A4 | Data to player 1 stage I/O  |
|     A5 | Clock to player 1 stage I/O |
|  A6-A7 | _Unused_                    |
|     B0 | Player 2 up arrow           |
|     B1 | Player 2 down arrow         |
|     B2 | Player 2 left arrow         |
|     B3 | Player 2 right arrow        |
|     B4 | Data to player 2 stage I/O  |
|     B5 | Clock to player 2 stage I/O |
|  B6-B7 | _Unused_                    |
|  C0-C1 | _Unused_                    |
|     C2 | Player 1 buttons            |
|     C3 | Player 2 buttons            |
|     C4 | Bottom right marquee light  |
|     C5 | Top right marquee light     |
|     C6 | Bottom left marquee light   |
|     C7 | Top left marquee light      |
|     D0 | Speaker neon                |
|  D1-D3 | _Unused_                    |

Light outputs A4, A5, B4 and B5 do not actually control any lamps, but are used
to communicate with each stage's I/O board. See the external modules section
for more details.

### DDR Solo input and light mapping

Dance Dance Revolution Solo cabinets, unlike 2-player cabinets, do not use a
stage I/O board to multiplex the sensors as each arrow panel only has 2 sensors
(rather than 4). Each sensor is instead wired directly to the JAMMA connector,
making use of most of the available inputs.

| JAMMA input       | Connected to        |
| :---------------- | :------------------ |
| Player 1 left     | Left sensor A       |
| Player 1 right    | Right sensor A      |
| Player 1 up       | Up sensor A         |
| Player 1 down     | Down sensor A       |
| Player 1 button 1 | Up-left sensor B    |
| Player 1 button 2 | Left sensor B       |
| Player 1 button 3 | Down sensor B       |
| Player 1 button 4 | _Unused_            |
| Player 1 button 5 | Left button         |
| Player 1 start    | Start button        |
| Player 2 left     | Up-left sensor A    |
| Player 2 right    | Up-right sensor A   |
| Player 2 up       | _Unused_            |
| Player 2 down     | _Unused_            |
| Player 2 button 1 | Up sensor B         |
| Player 2 button 2 | Right sensor B      |
| Player 2 button 3 | Up-right sensor B   |
| Player 2 button 4 | _Unused_            |
| Player 2 button 5 | Right button        |
| Player 2 start    | _Unused_ (shorted?) |

The light mapping is currently unknown. Solo cabinets have less lights compared
to their 2-player counterparts (e.g. arrow panel lamps are missing).

### DrumMania light mapping

First-generation DrumMania cabinets have lights wired up to the I/O board as
follows:

| Output | Connected to  |
| -----: | :------------ |
|  A0-A7 | _Unused_      |
|  B0-B7 | _Unused_      |
|     C0 | Hi-hat        |
|     C1 | Snare         |
|     C2 | High tom      |
|     C3 | Low tom       |
|     C4 | Cymbal        |
|     C5 | _Unused_      |
|     C6 | Start button  |
|     C7 | Select button |
|     D0 | Spotlight     |
|     D1 | Top neon      |
|     D2 | _Unused_      |
|     D3 | Bottom neon   |

The wiring was changed in later cabinets, which use the following mapping
instead:

| Output | Connected to  |
| -----: | :------------ |
|     A0 | Hi-hat        |
|     A1 | Snare         |
|     A2 | High tom      |
|     A3 | Low tom       |
|  A4-A7 | _Unused_      |
|     B0 | Spotlight     |
|     B1 | Bottom neon   |
|     B2 | Top neon      |
|     B3 | _Unused_      |
|     B4 | Cymbal        |
|     B5 | _Unused_      |
|     B6 | Start button  |
|     B7 | Select button |
|  C0-C7 | _Unused_      |
|  D0-D3 | _Unused_      |

## Notes

- [Hard-to-install games](#hard-to-install-games)
- [Homebrew guidelines](#homebrew-guidelines)
- [Missing support for PAL mode](#missing-support-for-pal-mode)
- [Flash chips and PCMCIA cards](#flash-chips-and-pcmcia-cards)
- [Known working replacement PCMCIA cards](#known-working-replacement-pcmcia-cards)
- [Known working replacement drives](#known-working-replacement-drives)
- [Bemani launcher error and status codes](#bemani-launcher-error-and-status-codes)

### Hard-to-install games

While the vast majority of 573 games can be trivially installed by inserting the
respective game disc (or sometimes a separate install disc) and a new security
cartridge, there are a few ones that require more complex installation
procedures:

- **Games without a CD-ROM**: for what should be obvious reasons, such games
  cannot be installed without either using homebrew flashing tools or injecting
  a flash image into another game's CD-ROM installer. Konami's "official"
  installation method was to boot the flash image from a PCMCIA card, which the
  game will detect and copy over to the internal flash.
- **Hyper Bishi Bashi Champ**, **Handle/Steering Champ**: RTC RAM is employed as
  a "suicide battery" of sorts by pre-populating it with a header and other data
  at the factory. If any of the data is corrupted or missing, the game will
  display "HARDWARE UNMATCHED" and refuse to boot any further.
- **Dance Dance Revolution (`JAB` version)**: also checks RTC RAM and will not
  boot if its header is missing from the first 32 bytes (subsequent data can be
  uninitialized and will be rebuilt automatically if needed). Additionally, even
  though the game requires a CD-ROM, its disc only contains CD-DA tracks and
  lacks an installer or flash image, requiring the same workarounds as
  CD-ROM-less games in order to install it.
- **Dance Dance Revolution 4thMIX PLUS** and **PLUS Solo**: as this game is an
  upgrade to DDR 4thMIX, the installer will refuse to proceed unless 4thMIX's
  header is present in the first 32 bytes of RTC RAM. This check is only
  performed during installation; the game itself will rebuild the entire
  contents of the RTC if the header is invalid.
- **Dancing Stage feat. Dreams Come True** (both analog I/O and digital I/O
  versions): notorious for requiring a lot of juggling with security cartridges.
  The installer prompts for a cartridge from a previous game that is allowed to
  be upgraded, which will be invalidated and made unusable as part of the
  installation process.

### Homebrew guidelines

It is relatively easy to develop homebrew games that can run on both a System
573 and a regular PlayStation 1, or to port existing PS1 homebrew to the 573.
Nevertheless, there are some significant differences between the two systems
and a game meant to run on both shall avoid using any feature that is only
available on one. "Hybrid" PS1/573 games shall adhere to the following
guidelines:

- **Do not use the extra RAM.** With the exception of development kits and
  modified units, consoles always have 2 MB of main RAM and 1 MB of VRAM. The
  additional RAM on the 573 might still be useful for 573-specific purposes
  such as FAT filesystem handling if an IDE hard drive is used.
- **Do not use XA-ADPCM.** XA is not supported by any ATAPI drive. CD-DA is
  supported by both the PS1 CD drive and ATAPI drives, however it will not work
  out-of-the-box on a 573 fitted with a digital I/O board as the 4-pin CD audio
  cable will not be plugged into the drive. Homebrew games that use CD-DA
  should display a splash screen showing how to unplug the cable from the I/O
  board and plug it into the drive (which is a quick reversible modification).
  SPU audio streaming can replace XA and will work on both platforms.
- **Have separate executables for PS1 and 573.** Since the PS1 BIOS parses
  `SYSTEM.CNF` while the 573 BIOS ignores it, a disc can have two different
  executables, one named `PSX.EXE` (which will be launched on a 573) and the
  other (which will run on a PS1) referenced by `SYSTEM.CNF`. This makes it
  easier to have two separate builds of the game rather than having to detect
  system type at runtime. Additional copies of `PSX.EXE` with the file names
  commonly used by BIOS mod boards (`QSY.DXD`, `TSV.AXG` and so on) shall also
  be present.
- **Do not rely on the RTC.** Most 573 boards have a dead RTC battery by now.
  As the battery is sealed inside the RTC it is basically impossible to replace
  without replacing the entire chip, which is something not all 573 owners can
  do. RTC RAM is additionally used by some games to store security-related data
  and shall not be used for saving.
- **Implement an operator/settings menu.** Among other things, the menu should
  allow the user to adjust the SPU's master volume, enable or disable the 573's
  built-in amplifier (which has no physical volume controls), test cabinet
  lights and eject the CD (as some cases hide the drive's eject button behind a
  small hole or make it difficult to access otherwise).

### Missing support for PAL mode

The 573 only supports 60 Hz mode (i.e. "NTSC", even though the video DAC has no
composite or S-video output so no color modulation is involved). Attempting to
switch the GPU into 50 Hz PAL mode using the `GP1(0x08)` command will result in
a crash, as only the NTSC clock input pin is wired up.

Support for 50 Hz can be added back by shorting pins 192 and 196 on the GPU
(which will give "PAL-on-NTSC" timings) or by connecting pin 192 to an external
oscillator tuned to generate a PAL clock. See the timings section of the GPU
page for more details.

### Flash chips and PCMCIA cards

The PCMCIA flash cards required by most 573 games are "linear" (memory mapped)
cards consisting of one or more parallel flash memory chips wired directly to
the bus, rather than CF or ATA-compatible cards. As neither linear cards nor
parallel flash command sets are fully standardized, working with these cards may
be difficult without some prior knowledge.

There are two main variants of such cards:

- **8-bit**: these contain one or more pairs of flash chips with an 8-bit data
  bus each. Each pair has one chip wired to the lower byte of the data bus and
  the other wired to the upper byte. Commands must thus be issued to both chips
  at once by repeating the command byte (e.g. writing `0x9090` to issue the
  `0x90` JEDEC ID command). Issuing 8-bit writes to a single chip is *not*
  supported on the 573 due to the way chip select lines are wired up; see the
  BIOS CF card support section for more details.
- **16-bit**: these contain flash chips with a native 16-bit bus. The chips are
  simply mapped next to each other within the card's address space.

Konami's flash driver only supports 8-bit cards that use one of the following
chips:

| Manufacturer | Chip       | Capacity | Manuf. ID | Device ID |
| :----------- | :--------- | -------: | :-------- | :-------- |
| Fujitsu      | MBM29F016A |     2 MB | `0x04`    | `0xad`    |
| Fujitsu      | MBM29F017A |     2 MB | `0x04`    | `0x3d`    |
| Fujitsu      | MBM29F040A |   512 KB | `0x04`    | `0xa4`    |
| Intel        | 28F016S5   |     2 MB | `0x89`    | `0xaa`    |
| Sharp        | LH28F016S  |     2 MB | `0x89`    | `0xaa`    |

Most games, including the launchers used by later Bemani games, will check the
JEDEC IDs of the cards' chips on startup and **reject any unsupported chip,**
**even if valid game data is otherwise present on the card**. This makes it
impossible to manually install a game onto an unsupported card (e.g. through
homebrew tools) without also patching the launcher in order to skip the check.

The 573 main board seems to always be fitted with either MBM29F016A or LH28F016S
chips. The internal flash memory is accessed using the same driver as the flash
cards and has the same caveats (having to issue commands to two chips at once
and so on).

### Known working replacement PCMCIA cards

This is an incomplete list of PCMCIA flash cards that are known to work, or not
to work, with Konami's flash driver. Due to the JEDEC ID checks, only cards that
contain flash chips listed in the previous section will work.

| Manufacturer   | Model                                | Flash chips    | Capacity | Bus type | Manuf. ID | Device ID | Working | Notes                                                                     |
| :------------- | :----------------------------------- | :------------- | -------: | -------: | :-------- | :-------- | :------ | :------------------------------------------------------------------------ |
| ~~Centennial~~ | ~~PM24265, FL32M-20-\*-67~~          | 16x 28F016S5   |    32 MB |    8-bit | `0x8989`  | `0xaaaa`  | Yes\*   | See note below on model numbers                                           |
| ~~Centennial~~ | ~~PM24265, FL32M-20-\*-67~~          | 16x AM29F016   |    32 MB |    8-bit | `0x0101`  | `0xadad`  | No      | Same command set as Fujitsu cards, may work with ID check patching        |
| ~~Centennial~~ | ~~PM24276, FL32M-20-\*-J5-03~~       | 4x 28F640J5    |    32 MB |   16-bit | `0x0089`  | `0x0015`  | No      |                                                                           |
| ~~Centennial~~ | ~~PM24282, FL32M-20-\*-S5-03~~       | 16x AM29F016   |    32 MB |    8-bit | `0x0101`  | `0xadad`  | No      | Same command set as Fujitsu cards, may work with ID check patching        |
| Fujitsu        | "32MB Flash Card" (no model number?) | 16x MBM29F016A |    32 MB |    8-bit | `0x0404`  | `0xadad`  | **Yes** | Stock card (Konami sticker covers Fujitsu logo)                           |
| Fujitsu        | "32MB Flash Card" (no model number?) | 16x MBM29F017A |    32 MB |    8-bit | `0x0404`  | `0x3d3d`  | **Yes** | Stock card (Konami sticker covers Fujitsu logo)                           |
| Sharp          | ID245G01                             | 4x LH28F016S   |     8 MB |    8-bit | `0x8989`  | `0xaaaa`  | **Yes** | Stock card (Konami sticker covers Sharp logo), used by GunMania Zone Plus |
| Sharp          | ID245P01                             | 16x LH28F016S  |    32 MB |    8-bit | `0x8989`  | `0xaaaa`  | **Yes** | Stock card (Konami sticker covers Sharp logo)                             |

Note that most of these cards have identical labels and can typically only be
told apart from the model number printed on the bottom side or one of the edges.

**IMPORTANT**: the model numbers on Centennial cards seem to be inconsistent and
not necessarily related to which flash chips the card is fitted with. As such
**buying these cards for use with 573 games is strongly discouraged**, even
though some of them are known to use parts compatible with Konami's driver.

### Known working replacement drives

This is an incomplete list of drives that are known to work, or to be
incompatible, with the ATAPI driver Konami used in the BIOS shell and games. The
driver was likely written using an old version of the ATAPI specification as a
reference; CD-ROM drives manufactured in the late 1990s and very early 2000s
have a higher chance of being compatible than drives manufactured later,
possibly due to changes introduced in later revisions of the ATAPI specification
that broke the assumptions Konami's driver makes.

CD-DA playback is particularly problematic as Konami's code seems to be unable
to handle the subtle implementation differences across different drives. To add
insult to injury, some of the few drives that *do* work have bugs in their
subchannel handling that result in incorrect playback status data being reported
to the 573, completely breaking pre-digital-I/O Bemani titles that rely heavily
on audio timing.

| Manufacturer         | Known rebrands | Model          | Type | BIOS    | CD-DA   | Notes                               |
| :------------------- | :------------- | :------------- | :--- | :------ | :------ | :---------------------------------- |
| ASUSTeK              |                | DVD-E616P3     | DVD  | **Yes** | Unknown |                                     |
| Creative             |                | CD4832E        | CD   | **Yes** | No      |                                     |
| Hitachi              |                | CDR-7930       | CD   | **Yes** | No      |                                     |
| LG                   | Compaq         | CRD-8400B      |      | **Yes** | Unknown |                                     |
| LG?                  | Compaq         | CRN-8241B      | CD   | **Yes** | **Yes** | Laptop drive, has CD-DA sync issues |
| LG                   |                | GCE-8160B      | CD   | **Yes** | No      |                                     |
| LG                   |                | GCR-8523B      | CD   | **Yes** | Unknown |                                     |
| LG                   |                | GCR-8525B      | CD   | **Yes** | **Yes** | Has CD-DA sync issues               |
| LG                   |                | GDR-8163B      | DVD  | **Yes** | **Yes** |                                     |
| LG                   | HP             | GDR-8164B      | DVD  | **Yes** | **Yes** |                                     |
| LG                   |                | GH22LP20       | DVD  | **Yes** | Unknown |                                     |
| LG                   |                | GH22NP20       | DVD  | **Yes** | Unknown |                                     |
| ~~LG~~               |                | ~~GSA-4165B~~  | DVD  | No      |         |                                     |
| LG                   |                | GWA-4166B      | DVD  | **Yes** | Unknown |                                     |
| Lite-On              |                | DH-20A4P       |      | **Yes** | Unknown |                                     |
| Lite-On              |                | LH-18A1H       | DVD  | **Yes** | **Yes** |                                     |
| Lite-On              |                | LTD-163        | DVD  | **Yes** | Unknown |                                     |
| Lite-On              |                | LTD-165H       | DVD  | **Yes** | Unknown |                                     |
| Lite-On              |                | LTR-40125S     | CD   | **Yes** | Unknown |                                     |
| Lite-On              |                | SHW-160P6S     | DVD  | **Yes** | Unknown |                                     |
| Lite-On              |                | SOHR-48327S    |      | **Yes** | Unknown |                                     |
| Lite-On              | HP             | SOHR-4839S     | CD   | **Yes** | Unknown | Jitters on CD-RW                    |
| Lite-On              |                | XJ-HD166S      | DVD  | **Yes** | Unknown |                                     |
| Matsushita/Panasonic |                | CR-583         | CD   | **Yes** | **Yes** | Stock drive                         |
| Matsushita/Panasonic |                | CR-587         | CD   | **Yes** | **Yes** | Stock drive, can't read CD-R        |
| Matsushita/Panasonic |                | CR-589B        | CD   | **Yes** | **Yes** | Stock drive                         |
| Matsushita/Panasonic |                | CR-594C        | CD   | **Yes** | Unknown |                                     |
| Matsushita/Panasonic | HP             | SR-8585B       | DVD  | **Yes** | Unknown |                                     |
| Matsushita/Panasonic |                | SR-8589B       | DVD  | **Yes** | Unknown |                                     |
| Matsushita/Panasonic |                | UJDA770        |      | **Yes** | Unknown | Laptop drive                        |
| Mitsumi              |                | CRMC-FX4830T   | CD   | **Yes** | Unknown |                                     |
| NEC                  |                | CDR-1900A      | CD   | **Yes** | Unknown |                                     |
| ~~NEC~~              |                | ~~ND-2510A~~   | DVD  | No      |         |                                     |
| Sony                 | Compaq         | CDU701-Q1      | CD   | **Yes** | Unknown |                                     |
| Sony                 |                | CRX217E        | CD   | **Yes** | Unknown |                                     |
| Sony                 |                | DRU-510A       | DVD  | **Yes** | Unknown |                                     |
| Sony                 |                | DRU-810A       | DVD  | **Yes** | Unknown |                                     |
| TDK                  |                | AI-CDRW241040B | CD   | **Yes** | Unknown |                                     |
| TDK                  |                | AI-481648B     | CD   | **Yes** | Unknown |                                     |
| TEAC                 |                | CD-W552E       | CD   | **Yes** | Unknown |                                     |
| Toshiba              |                | SW-252         |      | **Yes** | Unknown |                                     |
| Toshiba              |                | TS-H292C       | CD   | **Yes** | Unknown |                                     |
| Toshiba              |                | XM-5702B       | CD   | **Yes** | Unknown |                                     |
| Toshiba              |                | XM-6102B       | CD   | **Yes** | **Yes** | Stock drive                         |
| Toshiba              |                | XM-7002B       | CD   | **Yes** | Unknown | Stock drive, laptop drive           |

**NOTE**: Konami shipped some units with a Toshiba XM-7002B laptop drive and a
passive adapter board (`GX874-PWB(B)`) to break out the drive's signals to a
regular 40-pin IDE connector. Laptop drives were also used by Konami in the
`GXA25-PWB(A)` multisession unit.

### Bemani launcher error and status codes

The installers and launchers used by Bemani titles that require the digital I/O
board have an extensive error and status reporting system. Launcher messages are
easily recognizable as they are always displayed in a blue window and have a
3-digit status code, however Japanese versions of the games will show them in
Japanese with no way to switch language (short of patching the launcher; all
launcher variants contain both English and Japanese strings).

Below is a list of all messages from launcher version 1.95 in both English and
Japanese, along with the respective status codes and indices in the launcher's
internal message array.

| Index | Type  | Status codes  | Description (English)                                                                                                                                                                                                                                                | Description (Japanese) |
| ----: | :---- | :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------- |
|     0 | Error | 100           | <pre>Boot is not available from this device.<br />DEVICE=%s1</pre>                                                                                                                                                                                                   | <pre lang="ja">このデバイスからのブートはできません.<br />DEVICE=%s1</pre> |
|     1 | Error | 101           | <pre>Digital Sound PCB intialization failed.</pre>                                                                                                                                                                                                                   | <pre lang="ja">デジタルサウンド基板の初期化に失敗しました.</pre> |
|     2 | Error | 102           | <pre>Digital Sound PCB ROM error.</pre>                                                                                                                                                                                                                              | <pre lang="ja">デジタルサウンド基板ROMエラー.</pre> |
|     4 | Error | 104           | <pre>CD-ROM initialization failed.</pre>                                                                                                                                                                                                                             | <pre lang="ja">CD-ROMドライブの初期化に失敗しました.</pre> |
|     7 | Error | 107           | <pre>File system mounting failed.<br />Please check that correct CD-ROM is in use.</pre>                                                                                                                                                                             | <pre lang="ja">ファイルシステムのマウントに失敗しました.<br />CD-ROMが間違っていないか確認してください.</pre> |
|     9 | Error | 109           | <pre>File system mounting failed.<br />Please check that correct CD-ROM is in use.</pre>                                                                                                                                                                             | <pre lang="ja">ファイルシステムのマウントに失敗しました.<br />CD-ROMが間違っていないか確認してください.</pre> |
|    10 | Error | 110           | <pre>File system mounting failed.<br />Please check that correct CD-ROM is in use.</pre>                                                                                                                                                                             | <pre lang="ja">ファイルシステムのマウントに失敗しました.<br />CD-ROMが間違っていないか確認してください.</pre> |
|    11 | Error | 111           | <pre>File system mounting failed.<br />Please check that correct CD-ROM is in use.</pre>                                                                                                                                                                             | <pre lang="ja">ファイルシステムのマウントに失敗しました.<br />CD-ROMが間違っていないか確認してください.</pre> |
|    12 | Error | 112           | <pre>File system mounting failed.<br />Please check that correct CD-ROM is in use.</pre>                                                                                                                                                                             | <pre lang="ja">ファイルシステムのマウントに失敗しました.<br />CD-ROMが間違っていないか確認してください.</pre> |
|    13 | Error | 113           | <pre>Disc device initialization failed.</pre>                                                                                                                                                                                                                        | <pre lang="ja">ディスクデバイスの初期化に失敗しました.</pre> |
|    14 | Error | 114           | <pre>You are using an incorrect CD-ROM.<br />Replace CD-ROM to %s1 and<br />turn on the main power.</pre>                                                                                                                                                            | <pre lang="ja">CD-ROMが違います.<br />CD-ROMを%s1に交換し,電源を<br />入れ直してください.</pre> |
|    15 | Error | 115           | <pre>Disc device initialization failed.</pre>                                                                                                                                                                                                                        | <pre lang="ja">ディスクデバイスの初期化に失敗しました.</pre> |
|    16 | Error | 116           | <pre>Disc device initialization failed.</pre>                                                                                                                                                                                                                        | <pre lang="ja">ディスクデバイスの初期化に失敗しました.</pre> |
|    17 | Error | 117           | <pre>Config file error.<br />FILE=%s1<br />ERROR=%d2, LINE=%d3, COLUMN=%d4</pre>                                                                                                                                                                                     | <pre lang="ja">コンフィグファイルエラー.<br />FILE=%s1<br />ERROR=%d2, LINE=%d3, COLUMN=%d4</pre> |
|    19 | Error | 119           | <pre>You are using an incorrect CD-ROM.<br />Replace CD-ROM to %s1 and<br />turn on the main power.</pre>                                                                                                                                                            | <pre lang="ja">CD-ROMが違います.<br />CD-ROMを%s1に交換し,電源を<br />入れ直してください.</pre> |
|    20 | Error | 120           | <pre>Cassette is not installed.<br />Turn off the main power and install the<br />correct cassette then turn the power on.</pre>                                                                                                                                     | <pre lang="ja">カセットがセットされていません.<br />電源を切り,正しいカセットをセットして<br />再度電源を入れてください.</pre> |
|    21 | Error | 121           | <pre>Cassette error. (%d1)<br />Cassette does not match this game.<br />Check if the cassette is for this<br />game (%s2)<br />Refer to manual for more information.</pre>                                                                                           | <pre lang="ja">カセットエラー (%d1)<br />ゲームとカセットが対応していません.<br />カセットがこのゲーム(%s2)用のものか<br />確認してください.<br />詳しくは取り扱い説明書を参照してください.</pre> |
|    25 | Error | 125           | <pre>Boot is not available from this device.<br />DEVICE=%s1</pre>                                                                                                                                                                                                   | <pre lang="ja">このデバイスからゲームのブートはできません.<br />DEVICE=%s1</pre> |
|    26 | Error | 126           | <pre>Cassette error (%d1)</pre>                                                                                                                                                                                                                                      | <pre lang="ja">カセットエラー (%d1)</pre> |
|    27 | Error | 127           | <pre>Master Calendar network error.</pre>                                                                                                                                                                                                                            | <pre lang="ja">マスターカレンダー通信エラー.</pre> |
|    28 | Error | 128           | <pre>Master Calendar network error.</pre>                                                                                                                                                                                                                            | <pre lang="ja">マスターカレンダー通信エラー.</pre> |
|    29 | Error | 129           | <pre>Master Calendar network error.</pre>                                                                                                                                                                                                                            | <pre lang="ja">マスターカレンダー通信エラー.</pre> |
|    30 | Error | 130           | <pre>Installation boot device error.<br />Installation cassette is inserted.<br />Turn off the power.  Before turning the<br />power on:  1. Change the cassette to the<br />Operating Cassette to enter the game or<br />2. Set DIP-SW4 to "OFF" to install.</pre>  | <pre lang="ja">インストールブートデバイスエラー.<br />インストールカセットがセットされています.<br />電源を切り,ゲームを行うには運用カセットに<br />交換, インストールするにはDIP-SW4をOFFに<br />し,再度電源を入れてください.</pre> |
|    31 | Error | 131           | <pre>Installation Cassette does not correspond<br />to the machine.<br />Please use Installation Cassette marked<br />%s1 for installation.</pre>                                                                                                                    | <pre lang="ja">インストールカセットと本体との対応がとれて<br />いません. 認証番号%s1が記入された<br />インストールカセットを用いてインストール<br />してください.</pre> |
|    32 | Error | 132           | <pre>Cassette error (%d1)</pre>                                                                                                                                                                                                                                      | <pre lang="ja">カセットエラー (%d1)</pre> |
|    35 | Error | 135           | <pre>This cassette is used to convert another<br />game. This can not be used as an operating<br />cassette.</pre>                                                                                                                                                   | <pre lang="ja">このカセットはいちど次機種への<br />コンバージョンに使用されたものです.<br />運用カセットとして使用することはできません.</pre> |
|    36 | Error | 136           | <pre>Cassette error (%d1)</pre>                                                                                                                                                                                                                                      | <pre lang="ja">カセットエラー (%d1)</pre> |
|    38 | Error | 138           | <pre>File not found.<br />FILE=%s1</pre>                                                                                                                                                                                                                             | <pre lang="ja">ファイルが見つかりません.<br />FILE=%s1</pre> |
|    39 | Error | 139           | <pre>File reading error.<br />FILE=%s1</pre>                                                                                                                                                                                                                         | <pre lang="ja">ファイルリードエラー.<br />FILE=%s1</pre> |
|    40 | Error | 140           | <pre>File not found.<br />FILE=%s1</pre>                                                                                                                                                                                                                             | <pre lang="ja">ファイルが見つかりません.<br />FILE=%s1</pre> |
|    41 | Error | 141           | <pre>File reading error.<br />FILE=%s1</pre>                                                                                                                                                                                                                         | <pre lang="ja">ファイルリードエラー.<br />FILE=%s1</pre> |
|    42 | Error | 142           | <pre>File reading error.<br />FILE=%s1</pre>                                                                                                                                                                                                                         | <pre lang="ja">ファイルリードエラー.<br />FILE=%s1</pre> |
|    43 | Error | 143           | <pre>File reading error.<br />FILE=%s1</pre>                                                                                                                                                                                                                         | <pre lang="ja">ファイルリードエラー.<br />FILE=%s1</pre> |
|    44 | Error | 144           | <pre>File data error.<br />FILE=%s1</pre>                                                                                                                                                                                                                            | <pre lang="ja">ファイルデータエラー.<br />FILE=%s1</pre> |
|    45 | Error | 145           | <pre>File data error.<br />FILE=%s1</pre>                                                                                                                                                                                                                            | <pre lang="ja">ファイルデータエラー.<br />FILE=%s1</pre> |
|    46 | Error | 146           | <pre>Turn off the power and check if the Flash<br />Card is inserted properly.<br />Please turn the power on after checking.<br />DEVICE=%s1</pre>                                                                                                                   | <pre lang="ja">電源を切り, フラッシュカードが正しくセット<br />されているか確認してください. 準備が整って<br />から再び電源を入れてください.<br />DEVICE=%s1</pre> |
|    47 | Error | 147           | <pre>Checksum error.  If you have the latest<br />CD-ROM, please replace.  Turn off the<br />power and insert installation cassette.<br />Set DIP-SW4 to "OFF", then turn on the<br />power and reinstall CD-ROM.</pre>                                              | <pre lang="ja">チェックサムエラー. 最新のCD-ROMがあれば,<br />それに交換してください. 電源を切り,インス<br />トールカセットに交換,DIP-SW4をOFFにして<br />電源を入れ,再インストールしてください.</pre> |
|    48 | Error | 148           | <pre>Area specification error.<br />Only area specification below is available.<br /> %s1<br />Check the DIP-SW of Master Calendar.</pre>                                                                                                                            | <pre lang="ja">仕向地指定エラー.<br />本タイトルは次の仕向地のみ指定できます.<br /> %s1<br />マスターカレンダーのDIP-SWを確認して<br />ください.</pre> |
|    49 | Error | 149           | <pre>Cassette initialization error.<br />The cassette is already initialized as<br />Operating Cassette (%s1)<br />Reinitialization can not be completed.</pre>                                                                                                      | <pre lang="ja">カセット初期化エラー.<br />カセットはすでに運用カセット(%s1)<br />として初期化されています.<br />再初期化はできません.</pre> |
|    50 | Error | 150           | <pre>Cassette initialization error.<br />The cassette is already initialized as<br />Installation Cassette (%s1)<br />Reinitialization can not be completed.</pre>                                                                                                   | <pre lang="ja">カセット初期化エラー.<br />カセットはすでにインストールカセット<br />(%s1)として初期化されています.<br />再初期化はできません.</pre> |
|    51 | Error | 151           | <pre>File not found.<br />FILE=%s1</pre>                                                                                                                                                                                                                             | <pre lang="ja">ファイルが見つかりません.<br />FILE=%s1</pre> |
|    52 | Error | 152           | <pre>Turn off the power and check if the Flash<br />Card is inserted properly.<br />Please turn the power on after checking.<br />DEVICE=%s1</pre>                                                                                                                   | <pre lang="ja">電源を切り, フラッシュカードが正しくセット<br />されているか確認してください. 準備が整って<br />から再び電源を入れてください.<br />DEVICE=%s1</pre> |
|    53 | Error | 153           | <pre>Installation failed. (%d1)</pre>                                                                                                                                                                                                                                | <pre lang="ja">インストールに失敗しました (%d1)</pre> |
|    54 | Error | 154           | <pre>Assertion failed.<br />FILE=%s1<br />LINE=%d2</pre>                                                                                                                                                                                                             | <pre lang="ja">アサーションフェイル.<br />FILE=%s1<br />LINE=%d2</pre> |
|    55 | Error | 155           | <pre>Argument buffer overflow.</pre>                                                                                                                                                                                                                                 | <pre lang="ja">引数バッファオーバーフロー.</pre> |
|    56 | Error | 156           | <pre>File not found.<br />FILE=%s1</pre>                                                                                                                                                                                                                             | <pre lang="ja">ファイルが見つかりません.<br />FILE=%s1</pre> |
|    57 | Error | 157           | <pre>File data error.<br />FILE=%s1</pre>                                                                                                                                                                                                                            | <pre lang="ja">ファイルデータエラー.<br />FILE=%s1</pre> |
|    58 | Error | 158           | <pre>File reading error.<br />FILE=%s1</pre>                                                                                                                                                                                                                         | <pre lang="ja">ファイルリードエラー.<br />FILE=%s1</pre> |
|    59 | Error | 159           | <pre>Security Chip error. (%d1)<br />This Security Chip was initialized for<br />another title.</pre>                                                                                                                                                                | <pre lang="ja">セキュリティチップエラー.(%d1)<br />このセキュリティチップは他のタイトル用に<br />初期化されています.</pre> |
|    60 | Error | 160           | <pre>CD-ROM drive error</pre>                                                                                                                                                                                                                                        | <pre lang="ja">CD-ROMドライブエラー.</pre> |
|    61 | Error | 161           | <pre>RTC error</pre>                                                                                                                                                                                                                                                 | <pre lang="ja">RTCエラー.</pre> |
|    62 | Error | 162           | <pre>Specification selection error<br />Only specification below can be<br />selected for this title.<br /> %s1<br />Check the DIP-SW of machine.</pre>                                                                                                              | <pre lang="ja">商品仕様指定エラー.<br />本タイトルは次の商品仕様のみ指定できます.<br /> %s1<br />本体のDIP-SWを確認してください.</pre> |
|    64 | Error | 164           | <pre>Operating Cassette is not corresponding<br />with the machine.  Turn off the power and<br />replace it with Operating Cassette<br />No.%s1 then reboot.</pre>                                                                                                   | <pre lang="ja">運用カセットと本体との対応がとれていません.<br />電源を切り,認証番号%s1が記入された<br />運用カセットに交換して再起動してください.</pre> |
|    66 | Error | 166           | <pre>Incorrect cassette installed.</pre>                                                                                                                                                                                                                             | <pre lang="ja">不当なカセットです.</pre> |
|    67 | Error | 167           | <pre>Security Chip initialization failed. (%d1)</pre>                                                                                                                                                                                                                | <pre lang="ja">セキュリティチップ初期化エラー. (%d1)</pre> |
|    69 | Error | 169           | <pre>Cannot use this security cassette<br />as Installation Cassette.</pre>                                                                                                                                                                                          | <pre lang="ja">このセキュリティカセットはインストール<br />カセットとして使用することはできません.</pre> |
|    70 | Error | 170           | <pre>Cannot use this security cassette<br />as Installation Cassette.</pre>                                                                                                                                                                                          | <pre lang="ja">このセキュリティカセットはインストール<br />カセットとして使用することはできません.</pre> |
|    71 | Error | 171           | <pre>This version cannot initialize a cassette.<br />Please replace CD-ROM to %s1<br />for initialize, and turn off the power.<br />Set DIP-SW4 to "OFF", then turn on<br />the power.</pre>                                                                         | <pre lang="ja">このバージョンはカセットを初期化できません.<br />初期化するにはCD-ROMを%s1に<br />交換して電源を切り,DIP-SW4をOFFにして<br />再起動してください.</pre> |
|    72 | Error | 172           | <pre>You are using an incorrect CD-ROM.<br />Replace CD-ROM to %s1 and<br />turn on the main power.</pre>                                                                                                                                                            | <pre lang="ja">CD-ROMが違います.<br />CD-ROMを%s1に交換し,電源を<br />入れ直してください.</pre> |
|    73 | Error | 173           | <pre>Cannot use this security cassette.</pre>                                                                                                                                                                                                                        | <pre lang="ja">このセキュリティカセットは使用できません.</pre> |
|    74 | Error | 174           | <pre>Cannot use this security cassette.</pre>                                                                                                                                                                                                                        | <pre lang="ja">このセキュリティカセットは使用できません.</pre> |
|    75 | Error | 175           | <pre>Cassette is not corresponding with the<br />machine.  Turn off the power and<br />replace it with Cassette No.%s1<br />then reboot.</pre>                                                                                                                       | <pre lang="ja">カセットと本体との対応がとれていません.<br />電源を切り,認証番号%s1が記入された<br />カセットに交換して再起動してください.</pre> |
|    76 | Error | 176           | <pre>Cassette is not corresponding with the<br />machine.  Turn off the power and<br />replace it with Cassette No.%s1<br />then reboot.</pre>                                                                                                                       | <pre lang="ja">カセットと本体との対応がとれていません.<br />電源を切り,認証番号%s1が記入された<br />カセットに交換して再起動してください.</pre> |
|    77 | Error | 177           | <pre>Checksum error.<br />If you have the latest CD-ROM, please<br />replace.  Turn off the power and set<br />DIP-SW4 to "OFF", then turn on<br />the power and reinstall CD-ROM.</pre>                                                                             | <pre lang="ja">チェックサムエラー.<br />最新のCD-ROMがあればそれに交換してください.<br />電源を切ってDIP-SW4をOFFにしたあと,<br />電源を入れて再インストールしてください.</pre> |
|    78 | Error | 178           | <pre>This cassette is used to convert another<br />game. This can not be used to this game.</pre>                                                                                                                                                                    | <pre lang="ja">このカセットは次機種へのコンバージョンに<br />使用されたものです.<br />この機種で再び使用することはできません.</pre> |
|    79 | Error | 179           | <pre>Boot is not available from this device.<br />DEVICE=%s1</pre>                                                                                                                                                                                                   | <pre lang="ja">このデバイスからゲームのブートはできません.<br />DEVICE=%s1</pre> |
|    80 | Error | 180           | <pre>You are using an incorrect CD-ROM.<br />Replace CD-ROM to %s1 and<br />turn on the main power.</pre>                                                                                                                                                            | <pre lang="ja">CD-ROMが違います.<br />CD-ROMを%s1に交換し,電源を<br />入れ直してください.</pre> |
|    81 | Error | 181           | <pre>File system mounting failed.<br />Please check that correct CD-ROM is in use.</pre>                                                                                                                                                                             | <pre lang="ja">ファイルシステムのマウントに失敗しました.<br />CD-ROMが間違っていないか確認してください.</pre> |
|    82 | Error | 182           | <pre>File system mounting failed.<br />Please check that correct CD-ROM is in use.</pre>                                                                                                                                                                             | <pre lang="ja">ファイルシステムのマウントに失敗しました.<br />CD-ROMが間違っていないか確認してください.</pre> |
|    83 | Error | 183           | <pre>Installation boot device error.<br />Please turn off the power for installation,<br />and set DIP-SW4 to "OFF", then turn on<br />the power.</pre>                                                                                                              | <pre lang="ja">インストールブートデバイスエラー.<br />インストールするには電源を切り,DIP-SW4を<br />OFFにして再起動してください.</pre> |
|    84 | Error | 184           | <pre>CD-ROM drive error</pre>                                                                                                                                                                                                                                        | <pre lang="ja">CD-ROMドライブエラー.</pre> |
|    85 | Error | 185           | <pre>CD-ROM drive version update failed. (%d1)<br />Please call a dealer near you.</pre>                                                                                                                                                                             | <pre lang="ja">CD-ROMドライブのバージョンアップに失敗<br />しました. (%d1)<br />最寄りのサービスセンターにお問い合わせ<br />下さい.</pre> |
|    86 | Error | 186           | <pre>Cassette error (%d1)</pre>                                                                                                                                                                                                                                      | <pre lang="ja">カセットエラー (%d1)</pre> |
|    87 | Error | 187           | <pre>You are using the cassette of another<br />cabinet. Please use the correct cassette.<br />Please see details in operator's manual.</pre>                                                                                                                        | <pre lang="ja">異なる本体向けのカセットを使用しています.<br />正しい本体との組み合わせで使用してください.<br />詳しくは取り扱い説明書を参照してください.</pre> |
|    88 | Error | 188           | <pre>You are using the cassette of another<br />cabinet. Please use the correct cassette.<br />Please see details in operator's manual.</pre>                                                                                                                        | <pre lang="ja">異なる本体向けのカセットを使用しています.<br />正しい本体との組み合わせで使用してください.<br />詳しくは取り扱い説明書を参照してください.</pre> |
|    89 | Error | 189           | <pre>You are using unknown cabinet.<br />Check all connectors.<br />Please see details in operator's manual.</pre>                                                                                                                                                   | <pre lang="ja">不明な本体を使用しています.<br />各コネクタが外れていないか確認してください.<br />詳しくは取り扱い説明書を参照してください.</pre> |
|    90 | Error | 190           | <pre>You are using unknown cabinet.<br />Check all connectors.<br />Please see details in operator's manual.</pre>                                                                                                                                                   | <pre lang="ja">不明な本体を使用しています.<br />各コネクタが外れていないか確認してください.<br />詳しくは取り扱い説明書を参照してください.</pre> |
|    91 | Error | 191           | <pre>Non-applicable game installed.<br />To install this game,<br /> %s1<br />shall be installed first.</pre>                                                                                                                                                        | <pre lang="ja">異なるゲームがインストールされています.<br />このゲームをインストールするにはあらかじめ<br /> %s1<br />がインストールされている必要があります.</pre> |
|    92 | Error | 192           | <pre>This software is for the e-Amusement<br />system.<br />The game will only work on the e-Amusement<br />cabinet.</pre>                                                                                                                                           | <pre lang="ja">このゲームソフトはe-Amusement(レンタル)用<br />ソフトです.<br />e-Amusement用筐体でのみ動作します.</pre> |
|    93 | Error | 193           | <pre>This software is not for the e-Amusement<br />system.<br />The game doesn't work on the e-Amusement<br />cabinet.</pre>                                                                                                                                         | <pre lang="ja">このゲームソフトはe-Amusement(レンタル)用<br />ソフトではありません.<br />e-Amusement用筐体では動作しません.</pre> |
|    94 | Error | 194           | <pre>Non-applicable game installed.<br />To install this game,<br /> %s1<br />shall be installed first.</pre>                                                                                                                                                        | <pre lang="ja">異なるゲームがインストールされています.<br />このゲームをインストールするにはあらかじめ<br /> %s1<br />がインストールされている必要があります.</pre> |
|    95 | Error | 195           | <pre>Cassette initialization error.<br />The cassette is already initialized as<br />%s1<br />Reinitialization can not be completed.</pre>                                                                                                                           | <pre lang="ja">カセット初期化エラー.<br />カセットはすでに%s1として初期化<br />されています. 再初期化はできません.</pre> |
|    96 | Error | 196           | <pre>Cassette initialization error.<br />The cassette is already initialized as<br />%s1<br />Reinitialization can not be completed.</pre>                                                                                                                           | <pre lang="ja">カセット初期化エラー.<br />カセットはすでに%s1として初期化<br />されています. 再初期化はできません.</pre> |
|    97 | Error | 197           | <pre>Cassette initialization error.<br />The cassette is already initialized as<br />%s1<br />Reinitialization can not be completed.</pre>                                                                                                                           | <pre lang="ja">カセット初期化エラー.<br />カセットはすでに%s1として初期化<br />されています. 再初期化はできません.</pre> |
|    98 | Info  | 198, 500      | <pre>Installation completed.<br />Please write down the No.%s2<br />on cassette and machine.  Turn off the<br />power and replace cassette to<br />%s1 then turn on the power.</pre>                                                                                 | <pre lang="ja">インストール完了.<br />カセットと本体に認証番号%s2を記入<br />してください.電源を切ってカセットを<br />%s1に交換し,再度電源を入れて<br />ください.</pre> |
|    99 | Info  | 199, 501      | <pre>Installation complete.  Please write down<br />the No.%s3 on cassette and machine.<br />Replace CD-ROM to %s1 and turn off<br />the power then replace cassette to<br />%s2.  Set DIP-SW4 to "ON",<br />then turn on the power.</pre>                           | <pre lang="ja">インストール完了. カセットと本体に認証番号<br />%s3を記入してください.<br />CD-ROMを%s1に交換して電源を切り,<br />カセットを%s2に交換し,<br />DIP-SW4をONにして再度電源を入れてください.</pre> |
|   100 | Info  | 200, 502      | <pre>Operating cassette initialized.<br />The cassette was initialized as Operating<br />Cassette (%s1)</pre>                                                                                                                                                        | <pre lang="ja">運用カセット初期化完了.<br />カセットを運用カセット(%s1)として<br />初期化しました.</pre> |
|   101 | Info  | 201, 503      | <pre>Installation cassette initialized.<br />The cassette was initialized as<br />Installation Cassette (%s1)</pre>                                                                                                                                                  | <pre lang="ja">インストールカセット初期化完了.<br />カセットをインストールカセット(%s1)<br />として初期化しました.</pre> |
|   102 | Info  | 202, 504      | <pre>Initialized Operating Cassette<br />The cassette is already initialized as<br />Operating Cassette (%s1)<br />Reinitialization is not necessary.</pre>                                                                                                          | <pre lang="ja">初期化済み運用カセット.<br />カセットはすでに運用カセット(%s1)<br />として初期化されています. <br />再初期化の必要はありません.</pre> |
|   103 | Info  | 203, 505      | <pre>Initialized Installation Cassette<br />The cassette is already initialized as<br />Installation Cassette (%s1)<br />Reinitialization is not necessary.</pre>                                                                                                    | <pre lang="ja">初期化済みインストールカセット.<br />カセットはすでにインストールカセット<br />(%s1)として初期化されています.<br />再初期化の必要はありません.</pre> |
|   104 | Info  | 204, 506      | <pre>Installation completed.<br />Please write down the No.%s2<br />on cassette and machine.  Turn off the<br />power and replace cassette to<br />%s1 then turn on the power.</pre>                                                                                 | <pre lang="ja">インストール完了.<br />カセットと本体に認証番号%s2を記入<br />してください.電源を切ってカセットを<br />%s1に交換し,再度電源を入れて<br />ください.</pre> |
|   105 | Info  | 205, 507      | <pre>Installation complete.  Please write down<br />the No.%s3 on cassette and machine.<br />Replace CD-ROM to %s1 and turn off<br />the power then replace cassette to<br />%s2.  Set DIP-SW4 to "ON",<br />then turn on the power.</pre>                           | <pre lang="ja">インストール完了. カセットと本体に認証番号<br />%s3を記入してください.<br />CD-ROMを%s1に交換して電源を切り,<br />カセットを%s2に交換し,<br />DIP-SW4をONにして再度電源を入れてください.</pre> |
|   106 | Info  | 206, 508      | <pre>Installation completed.<br />Please write down the No.%s1<br />on cassette and machine.<br />Turn off the power, then reboot.</pre>                                                                                                                             | <pre lang="ja">インストール完了.<br />カセットと本体に認証番号%s1を記入<br />してください.<br />電源を切って再起動してください.</pre> |
|   107 | Info  | 207, 509      | <pre>Installation complete.<br />Please write down the No.%s2<br />on cassette and machine.<br />Replace CD-ROM to %s1 and turn off<br />the power.<br />Set DIP-SW4 to "ON", then reboot.</pre>                                                                     | <pre lang="ja">インストール完了.<br />カセットと本体に認証番号%s2を<br />記入してください.<br />CD-ROMを%s1に交換して電源を切り,<br />DIP-SW4をONにして再起動してください.</pre> |
|   108 | Info  | 208, 510      | <pre>Security cassette initialized.<br />The cassette was initialized for<br />%s1.</pre>                                                                                                                                                                            | <pre lang="ja">セキュリティカセット初期化完了.<br />カセットを%s1に初期化しました.</pre> |
|   109 | Info  | 209, 511      | <pre>Initialized Security Cassette<br />The cassette is already initialized for<br />%s1.<br />Reinitialization is not necessary.</pre>                                                                                                                              | <pre lang="ja">初期化済みセキュリティカセット.<br />カセットはすでに%s1に初期化<br />されています. 再初期化の必要はありません.</pre> |
|   110 | Info  | 210, 512      | <pre>SERVICE button is pressed.<br />To force installation, turn off the power,<br />change the cassette to the Installation<br />Cassette, and turn on the power with<br />pressing SERVICE switch.</pre>                                                           | <pre lang="ja">サービスボタンが押されています.<br />強制インストールを行うには電源を切り,<br />インストールカセットに交換して, サービス<br />ボタンを押しながら電源を入れてください.</pre> |
|   111 | Note  | 211, 513, 602 | <pre>CD-ROM drive version update in progress.<br />Please do not shut off power.<br />This will take a few moments.</pre>                                                                                                                                            | <pre lang="ja">現在CD-ROMドライブのバージョンアップを<br />実行しています.<br />電源を切らずにそのままお待ち下さい.</pre> |
|   112 | Note  | 212, 514, 603 | <pre>CD-ROM drive version update completed.</pre>                                                                                                                                                                                                                    | <pre lang="ja">CD-ROMドライブのバージョンアップが完了<br />しました.</pre> |
|   113 | Note  | 213, 515, 604 | <pre>Starting CD-ROM drive version update.<br />Please do not turn off the power while<br />updating.<br />Press TEST button to begin updating.</pre>                                                                                                                | <pre lang="ja">CD-ROMドライブのバージョンアップを行います.<br />バージョンアップ中は絶対に電源を切らないで<br />下さい.<br />テストボタンを押すとバージョンアップを開始<br />します.</pre> |
|   114 | Note  | 214, 516, 605 | <pre>Cleared RTC-RAM.<br />At Game Demo screen, press the test button<br />for the Test Mode and re-do the settings.<br /><br />Press the Test Button for the next screen.</pre>                                                                                     | <pre lang="ja">RTC-RAMをクリアしました.<br />ゲームデモが始まったらテストボタンを押して<br />テストモードに入り設定をやり直してください.<br /><br />テストボタンを押すと次に進みます.</pre> |

## Pinouts

- [Main board pinouts (`GX700-PWB(A)`)](#main-board-pinouts-gx700-pwba)
- [Analog I/O board pinouts (`GX700-PWB(F)`)](#analog-io-board-pinouts-gx700-pwbf)
- [Digital I/O board pinouts (`GX894-PWB(B)A`)](#digital-io-board-pinouts-gx894-pwbba)
- [Security cartridge pinouts](#security-cartridge-pinouts)

### Main board pinouts (`GX700-PWB(A)`)

#### Analog input port (`ANALOG`, `CN3`)

The inputs are wired directly to the 573's built-in ADC with no protection, so
they can only accept voltages in 0-5V range. This connector is usually used for
potentiometers and similar resistive analog controls.

| Pin | Name  | Dir |
| --: | :---- | :-- |
|   1 | `5V`  |     |
|   2 | `5V`  |     |
|   3 | `NC`  |     |
|   4 | `NC`  |     |
|   5 | `CH0` | I   |
|   6 | `GND` |     |
|   7 | `CH1` | I   |
|   8 | `CH2` | I   |
|   9 | `CH3` | I   |
|  10 | `GND` |     |

#### Digital output port (`EXT-OUT`, `CN4`)

Unlike the light output ports on most I/O boards, these are unisolated 5V logic
level outputs.

| Pin | Name   | Dir |
| --: | :----- | :-- |
|   1 | `5V`   |     |
|   2 | `5V`   |     |
|   3 | `OUT7` | O   |
|   4 | `OUT6` | O   |
|   5 | `OUT5` | O   |
|   6 | `OUT4` | O   |
|   7 | `OUT3` | O   |
|   8 | `OUT2` | O   |
|   9 | `OUT1` | O   |
|  10 | `OUT0` | O   |
|  11 | `GND`  |     |
|  12 | `GND`  |     |

#### Digital input port (`EXT-IN`, `CN5`)

Unlike `EXT-OUT`, this port is not a separate input port. It piggybacks on the
JAMMA button inputs instead, exposing the button 4 and 5 pins for both players
as well as a sixth button input which is not available on the JAMMA connector.
All inputs have a pullup resistor to 5V.

| Pin | Name    | Dir | JAMMA pin |
| --: | :------ | :-- | --------: |
|   1 | `5V`    |     |           |
|   2 | `5V`    |     |           |
|   3 | `P1_B4` | I   |        25 |
|   4 | `P1_B5` | I   |        26 |
|   5 | `P1_B6` | I   |           |
|   6 | `GND`   |     |           |
|   7 | `P2_B4` | I   |         c |
|   8 | `P2_B5` | I   |         d |
|   9 | `P2_B6` | I   |           |
|  10 | `GND`   |     |           |

#### Amplified speaker output (`SOUND-OUT`, `CN9`)

The pinout of this connector is currently unknown.

#### Main I/O board connector (`CN10`)

Used by I/O boards to connect to the motherboard. Note that the address and data
bus are 3.3V, while all other signals are 5V as they go through the CPLD.

| Pin | Name     | Dir | Pin | Name     | Dir |
| --: | :------- | :-- | --: | :------- | :-- |
|  A1 | `5V`     |     |  B1 | `5V`     |     |
|  A2 | `5V`     |     |  B2 | `5V`     |     |
|  A3 | `5V`     |     |  B3 | `5V`     |     |
|  A4 | `5V`     |     |  B4 | `5V`     |     |
|  A5 | `5V`     |     |  B5 | `5V`     |     |
|  A6 | `/RD`    | O   |  B6 | `/WR0`   | O   |
|  A7 | `/WR1`   | O   |  B7 | `GND`    |     |
|  A8 | `GND`    |     |  B8 | `SYSCLK` | O   |
|  A9 | `GND`    |     |  B9 | `GND`    |     |
| A10 | `/RESET` | O   | B10 | `/RESET` | O   |
| A11 | `GND`    |     | B11 | `GND`    |     |
| A12 | `/CS1`   | O   | B12 | `DMARQ5` | I   |
| A13 | `GND`    |     | B13 | `GND`    |     |
| A14 | `DMARQ5` | I   | B14 | `/CS1`   | O   |
| A15 | `/CS2`   | O   | B15 | `NC`     |     |
| A16 | `/IRQ10` | I   | B16 | `/IRQ10` | I   |
| A17 | `A22`    | O   | B17 | `A23`    | O   |
| A18 | `A20`    | O   | B18 | `A21`    | O   |
| A19 | `A14`    | O   | B19 | `A15`    | O   |
| A20 | `A12`    | O   | B20 | `A13`    | O   |
| A21 | `A6`     | O   | B21 | `A7`     | O   |
| A22 | `A4`     | O   | B22 | `A5`     | O   |
| A23 | `A2`     | O   | B23 | `A3`     | O   |
| A24 | `A0`     | O   | B24 | `A1`     | O   |
| A25 | `D14`    | IO  | B25 | `D15`    | IO  |
| A26 | `D12`    | IO  | B26 | `D13`    | IO  |
| A27 | `D10`    | IO  | B27 | `D11`    | IO  |
| A28 | `D8`     | IO  | B28 | `D9`     | IO  |
| A29 | `D6`     | IO  | B29 | `D7`     | IO  |
| A30 | `D4`     | IO  | B30 | `D5`     | IO  |
| A31 | `D2`     | IO  | B31 | `D3`     | IO  |
| A32 | `D0`     | IO  | B32 | `D1`     | IO  |
| A33 | `GND`    |     | B33 | `GND`    |     |
| A34 | `GND`    |     | B34 | `GND`    |     |
| A35 | `GND`    |     | B35 | `GND`    |     |
| A36 | `3.3V`   |     | B36 | `3.3V`   |     |
| A37 | `3.3V`   |     | B37 | `3.3V`   |     |
| A38 | `3.3V`   |     | B38 | `3.3V`   |     |
| A39 | `3.3V`   |     | B39 | `3.3V`   |     |
| A40 | `3.3V`   |     | B40 | `3.3V`   |     |

#### Analog CD-DA/MP3 audio input (`CD-DA IN`, `CN12`)

Connected to either the CD-ROM drive's audio output or to `CN16` on the digital
I/O board on systems equipped with a drive.

| Pin | Name   | Dir |
| --: | :----- | :-- |
|   1 | `LIN`  | I   |
|   2 | `AGND` |     |
|   3 | `AGND` |     |
|   4 | `RIN`  | I   |

#### Security cartridge slot (`CN14`)

All signals are 5V as they go through level shifters.

| Pin | Name     | Dir | Notes                        | Pin | Name     | Dir | Notes                              |
| --: | :------- | :-- | :--------------------------- | --: | :------- | :-- | :--------------------------------- |
|   1 | `GND`    |     |                              |  23 | `GND`    |     |                                    |
|   2 | `GND`    |     |                              |  24 | `GND`    |     |                                    |
|   3 | `/DSR`   | I   | Usually shorted to ground    |  25 | `MCUCLK` | O   | 7.3728 MHz JVS MCU clock           |
|   4 | `NC`     |     | May actually be `/DTR`?      |  26 | `GND`    |     |                                    |
|   5 | `TX`     | O   |                              |  27 | `DRDY`   | O   | Goes high when 573 updates `D0-D7` |
|   6 | `RX`     | I   |                              |  28 | `IO0`    | IO  |                                    |
|   7 | `/RESET` | IO  | System reset (from watchdog) |  29 | `/IREQ`  | I   | Sets `IRDY` when pulsed low        |
|   8 | `GND`    |     |                              |  30 | `/DACK`  | I   | Clears `DRDY` when pulsed low      |
|   9 | `GND`    |     |                              |  31 | `IRDY`   | O   | Goes low when 573 reads `I0-I7`    |
|  10 |          |     | Key (missing pin)            |  32 |          |     | Key (missing pin)                  |
|  11 | `?`      |     | Not connected?               |  33 | `I7`     | I   |                                    |
|  12 | `?`      |     | Not connected?               |  34 | `I6`     | I   |                                    |
|  13 | `D7`     | O   |                              |  35 | `I5`     | I   |                                    |
|  14 | `D6`     | O   |                              |  36 | `I4`     | I   |                                    |
|  15 | `D5`     | O   |                              |  37 | `I3`     | I   |                                    |
|  16 | `D4`     | O   |                              |  38 | `I2`     | I   |                                    |
|  17 | `D3`     | O   |                              |  39 | `I1`     | I   |                                    |
|  18 | `D2`     | O   |                              |  40 | `I0`     | I   |                                    |
|  19 | `D1`     | O   |                              |  41 | `5V`     |     |                                    |
|  20 | `D0`     | O   |                              |  42 | `5V`     |     |                                    |
|  21 | `5V`     |     |                              |  43 | `/RTS`   | O   | Usually shorted to `/CTS`          |
|  22 | `5V`     |     |                              |  44 | `/CTS`   | I   | Usually shorted to `/RTS`          |

#### Power input or output (`CN17`)

Commonly used to distribute the 12V rail to security cartridges with built-in
light drivers or external modules, but it can also used instead of the JAMMA
connector to supply power to the 573. The pinout is silkscreened on the board.

| Pin | Name  |
| --: | :---- |
|   1 | `12V` |
|   2 | `12V` |
|   3 | `GND` |
|   4 | `GND` |
|   5 | `5V`  |
|   6 | `5V`  |

#### I2S digital SPU audio output (`DIGITAL-AUDIO`, `CN19`)

Always unpopulated. Pin 4 outputs a 16.9344 MHz master clock (system clock
divided by 2, or 44100 Hz sampling rate multiplied by 384). This port does *not*
output audio from the CD-DA/MP3 input, which is not routed through the SPU.

| Pin | Name    | Dir |
| --: | :------ | :-- |
|   1 | `BCLK`  | O   |
|   2 | `SDOUT` | O   |
|   3 | `GND`   |     |
|   4 | `MCLK`  | O   |
|   5 | `LRCK`  | O   |

#### Secondary I/O board connector (`CN21`)

The address lines not wired to `CN10`, as well as the otherwise unused SIO0
controller and memory card bus, are broken out to this connector. No currently
known I/O board uses it. All signals are 3.3V.

| Pin | Name   | Dir | Pin | Name     | Dir |
| --: | :----- | :-- | --: | :------- | :-- |
|  A1 | `A8`   | O   |  B1 | `A9`     | O   |
|  A2 | `A10`  | O   |  B2 | `A11`    | O   |
|  A3 | `A16`  | O   |  B3 | `A17`    | O   |
|  A4 | `A18`  | O   |  B4 | `A19`    | O   |
|  A5 | `GND`  |     |  B5 | `?`      |     |
|  A6 | `GND`  |     |  B6 | `?`      |     |
|  A7 | `GND`  |     |  B7 | `GND`    |     |
|  A8 | `GND`  |     |  B8 | `DOTCLK` | O   |
|  A9 | `GND`  |     |  B9 | `GND`    |     |
| A10 | `GND`  |     | B10 | `/DSR`   | I   |
| A11 | `GND`  |     | B11 | `/DTR2`  | O   |
| A12 | `GND`  |     | B12 | `/DTR1`  | O   |
| A13 | `GND`  |     | B13 | `RX`     | I   |
| A14 | `GND`  |     | B14 | `TX`     | O   |
| A15 | `GND`  |     | B15 | `SCK`    | O   |

#### Watchdog test header (`WD-CHECK`, `CN22`)

Always unpopulated. Exposes the watchdog's clear input (pulsed whenever the CPU
writes to the watchdog clear register) as well as the reset output. Injecting
pulses to forcefully clear the watchdog should work, although it's much easier
to simply disable it by placing a jumper on `S86`.

| Pin | Name     | Dir |
| --: | :------- | :-- |
|   1 | `WDCLR`  | IO  |
|   2 | `/RESET` | O   |
|   3 | `5V`     |     |
|   4 | `GND`    |     |

#### GPU clock and compositing output (`CN23`)

Only present on later revisions of the main board and only populated on DDR
Karaoke Mix, which uses the semitransparency plane of the currently displayed
framebuffer as an alpha mask in order to composite the 573's output on top of
the incoming karaoke video feed.

| Pin | Name    | Dir | GPU pin |
| --: | :------ | :-- | ------: |
|   1 | `FSC`   | O   |     153 |
|   2 | `DMASK` | O   |     202 |
|   3 | `GND`   |     |         |

#### Security cartridge serial port (`CN24`)

Only present on later revisions of the main board and always unpopulated.
Exposes the same 5V SIO1 signals as the security cartridge slot.

| Pin | Name   | Dir | Cart pin |
| --: | :----- | :-- | -------: |
|   1 | `TX`   | O   |        5 |
|   2 | `RX`   | I   |        6 |
|   3 | `GND`  |     |          |
|   4 | `GND`  |     |          |
|   5 | `/RTS` | O   |       43 |
|   6 | `/CTS` | I   |       44 |

#### RGB video output (`CN25`)

Only present on later revisions of the main board and only populated on GunMania
and DDR Karaoke Mix, whose I/O boards feature RGB to S-video and composite
converters respectively. Exposes the same RGB signals as the JAMMA and DB15
connectors.

| Pin | Name    | Dir | JAMMA pin |
| --: | :------ | :-- | --------: |
|   1 | `GND`   | O   |           |
|   2 | `CSYNC` | O   |         P |
|   3 | `BOUT`  | O   |        13 |
|   4 | `GOUT`  | O   |         N |
|   5 | `ROUT`  | O   |        12 |

#### Watchdog configuration jumper (`S86`)

Always unpopulated. Shorting pins 2 and 3 will disable the watchdog while
keeping power-on reset functional. Pin 1 seems to be an active-high reset
output, unused by the 573.

| Pin | Name    | Dir |
| --: | :------ | :-- |
|   1 | `RESET` | O   |
|   2 | `GND`   |     |
|   3 | `WDEN`  | I   |

#### H8/3644 JVS MCU pin mapping

| Pin   | H8 GPIO   | Dir | Connected to       | Usage                                         |
| ----: | :-------- | :-- | :----------------- | :-------------------------------------------- |
|    11 | `P9_0`    | I   |                    | _Unused_                                      |
|    12 | `P9_1-2`  | O   | Konami ASIC        | Status code (readable from `0x1f400004`)      |
|    12 | `P9_3-4`  | O   | Konami ASIC        | Error code (readable from `0x1f400004`)       |
|    16 | `IRQ0`    | I   |                    | _Unused_                                      |
| 17-24 | `P6_0-7`  | O   | Konami ASIC        | Low byte of value readable from `0x1f40000a`  |
| 25-32 | `P5_0-7`  | O   | Konami ASIC        | High byte of value readable from `0x1f40000a` |
|    34 | `P7_3`    | I   | Handshaking logic  | Current `JVSDRDY` status                      |
|    35 | `P7_4`    | I   | Handshaking logic  | Current `JVSIRDY` status                      |
|    36 | `P7_5`    | I   |                    | _Unused_                                      |
|    37 | `P7_6`    | I   |                    | _Unused_                                      |
|    38 | `P7_7`    | I   |                    | _Unused_                                      |
| 39-46 | `P8_0-7`  | I   | Bus (via latch)    | High byte of value written to `0x1f680000`    |
|    47 | `P2_0`    | O   | RS-485 transceiver | JVS driver output enable                      |
|    48 | `P2_1`    | I   | RS-485 transceiver | JVS serial port RX                            |
|    49 | `P2_2`    | O   | RS-485 transceiver | JVS serial port TX                            |
|    50 | `P3_2`    | I   |                    | _Unused_                                      |
|    51 | `P3_1`    | I   |                    | _Unused_                                      |
|    52 | `P3_0`    | I   |                    | _Unused_                                      |
|    53 | `P1_0`    | O   | Handshaking logic  | `/JVSDACK` (clears `JVSDRDY` when pulsed low) |
|    54 | `P1_4`    | O   | Handshaking logic  | `JVSIREQ` (sets `JVSIRDY` when pulsed high)   |
|    55 | `P1_5`    | I   |                    | _Unused_                                      |
|    56 | `P1_6`    | I   |                    | _Unused_                                      |
|    57 | `P1_7`    | I   |                    | _Unused_                                      |
|  59-2 | `PB_7-0`  | I   | Bus (via latch)    | Low byte of value written to `0x1f680000`     |

### Analog I/O board pinouts (`GX700-PWB(F)`)

#### Output banks A, B (`CN33`, `CN34` respectively)

All outputs are open-drain. Pins 1 and 10 are tied together and connected to the
optocouplers' emitters.

| Pin | Name          | Dir |
| --: | :------------ | :-- |
|   1 | `ACOM`/`BCOM` |     |
|   2 | `A0`/`B0`     | O   |
|   3 | `A1`/`B1`     | O   |
|   4 | `A2`/`B2`     | O   |
|   5 | `A3`/`B3`     | O   |
|   6 | `A4`/`B4`     | O   |
|   7 | `A5`/`B5`     | O   |
|   8 | `A6`/`B6`     | O   |
|   9 | `A7`/`B7`     | O   |
|  10 | `ACOM`/`BCOM` |     |

#### Output bank C (`CN35`)

All outputs are open-drain. Unlike banks A and B, pin 10 is not tied to pin 1
but is instead connected to the EMI filters' ground (`FGND`), isolated from the
system ground but shared across all output banks.

| Pin | Name   | Dir |
| --: | :----- | :-- |
|   1 | `CCOM` |     |
|   2 | `C0`   | O   |
|   3 | `C1`   | O   |
|   4 | `C2`   | O   |
|   5 | `C3`   | O   |
|   6 | `C4`   | O   |
|   7 | `C5`   | O   |
|   8 | `C6`   | O   |
|   9 | `C7`   | O   |
|  10 | `FGND` |     |

#### Output bank D (`CN36`)

All outputs are open-drain.

| Pin | Name   | Dir |
| --: | :----- | :-- |
|   1 | `DCOM` |     |
|   2 | `D0`   | O   |
|   3 | `D1`   | O   |
|   4 | `D2`   | O   |
|   5 | `D3`   | O   |
|   6 | `FGND` |     |

### Digital I/O board pinouts (`GX894-PWB(B)A`)

#### Output bank C (`CN10`)

All outputs are open-drain. The optocouplers driving `C0-C3` have their emitters
wired to `CCOM0`, while those driving `C4-C7` have their emitters wired to
`CCOM1`.

| Pin | Name    | Dir |
| --: | :------ | :-- |
|   1 | `CCOM0` |     |
|   2 | `C0`    | O   |
|   3 | `C1`    | O   |
|   4 | `C2`    | O   |
|   5 | `C3`    | O   |
|   6 | `CCOM1` |     |
|   7 | `C4`    | O   |
|   8 | `C5`    | O   |
|   9 | `C6`    | O   |
|  10 | `C7`    | O   |

#### Output bank B (`CN11`)

All outputs are open-drain. The optocouplers driving `B0-B3` have their emitters
wired to `BCOM0`, while those driving `B4-B7` have their emitters wired to
`BCOM1`.

| Pin | Name    | Dir |
| --: | :------ | :-- |
|   1 | `BCOM0` |     |
|   2 | `B0`    | O   |
|   3 | `B1`    | O   |
|   4 | `B2`    | O   |
|   5 | `B3`    | O   |
|   6 | `BCOM1` |     |
|   7 | `B4`    | O   |
|   8 | `B5`    | O   |
|   9 | `B6`    | O   |
|  10 | `B7`    | O   |
|  11 | `NC`    |     |
|  12 | `NC`    |     |

#### Output bank A (`CN12`)

All outputs are open-drain. The optocouplers driving `A0-A3` have their emitters
wired to `ACOM0`, while those driving `A4-A7` have their emitters wired to
`ACOM1`.

| Pin | Name    | Dir |
| --: | :------ | :-- |
|   1 | `ACOM0` |     |
|   2 | `A0`    | O   |
|   3 | `A1`    | O   |
|   4 | `A2`    | O   |
|   5 | `A3`    | O   |
|   6 | `ACOM1` |     |
|   7 | `A4`    | O   |
|   8 | `A5`    | O   |
|   9 | `A6`    | O   |
|  10 | `A7`    | O   |
|  11 | `NC`    |     |
|  12 | `NC`    |     |
|  13 | `NC`    |     |

#### Output bank D (`CN13`)

All outputs are open-drain.

| Pin | Name   | Dir |
| --: | :----- | :-- |
|   1 | `DCOM` |     |
|   2 | `D0`   | O   |
|   3 | `D1`   | O   |
|   4 | `D2`   | O   |
|   5 | `D3`   | O   |

#### Input bank (`CN14`)

The pinout of this connector is currently unknown.

#### RS-232 serial port (`CN15`)

| Pin | Name   | Dir |
| --: | :----- | :-- |
|   1 | `TX`   | O   |
|   2 | `RX`   | O   |
|   3 | `GND`  |     |
|   4 | `GND`  |     |
|   5 | `RTS`  | O   |
|   6 | `CTS`  | O   |
|   7 | `DTR`  | O   |
|   8 | `DSR`  | O   |

#### Analog MP3 audio output (`CN16`)

Usually connected to `CN12` on the main board. GuitarFreaks routes this output
to a separate set of RCA jacks on the front I/O panel instead.

| Pin | Name   | Dir |
| --: | :----- | :-- |
|   1 | `LOUT` | O   |
|   2 | `AGND` |     |
|   3 | `AGND` |     |
|   4 | `ROUT` | O   |

#### Unknown (`CN17`)

The pinout of this connector is currently unknown.

#### I2S digital MP3 audio output (`CN18`)

| Pin | Name    | Dir | FPGA pin |
| --: | :------ | :-- | -------: |
|   1 | `MCLK`  | O   |       97 |
|   2 | `BCLK`  | O   |       94 |
|   3 | `SDOUT` | O   |       96 |
|   4 | `LRCK`  | O   |       95 |
|   5 | `?`     |     |          |
|   6 | `?`     |     |          |

#### Digital I/O XC9536 CPLD pin mapping

| Pin | JTAG | CPLD alt. | Dir | Connected to | Usage                                |
| --: | ---: | :-------- | :-- | :----------- | :----------------------------------- |
|   1 |   51 |           | IO  | System bus   | Data bus bit 15                      |
|   2 |  105 |           | IO  | System bus   | Data bus bit 14                      |
|   3 |  102 |           | IO  | System bus   | Data bus bit 13                      |
|   4 |   96 |           | IO  | System bus   | Data bus bit 12                      |
|   5 |   99 | `GCK1`    |     | Unknown      | Unknown (system clock?)              |
|   6 |   93 | `GCK2`    |     |              | _Unused_                             |
|   7 |   87 | `GCK3`    | O   | Light bank B | Output B3                            |
|   8 |   90 |           | O   | Light bank B | Output B2                            |
|   9 |   84 |           | O   | Light bank B | Output B1                            |
|  11 |   81 |           | O   | Light bank B | Output B0                            |
|  12 |   78 |           | O   | Light bank C | Output C7                            |
|  13 |   75 |           | O   | Light bank C | Output C6                            |
|  14 |   72 |           | O   | Light bank C | Output C5                            |
|  18 |   69 |           | O   | Light bank C | Output C4                            |
|  19 |   66 |           | O   | Light bank C | Output C3                            |
|  20 |   63 |           | O   | Light bank C | Output C2                            |
|  22 |   60 |           | O   | Light bank C | Output C1                            |
|  24 |   57 |           | O   | Light bank C | Output C0                            |
|  25 |    3 |           | O   | Audio DAC    | Chip reset/mute                      |
|  26 |    6 |           | ?   | FPGA         | Configuration status/reset (`/INIT`) |
|  27 |    9 |           | ?   | FPGA         | Configuration status (`DONE`)        |
|  28 |   12 |           | O   | FPGA         | Configuration reset (`/PROGRAM`)     |
|  29 |   15 |           | O   | FPGA         | Configuration data (`DIN`)           |
|  33 |   18 |           | O   | FPGA         | Configuration bit clock (`CCLK`)     |
|  34 |   21 |           | I   | System bus   | I/O board chip select (`/CS?`)       |
|  35 |   24 |           | I   | System bus   | Read/write strobe?                   |
|  36 |   27 |           | I   | System bus   | Read/write strobe?                   |
|  37 |   30 |           | I   | System bus   | Address bus bit 7                    |
|  38 |   33 |           | I   | System bus   | Address bus bit 6                    |
|  39 |   36 | `GSR`     | I   | System bus   | Address bus bit 5                    |
|  40 |   39 | `GTS2`    | I   | System bus   | Address bus bit 4                    |
|  42 |   45 | `GTS1`    | I   | System bus   | Address bus bit 3                    |
|  43 |   42 |           | I   | System bus   | Address bus bit 2                    |
|  44 |   48 |           | I   | System bus   | Address bus bit 1                    |

#### Digital I/O XCS40XL FPGA pin mapping

| Pin   | JTAG | FPGA alt.     | Dir | Delay | Slew | Connected to         | Usage                            |
| ----: | ---: | :------------ | :-- | :---- | :--- | :------------------- | :------------------------------- |
|     2 |  170 | `GCK1`        | IO  | No    | Slow | DRAM                 | Data bus bit 4                   |
|     3 |  173 |               | IO  | No    | Slow | DRAM                 | Data bus bit 8                   |
|     4 |  176 |               | IO  | No    | Slow | DRAM                 | Data bus bit 9                   |
|     5 |  179 |               | IO  | No    | Slow | DRAM                 | Data bus bit 10                  |
|     6 |  182 | `TDI`         |     |       |      |                      | _Unused_                         |
|     7 |  185 | `TCK`         |     |       |      |                      | _Unused_                         |
|     8 |  194 |               | IO  | No    | Slow | DRAM                 | Data bus bit 3                   |
|     9 |  197 |               | IO  | No    | Slow | DRAM                 | Data bus bit 11                  |
|    10 |  200 |               | IO  | No    | Slow | DRAM                 | Data bus bit 2                   |
|    11 |  203 |               | IO  | No    | Slow | DRAM                 | Data bus bit 12                  |
|    12 |  206 |               |     |       |      |                      | _Unused_                         |
|    14 |  212 |               | IO  | No    | Slow | DRAM                 | Data bus bit 1                   |
|    15 |  215 |               | IO  | No    | Slow | DRAM                 | Data bus bit 0                   |
|    16 |  218 | `TMS`         |     |       |      |                      | _Unused_                         |
|    17 |  221 |               | IO  | No    | Slow | DRAM                 | Data bus bit 13                  |
|    19 |  236 |               | IO  | No    | Slow | DRAM                 | Data bus bit 14                  |
|    20 |  239 |               | IO  | No    | Slow | DRAM                 | Data bus bit 15                  |
|    21 |  242 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 3                   |
|    22 |  245 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 2                   |
|    23 |  248 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 4                   |
|    24 |  251 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 1                   |
|    27 |  254 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 5                   |
|    28 |  257 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 0                   |
|    29 |  260 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 6                   |
|    30 |  263 |               | O   |       | Slow | SRAM                 | Address bus bit 0                |
|    31 |  266 |               | IO  | Yes   | Slow | SRAM                 | Data bus bit 7                   |
|    32 |  269 |               | O   |       | Slow | SRAM                 | Address bus bit 1                |
|    34 |  284 |               | O   |       | Fast | SRAM                 | Chip select                      |
|    35 |  287 |               | O   |       | Slow | SRAM                 | Address bus bit 2                |
|    36 |  290 |               | O   |       | Slow | SRAM                 | Address bus bit 10               |
|    37 |  293 |               | O   |       | Slow | SRAM                 | Address bus bit 3                |
|    39 |  299 |               |     |       |      |                      | _Unused_                         |
|    40 |  302 |               | O   |       | Fast | SRAM                 | Output enable                    |
|    41 |  305 |               | O   |       | Slow | SRAM                 | Address bus bit 4                |
|    42 |  308 |               | O   |       | Slow | SRAM                 | Address bus bit 11               |
|    43 |  311 |               | O   |       | Slow | SRAM                 | Address bus bit 5                |
|    44 |  320 |               | O   |       | Slow | SRAM                 | Address bus bit 9                |
|    45 |  323 |               | O   |       | Slow | SRAM                 | Address bus bit 6                |
|    46 |  326 |               | O   |       | Slow | SRAM                 | Address bus bit 8                |
|    47 |  329 |               | O   |       | Slow | SRAM                 | Address bus bit 7                |
|    48 |  332 |               | O   |       | Slow | SRAM                 | Address bus bit 13               |
|    49 |  335 | `GCK2`        | O   |       | Slow | SRAM                 | Address bus bit 12               |
|    55 |  342 | `GCK3`        | O   |       | Fast | SRAM                 | Write enable                     |
|    56 |  345 | `/HDC`        | O   |       | Slow | SRAM                 | Address bus bit 14               |
|    57 |  348 |               | O   |       | Slow | SRAM                 | Address bus bit 16               |
|    58 |  351 |               | O   |       | Slow | SRAM                 | Address bus bit 15               |
|    59 |  354 |               | O   |       | Slow | Light bank D         | Output D3                        |
|    60 |  357 | `LDC`         | O   |       | Slow | Light bank D         | Output D2                        |
|    61 |  366 |               | I   | No    |      | Input bank           | Input 0                          |
|    62 |  369 |               | I   | No    |      | Input bank           | Input 1                          |
|    63 |  372 |               | I   | No    |      | Input bank           | Input 2                          |
|    64 |  375 |               | I   | No    |      | Input bank           | Input 3                          |
|    65 |  378 |               |     |       |      |                      | _Unused_                         |
|    67 |  384 |               | O   |       | Slow | Light bank D         | Output D1                        |
|    68 |  387 |               | O   |       | Slow | Light bank D         | Output D0                        |
|    69 |  390 |               | O   |       | Slow | Light bank B         | Output B7                        |
|    70 |  393 |               | O   |       | Slow | Light bank B         | Output B6                        |
|    72 |  396 |               | O   |       | Slow | Light bank B         | Output B5                        |
|    73 |  399 |               | O   |       | Slow | Light bank B         | Output B4                        |
|    74 |  414 |               | O   |       | Slow | Light bank A         | Output A3                        |
|    75 |  417 |               | O   |       | Slow | Light bank A         | Output A2                        |
|    76 |  420 |               | O   |       | Slow | Light bank A         | Output A1                        |
|    77 |  423 | `/INIT`       | IO  | -     | -    | CPLD                 | Configuration status/reset       |
|    80 |  426 |               | O   |       | Slow | Light bank A         | Output A0                        |
|    81 |  429 |               | O   |       | Slow | Light bank A         | Output A7                        |
|    82 |  432 |               | O   |       | Slow | Light bank A         | Output A6                        |
|    83 |  435 |               | O   |       | Slow | Light bank A         | Output A5                        |
|    84 |  438 |               | O   |       | Slow | Light bank A         | Output A4                        |
|    85 |  441 |               | I   | No    |      | RS-232 transceiver   | Serial port DSR                  |
|    87 |  456 |               | O   |       | Slow | RS-232 transceiver   | Serial port DTR                  |
|    88 |  459 |               | I   | No    |      | RS-232 transceiver   | Serial port RX                   |
|    89 |  462 |               | O   |       | Slow | RS-232 transceiver   | Serial port TX                   |
|    90 |  465 |               | I   | Yes   |      | RS-232 transceiver   | Serial port CTS                  |
|    92 |  471 |               |     |       |      |                      | _Unused_                         |
|    93 |  474 |               | O   |       | Slow | RS-232 transceiver   | Serial port RTS                  |
|    94 |  477 |               | O   |       | Slow | Audio DAC            | I2S bit clock (`BCLK`)           |
|    95 |  480 |               | O   |       | Slow | Audio DAC            | I2S frame clock (`LRCK`)         |
|    96 |  483 |               | O   |       | Slow | Audio DAC            | I2S data input (`SDIN`)          |
|    97 |  492 |               | O   |       | Slow | Audio DAC            | I2S master clock (`MCLK`)        |
|    98 |  495 |               | O   |       | Slow | ARCnet transceiver   | Network TX enable?               |
|    99 |  498 |               | O   |       | Slow | ARCnet transceiver   | Network TX?                      |
|   100 |  501 |               | I   | Yes   |      | ARCnet transceiver   | Network RX                       |
|   101 |  504 |               |     |       |      |                      | _Unused_                         |
|   102 |  507 | `GCK4`        |     |       |      |                      | _Unused_                         |
|   104 |      | `DONE`        | IO  | -     | -    | CPLD                 | Configuration status             |
|   106 |      | `/PROGRAM`    | I   | -     | -    | CPLD                 | Configuration reset              |
|   107 |  510 | `D7`          | IO  | No    | Slow | DS2433 (unpopulated) | Unused 1-wire bus (open-drain)   |
|   108 |  513 | `GCK5`        |     |       |      |                      | _Unused_                         |
|   109 |  516 |               | IO  | No    | Slow | DS2401               | 1-wire bus (open-drain)          |
|   110 |  519 |               | I   | No    |      | System bus           | Address bus bit 7                |
|   111 |  525 |               |     |       |      |                      | _Unused_                         |
|   112 |  534 | `D6`          | I   | No    |      | System bus           | Address bus bit 6                |
|   113 |  537 |               | I   | No    |      | System bus           | Address bus bit 5                |
|   114 |  540 |               | I   | No    |      | System bus           | Address bus bit 4                |
|   115 |  543 |               | I   | No    |      | System bus           | Address bus bit 3                |
|   116 |  546 |               | I   | No    |      | System bus           | Address bus bit 2                |
|   117 |  549 |               | I   | No    |      | System bus           | Address bus bit 1                |
|   119 |  558 |               | O   |       | Slow | Unknown              | Unknown                          |
|   120 |  561 |               | IO  | Yes   | Slow | System bus           | Data bus bit 15                  |
|   122 |  564 | `D5`          | IO  | Yes   | Slow | System bus           | Data bus bit 14                  |
|   123 |  567 |               | IO  | Yes   | Slow | System bus           | Data bus bit 13                  |
|   124 |  576 |               | IO  | Yes   | Slow | System bus           | Data bus bit 12                  |
|   125 |  579 |               | IO  | Yes   | Slow | System bus           | Data bus bit 11                  |
|   126 |  582 |               | IO  | Yes   | Slow | System bus           | Data bus bit 10                  |
|   127 |  585 |               | IO  | Yes   | Slow | System bus           | Data bus bit 9                   |
|   128 |  588 | `D4`          | IO  | Yes   | Slow | System bus           | Data bus bit 8                   |
|   129 |  591 |               | IO  | Yes   | Slow | System bus           | Data bus bit 7                   |
|   132 |  594 | `D3`          | IO  | Yes   | Slow | System bus           | Data bus bit 6                   |
|   133 |  597 |               | IO  | Yes   | Slow | System bus           | Data bus bit 5                   |
|   134 |  600 |               | IO  | Yes   | Slow | System bus           | Data bus bit 4                   |
|   135 |  603 |               | IO  | Yes   | Slow | System bus           | Data bus bit 3                   |
|   136 |  606 |               | IO  | Yes   | Slow | System bus           | Data bus bit 2                   |
|   137 |  609 |               | IO  | Yes   | Slow | System bus           | Data bus bit 1                   |
|   138 |  618 | `D2`          | IO  | Yes   | Slow | System bus           | Data bus bit 0                   |
|   139 |  621 |               |     |       |      |                      | _Unused_                         |
|   141 |  624 |               |     |       |      |                      | _Unused_                         |
|   142 |  627 |               | I   | No    |      | System bus           | I/O board chip select (`/CS?`)   |
|   144 |  639 |               |     |       |      |                      | _Unused_                         |
|   145 |  642 |               | I   | No    |      | System bus           | Write strobe (`/WR0`)            |
|   146 |  645 |               | I   | No    |      | System bus           | Read strobe (`/RD`)              |
|   147 |  648 |               |     |       |      |                      | _Unused_                         |
|   148 |  651 |               | I   | No    |      | MAS3507D             | MP3 data request flag (`PI19`)   |
|   149 |  654 | `D1`          | O   |       | Slow | MAS3507D             | PIO chip select (`/PCS`)         |
|   150 |  657 |               | IO  | No    | Slow | MAS3507D             | I2C `SDA`                        |
|   151 |  666 |               | IO  | No    | Slow | MAS3507D             | I2C `SCL`                        |
|   152 |  669 |               | O   |       | Slow | MAS3507D             | Chip reset (`/POR`)              |
|   153 |  672 | `D0`/`DIN`    | I   | -     | -    | CPLD                 | Configuration data               |
|   154 |  675 | `GCK6`/`DOUT` |     |       |      |                      | _Unused_                         |
|   155 |      | `CCLK`        | I   | -     | -    | CPLD                 | Configuration bit clock          |
|   157 |    0 | `TDO`         |     |       |      |                      | _Unused_                         |
|   159 |    2 |               | I   | No    |      | MAS3507D             | Master clock ready flag (`WRDY`) |
|   160 |    5 | `GCK7`        | I   | No    |      | Crystal oscillator   | 29.45 MHz main clock             |
|   161 |    8 |               | I   | No    |      | MAS3507D             | MP3 frame sync flag (`PI4`)      |
|   162 |   11 |               | I   | No    |      | MAS3507D             | I2S master clock (`CLKO`/`MCLK`) |
|   163 |   14 | `CS1`         | O   |       | Slow | MAS3507D             | 14.725 MHz clock input (`CLKI`)  |
|   164 |   17 |               | O   |       | Slow | MAS3507D             | MP3 stream bit clock (`SIC`)     |
|   165 |   26 |               |     |       |      |                      | _Unused_                         |
|   166 |   32 |               | O   |       | Slow | MAS3507D             | MP3 stream frame clock (`SII`)   |
|   167 |   35 |               | O   |       | Slow | MAS3507D             | MP3 stream data input (`SID`)    |
|   168 |   38 |               | I   | No    |      | MAS3507D             | MP3 error flag (`PI8`)           |
|   169 |   41 |               | I   | No    |      | MAS3507D             | I2S bit clock (`SOC`/`BCLK`)     |
|   171 |   44 |               | I   | No    |      | MAS3507D             | I2S frame clock (`SOI`/`LRCK`)   |
|   172 |   47 |               | I   | No    |      | MAS3507D             | I2S data output (`SOD`/`SDOUT`)  |
|   174 |   62 |               | O   |       | Slow | DRAM                 | Address bus bit 5                |
|   175 |   65 |               | O   |       | Slow | DRAM                 | Address bus bit 6                |
|   176 |   68 |               | O   |       | Slow | DRAM                 | Address bus bit 4                |
|   177 |   71 |               | O   |       | Slow | DRAM                 | Address bus bit 7                |
|   178 |   74 |               | O   |       | Slow | DRAM                 | Address bus bit 3                |
|   179 |   77 |               | O   |       | Slow | DRAM                 | Address bus bit 8                |
|   180 |   80 |               | O   |       | Slow | DRAM                 | Address bus bit 2                |
|   181 |   83 |               | O   |       | Slow | DRAM                 | Address bus bit 9                |
|   184 |   86 |               | O   |       | Slow | DRAM                 | Address bus bit 1                |
|   185 |   89 |               | O   |       | Slow | DRAM                 | Address bus bit 10               |
|   186 |   92 |               | O   |       | Slow | DRAM                 | Address bus bit 0                |
|   187 |   95 |               | O   |       | Slow | DRAM                 | Address bus bit 11               |
|   188 |   98 |               | O   |       | Slow | DRAM                 | Address bus bit 12               |
|   189 |  101 |               | O   |       | Fast | DRAM                 | 22J row address strobe           |
|   190 |  104 |               | O   |       | Fast | DRAM                 | Output enable                    |
|   191 |  107 |               | O   |       | Fast | DRAM                 | 22H row address strobe           |
|   193 |  122 |               | O   |       | Fast | DRAM                 | 22G row address strobe           |
|   194 |  125 |               | O   |       | Fast | DRAM                 | 22G upper column address strobe  |
|   196 |  128 |               | O   |       | Fast | DRAM                 | Write enable                     |
|   197 |  131 |               | O   |       | Fast | DRAM                 | 22G lower column address strobe  |
|   198 |  134 |               | O   |       | Fast | DRAM                 | 22H upper column address strobe  |
|   199 |  137 |               | O   |       | Fast | DRAM                 | 22H lower column address strobe  |
|   200 |  140 |               | O   |       | Fast | DRAM                 | 22J upper column address strobe  |
|   201 |  143 |               | O   |       | Fast | DRAM                 | 22J lower column address strobe  |
|   202 |  152 |               |     |       |      |                      | _Unused_                         |
|   203 |  155 |               |     |       |      |                      | _Unused_                         |
|   204 |  158 |               | IO  | No    | Slow | DRAM                 | Data bus bit 7                   |
|   205 |  161 |               | IO  | No    | Slow | DRAM                 | Data bus bit 6                   |
|   206 |  164 |               | IO  | No    | Slow | DRAM                 | Data bus bit 5                   |
|   207 |  167 | `GCK8`        | I   | No    |      | Crystal oscillator   | 19.6608 MHz (UART?) clock        |

Notes:

- The FPGA has no access to the 33.8688 MHz system clock, despite it being
  broken out to the I/O board connector. Konami's bitstreams use the 29.45 MHz
  oscillator as the main clock, additionally dividing it down to 14.725 MHz and
  feeding it to the MAS3507D's clock input.
- The 19.6608 MHz clock is left unused by most (all?) bitstream variants, but
  was likely meant to be used for RS-232. Dividing it by 512, 1024, 2048 or 4096
  will give the standard baud rates of 38400, 19200, 9600 and 4800 respectively.
  The UART driving the RS-232 port may have been removed from the bitstream at
  some point to make room for the other circuitry.
- Most input pins have external pullup resistors, so enabling the FPGA's
  internal pullups is not necessary.
- Light outputs must be configured as open-drain in order to work properly. The
  optocouplers' anodes are fed 5V rather than 3.3V; setting the outputs high
  instead of putting them into high-z will result in a voltage difference of
  ~1.7V across the optocouplers' LEDs, which is enough to trigger them.
- The "5V tolerant I/O" option in Xilinx's bitstream generator **must** be
  enabled when building custom bitstreams. There are no level shifters between
  the FPGA and the 573's system bus.
- The FPGA's `M0`, `M1` and `/PWRDWN` pins seem to be hardwired to 3.3V.
- The DAC's `CKS` pin is hardwired to ground, so the I2S master clock must
  always be 256 \* the sampling rate.
- Pin 119 is set up by the DDR bitstream as a logical AND of pins 61-64. It is
  currently unclear if it goes to any other part on the board.
- Konami's bitstreams map the DRAM chips into a single address space as follows:
  - `0x0000000-0x07fffff`: 22H
  - `0x0800000-0x0ffffff`: 22J
  - `0x1000000-0x17fffff`: 22G

### Security cartridge pinouts

#### RS-232 "network" connector

Present on `GX700-PWB(E)`, `GX896-PWB(A)A`, `GX883-PWB(D)` and `GE949-PWB(D)A`
cartridges. All signals use RS-232 voltage levels. Note that DTR and DSR are
*not* wired to the respective SIO1 pins but to the security cartridge I/O pins.

On the `GX700-PWB(E)` cartridge the signals are referenced to the 573's ground
and not isolated. On all other cartridge types, the RS-232 transceiver is
powered through an isolated DC-DC module and fully eletrically isolated from the
573; the `GND` pin is the transceiver's isolated ground.

| Pin | Name  | Dir |
| --: | :---- | :-- |
|   1 | `TX`  | O   |
|   2 | `RX`  | I   |
|   3 | `DTR` | O   |
|   4 | `DSR` | I   |
|   5 | `GND` |     |

#### "Control" or "amp box" connector

Present on `GX896-PWB(A)A`, `GX883-PWB(D)` and `GE949-PWB(D)A` cartridges.
Unlike the RS-232 connector these are unisolated 5V logic level signals driven
through open-drain buffers, with pullup resistors to 5V.

| Pin | Name    | Dir |
| --: | :------ | :-- |
|   1 | `GND`   |     |
|   2 | `CTRL0` | O   |
|   3 | `GND`   |     |
|   4 | `CTRL1` | O   |
|   5 | `CTRL2` | O   |
|   6 | `5V`    |     |

## Credits, sources and links

This document is the result of a joint effort consisting of years' worth of
research, brought to you by:

- **spicyjpeg** (documentation writing, software reverse engineering, testing)
- **Naoki Saito** (hardware reverse engineering, schematic tracing, testing)
- **987123879113** (digital I/O board reverse engineering, testing)
- **smf** (initial reverse engineering and implementation of the 573 MAME
  driver)
- **tensionvex** (testing)
- **Shiz** (security cartridge details)

Traced schematics, images, datasheets and additional resources are available in
[Naoki's 573 repo](https://github.com/NaokiS28/KSystem-573). Shiz also maintains
a [general documentation repo](https://github.com/Shizmob/arcade-docs) for
several arcade systems including the 573.

Some information has been aggregated from the following sources:

- [System 573 MAME driver](https://github.com/mamedev/mame/blob/master/src/mame/konami/ksys573.cpp)
- [987123879113's MAME fork](https://github.com/987123879113/mame) and
  [gobbletools](https://github.com/987123879113/gobbletools)
- ATAPI specification (revision 2.6, January 1996)
- ATA/ATAPI-6 specification (revision 1e, June 2001)
- JVS specification (third edition, command reference revision 1.3)
- HD6473644, M48T58, ADC0834, XCS40XL, MAS3507D, X76F041 and X76F100 datasheets
- [DDR stage I/O protocol notes](https://github.com/nchowning/open-io/blob/master/NOTES.txt)
- [JVS protocol notes](https://github.com/TheOnlyJoey/openjvs/wiki/Protocol)
- [Original (incomplete) list of working ATAPI drives](https://gamerepair.info/hardware/1_system_573)
- ["The Almost Definitive Guide to Session Mode Linking"](https://www2.gvsu.edu/brittedg/SessionGuide.pdf)
- [Callus Next PCB information](https://callusnext.com/pcbs)
- [Light output for Salary Man Champ](http://solid-orange.com/1569) and
  [Hyper Bishi Bashi Champ](http://solid-orange.com/1581)
- [system573\_tool](https://github.com/mrdion/system573_tool)
- [Arduino-based master calendar implementation](https://www.arcade-projects.com/threads/konami-system-573-master-calendar.2646/#post-34907)
- [Z-I-v forum post with security cartridge info](https://zenius-i-vanisher.com/v5.2/viewthread.php?threadid=2825)

Huge thanks to the Rhythm Game Cabs Discord server and everyone who provided
valuable information about the 573!
