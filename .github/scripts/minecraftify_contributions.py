from __future__ import annotations

import math
import re
import sys
from pathlib import Path

LOOP_MS = 28000
TRIP_COUNT = 10
BUILD_STAND_X = 664
BUILD_STAND_Y = 116

PIXEL_COLORS = ("#22D3EE", "#34D399", "#FACC15", "#A78BFA", "#F97316", "#84CC16")


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def select_mining_blocks(svg: str, count: int) -> list[tuple[str, float, float]]:
    matches = re.findall(
        r'<rect class="c (c[0-9a-z]+)" x="([0-9.]+)" y="([0-9.]+)"',
        svg,
    )
    unique: list[tuple[str, float, float]] = []
    seen: set[str] = set()

    for cls, x, y in matches:
        if cls in seen:
            continue
        seen.add(cls)
        unique.append((cls, float(x), float(y)))

    unique.sort(key=lambda item: (item[1], item[2]))

    if not unique:
        raise RuntimeError("No contribution blocks were found in the generated SVG")

    if len(unique) <= count:
        return unique

    # Spread the trips across the contribution history instead of mining
    # several neighbouring blocks in a row.
    selected: list[tuple[str, float, float]] = []
    for i in range(count):
        index = round(i * (len(unique) - 1) / (count - 1))
        selected.append(unique[index])
    return selected


def steven_markup() -> str:
    return (
        '<g id="steven" aria-hidden="true">'
        '<g class="steven-body">'
        # legs
        '<rect x="5" y="26" width="6" height="10" fill="#1D4ED8"/>'
        '<rect x="12" y="26" width="6" height="10" fill="#1E40AF"/>'
        '<rect x="4" y="35" width="7" height="3" fill="#111827"/>'
        '<rect x="12" y="35" width="7" height="3" fill="#111827"/>'
        # torso
        '<rect x="4" y="14" width="15" height="13" fill="#22D3EE"/>'
        '<rect x="5" y="15" width="13" height="3" fill="#67E8F9"/>'
        # head
        '<rect x="5" y="2" width="14" height="13" fill="#C98D62"/>'
        '<rect x="5" y="2" width="14" height="4" fill="#3F2A1D"/>'
        '<rect x="7" y="7" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="14" y="7" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="8" y="7" width="1" height="2" fill="#2563EB"/>'
        '<rect x="15" y="7" width="1" height="2" fill="#2563EB"/>'
        # left arm
        '<rect x="1" y="15" width="4" height="11" fill="#C98D62"/>'
        # mining arm + pickaxe
        '<g class="pickaxe-arm">'
        '<rect x="18" y="15" width="4" height="11" fill="#C98D62"/>'
        '<rect x="22" y="7" width="3" height="22" fill="#8B5A2B"/>'
        '<rect x="17" y="5" width="15" height="4" fill="#A3A3A3"/>'
        '<rect x="15" y="6" width="5" height="3" fill="#D4D4D4"/>'
        '</g>'
        # exactly one carried block appears only on the return trip
        '<g class="carried-block">'
        '<rect x="-8" y="17" width="10" height="10" fill="#A16207" stroke="#111827" stroke-width="1"/>'
        '<rect x="-6" y="19" width="3" height="3" fill="#D97706"/>'
        '</g>'
        # reward trophy only after the house is complete
        '<g class="reward-trophy">'
        '<rect x="-2" y="4" width="11" height="7" fill="#FDE047"/>'
        '<rect x="-5" y="5" width="4" height="5" fill="none" stroke="#FACC15" stroke-width="2"/>'
        '<rect x="9" y="5" width="4" height="5" fill="none" stroke="#FACC15" stroke-width="2"/>'
        '<rect x="2" y="11" width="3" height="8" fill="#FACC15"/>'
        '<rect x="-1" y="19" width="9" height="3" fill="#A16207"/>'
        '</g>'
        '</g>'
        '</g>'
    )


