from __future__ import annotations

import math
import re
import sys
from pathlib import Path

PIXEL_COLORS = ("#22D3EE", "#34D399", "#FACC15", "#A78BFA", "#F97316")


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def particle_markup(cx: float, cy: float) -> str:
    parts = ['<g id="voxel-particles" aria-hidden="true">']
    for i in range(18):
        angle = math.radians(i * 20)
        distance = 28 + (i % 5) * 10
        dx = math.cos(angle) * distance
        dy = math.sin(angle) * distance
        size = 4 + (i % 3) * 2
        color = PIXEL_COLORS[i % len(PIXEL_COLORS)]
        parts.append(
            f'<rect class="voxel-particle p{i}" x="{fmt(cx - size/2)}" y="{fmt(cy - size/2)}" '
            f'width="{size}" height="{size}" fill="{color}" '
            f'style="--dx:{fmt(dx)}px;--dy:{fmt(dy)}px"/>'
        )
    parts.append("</g>")
    return "".join(parts)


def completion_keyframes(start: float) -> str:
    a = min(start, 88.0)
    b = min(a + 0.8, 91.0)
    c = min(a + 5.5, 96.0)
    d = min(a + 10.0, 99.0)
    return (
        f"@keyframes voxelBurst{{"
        f"0%,{fmt(a)}%{{opacity:0;transform:translate(0,0) scale(.3)}}"
        f"{fmt(b)}%{{opacity:1;transform:translate(0,0) scale(.8)}}"
        f"{fmt(c)}%{{opacity:1;transform:translate(var(--dx),var(--dy)) scale(1)}}"
        f"{fmt(d)}%,100%{{opacity:0;transform:translate(calc(var(--dx)*1.25),calc(var(--dy)*1.25)) scale(.4)}}"
        f"}}"
        f"@keyframes completeText{{"
        f"0%,{fmt(a)}%{{opacity:0}}"
        f"{fmt(b)}%,{fmt(c)}%{{opacity:1}}"
        f"{fmt(d)}%,100%{{opacity:0}}"
        f"}}"
    )


def minecraftify(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")

    if 'id="voxel-mining"' in svg:
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
    complete_at = last_eaten + 0.9

    css = (
        ".s{display:none!important}"
        ".c{shape-rendering:crispEdges;rx:0;ry:0;stroke:#111827;stroke-width:1.15px}"
        ".u{fill:#84CC16!important;opacity:.92;shape-rendering:crispEdges}"
        ".pickaxe{animation:none linear " + duration + "ms infinite;animation-name:s0}"
        ".pick-swing{animation:pickSwing 360ms steps(2,end) infinite;transform-origin:8px 8px}"
        "@keyframes pickSwing{0%,100%{transform:rotate(-24deg)}50%{transform:rotate(24deg)}}"
        ".voxel-particle{opacity:0;shape-rendering:crispEdges;"
        "animation:voxelBurst " + duration + "ms steps(8,end) infinite}"
        ".mine-complete{opacity:0;font-family:monospace;font-weight:800;letter-spacing:2px;"
        "animation:completeText " + duration + "ms steps(2,end) infinite}"
        + completion_keyframes(complete_at)
    )

    mining = (
        '<g id="voxel-mining" aria-hidden="true">'
        '<g class="pickaxe">'
        '<g class="pick-swing">'
        '<rect x="6" y="-4" width="4" height="24" fill="#8B5A2B"/>'
        '<rect x="2" y="-6" width="16" height="4" fill="#9CA3AF"/>'
        '<rect x="0" y="-4" width="6" height="4" fill="#D1D5DB"/>'
        '<rect x="14" y="-4" width="6" height="4" fill="#6B7280"/>'
        '<rect x="7" y="17" width="3" height="5" fill="#5B3A29"/>'
        '</g>'
        '</g>'
        + particle_markup(424, 64)
        + '<text class="mine-complete" x="424" y="132" text-anchor="middle" '
          'font-size="15" fill="#84CC16">MINE COMPLETE +XP</text>'
        + '<text x="8" y="177" font-family="monospace" font-size="11" '
          'font-weight="700" fill="#84CC16">XP</text>'
        + '</g>'
    )

    if "</style>" not in svg or "</svg>" not in svg:
        raise RuntimeError(f"Unexpected SVG structure in {path}")

    svg = svg.replace("</style>", css + "</style>", 1)
    svg = svg.replace("</svg>", mining + "</svg>", 1)
    path.write_text(svg, encoding="utf-8")
    print(
        f"Minecraft-style contribution mine added to {path}; "
        f"completion begins at {fmt(complete_at)}% of {duration}ms cycle"
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
