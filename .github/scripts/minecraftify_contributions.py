from __future__ import annotations

import math
import re
import sys
from pathlib import Path

PIXEL_COLORS = ("#22D3EE", "#34D399", "#FACC15", "#A78BFA", "#F97316", "#84CC16")


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def pct(value: float) -> float:
    return max(0.0, min(99.0, value))


def pop_keyframes(name: str, start: float, direction: str = "y") -> str:
    start = pct(start)
    on = pct(start + 0.8)
    if direction == "roof":
        hidden = "opacity:0;transform:translateY(-10px) scale(.7)"
        shown = "opacity:1;transform:translateY(0) scale(1)"
    elif direction == "x":
        hidden = "opacity:0;transform:scaleX(0)"
        shown = "opacity:1;transform:scaleX(1)"
    else:
        hidden = "opacity:0;transform:scaleY(0)"
        shown = "opacity:1;transform:scaleY(1)"
    return (
        f"@keyframes {name}{{"
        f"0%,{fmt(start)}%{{{hidden}}}"
        f"{fmt(on)}%,99%{{{shown}}}"
        f"100%{{opacity:0}}"
        f"}}"
    )


def visibility_keyframes(name: str, show: float, hide: float) -> str:
    show = pct(show)
    hide = pct(hide)
    a = max(0.0, show - 0.15)
    b = min(99.0, show + 0.15)
    c = max(b, hide - 0.15)
    d = min(99.4, hide + 0.15)
    return (
        f"@keyframes {name}{{"
        f"0%,{fmt(a)}%{{opacity:0}}"
        f"{fmt(b)}%,{fmt(c)}%{{opacity:1}}"
        f"{fmt(d)}%,100%{{opacity:0}}"
        f"}}"
    )


def loot_keyframes(name: str, start: float, end: float, dx: float, dy: float) -> str:
    start = pct(start)
    end = pct(end)
    mid = (start + end) / 2
    return (
        f"@keyframes {name}{{"
        f"0%,{fmt(start)}%{{opacity:0;transform:translate(0,0) rotate(0deg) scale(.5)}}"
        f"{fmt(start + .25)}%{{opacity:1}}"
        f"{fmt(mid)}%{{opacity:1;transform:translate({fmt(dx*.55)}px,{fmt(dy*.25 - 16)}px) rotate(90deg) scale(1)}}"
        f"{fmt(end)}%{{opacity:1;transform:translate({fmt(dx)}px,{fmt(dy)}px) rotate(180deg) scale(.7)}}"
        f"{fmt(end + .35)}%,100%{{opacity:0;transform:translate({fmt(dx)}px,{fmt(dy)}px) rotate(180deg) scale(.3)}}"
        f"}}"
    )


def particle_keyframes(start: float) -> str:
    a = pct(start)
    b = pct(start + 0.5)
    c = pct(start + 3.5)
    d = pct(start + 6.0)
    return (
        "@keyframes voxelBurst{"
        f"0%,{fmt(a)}%{{opacity:0;transform:translate(0,0) scale(.3)}}"
        f"{fmt(b)}%{{opacity:1;transform:translate(0,0) scale(.8)}}"
        f"{fmt(c)}%{{opacity:1;transform:translate(var(--dx),var(--dy)) scale(1)}}"
        f"{fmt(d)}%,100%{{opacity:0;transform:translate(calc(var(--dx)*1.2),calc(var(--dy)*1.2)) scale(.4)}}"
        "}"
    )


def completion_keyframes(start: float) -> str:
    a = pct(start)
    b = pct(start + 0.5)
    c = pct(start + 4.5)
    d = 99.2
    return (
        "@keyframes completeText{"
        f"0%,{fmt(a)}%{{opacity:0;transform:translateY(4px)}}"
        f"{fmt(b)}%,{fmt(c)}%{{opacity:1;transform:translateY(0)}}"
        f"{fmt(d)}%,100%{{opacity:0;transform:translateY(-2px)}}"
        "}"
    )