def house_pieces_markup() -> str:
    pieces = [
        # foundation: 3 blocks
        ('<rect x="700" y="160" width="18" height="16" fill="#65A30D"/>'
         '<rect x="700" y="168" width="18" height="8" fill="#795548"/>'),
        ('<rect x="718" y="160" width="18" height="16" fill="#65A30D"/>'
         '<rect x="718" y="168" width="18" height="8" fill="#795548"/>'),
        ('<rect x="736" y="160" width="18" height="16" fill="#65A30D"/>'
         '<rect x="736" y="168" width="18" height="8" fill="#795548"/>'),
        # walls: 3 blocks
        ('<rect x="700" y="142" width="18" height="18" fill="#A16207"/>'
         '<path d="M702 148h14M702 154h14" stroke="#7C4A17" stroke-width="2"/>'),
        ('<rect x="718" y="142" width="18" height="18" fill="#B45309"/>'
         '<rect x="723" y="146" width="8" height="14" fill="#5B3A29"/>'
         '<rect x="729" y="153" width="2" height="2" fill="#FACC15"/>'),
        ('<rect x="736" y="142" width="18" height="18" fill="#A16207"/>'
         '<rect x="740" y="146" width="10" height="8" fill="#67E8F9"/>'
         '<path d="M745 146v8M740 150h10" stroke="#E0F2FE" stroke-width="1"/>'),
        # upper wall / trim
        ('<rect x="709" y="126" width="36" height="16" fill="#92400E"/>'
         '<rect x="713" y="130" width="28" height="8" fill="#B45309"/>'),
        # roof: 3 blocks/pieces
        ('<path d="M697 128 L715 116 L724 128 Z" fill="#991B1B"/>'
         '<path d="M700 126 L715 119 L721 126 Z" fill="#DC2626"/>'),
        ('<path d="M714 128 L727 108 L741 128 Z" fill="#7F1D1D"/>'
         '<path d="M718 126 L727 112 L737 126 Z" fill="#EF4444"/>'),
        ('<path d="M738 128 L747 116 L758 128 Z" fill="#991B1B"/>'
         '<path d="M741 126 L747 119 L755 126 Z" fill="#DC2626"/>'),
    ]

    out = ['<g id="voxel-house" aria-hidden="true">']
    # subtle build pad is visible from the start so the destination is clear
    out.append('<rect x="694" y="176" width="66" height="3" fill="#3F6212" opacity=".45"/>')
    for i, markup in enumerate(pieces):
        out.append(f'<g class="house-piece piece-{i}">{markup}</g>')
    # torch appears with the last roof piece
    out.append(
        '<g class="house-piece piece-9">'
        '<rect x="704" y="143" width="3" height="10" fill="#8B5A2B"/>'
        '<rect x="703" y="139" width="5" height="6" fill="#F59E0B"/>'
        '<rect x="704" y="138" width="3" height="3" fill="#FDE047"/>'
        '</g>'
    )
    out.append('</g>')
    return "".join(out)


def particles_markup(cx: float, cy: float) -> str:
    parts = ['<g id="build-particles" aria-hidden="true">']
    for i in range(20):
        angle = math.radians(i * 18)
        distance = 22 + (i % 5) * 8
        dx = math.cos(angle) * distance
        dy = math.sin(angle) * distance
        size = 3 + (i % 3)
        color = PIXEL_COLORS[i % len(PIXEL_COLORS)]
        parts.append(
            f'<rect class="voxel-particle" x="{fmt(cx-size/2)}" y="{fmt(cy-size/2)}" '
            f'width="{size}" height="{size}" fill="{color}" '
            f'style="--dx:{fmt(dx)}px;--dy:{fmt(dy)}px"/>'
        )
    parts.append('</g>')
    return "".join(parts)


def build_motion_keyframes(
    mining_blocks: list[tuple[str, float, float]],
) -> tuple[str, list[float], list[float]]:
    start_pct = 2.0
    end_pct = 86.0
    span = (end_pct - start_pct) / len(mining_blocks)

    motion_points: list[tuple[float, float, float]] = []
    mine_times: list[float] = []
    place_times: list[float] = []

    # Start at the build site, then repeatedly go get one block and return it.
    motion_points.append((0.0, BUILD_STAND_X, BUILD_STAND_Y))
    motion_points.append((start_pct, BUILD_STAND_X, BUILD_STAND_Y))

    for i, (_, bx, by) in enumerate(mining_blocks):
        trip = start_pct + i * span
        mine_x = bx - 8
        mine_y = by - 35

        arrive_mine = trip + span * 0.30
        finish_mine = trip + span * 0.40
        arrive_build = trip + span * 0.78
        finish_place = trip + span * 0.90

        motion_points.extend(
            [
                (arrive_mine, mine_x, mine_y),
                (finish_mine, mine_x, mine_y),
                (arrive_build, BUILD_STAND_X, BUILD_STAND_Y),
                (finish_place, BUILD_STAND_X, BUILD_STAND_Y),
            ]
        )

        mine_times.append(finish_mine)
        place_times.append(finish_place)

    motion_points.append((92.0, BUILD_STAND_X, BUILD_STAND_Y))
    motion_points.append((99.5, BUILD_STAND_X, BUILD_STAND_Y))
    motion_points.append((100.0, BUILD_STAND_X, BUILD_STAND_Y))

    # Remove duplicate percentages and keep the latest coordinate.
    compact: dict[float, tuple[float, float]] = {}
    for p, x, y in motion_points:
        compact[round(clamp(p), 2)] = (x, y)

    frames = []
    for p in sorted(compact):
        x, y = compact[p]
        frames.append(f"{fmt(p)}%{{transform:translate({fmt(x)}px,{fmt(y)}px)}}")

    return "@keyframes stevenRoute{" + "".join(frames) + "}", mine_times, place_times


