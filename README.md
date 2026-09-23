# psx-spx — PSX Hardware Reference Plugin for Claude Code

Complete PlayStation 1 hardware reference archived from [psx-spx.consoledev.net](https://psx-spx.consoledev.net) as Claude Code model-invoked skills.

## What's included

46 skills covering the entire PSX technical specification:

- **CPU** — MIPS R3000A registers, opcodes, COP0 exceptions
- **GPU** — GP0/GP1 commands, VRAM, textures, timings
- **GTE** — Geometry Transformation Engine commands and registers, measured pipeline timings
- **MDEC** — Macroblock decoder, video decompression
- **SPU** — Sound processing, ADPCM, reverb
- **DMA** — DMA channels, linked list transfers
- **Memory** — Memory map, I/O map, memory control, partial-word MMIO writes
- **CDROM** — Drive commands, disc format, file formats, compression
- **Controllers** — Pad protocol, memory cards, special controllers
- **BIOS/Kernel** — Function reference, boot sequence, internals
- **Timers, Interrupts, Serial I/O**
- **Hardware** — Pinouts, model numbers, arcade cabinets, Pocketstation, dev boards and DECI/PCDRV protocol

Skills are model-invoked — Claude loads them automatically when the task context matches.

## Installation

```bash
# Add the marketplace (once)
/plugin marketplace add sadnescity/claude-plugins

# Install the plugin
/plugin install psx-spx@sadnescity-plugins
```

For local development/testing:

```bash
claude --plugin-dir /path/to/psx-spx-claude-plugin
```

## Source

Content archived from [psx-spx.consoledev.net](https://psx-spx.consoledev.net),
sourced from [github.com/psx-spx/psx-spx.github.io](https://github.com/psx-spx/psx-spx.github.io).

Built from upstream commit
[`d4b3d802e20c7e079482a8f5d09d05dc6cba9b09`](https://github.com/psx-spx/psx-spx.github.io/commit/d4b3d802e20c7e079482a8f5d09d05dc6cba9b09)
(2026-09-23). To rebuild:

```bash
git clone https://github.com/psx-spx/psx-spx.github.io /tmp/psx-spx-repo
git -C /tmp/psx-spx-repo checkout d4b3d802e20c7e079482a8f5d09d05dc6cba9b09
PSX_SPX_DOCS=/tmp/psx-spx-repo/docs python3 build_plugin.py
python3 check_links.py
```

The file-to-skill mapping lives in the `SKILLS` table of `build_plugin.py`.

## License

Content is [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) (public domain).