def trophy_keyframes(start: float) -> str:
    a = pct(start)
    b = pct(start + 1.0)
    c = pct(start + 3.8)
    return (
        "@keyframes trophyRaise{"
        f"0%,{fmt(a)}%{{opacity:0;transform:translate(0,8px) rotate(-8deg)}}"
        f"{fmt(b)}%,{fmt(c)}%{{opacity:1;transform:translate(0,-8px) rotate(0deg)}}"
        "99%{opacity:1;transform:translate(0,-8px)}"
        "100%{opacity:0}"
        "}"
    )


def particles_markup(cx: float, cy: float) -> str:
    parts = ['<g id="build-particles" aria-hidden="true">']
    for i in range(22):
        angle = math.radians(i * (360 / 22))
        distance = 24 + (i % 5) * 9
        dx = math.cos(angle) * distance
        dy = math.sin(angle) * distance
        size = 3 + (i % 3) * 2
        color = PIXEL_COLORS[i % len(PIXEL_COLORS)]
        parts.append(
            f'<rect class="voxel-particle" x="{fmt(cx-size/2)}" y="{fmt(cy-size/2)}" '
            f'width="{size}" height="{size}" fill="{color}" '
            f'style="--dx:{fmt(dx)}px;--dy:{fmt(dy)}px"/>'
        )
    parts.append("</g>")
    return "".join(parts)


def miner_markup() -> str:
    return (
        '<g class="miner-path" aria-hidden="true">'
        '<g transform="translate(-9,-25)">'
        '<g class="miner-bob">'
        # trophy/backpack
        '<rect x="-5" y="10" width="6" height="12" fill="#8B5A2B"/>'
        '<rect x="-4" y="11" width="4" height="4" fill="#FACC15"/>'
        # legs
        '<rect x="5" y="25" width="6" height="10" fill="#1D4ED8"/>'
        '<rect x="12" y="25" width="6" height="10" fill="#1E40AF"/>'
        '<rect x="4" y="34" width="7" height="3" fill="#111827"/>'
        '<rect x="12" y="34" width="7" height="3" fill="#111827"/>'
        # torso
        '<rect x="4" y="13" width="15" height="13" fill="#22D3EE"/>'
        '<rect x="5" y="14" width="13" height="3" fill="#67E8F9"/>'
        # head
        '<rect x="5" y="1" width="14" height="13" fill="#C98D62"/>'
        '<rect x="5" y="1" width="14" height="4" fill="#3F2A1D"/>'
        '<rect x="7" y="6" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="14" y="6" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="8" y="6" width="1" height="2" fill="#2563EB"/>'
        '<rect x="15" y="6" width="1" height="2" fill="#2563EB"/>'
        # mining arm + pickaxe
        '<g class="pick-swing">'
        '<rect x="18" y="14" width="4" height="11" fill="#C98D62"/>'
        '<rect x="21" y="7" width="3" height="21" fill="#8B5A2B"/>'
        '<rect x="17" y="5" width="14" height="4" fill="#A3A3A3"/>'
        '<rect x="15" y="6" width="5" height="3" fill="#D4D4D4"/>'
        '</g>'
        '</g>'
        '</g>'
        '</g>'
    )