def carried_block_keyframes(
    mining_blocks: list[tuple[str, float, float]],
) -> str:
    start_pct = 2.0
    end_pct = 86.0
    span = (end_pct - start_pct) / len(mining_blocks)
    frames = ["0%{opacity:0}"]

    for i in range(len(mining_blocks)):
        trip = start_pct + i * span
        pickup = trip + span * 0.42
        carry_end = trip + span * 0.78
        drop = trip + span * 0.90

        frames.extend(
            [
                f"{fmt(pickup - .08)}%{{opacity:0}}",
                f"{fmt(pickup)}%{{opacity:1}}",
                f"{fmt(carry_end)}%{{opacity:1}}",
                f"{fmt(drop)}%{{opacity:0}}",
            ]
        )

    frames.append("100%{opacity:0}")
    return "@keyframes carryOneBlock{" + "".join(frames) + "}"


def status_keyframes(
    mining_blocks: list[tuple[str, float, float]],
) -> str:
    start_pct = 2.0
    end_pct = 86.0
    span = (end_pct - start_pct) / len(mining_blocks)
    frames = ["0%{opacity:.55}"]

    for i in range(len(mining_blocks)):
        trip = start_pct + i * span
        mine = trip + span * 0.30
        return_trip = trip + span * 0.42
        place = trip + span * 0.78

        frames.extend(
            [
                f"{fmt(mine)}%{{opacity:1}}",
                f"{fmt(return_trip)}%{{opacity:.75}}",
                f"{fmt(place)}%{{opacity:1}}",
            ]
        )

    frames.extend(["90%{opacity:1}", "100%{opacity:.55}"])
    return "@keyframes statusPulse{" + "".join(frames) + "}"


