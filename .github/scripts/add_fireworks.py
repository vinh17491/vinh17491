from __future__ import annotations

import math
import re
import sys
from pathlib import Path

COLORS = ("#67E8F9", "#A78BFA", "#F472B6", "#FDE047", "#22D3EE")


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def burst_markup(cx: float, cy: float, cls: str, phase: int) -> str:
    parts = [f'<g class="fw-burst {cls}" aria-hidden="true">']
    for index in range(12):
        angle = math.radians(index * 30 + phase)
        inner = 8 + (index % 3)
        outer = 24 + (index % 4) * 2
        x1 = cx + math.cos(angle) * inner
        y1 = cy + math.sin(angle) * inner
        x2 = cx + math.cos(angle) * outer
        y2 = cy + math.sin(angle) * outer
        color = COLORS[index % len(COLORS)]
        parts.append(
            f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
            f'stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>'
        )
        parts.append(
            f'<circle cx="{fmt(x2)}" cy="{fmt(y2)}" r="1.8" fill="{color}"/>'
        )
    parts.append(
        f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="4" fill="none" '
        f'stroke="{COLORS[phase % len(COLORS)]}" stroke-width="2"/>'
    )
    parts.append("</g>")
    return "".join(parts)


def keyframes(name: str, start: float) -> str:
    start = min(start, 89.0)
    ignite = min(start + 0.45, 92.0)
    peak = min(start + 2.8, 95.0)
    fade = min(start + 6.0, 98.0)
    return (
        f"@keyframes {name}{{"
        f"0%,{fmt(start)}%{{opacity:0;transform:scale(.12)}}"
        f"{fmt(ignite)}%{{opacity:1;transform:scale(.25)}}"
        f"{fmt(peak)}%{{opacity:1;transform:scale(1)}}"
        f"{fmt(fade)}%,100%{{opacity:0;transform:scale(1.35)}}"
        f"}}"
    )


def add_fireworks(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")

    if "fw-burst" in svg:
        return

    duration_match = re.search(r"animation:none\s+(\d+)ms\s+linear\s+infinite", svg)
    if not duration_match:
        raise RuntimeError(f"Could not determine snake animation duration in {path}")
    duration = duration_match.group(1)

    eaten = [
        float(value)
        for value in re.findall(
            r"@keyframes\s+c[0-9a-z]+\{([0-9]+(?:\.[0-9]+)?)%\{fill:",
            svg,
        )
    ]
    if not eaten:
        raise RuntimeError(f"Could not determine contribution-eating timing in {path}")

    last_eaten = max(eaten)
    starts = (last_eaten + 0.8, last_eaten + 3.2, last_eaten + 5.6, last_eaten + 8.0)

    css = (
        ".fw-burst{opacity:0;pointer-events:none;transform-box:view-box;"
        f"animation-duration:{duration}ms;animation-timing-function:ease-out;"
        "animation-iteration-count:infinite}"
        ".fw-1{transform-origin:180px 38px;animation-name:fw1}"
        ".fw-2{transform-origin:390px 78px;animation-name:fw2}"
        ".fw-3{transform-origin:610px 35px;animation-name:fw3}"
        ".fw-4{transform-origin:785px 78px;animation-name:fw4}"
        + keyframes("fw1", starts[0])
        + keyframes("fw2", starts[1])
        + keyframes("fw3", starts[2])
        + keyframes("fw4", starts[3])
    )

    fireworks = (
        '<g id="fireworks" aria-hidden="true">'
        + burst_markup(180, 38, "fw-1", 0)
        + burst_markup(390, 78, "fw-2", 9)
        + burst_markup(610, 35, "fw-3", 18)
        + burst_markup(785, 78, "fw-4", 27)
        + "</g>"
    )

    if "</style>" not in svg or "</svg>" not in svg:
        raise RuntimeError(f"Unexpected SVG structure in {path}")

    svg = svg.replace("</style>", css + "</style>", 1)
    svg = svg.replace("</svg>", fireworks + "</svg>", 1)
    path.write_text(svg, encoding="utf-8")
    print(
        f"Added synchronized fireworks to {path} "
        f"(last contribution eaten at {fmt(last_eaten)}%, duration {duration}ms)"
    )


def main() -> None:
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted(Path("dist").glob("*.svg"))
    if not paths:
        raise SystemExit("No SVG files supplied or found in dist/")
    for path in paths:
        add_fireworks(path)


if __name__ == "__main__":
    main()