def builder_markup() -> str:
    return (
        '<g class="builder" transform="translate(625,115)" aria-hidden="true">'
        '<g class="builder-bob">'
        '<rect x="5" y="25" width="6" height="10" fill="#1D4ED8"/>'
        '<rect x="12" y="25" width="6" height="10" fill="#1E40AF"/>'
        '<rect x="4" y="34" width="7" height="3" fill="#111827"/>'
        '<rect x="12" y="34" width="7" height="3" fill="#111827"/>'
        '<rect x="4" y="13" width="15" height="13" fill="#22D3EE"/>'
        '<rect x="5" y="1" width="14" height="13" fill="#C98D62"/>'
        '<rect x="5" y="1" width="14" height="4" fill="#3F2A1D"/>'
        '<rect x="7" y="6" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="14" y="6" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="8" y="6" width="1" height="2" fill="#2563EB"/>'
        '<rect x="15" y="6" width="1" height="2" fill="#2563EB"/>'
        # carried block
        '<rect class="carried-block" x="20" y="16" width="9" height="9" fill="#8B5A2B"/>'
        '<rect class="carried-block" x="21" y="17" width="3" height="3" fill="#A16207"/>'
        # trophy
        '<g class="trophy">'
        '<rect x="-1" y="7" width="3" height="12" fill="#FACC15"/>'
        '<rect x="-5" y="4" width="11" height="7" fill="#FDE047"/>'
        '<rect x="-8" y="5" width="4" height="5" fill="none" stroke="#FACC15" stroke-width="2"/>'
        '<rect x="6" y="5" width="4" height="5" fill="none" stroke="#FACC15" stroke-width="2"/>'
        '<rect x="0" y="18" width="5" height="3" fill="#CA8A04"/>'
        '<rect x="-2" y="21" width="9" height="3" fill="#A16207"/>'
        '</g>'
        '</g>'
        '</g>'
    )


def house_markup() -> str:
    return (
        '<g id="voxel-house" aria-hidden="true">'
        # grass/foundation
        '<g class="house-base">'
        '<rect x="682" y="161" width="126" height="9" fill="#65A30D"/>'
        '<rect x="682" y="169" width="126" height="7" fill="#795548"/>'
        '<rect x="688" y="162" width="18" height="2" fill="#A3E635"/>'
        '<rect x="748" y="162" width="22" height="2" fill="#A3E635"/>'
        '</g>'
        # wall lower
        '<g class="house-wall-a">'
        '<rect x="696" y="136" width="98" height="26" fill="#A16207"/>'
        '<rect x="699" y="139" width="92" height="20" fill="#B7791F"/>'
        '<path d="M699 146h92M699 153h92" stroke="#7C4A17" stroke-width="2"/>'
        '</g>'
        # wall upper
        '<g class="house-wall-b">'
        '<rect x="705" y="121" width="80" height="17" fill="#92400E"/>'
        '<rect x="708" y="124" width="74" height="11" fill="#B45309"/>'
        '</g>'
        # roof
        '<g class="house-roof">'
        '<path d="M690 124 L744 99 L801 124 Z" fill="#7F1D1D"/>'
        '<path d="M697 123 L744 104 L793 123 Z" fill="#B91C1C"/>'
        '<rect x="739" y="101" width="10" height="4" fill="#EF4444"/>'
        '</g>'
        # door
        '<g class="house-door">'
        '<rect x="735" y="141" width="18" height="21" fill="#5B3A29"/>'
        '<rect x="738" y="144" width="12" height="18" fill="#6B4423"/>'
        '<rect x="748" y="153" width="2" height="2" fill="#FACC15"/>'
        '</g>'
        # window + torch
        '<g class="house-window">'
        '<rect x="766" y="142" width="15" height="13" fill="#422006"/>'
        '<rect x="769" y="144" width="9" height="8" fill="#67E8F9"/>'
        '<path d="M773.5 144v8M769 148h9" stroke="#E0F2FE" stroke-width="1"/>'
        '<rect x="711" y="143" width="3" height="10" fill="#8B5A2B"/>'
        '<rect x="710" y="139" width="5" height="6" fill="#F59E0B"/>'
        '<rect x="711" y="138" width="3" height="3" fill="#FDE047"/>'
        '</g>'
        '</g>'
    )


def inventory_markup() -> str:
    return (
        '<g id="inventory" aria-hidden="true">'
        '<rect x="18" y="166" width="176" height="17" rx="2" fill="#111827" stroke="#57534E" stroke-width="2"/>'
        '<rect class="xp-fill" x="23" y="171" width="128" height="7" fill="#84CC16"/>'
        '<text x="158" y="178" font-family="monospace" font-size="10" font-weight="700" fill="#A3E635">XP</text>'
        '<rect x="205" y="164" width="22" height="22" fill="#292524" stroke="#78716C" stroke-width="2"/>'
        '<rect class="inv-block" x="211" y="170" width="10" height="10" fill="#A16207"/>'
        '<text class="inv-count" x="232" y="179" font-family="monospace" font-size="10" font-weight="700" fill="#E7E5E4">BLOCKS</text>'
        '</g>'
    )