def minecraftify(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")

    if 'id="one-block-build-loop"' in svg:
        return

    mining_blocks = select_mining_blocks(svg, TRIP_COUNT)
    route_css, mine_times, place_times = build_motion_keyframes(mining_blocks)

    css_parts = [
        ".s{display:none!important}",
        ".u{display:none!important}",
        ".c{animation:none!important;shape-rendering:crispEdges;rx:0;ry:0;stroke:#111827;stroke-width:1.1px}",
        f".steven-route{{animation:stevenRoute {LOOP_MS}ms linear infinite}}",
        ".steven-body{animation:stevenBob 420ms steps(2,end) infinite}",
        "@keyframes stevenBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}",
        ".pickaxe-arm{animation:pickSwing 320ms steps(2,end) infinite;transform-origin:20px 18px}",
        "@keyframes pickSwing{0%,100%{transform:rotate(-28deg)}50%{transform:rotate(34deg)}}",
        f".carried-block{{opacity:0;animation:carryOneBlock {LOOP_MS}ms steps(1,end) infinite}}",
        f".scene-status{{animation:statusPulse {LOOP_MS}ms steps(1,end) infinite}}",
        route_css,
        carried_block_keyframes(mining_blocks),
        status_keyframes(mining_blocks),
    ]

    # Each selected contribution block disappears only when Steven mines it.
    # Each house piece appears only after he returns and places that one block.
    for i, ((cls, _, _), mine_time, place_time) in enumerate(
        zip(mining_blocks, mine_times, place_times)
    ):
        reset = 99.65
        css_parts.append(
            f".c.{cls}{{animation:mineBlock{i} {LOOP_MS}ms steps(1,end) infinite!important}}"
            f"@keyframes mineBlock{i}{{"
            f"0%,{fmt(mine_time - .05)}%{{opacity:1}}"
            f"{fmt(mine_time)}%,{fmt(reset)}%{{opacity:0}}"
            "100%{opacity:1}"
            "}"
        )
        css_parts.append(
            f".piece-{i}{{opacity:0;animation:placePiece{i} {LOOP_MS}ms steps(1,end) infinite}}"
            f"@keyframes placePiece{i}{{"
            f"0%,{fmt(place_time - .05)}%{{opacity:0}}"
            f"{fmt(place_time)}%,99.65%{{opacity:1}}"
            "100%{opacity:0}"
            "}"
        )

    complete_at = 88.0
    css_parts.extend(
        [
            f".reward-trophy{{opacity:0;animation:rewardTrophy {LOOP_MS}ms steps(3,end) infinite}}",
            "@keyframes rewardTrophy{"
            f"0%,{fmt(complete_at)}%{{opacity:0;transform:translateY(7px)}}"
            "89%,97.5%{opacity:1;transform:translateY(-7px)}"
            "99.5%,100%{opacity:0;transform:translateY(7px)}}",
            f".build-complete{{opacity:0;font-family:monospace;font-weight:900;letter-spacing:1.5px;"
            f"animation:completeText {LOOP_MS}ms steps(2,end) infinite}}",
            "@keyframes completeText{0%,88%{opacity:0}89%,97%{opacity:1}99.5%,100%{opacity:0}}",
            f".voxel-particle{{opacity:0;shape-rendering:crispEdges;animation:voxelBurst {LOOP_MS}ms steps(8,end) infinite}}",
            "@keyframes voxelBurst{"
            "0%,88%{opacity:0;transform:translate(0,0) scale(.3)}"
            "89%{opacity:1;transform:translate(0,0) scale(.8)}"
            "94%{opacity:1;transform:translate(var(--dx),var(--dy)) scale(1)}"
            "98%,100%{opacity:0;transform:translate(calc(var(--dx)*1.2),calc(var(--dy)*1.2)) scale(.4)}}",
            f".xp-fill{{transform-origin:left center;animation:xpFill {LOOP_MS}ms steps({len(place_times)},end) infinite}}",
        ]
    )

    xp_frames = ["0%{transform:scaleX(.05)}"]
    for i, place_time in enumerate(place_times, start=1):
        scale = i / len(place_times)
        xp_frames.append(f"{fmt(place_time)}%{{transform:scaleX({scale:.3f})}}")
    xp_frames.extend(["99.5%{transform:scaleX(1)}", "100%{transform:scaleX(.05)}"])
    css_parts.append("@keyframes xpFill{" + "".join(xp_frames) + "}")

    scene = (
        '<g id="one-block-build-loop">'
        '<g class="steven-route">'
        + steven_markup()
        + '</g>'
        + house_pieces_markup()
        + '<g id="hud" aria-hidden="true">'
          '<rect x="18" y="166" width="180" height="17" rx="2" fill="#111827" stroke="#57534E" stroke-width="2"/>'
          '<rect class="xp-fill" x="23" y="171" width="130" height="7" fill="#84CC16"/>'
          '<text x="160" y="178" font-family="monospace" font-size="10" font-weight="800" fill="#A3E635">XP</text>'
          '<text class="scene-status" x="205" y="178" font-family="monospace" font-size="10" font-weight="800" fill="#E7E5E4">'
          '1 BLOCK → 1 BUILD → REPEAT</text>'
        '</g>'
        + particles_markup(728, 126)
        + '<text class="build-complete" x="728" y="103" text-anchor="middle" font-size="13" fill="#A3E635">'
          'BUILD COMPLETE +XP</text>'
        + '</g>'
    )

    if "</style>" not in svg or "</svg>" not in svg:
        raise RuntimeError(f"Unexpected SVG structure in {path}")

    svg = svg.replace("</style>", "".join(css_parts) + "</style>", 1)
    svg = svg.replace("</svg>", scene + "</svg>", 1)
    path.write_text(svg, encoding="utf-8")

    selected = ", ".join(cls for cls, _, _ in mining_blocks)
    print(
        f"Added one-block-at-a-time Steven build loop to {path}: "
        f"{len(mining_blocks)} round trips, selected contributions [{selected}]"
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
