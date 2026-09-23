#!/usr/bin/env python3
"""Build script for psx-spx Claude Code plugin skills.

Reads source markdown files from the psx-spx docs directory ($PSX_SPX_DOCS,
default /tmp/psx-spx-repo/docs, a checkout of
https://github.com/psx-spx/psx-spx.github.io) and generates Claude Code plugin
skills at <repo>/skills/<name>/SKILL.md ($PSX_SPX_SKILLS overrides).

Each skill gets YAML frontmatter (name + description) prepended to the
markdown content.

Internal links of the original site (``file.md#anchor``) are rewritten to point
at the skill that contains the target section (``../<skill>/SKILL.md#anchor``,
or ``#anchor`` inside the same skill), using GitHub-flavoured markdown anchors
computed from the generated headings. Links whose target is not part of the
plugin are turned into plain text and listed at the end of the build.
"""

import html
import os
import re
import shutil
import sys
import unicodedata
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.environ.get("PSX_SPX_DOCS", "/tmp/psx-spx-repo/docs")
OUTPUT_DIR = os.environ.get("PSX_SPX_SKILLS", os.path.join(SCRIPT_DIR, "skills"))

# ---------------------------------------------------------------------------
# Skill configuration
# ---------------------------------------------------------------------------
# Each entry is either:
#   - Intact: {"name", "source", "description"} — copies entire file
#   - Split:  {"name", "source", "description", "splits": [...]} — splits at
#             H2 boundaries. Each split has name, description, start_heading
#             (inclusive), end_heading (exclusive or None for last chunk).
#             The top-level name/description are unused for split entries.