def minecraftify(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")

    if 'id="steven-builder-scene"' in svg:
        return

    duration_match = re.search(r"animation:none\s+(\d+)ms\s+linear\s+infinite", svg)
    if not duration_match:
        raise RuntimeError(f"Could not determine animation duration in {path}")
    duration = duration_match.group(1)

    eaten = [
        float(value)
        for value in re.findall(
            r"@keyframes\s+c[0-9a-z]+\{([0-9]+(?:\.[0-9]+)?)%\{fill:",
            svg,
        )
    ]
    if not eaten:
        raise RuntimeError(f"Could not determine contribution timing in {path}")

    last_eaten = max(eaten)
    room = max(14.0, 98.0 - last_eaten)

    loot_start = last_eaten + room * 0.04
    builder_show = last_eaten + room * 0.14
    phase_base = last_eaten + room * 0.22
    phase_wall_a = last_eaten + room * 0.34
    phase_wall_b = last_eaten + room * 0.46
    phase_roof = last_eaten + room * 0.58
    phase_door = last_eaten + room * 0.68
    phase_window = last_eaten + room * 0.76
    trophy_start = last_eaten + room * 0.84
    complete_start = last_eaten + room * 0.88
    burst_start = last_eaten + room * 0.90

    css = (
        ".s{display:none!important}"
        ".u{display:none!important}"
        ".c{shape-rendering:crispEdges;rx:0;ry:0;stroke:#111827;stroke-width:1.15px}"
        f".miner-path{{animation:s0 {duration}ms linear infinite,minerVis {duration}ms steps(1,end) infinite}}"
        f"@keyframes minerVis{{0%,{fmt(pct(last_eaten + .15))}%{{opacity:1}}"
        f"{fmt(pct(last_eaten + .7))}%,100%{{opacity:0}}}}"
        ".miner-bob{animation:minerBob 460ms steps(2,end) infinite}"
        "@keyframes minerBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}"
        ".pick-swing{animation:pickSwing 330ms steps(2,end) infinite;transform-origin:21px 18px}"
        "@keyframes pickSwing{0%,100%{transform:rotate(-28deg)}50%{transform:rotate(32deg)}}"
        f".builder{{animation:builderVis {duration}ms steps(1,end) infinite}}"
        + visibility_keyframes("builderVis", builder_show, 99.1)
        + ".builder-bob{animation:builderBob 520ms steps(2,end) infinite}"
        "@keyframes builderBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-1px)}}"
        f".carried-block{{animation:carryBlock {duration}ms steps(2,end) infinite}}"
        f"@keyframes carryBlock{{0%,{fmt(pct(phase_wall_b))}%{{opacity:1}}"
        f"{fmt(pct(phase_roof))}%,100%{{opacity:0}}}}"
        f".trophy{{opacity:0;animation:trophyRaise {duration}ms steps(4,end) infinite}}"
        + trophy_keyframes(trophy_start)
        + f".house-base{{transform-box:fill-box;transform-origin:center bottom;animation:houseBase {duration}ms steps(5,end) infinite}}"
        + pop_keyframes("houseBase", phase_base)
        + f".house-wall-a{{transform-box:fill-box;transform-origin:center bottom;animation:houseWallA {duration}ms steps(5,end) infinite}}"
        + pop_keyframes("houseWallA", phase_wall_a)
        + f".house-wall-b{{transform-box:fill-box;transform-origin:center bottom;animation:houseWallB {duration}ms steps(5,end) infinite}}"
        + pop_keyframes("houseWallB", phase_wall_b)
        + f".house-roof{{transform-box:fill-box;transform-origin:center center;animation:houseRoof {duration}ms steps(5,end) infinite}}"
        + pop_keyframes("houseRoof", phase_roof, "roof")
        + f".house-door{{transform-box:fill-box;transform-origin:center bottom;animation:houseDoor {duration}ms steps(4,end) infinite}}"
        + pop_keyframes("houseDoor", phase_door)
        + f".house-window{{transform-box:fill-box;transform-origin:center center;animation:houseWindow {duration}ms steps(4,end) infinite}}"
        + pop_keyframes("houseWindow", phase_window, "x")
        + f".voxel-particle{{opacity:0;shape-rendering:crispEdges;animation:voxelBurst {duration}ms steps(8,end) infinite}}"
        + particle_keyframes(burst_start)
        + f".build-complete{{opacity:0;font-family:monospace;font-weight:900;letter-spacing:1.5px;animation:completeText {duration}ms steps(2,end) infinite}}"
        + completion_keyframes(complete_start)
        + f".xp-fill{{transform-origin:left center;animation:xpFill {duration}ms linear infinite}}"
        f"@keyframes xpFill{{0%,{fmt(pct(last_eaten))}%{{transform:scaleX(.2)}}"
        f"{fmt(pct(phase_window))}%{{transform:scaleX(.82)}}"
        f"{fmt(pct(complete_start))}%,99%{{transform:scaleX(1)}}100%{{transform:scaleX(.2)}}}}"
        + f".inv-count{{animation:invText {duration}ms steps(1,end) infinite}}"
        f"@keyframes invText{{0%,{fmt(pct(last_eaten))}%{{opacity:.45}}"
        f"{fmt(pct(loot_start))}%,99%{{opacity:1}}100%{{opacity:.45}}}}"
    )

    loot_specs = [
        (90, 28, 610, 100),
        (210, 70, 500, 58),
        (340, 42, 380, 86),
        (470, 76, 260, 56),
        (590, 30, 150, 102),
        (710, 62, 45, 68),
    ]
    loot_parts = ['<g id="collected-blocks" aria-hidden="true">']
    for i, (x, y, dx, dy) in enumerate(loot_specs):
        start = loot_start + i * 0.35
        end = builder_show + 2.8 + i * 0.2
        css += (
            f".loot-{i}{{transform-box:fill-box;animation:loot{i} {duration}ms steps(12,end) infinite}}"
            + loot_keyframes(f"loot{i}", start, end, dx, dy)
        )
        fill = ("#A16207", "#78716C", "#16A34A", "#22D3EE", "#A16207", "#84CC16")[i]
        loot_parts.append(
            f'<rect class="loot-{i}" x="{x}" y="{y}" width="9" height="9" fill="{fill}" '
            f'stroke="#111827" stroke-width="1"/>'
        )
    loot_parts.append("</g>")

    scene = (
        '<g id="steven-builder-scene">'
        + miner_markup()
        + "".join(loot_parts)
        + builder_markup()
        + house_markup()
        + inventory_markup()
        + particles_markup(744, 121)
        + '<text class="build-complete" x="744" y="91" text-anchor="middle" font-size="14" fill="#A3E635">'
          'BUILD COMPLETE +XP</text>'
        + '<text x="18" y="157" font-family="monospace" font-size="10" font-weight="800" fill="#A3E635">'
          'STEVEN // MINING → COLLECTING → BUILDING</text>'
        + '</g>'
    )

    if "</style>" not in svg or "</svg>" not in svg:
        raise RuntimeError(f"Unexpected SVG structure in {path}")

    svg = svg.replace("</style>", css + "</style>", 1)
    svg = svg.replace("</svg>", scene + "</svg>", 1)
    path.write_text(svg, encoding="utf-8")

    print(
        f"Steven builder scene added to {path}; last mined contribution "
        f"at {fmt(last_eaten)}%, build completes near {fmt(complete_start)}% "
        f"of {duration}ms cycle"
    )


def main() -> None:
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted(Path("dist").glob("*.svg"))
    if not paths:
        raise SystemExit("No SVG files supplied or found in dist/")
    for path in paths:
        minecraftify(path)


if __name__ == "__main__":
    main()