SKILLS = [
    # ── Intact pages (19) ──────────────────────────────────────────────
    {
        "name": "gpu",
        "source": "graphicsprocessingunitgpu.md",
        "description": "PSX GPU specifications: GP0 rendering commands (polygons, lines, rectangles), GP1 display control, texture formats, semi-transparency, VRAM layout, texture caching, GPU timings, status register. Use when working with GPU commands, VRAM, textures, or display modes.",
    },
    {
        "name": "spu",
        "source": "soundprocessingunitspu.md",
        "description": "PSX SPU (Sound Processing Unit): ADPCM samples/pitch, volume/ADSR envelopes, voice flags, noise generator, control/status registers, SPU RAM access, reverb, IRQ. Use when working with audio, sound effects, music playback, or SPU registers.",
    },
    {
        "name": "cheat-devices",
        "source": "cheatdevices.md",
        "description": "PSX cheat devices: GameShark, Action Replay, Xplorer/Caetla, cheat code formats, memory patching. Use when working with cheat codes or memory patching devices.",
    },
    {
        "name": "cdrom-vcd",
        "source": "cdromvideocdsvcd.md",
        "description": "PSX Video CD (VCD) support: ISO filesystem, MPEG-1 streams, VCD versions, playback control, MP2 audio. Use when working with Video CDs or MPEG playback on PSX.",
    },
    {
        "name": "cpu",
        "source": "cpuspecifications.md",
        "description": "PSX CPU (MIPS R3000A): registers (R0-R31, HI/LO, PC), opcode encoding, load/store/ALU/jump/coprocessor opcodes, pseudo opcodes, COP0 exception handling, debug registers. Use when writing or analyzing MIPS assembly, understanding instruction encoding, or debugging exceptions.",
    },
    {
        "name": "gte",
        "source": "geometrytransformationenginegte.md",
        "description": "PSX GTE (Geometry Transformation Engine, COP2): data/control registers, opcode encoding, coordinate calculation (RTPS/RTPT/MVMVA), general purpose math (SQR/OP/GPF), color calculation (DPCS/NCDS/CDP), division inaccuracy. Use when working with 3D transformations, GTE commands, or fixed-point math.",
    },
    {
        "name": "expansion-port",
        "source": "expansionportpio.md",
        "description": "PSX Expansion Port (PIO): EXP1/EXP2/EXP3 regions, ROM header, DUART (SCN2681), DTL-H2000 dev board I/O, emulation expansions (Nocash, PCSX-Redux). Use when working with expansion hardware or dev board features.",
    },
    {
        "name": "hardware-numbers",
        "source": "hardwarenumbers.md",
        "description": "PSX hardware model numbers: console variants (SCPH-xxxx), PSone, PS2, dev kits (DTL), SN Systems/Psy-Q, licensed peripherals by region, CDROM game codes. Use when identifying hardware models or peripheral part numbers.",
    },
    {
        "name": "mdec",
        "source": "macroblockdecodermdec.md",
        "description": "PSX MDEC (Macroblock Decoder): I/O ports, decode commands, quant/scale tables, decompression pipeline (RLE, IDCT, YUV-to-RGB), data format (colored 16x16 / mono 8x8 macroblocks), STR files. Use when working with FMV video decoding, MDEC commands, or video compression.",
    },
    {
        "name": "dev-boards",
        "source": "psxdevboardchipsets.md",
        "description": "PSX development board chipsets: DTL-H2000/H2500/H2700 boards, blue/green debug stations, component lists. Use when working with PSX dev hardware or debug stations.",
    },
    {
        "name": "memory-control",
        "source": "memorycontrol.md",
        "description": "PSX Memory Control registers: expansion base addresses, delay/size configuration for EXP1/EXP2/EXP3/BIOS/SPU/CDROM, COM_DELAY, RAM_SIZE, cache configuration (BIU register at FFFE0130h). Use when configuring memory timings or cache behavior.",
    },
    {
        "name": "sio",
        "source": "serialinterfacessio.md",
        "description": "PSX Serial Interfaces (SIO): SIO0 (controller/memory card) and SIO1 (external serial) registers - TX/RX data, status, mode, control, baud rate. Link cable games list. Use when working with serial communication, controller protocol, or link cable.",
    },
    {
        "name": "io-map",
        "source": "iomap.md",
        "description": "PSX I/O Map: complete register address listing for all hardware - memory control, peripherals, interrupts, DMA, timers, CDROM, GPU, MDEC, SPU voices/control/reverb, expansion regions, BIOS. Use as quick reference to find which address maps to which hardware register.",
    },
    {
        "name": "dma",
        "source": "dmachannels.md",
        "description": "PSX DMA channels: MADR/BCR/CHCR registers, DPCR control, DICR interrupts, linked list DMA (for GPU OT), transfer rates, hyper page mode, CPU behavior during DMA. Use when working with DMA transfers, GPU ordering tables, or SPU/CDROM data streaming.",
    },
    {
        "name": "unpredictable-things",
        "source": "unpredictablethings.md",
        "description": "PSX hardware quirks: I/O write/read datasize restrictions, cache problems, writebuffer hazards, CPU load/store edge cases, register gotchas (R1/R26/R29), locked memory locations, I/O mirrors and garbage addresses. Use when debugging mysterious hardware behavior or emulation inaccuracies.",
    },
    {
        "name": "arcade-cabinets",
        "source": "arcadecabinets.md",
        "description": "PSX-based arcade cabinets: Namco System 11/12, Capcom ZN-1/ZN-2, Taito FX-1, Atlus PSX, Tecmo TPS. Use when working with PSX arcade hardware variants.",
    },
    {
        "name": "memory-map",
        "source": "memorymap.md",
        "description": "PSX Memory Map: KUSEG/KSEG0/KSEG1/KSEG2 regions, Main RAM (2MB), scratchpad, I/O ports, expansion regions, BIOS ROM, cache control. Address mirroring, memory exceptions, write queue behavior. Use when working with memory addresses, address translation, or RAM layout.",
    },
    {
        "name": "timers",
        "source": "timers.md",
        "description": "PSX Timers (Root Counters): Timer 0-2 registers - current value, counter mode (sync, reset, IRQ, clock source), target value. Dotclock/Hblank sources, reset/wrap behavior. Use when working with timer interrupts, vsync timing, or frame counting.",
    },
    {
        "name": "interrupts",
        "source": "interrupts.md",
        "description": "PSX Interrupts: I_STAT and I_MASK registers, IRQ list (VBLANK, GPU, CDROM, DMA, Timer0-2, Controller/MemCard, SIO, SPU, Lightgun), edge-triggered behavior, acknowledge sequence, COP0 interrupt handling. Use when working with interrupt handlers or IRQ configuration.",
    },
    # ── Split pages (9 source files → 21 skills) ──────────────────────
    {
        "name": "kernelbios",
        "source": "kernelbios.md",
        "description": "",
        "splits": [
            {
                "name": "bios-file-cd-memcard",
                "description": "PSX BIOS kernel functions: file I/O (open/read/write/close), CDROM access, memory card read/write, function tables (A/B/C), BIOS memory map. Use when calling BIOS functions for file or storage access.",
                "start_heading": None,
                "end_heading": "BIOS Interrupt/Exception Handling",
            },
            {
                "name": "bios-irq-threads-timer",
                "description": "PSX BIOS kernel functions: interrupt/exception handling, events, threads, timers, joypad, GPU, memory allocation, memcpy/memset, string functions, printf. Use when calling BIOS functions for IRQ, events, threading, memory management, or string operations.",
                "start_heading": "BIOS Interrupt/Exception Handling",
                "end_heading": "BIOS Internal Boot Functions",
            },
            {
                "name": "bios-boot-internals",
                "description": "PSX BIOS internals: boot sequence, internal functions, PC file server (DTL-H), TTY console (std_io), character sets (Shift-JIS/ASCII), control blocks (TCB/EvCB/FCB), BIOS versions and patches. Use when analyzing boot process, BIOS internals, or patching BIOS behavior.",
                "start_heading": "BIOS Internal Boot Functions",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "cdromdrive",
        "source": "cdromdrive.md",
        "description": "",
        "splits": [
            {
                "name": "cdrom-io-commands",
                "description": "PSX CDROM drive: I/O port registers (index 0-3), command protocol, control/seek/read/status/audio commands with parameters and responses. Use when working with CDROM I/O, reading sectors, seeking, or playing CD audio.",
                "start_heading": None,
                "end_heading": "CDROM - Test Commands",
            },
            {
                "name": "cdrom-test-protection",
                "description": "PSX CDROM drive: test commands (version/region/chipset/SCEx), secret unlock, Video CD commands, response timing and queueing, mainloop behavior. Use when working with CDROM test/debug commands, copy protection, or response timing.",
                "start_heading": "CDROM - Test Commands",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "cdromformat",
        "source": "cdromformat.md",
        "description": "",
        "splits": [
            {
                "name": "cdrom-format-sectors",
                "description": "CDROM disk format: physical layout (tracks, sessions, lead-in/out), subchannel data (P-Q-R-W), sector encoding (CIRC, L1/L2 ECC, EDC), scrambling. Use when working with raw sector data, subchannel processing, or error correction.",
                "start_heading": None,
                "end_heading": "CDROM XA Subheader, File, Channel, Interleave",
            },
            {
                "name": "cdrom-xa-iso",
                "description": "CDROM XA and ISO: XA subheader and ADPCM audio compression, ISO9660 volume/file/directory descriptors, Joliet extension, PSX copy protection (SCEx strings, modchips, LibCrypt). Use when working with ISO filesystem, XA audio, or disc protection.",
                "start_heading": "CDROM XA Subheader, File, Channel, Interleave",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "controllersandmemorycards",
        "source": "controllersandmemorycards.md",
        "description": "",
        "splits": [
            {
                "name": "controllers-digital-analog",
                "description": "PSX controllers: communication protocol (active-low select, clock, data), standard digital/analog pads, mouse, racing controllers, lightguns (GunCon, Justifier), multitap adaptor. Use when working with controller input, pad protocol, or lightgun implementation.",
                "start_heading": None,
                "end_heading": "Controllers - Configuration Commands",
            },
            {
                "name": "controllers-special",
                "description": "PSX controllers advanced: configuration commands (enter/exit config mode), vibration/rumble, DualShock2 analog buttons, special controllers (dance mat, fishing, keyboard, DVD remote). Use when working with controller configuration, rumble, or special input devices.",
                "start_heading": "Controllers - Configuration Commands",
                "end_heading": "Memory Card Read/Write Commands",
            },
            {
                "name": "memory-cards",
                "description": "PSX Memory Cards: read/write command protocol (81h/52h/57h), data format (16KB, 15 blocks, directory, icon frames), save file structure, memory card image formats. Use when working with memory card I/O, save file management, or card image conversion.",
                "start_heading": "Memory Card Read/Write Commands",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "pinouts",
        "source": "pinouts.md",
        "description": "",
        "splits": [
            {
                "name": "pinouts-external",
                "description": "PSX external pinouts: controller/memory card port pins, A/V multi-out, serial I/O, power connector, expansion port, chipset summary table. Use when working with PSX external connectors or identifying chipset components.",
                "start_heading": None,
                "end_heading": "Pinouts - CPU Pinouts",
            },
            {
                "name": "pinouts-internal",
                "description": "PSX internal pinouts: CPU/GPU/SPU/DRV/HC05/MEM/CLK/PWR chip pin mappings, controller/joypad/multitap PCB component lists, memory card internals, PAL/NTSC mods, XBOO upload. Use when working with PSX internals, hardware mods, or chip-level debugging.",
                "start_heading": "Pinouts - CPU Pinouts",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "pocketstation",
        "source": "pocketstation.md",
        "description": "",
        "splits": [
            {
                "name": "pocketstation-hardware",
                "description": "Pocketstation hardware: ARM7TDMI CPU, I/O map, memory map (2KB RAM, 128KB flash), LCD/buzzer, interrupts, timers, RTC, infrared, SIO/IrDA communication, power control, battery. Use when working with Pocketstation hardware or peripherals.",
                "start_heading": None,
                "end_heading": "Pocketstation SWI Function Summary",
            },
            {
                "name": "pocketstation-software",
                "description": "Pocketstation software: SWI function reference (misc, comms, execute, date/time, flash), BU protocol commands (standard memory card + Pocketstation extensions), file header/icon format, XBOO cable upload. Use when working with Pocketstation software, BIOS calls, or memory card protocol.",
                "start_heading": "Pocketstation SWI Function Summary",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "cdrominternalinfoonpsxcdromcontroller",
        "source": "cdrominternalinfoonpsxcdromcontroller.md",
        "description": "",
        "splits": [
            {
                "name": "cdrom-internal-hc05",
                "description": "PSX CDROM internal: Motorola MC68HC05 8-bit sub-CPU instruction set, on-chip I/O ports (port A-D, timer, SCI, SPI), PSX-specific I/O usage, selftest mode for 52pin/80pin chips. Use when reverse-engineering CDROM controller firmware or sub-CPU behavior.",
                "start_heading": None,
                "end_heading": "CDROM Internal CXD1815Q Sub-CPU Configuration Registers",
            },
            {
                "name": "cdrom-internal-decoder",
                "description": "PSX CDROM internal: CXD1815Q sub-CPU configuration/status/address/misc registers, servo/signal processor commands (CXA1782BR, CXD2510Q, CXD2545Q, CXD2938Q), coefficient tables. Use when working with CDROM decoder/servo internals or chipset-specific commands.",
                "start_heading": "CDROM Internal CXD1815Q Sub-CPU Configuration Registers",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "konamisystem573",
        "source": "konamisystem573.md",
        "description": "",
        "splits": [
            {
                "name": "konami573-hardware",
                "description": "Konami System 573 arcade hardware: differences from PS1, register map (flash ROM, RTC, ATAPI, DIP switches, watchdog), JVS interface, I/O board variants (analog, digital, fishing, gun, DDR). Use when working with System 573 arcade hardware.",
                "start_heading": None,
                "end_heading": "Security cartridges",
            },
            {
                "name": "konami573-security-io",
                "description": "Konami System 573: security cartridges (install, game, network), external modules (multisession/PCMCIA/HDD), BIOS, bootleg mod boards, game-specific technical notes, PCB pinouts. Use when working with System 573 security, BIOS, or game-specific details.",
                "start_heading": "Security cartridges",
                "end_heading": None,
            },
        ],
    },
    {
        "name": "cdromfileformats",
        "source": "cdromfileformats.md",
        "description": "",
        "splits": [
            {
                "name": "cdrom-file-exe-tim",
                "description": "PSX file formats - executables and textures: PSX-EXE header and SYSTEM.CNF, CPE/SYM debug formats, TIM texture format (4/8/15/24-bit, CLUT), TGA, PCX, other bitmap formats. Use when working with PSX executables, TIM textures, or image file formats.",
                "start_heading": None,
                "end_heading": "CDROM File Video 2D Graphics CEL/BGD/TSQ/ANM/SDF (Sony)",
            },
            {
                "name": "cdrom-file-video-3d",
                "description": "PSX file formats - video/3D: 2D sprite formats (CEL/BGD/TSQ/ANM), 3D model formats (TMD/PMD/TOD/HMD/RSD), STR video streaming (and variants), BS picture compression (v2/v3, DC/AC encoding), polygon streaming. Use when working with FMV, 3D models, sprite animations, or video compression.",
                "start_heading": "CDROM File Video 2D Graphics CEL/BGD/TSQ/ANM/SDF (Sony)",
                "end_heading": "CDROM File Audio Single Samples VAG (Sony)",
            },
            {
                "name": "cdrom-file-audio",
                "description": "PSX file formats - audio: VAG samples (ADPCM), VAB/VH+VB sample banks, SEQ/SEP MIDI sequences, XA-ADPCM streaming, CD-DA tracks. Use when working with sound effects, music, or audio streaming formats.",
                "start_heading": "CDROM File Audio Single Samples VAG (Sony)",
                "end_heading": "CDROM File Archives with Filename",
            },
            {
                "name": "cdrom-file-archives",
                "description": "PSX file formats - archives: archive formats organized by type (filename-based, offset+size, offset-only, chunks, folders), plus game-specific archives (FF7-9, Crash, Soul Reaver, Gran Turismo, Ape Escape, Croc, etc.). Use when reverse-engineering game data archives or container formats.",
                "start_heading": "CDROM File Archives with Filename",
                "end_heading": "CDROM File Compression",
            },
            {
                "name": "cdrom-file-compression",
                "description": "PSX file formats - compression: LZSS variants (Moto Racer, Dino Crisis, Lain), LZ5, GT-ZIP, BPE, RNC, Huffman, ZIP/GZIP/ZLIB (inflate/deflate), LHA, LZMA, XZ, FLAC, ARJ, ARC, RAR, and more. Use when decompressing game data or identifying compression algorithms.",
                "start_heading": "CDROM File Compression",
                "end_heading": "CDROM Disk Images CCD/IMG/SUB (CloneCD)",
            },
            {
                "name": "cdrom-file-disc-images",
                "description": "CDROM disc image formats: CCD/IMG/SUB (CloneCD), CDI (DiscJuggler), CUE/BIN (Cdrwin), MDS/MDF (Alcohol), NRG (Nero), CDZ, ECM, PBP (Sony PSP), CHD (MAME). Use when converting, reading, or writing disc images.",
                "start_heading": "CDROM Disk Images CCD/IMG/SUB (CloneCD)",
                "end_heading": None,
            },
        ],
    },
]


def normalize_heading(text: str) -> str:
    """Strip ## prefix and surrounding whitespace from a heading line."""
    # Remove leading ##, then strip whitespace
    return re.sub(r"^#+\s*", "", text).strip()


def find_h2_line_indices(lines: list[str]) -> list[tuple[int, str]]:
    """Find all H2 heading lines. Returns list of (line_index, normalized_heading)."""
    result = []
    for i, line in enumerate(lines):
        # Match lines starting with ## followed by space(s) or just ##<space>
        # but NOT ### (H3+)
        if re.match(r"^##\s", line) and not line.startswith("###"):
            result.append((i, normalize_heading(line)))
    return result


def find_heading_line(h2_list: list[tuple[int, str]], target: str) -> int:
    """Find the line index for a heading by normalized text match."""
    for line_idx, heading_text in h2_list:
        if heading_text == target:
            return line_idx
    # Try partial match as fallback (heading starts with target)
    for line_idx, heading_text in h2_list:
        if heading_text.startswith(target):
            return line_idx
    raise ValueError(f"Heading not found: {target!r}")


def make_frontmatter(name: str, description: str) -> str:
    """Generate YAML frontmatter for a skill."""
    # Escape quotes in description for YAML
    escaped = description.replace('"', '\\"')
    return f'---\nname: {name}\ndescription: "{escaped}"\n---\n\n'


# ---------------------------------------------------------------------------
# Headings and anchors
# ---------------------------------------------------------------------------
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
ATX_RE = re.compile(r"^\s{0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
TAG_RE = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>")
ENTITY_RE = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")
ASCII_PUNCT = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


def iter_outside_fences(lines: list[str]):
    """Yield (index, line, in_fence) for each line, tracking ``` / ~~~ fences."""
    fence = None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                yield i, line, True
                continue
            yield i, line, False
        else:
            yield i, line, True
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and line.strip() == m.group(1):
                fence = None


def parse_headings(lines: list[str]) -> list[tuple[int, str]]:
    """Return (line_index, raw heading text) for every ATX heading outside fences."""
    result = []
    for i, line, in_fence in iter_outside_fences(lines):
        if in_fence:
            continue
        m = ATX_RE.match(line.rstrip("\n"))
        if not m:
            continue
        text = m.group(2) or ""
        # Optional closing sequence of #'s (must be preceded by a space)
        text = re.sub(r"(?:^|[ \t]+)#+[ \t]*$", "", text)
        result.append((i, text.strip()))
    return result


def render_heading_text(raw: str) -> str:
    """Approximate the plain text GitHub renders for a heading's inline markdown."""
    out = []
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i]
        if c == "\\" and i + 1 < n and raw[i + 1] in ASCII_PUNCT:
            out.append(raw[i + 1])
            i += 2
        elif c == "`":
            j = i
            while j < n and raw[j] == "`":
                j += 1
            ticks = raw[i:j]
            end = raw.find(ticks, j)
            if end == -1:
                out.append(ticks)
                i = j
            else:
                out.append(raw[j:end])
                i = end + len(ticks)
        elif c == "<" and TAG_RE.match(raw, i):
            i = TAG_RE.match(raw, i).end()
        elif c == "&" and ENTITY_RE.match(raw, i):
            ent = ENTITY_RE.match(raw, i).group(0)
            out.append(html.unescape(ent))
            i += len(ent)
        elif c == "*":
            i += 1  # emphasis markers (punctuation: dropped by slugs anyway)
        else:
            out.append(c)
            i += 1
    return "".join(out).strip()


def gfm_slug(text: str) -> str:
    """GitHub-flavoured markdown anchor (github-slugger) for rendered heading text."""
    text = text.lower()
    # Keep letters, marks, numbers, connector punctuation (_), spaces and '-'
    kept = []
    for ch in text:
        cat = unicodedata.category(ch)
        if ch in (" ", "-") or cat[0] in ("L", "M", "N") or cat == "Pc":
            kept.append(ch)
    return "".join(kept).replace(" ", "-")


def mkdocs_slug(text: str) -> str:
    """Python-Markdown toc default slugify (used by the original mkdocs site)."""
    value = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def loose_key(anchor: str) -> str:
    return re.sub(r"[^a-z0-9]", "", anchor.lower())


def dedup_slugs(slugs: list[str], sep: str) -> list[str]:
    """Make slugs unique the way GitHub (sep='-') / Python-Markdown (sep='_') do."""
    seen = set()
    result = []
    for slug in slugs:
        candidate = slug
        k = 0
        while candidate in seen:
            k += 1
            candidate = f"{slug}{sep}{k}"
        seen.add(candidate)
        result.append(candidate)
    return result


def gfm_anchors(lines: list[str]) -> dict[int, str]:
    """Map heading line index -> GitHub anchor, for a whole markdown document."""
    heads = parse_headings(lines)
    slugs = dedup_slugs([gfm_slug(render_heading_text(t)) for _, t in heads], "-")
    return {idx: slug for (idx, _), slug in zip(heads, slugs)}


# ---------------------------------------------------------------------------
# Planning: which lines of which source file go into which skill
# ---------------------------------------------------------------------------
def plan_chunks() -> tuple[list[dict], dict[str, list[str]]]:
    """Return (chunks, source_lines). Each chunk: name, description, source, start, end."""
    chunks = []
    sources = {}
    for skill in SKILLS:
        source_path = os.path.join(SOURCE_DIR, skill["source"])
        if not os.path.exists(source_path):
            print(f"  ERROR: source not found: {source_path}")
            sys.exit(1)
        with open(source_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        sources[skill["source"]] = lines

        if "splits" not in skill:
            chunks.append({"name": skill["name"], "description": skill["description"],
                           "source": skill["source"], "start": 0, "end": len(lines)})
            continue

        h2_list = find_h2_line_indices(lines)
        for split in skill["splits"]:
            start = 0 if split["start_heading"] is None else \
                find_heading_line(h2_list, split["start_heading"])
            end = len(lines) if split["end_heading"] is None else \
                find_heading_line(h2_list, split["end_heading"])
            chunks.append({"name": split["name"], "description": split["description"],
                           "source": skill["source"], "start": start, "end": end})
    return chunks, sources


# ---------------------------------------------------------------------------
# Link rewriting
# ---------------------------------------------------------------------------
LINK_RE = re.compile(r"(!?)\[((?:[^\[\]\n]|\[[^\[\]\n]*\])*)\]\(([^()\s]*)\)")


class LinkResolver:
    def __init__(self, chunks: list[dict], sources: dict[str, list[str]]):
        self.chunks = chunks
        self.by_source = {}
        for ch in chunks:
            self.by_source.setdefault(ch["source"], []).append(ch)
        # Anchor lookup tables per source file: anchor -> heading line index
        self.lookup = {}
        for src, lines in sources.items():
            heads = parse_headings(lines)
            texts = [render_heading_text(t) for _, t in heads]
            idxs = [i for i, _ in heads]
            mk = dedup_slugs([mkdocs_slug(t) for t in texts], "_")
            gf = dedup_slugs([gfm_slug(t) for t in texts], "-")
            loose = {}
            for i, s in zip(idxs, gf):
                loose.setdefault(loose_key(s), i)
            self.lookup[src] = (dict(zip(mk, idxs)), dict(zip(gf, idxs)), loose)
        # GitHub anchors of each generated skill: line index (in source) -> anchor
        for ch in chunks:
            body = sources[ch["source"]][ch["start"]:ch["end"]]
            ch["anchors"] = {ch["start"] + k: v for k, v in gfm_anchors(body).items()}
        self.rewritten = 0
        self.unresolved = []  # (skill, link text, original target)
        self.assets = []      # (skill, asset filename)

    def chunk_at(self, src: str, line: int) -> dict:
        for ch in self.by_source[src]:
            if ch["start"] <= line < ch["end"]:
                return ch
        raise KeyError((src, line))

    def find_heading(self, src: str, frag: str):
        mk, gf, loose = self.lookup[src]
        for table, key in ((mk, frag), (gf, frag.lower()), (loose, loose_key(frag))):
            if key in table:
                return table[key]
        return None

    def resolve(self, cur: dict, target: str):
        """Return new href, or None if the target is not part of the plugin."""
        path, _, frag = target.partition("#")
        path = urllib.parse.unquote(path)
        frag = urllib.parse.unquote(frag)
        src = path or cur["source"]
        if src not in self.by_source:
            return None
        if frag:
            line = self.find_heading(src, frag)
            if line is None:
                return None
            ch = self.chunk_at(src, line)
            anchor = "#" + ch["anchors"][line]
        else:
            ch = self.chunk_at(src, 0)
            anchor = ""
        if ch is cur:
            return anchor or "SKILL.md"
        return f"../{ch['name']}/SKILL.md{anchor}"

    def rewrite(self, cur: dict, text: str) -> str:
        def repl(m):
            bang, label, target = m.groups()
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("//"):
                return m.group(0)  # external (http, https, mailto, ...)
            path = target.partition("#")[0]
            if path and not path.endswith(".md"):
                # Non-markdown asset (e.g. an image): ship it next to the skill
                if os.path.exists(os.path.join(SOURCE_DIR, path)):
                    self.assets.append((cur["name"], path))
                    return m.group(0)
                self.unresolved.append((cur["name"], label, target))
                return label
            new = self.resolve(cur, target)
            if new is None:
                self.unresolved.append((cur["name"], label, target))
                return label
            self.rewritten += 1
            return f"{bang}[{label}]({new})"

        out = []
        lines = text.splitlines(keepends=True)
        for _, line, in_fence in iter_outside_fences(lines):
            out.append(line if in_fence else LINK_RE.sub(repl, line))
        return "".join(out)


def main():
    # Clear and recreate output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    print(f"Source: {SOURCE_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    chunks, sources = plan_chunks()
    resolver = LinkResolver(chunks, sources)

    for ch in chunks:
        body = "".join(sources[ch["source"]][ch["start"]:ch["end"]])
        body = resolver.rewrite(ch, body)
        out_dir = os.path.join(OUTPUT_DIR, ch["name"])
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(make_frontmatter(ch["name"], ch["description"]))
            f.write(body)
        print(f"  {ch['name']}: {ch['source']} lines {ch['start'] + 1}-{ch['end']} "
              f"({len(body)} bytes)")

    for name, asset in resolver.assets:
        shutil.copy2(os.path.join(SOURCE_DIR, asset), os.path.join(OUTPUT_DIR, name, asset))

    print()
    print(f"Done: {len(chunks)} skills")
    print(f"Links rewritten: {resolver.rewritten}, assets copied: {len(resolver.assets)}, "
          f"unresolved (turned into plain text): {len(resolver.unresolved)}")
    for name, label, target in resolver.unresolved:
        print(f"  UNRESOLVED [{name}] {label!r} -> {target}")


if __name__ == "__main__":
    main()
