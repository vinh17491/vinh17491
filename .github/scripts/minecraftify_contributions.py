from __future__ import annotations

import re
import sys
from pathlib import Path

LOOP_MS = 30000
TRIP_COUNT = 9

FOODS = (
    ("pig", "carrot", "#F97316"),
    ("cow", "hay", "#FACC15"),
    ("sheep", "grass", "#65A30D"),
)

FARM_X = 8.0
FARM_Y = 58.0
STEVEN_IDLE_X = 278.0
STEVEN_IDLE_Y = 95.0

TARGETS = {
    "pig": (44.0, 94.0),
    "cow": (118.0, 94.0),
    "sheep": (194.0, 94.0),
}


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def select_blocks(svg: str, count: int) -> list[tuple[str, float, float]]:
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
        raise RuntimeError("No contribution blocks found")

    if len(unique) <= count:
        return unique

    selected = []
    for i in range(count):
        index = round(i * (len(unique) - 1) / (count - 1))
        selected.append(unique[index])
    return selected


def steven_markup() -> str:
    return (
        '<g id="steven" aria-hidden="true">'
        '<g class="steven-body">'
        '<rect x="5" y="26" width="6" height="10" fill="#1D4ED8"/>'
        '<rect x="12" y="26" width="6" height="10" fill="#1E40AF"/>'
        '<rect x="4" y="35" width="7" height="3" fill="#111827"/>'
        '<rect x="12" y="35" width="7" height="3" fill="#111827"/>'
        '<rect x="4" y="14" width="15" height="13" fill="#22D3EE"/>'
        '<rect x="5" y="15" width="13" height="3" fill="#67E8F9"/>'
        '<rect x="5" y="2" width="14" height="13" fill="#C98D62"/>'
        '<rect x="5" y="2" width="14" height="4" fill="#3F2A1D"/>'
        '<rect x="7" y="7" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="14" y="7" width="3" height="2" fill="#E5E7EB"/>'
        '<rect x="8" y="7" width="1" height="2" fill="#2563EB"/>'
        '<rect x="15" y="7" width="1" height="2" fill="#2563EB"/>'
        '<rect x="1" y="15" width="4" height="11" fill="#C98D62"/>'
        '<rect x="18" y="15" width="4" height="11" fill="#C98D62"/>'
        '<g class="food carrot-item">'
        '<rect x="-7" y="18" width="8" height="11" rx="1" fill="#F97316"/>'
        '<rect x="-7" y="15" width="3" height="4" fill="#22C55E"/>'
        '<rect x="-3" y="14" width="3" height="5" fill="#16A34A"/>'
        '</g>'
        '<g class="food hay-item">'
        '<rect x="-9" y="17" width="11" height="11" fill="#FACC15" stroke="#A16207" stroke-width="1"/>'
        '<path d="M-8 21h9M-8 25h9" stroke="#CA8A04" stroke-width="1"/>'
        '</g>'
        '<g class="food grass-item">'
        '<rect x="-9" y="23" width="12" height="6" fill="#795548"/>'
        '<rect x="-9" y="17" width="12" height="7" fill="#65A30D"/>'
        '<rect x="-7" y="15" width="3" height="4" fill="#84CC16"/>'
        '<rect x="-2" y="14" width="3" height="5" fill="#4D7C0F"/>'
        '</g>'
        '</g>'
        '</g>'
    )


def pig_markup() -> str:
    return (
        '<g class="animal pig-animal">'
        '<g class="pig-idle">'
        '<rect x="0" y="8" width="31" height="18" fill="#F9A8D4"/>'
        '<rect x="22" y="3" width="18" height="18" fill="#F9A8D4"/>'
        '<rect x="25" y="11" width="15" height="8" fill="#F472B6"/>'
        '<rect x="28" y="13" width="2" height="2" fill="#7C2D12"/>'
        '<rect x="35" y="13" width="2" height="2" fill="#7C2D12"/>'
        '<rect x="26" y="6" width="2" height="2" fill="#111827"/>'
        '<rect x="36" y="6" width="2" height="2" fill="#111827"/>'
        '<rect x="24" y="1" width="5" height="5" fill="#F472B6"/>'
        '<rect x="34" y="1" width="5" height="5" fill="#F472B6"/>'
        '<rect x="4" y="25" width="5" height="8" fill="#F472B6"/>'
        '<rect x="22" y="25" width="5" height="8" fill="#F472B6"/>'
        '</g>'
        '</g>'
    )


def cow_markup() -> str:
    return (
        '<g class="animal cow-animal">'
        '<g class="cow-idle">'
        '<rect x="0" y="8" width="32" height="19" fill="#F5F5F4"/>'
        '<rect x="4" y="10" width="9" height="8" fill="#78350F"/>'
        '<rect x="20" y="17" width="9" height="8" fill="#78350F"/>'
        '<rect x="23" y="2" width="18" height="19" fill="#A16207"/>'
        '<rect x="27" y="11" width="14" height="8" fill="#D6D3D1"/>'
        '<rect x="27" y="6" width="2" height="2" fill="#111827"/>'
        '<rect x="37" y="6" width="2" height="2" fill="#111827"/>'
        '<path d="M25 4l-5-5h5zM39 4l5-5h-5z" fill="#FDE68A"/>'
        '<rect x="4" y="26" width="5" height="8" fill="#78350F"/>'
        '<rect x="24" y="26" width="5" height="8" fill="#78350F"/>'
        '</g>'
        '</g>'
    )


def sheep_markup() -> str:
    return (
        '<g class="animal sheep-animal">'
        '<g class="sheep-idle">'
        '<rect x="0" y="7" width="33" height="20" rx="4" fill="#F8FAFC"/>'
        '<rect x="4" y="4" width="8" height="8" rx="3" fill="#FFFFFF"/>'
        '<rect x="12" y="3" width="9" height="9" rx="3" fill="#FFFFFF"/>'
        '<rect x="21" y="5" width="8" height="8" rx="3" fill="#FFFFFF"/>'
        '<rect x="24" y="6" width="16" height="18" fill="#78716C"/>'
        '<rect x="27" y="10" width="2" height="2" fill="#111827"/>'
        '<rect x="36" y="10" width="2" height="2" fill="#111827"/>'
        '<rect x="28" y="18" width="8" height="3" fill="#A8A29E"/>'
        '<rect x="5" y="26" width="5" height="8" fill="#57534E"/>'
        '<rect x="24" y="26" width="5" height="8" fill="#57534E"/>'
        '</g>'
        '</g>'
    )


def fence_segment(x: int, y: int, w: int) -> str:
    posts = []
    for px in range(x, x + w + 1, 18):
        posts.append(f'<rect x="{px}" y="{y}" width="4" height="32" fill="#92400E"/>')
        posts.append(f'<rect x="{px+1}" y="{y+2}" width="2" height="28" fill="#B45309"/>')
    rails = (
        f'<rect x="{x}" y="{y+8}" width="{w}" height="5" fill="#A16207"/>'
        f'<rect x="{x}" y="{y+22}" width="{w}" height="5" fill="#A16207"/>'
    )
    return rails + "".join(posts)


def farm_markup(bg: str, text: str) -> str:
    return (
        '<g id="voxel-farm" aria-hidden="true">'
        f'<rect x="{fmt(FARM_X)}" y="{fmt(FARM_Y)}" width="252" height="93" rx="5" fill="{bg}" opacity=".96" '
        'stroke="#65A30D" stroke-width="1.5"/>'
        + f'<rect x="{fmt(FARM_X + 6)}" y="132" width="240" height="12" fill="#65A30D"/>'
        + f'<rect x="{fmt(FARM_X + 6)}" y="141" width="240" height="7" fill="#795548"/>'
        + fence_segment(int(FARM_X + 8), 82, 72)
        + fence_segment(int(FARM_X + 86), 82, 72)
        + fence_segment(int(FARM_X + 164), 82, 72)
        + f'<rect x="{fmt(FARM_X + 8)}" y="128" width="228" height="4" fill="#92400E"/>'
        + f'<g transform="translate({fmt(FARM_X + 21)},96)">' + pig_markup() + '</g>'
        + f'<g transform="translate({fmt(FARM_X + 95)},96)">' + cow_markup() + '</g>'
        + f'<g transform="translate({fmt(FARM_X + 172)},96)">' + sheep_markup() + '</g>'
        + f'<rect x="{fmt(FARM_X + 24)}" y="124" width="34" height="7" fill="#78350F"/>'
        + f'<rect x="{fmt(FARM_X + 98)}" y="124" width="34" height="7" fill="#78350F"/>'
        + f'<rect x="{fmt(FARM_X + 176)}" y="124" width="34" height="7" fill="#78350F"/>'
        + f'<text x="{fmt(FARM_X + 42)}" y="76" text-anchor="middle" font-family="monospace" font-size="10" '
          f'font-weight="900" fill="{text}">PIG</text>'
        + f'<text x="{fmt(FARM_X + 120)}" y="76" text-anchor="middle" font-family="monospace" font-size="10" '
          f'font-weight="900" fill="{text}">COW</text>'
        + f'<text x="{fmt(FARM_X + 198)}" y="76" text-anchor="middle" font-family="monospace" font-size="10" '
          f'font-weight="900" fill="{text}">SHEEP</text>'
        + f'<g class="pig-heart"><text x="{fmt(FARM_X + 42)}" y="91" text-anchor="middle" font-size="16" fill="#FB7185">♥</text></g>'
        + f'<g class="cow-heart"><text x="{fmt(FARM_X + 120)}" y="91" text-anchor="middle" font-size="16" fill="#FB7185">♥</text></g>'
        + f'<g class="sheep-heart"><text x="{fmt(FARM_X + 198)}" y="91" text-anchor="middle" font-size="16" fill="#FB7185">♥</text></g>'
        + '</g>'
    )


def route_and_times(
    blocks: list[tuple[str, float, float]]
) -> tuple[str, list[float], list[float], list[tuple[str, str, str]]]:
    start = 2.0
    end = 86.0
    span = (end - start) / len(blocks)
    points: list[tuple[float, float, float]] = [
        (0.0, STEVEN_IDLE_X, STEVEN_IDLE_Y),
        (start, STEVEN_IDLE_X, STEVEN_IDLE_Y),
    ]
    pickup_times: list[float] = []
    feed_times: list[float] = []
    assignments: list[tuple[str, str, str]] = []

    for i, (_, bx, by) in enumerate(blocks):
        animal, food, color = FOODS[i % len(FOODS)]
        target_x, target_y = TARGETS[animal]
        trip = start + i * span
        source_x = bx - 8
        source_y = by - 34

        arrive_source = trip + span * 0.25
        pickup = trip + span * 0.36
        arrive_target = trip + span * 0.73
        feed = trip + span * 0.84

        points.extend([
            (arrive_source, source_x, source_y),
            (pickup, source_x, source_y),
            (arrive_target, target_x, target_y),
            (feed, target_x, target_y),
        ])
        pickup_times.append(pickup)
        feed_times.append(feed)
        assignments.append((animal, food, color))

    points.extend([
        (90.0, STEVEN_IDLE_X, STEVEN_IDLE_Y),
        (99.5, STEVEN_IDLE_X, STEVEN_IDLE_Y),
        (100.0, STEVEN_IDLE_X, STEVEN_IDLE_Y),
    ])

    compact: dict[float, tuple[float, float]] = {}
    for p, x, y in points:
        compact[round(p, 2)] = (x, y)

    frames = []
    for p in sorted(compact):
        x, y = compact[p]
        frames.append(f"{fmt(p)}%{{transform:translate({fmt(x)}px,{fmt(y)}px)}}")

    return "@keyframes stevenRoute{" + "".join(frames) + "}", pickup_times, feed_times, assignments


def visibility_keyframes(
    name: str,
    pickup_times: list[float],
    feed_times: list[float],
    assignments: list[tuple[str, str, str]],
    food_name: str,
) -> str:
    frames = ["0%{opacity:0}"]
    for pickup, feed, (_, food, _) in zip(pickup_times, feed_times, assignments):
        if food != food_name:
            continue
        frames.extend([
            f"{fmt(pickup - .05)}%{{opacity:0}}",
            f"{fmt(pickup)}%{{opacity:1}}",
            f"{fmt(feed - .05)}%{{opacity:1}}",
            f"{fmt(feed)}%{{opacity:0}}",
        ])
    frames.append("100%{opacity:0}")
    return f"@keyframes {name}" + "{" + "".join(frames) + "}"


def reaction_keyframes(
    name: str,
    feed_times: list[float],
    assignments: list[tuple[str, str, str]],
    animal_name: str,
) -> str:
    frames = ["0%{transform:translateY(0) scale(1)}"]
    for feed, (animal, _, _) in zip(feed_times, assignments):
        if animal != animal_name:
            continue
        frames.extend([
            f"{fmt(feed - .15)}%{{transform:translateY(0) scale(1)}}",
            f"{fmt(feed + .2)}%{{transform:translateY(-5px) scale(1.05)}}",
            f"{fmt(feed + .7)}%{{transform:translateY(0) scale(1)}}",
        ])
    frames.append("100%{transform:translateY(0) scale(1)}")
    return f"@keyframes {name}" + "{" + "".join(frames) + "}"


def heart_keyframes(
    name: str,
    feed_times: list[float],
    assignments: list[tuple[str, str, str]],
    animal_name: str,
) -> str:
    frames = ["0%{opacity:0;transform:translateY(5px) scale(.5)}"]
    for feed, (animal, _, _) in zip(feed_times, assignments):
        if animal != animal_name:
            continue
        frames.extend([
            f"{fmt(feed - .05)}%{{opacity:0;transform:translateY(5px) scale(.5)}}",
            f"{fmt(feed + .15)}%{{opacity:1;transform:translateY(0) scale(1)}}",
            f"{fmt(feed + .75)}%{{opacity:0;transform:translateY(-8px) scale(1.2)}}",
        ])
    frames.append("100%{opacity:0}")
    return f"@keyframes {name}" + "{" + "".join(frames) + "}"


def feed_status_keyframes(
    feed_times: list[float],
    assignments: list[tuple[str, str, str]],
) -> str:
    labels = {
        "pig": "CARROT → PIG",
        "cow": "HAY → COW",
        "sheep": "GRASS → SHEEP",
    }
    # We cannot change SVG text content from CSS, so pulse the status bar at each feed.
    frames = ["0%{opacity:.55}"]
    for feed, (animal, _, _) in zip(feed_times, assignments):
        frames.extend([
            f"{fmt(feed - .2)}%{{opacity:.55}}",
            f"{fmt(feed + .05)}%{{opacity:1}}",
            f"{fmt(feed + .7)}%{{opacity:.7}}",
        ])
    frames.append("100%{opacity:.55}")
    return "@keyframes statusPulse{" + "".join(frames) + "}"


def minecraftify(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")
    if 'id="animal-farm-loop"' in svg:
        return

    blocks = select_blocks(svg, TRIP_COUNT)
    route_css, pickup_times, feed_times, assignments = route_and_times(blocks)

    is_dark = "dark" in path.name
    panel_bg = "#0F172A" if is_dark else "#F8FAFC"
    panel_text = "#E5E7EB" if is_dark else "#334155"
    hud_bg = "#111827" if is_dark else "#E7E5E4"
    hud_text = "#E7E5E4" if is_dark else "#334155"

    css = [
        ".s{display:none!important}",
        ".u{display:none!important}",
        ".c{animation:none!important;shape-rendering:crispEdges;rx:0;ry:0;stroke:#111827;stroke-width:1.1px}",
        f".steven-route{{animation:stevenRoute {LOOP_MS}ms linear infinite}}",
        ".steven-body{animation:stevenBob 430ms steps(2,end) infinite}",
        "@keyframes stevenBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}",
        route_css,
        f".carrot-item{{opacity:0;animation:carrotCarry {LOOP_MS}ms steps(1,end) infinite}}",
        f".hay-item{{opacity:0;animation:hayCarry {LOOP_MS}ms steps(1,end) infinite}}",
        f".grass-item{{opacity:0;animation:grassCarry {LOOP_MS}ms steps(1,end) infinite}}",
        visibility_keyframes("carrotCarry", pickup_times, feed_times, assignments, "carrot"),
        visibility_keyframes("hayCarry", pickup_times, feed_times, assignments, "hay"),
        visibility_keyframes("grassCarry", pickup_times, feed_times, assignments, "grass"),
        f".pig-animal{{transform-origin:20px 25px;animation:pigReact {LOOP_MS}ms steps(5,end) infinite}}",
        f".cow-animal{{transform-origin:20px 25px;animation:cowReact {LOOP_MS}ms steps(5,end) infinite}}",
        f".sheep-animal{{transform-origin:20px 25px;animation:sheepReact {LOOP_MS}ms steps(5,end) infinite}}",
        reaction_keyframes("pigReact", feed_times, assignments, "pig"),
        reaction_keyframes("cowReact", feed_times, assignments, "cow"),
        reaction_keyframes("sheepReact", feed_times, assignments, "sheep"),
        ".pig-idle{animation:pigWander 5600ms steps(7,end) infinite;animation-delay:-900ms}",
        "@keyframes pigWander{0%,100%{transform:translate(0,0)}14%{transform:translate(6px,0)}28%{transform:translate(9px,-1px)}43%{transform:translate(4px,0)}57%{transform:translate(-4px,0)}72%{transform:translate(-8px,-1px)}86%{transform:translate(-3px,0)}}",
        ".cow-idle{animation:cowWander 7600ms steps(8,end) infinite;animation-delay:-2500ms}",
        "@keyframes cowWander{0%,100%{transform:translate(0,0)}13%{transform:translate(-3px,0)}25%{transform:translate(-6px,0)}38%{transform:translate(-6px,-1px)}50%{transform:translate(-1px,0)}63%{transform:translate(4px,0)}76%{transform:translate(6px,-1px)}88%{transform:translate(3px,0)}}",
        ".sheep-idle{animation:sheepWander 4800ms steps(7,end) infinite;animation-delay:-1700ms}",
        "@keyframes sheepWander{0%,100%{transform:translate(0,0)}15%{transform:translate(5px,-2px)}30%{transform:translate(8px,0)}45%{transform:translate(3px,-2px)}60%{transform:translate(-4px,0)}75%{transform:translate(-7px,-2px)}90%{transform:translate(-2px,0)}}",
        f".pig-heart{{opacity:0;animation:pigHeart {LOOP_MS}ms steps(5,end) infinite}}",
        f".cow-heart{{opacity:0;animation:cowHeart {LOOP_MS}ms steps(5,end) infinite}}",
        f".sheep-heart{{opacity:0;animation:sheepHeart {LOOP_MS}ms steps(5,end) infinite}}",
        heart_keyframes("pigHeart", feed_times, assignments, "pig"),
        heart_keyframes("cowHeart", feed_times, assignments, "cow"),
        heart_keyframes("sheepHeart", feed_times, assignments, "sheep"),
        f".scene-status{{animation:statusPulse {LOOP_MS}ms steps(1,end) infinite}}",
        feed_status_keyframes(feed_times, assignments),
    ]

    for i, ((cls, _, _), pickup, (_, food, color)) in enumerate(
        zip(blocks, pickup_times, assignments)
    ):
        reset = 99.6
        css.append(
            f".c.{cls}{{animation:harvest{i} {LOOP_MS}ms steps(1,end) infinite!important}}"
            f"@keyframes harvest{i}{{"
            f"0%,{fmt(pickup - .05)}%{{opacity:1;fill:{color}}}"
            f"{fmt(pickup)}%,{fmt(reset)}%{{opacity:0;fill:{color}}}"
            f"100%{{opacity:1;fill:{color}}}"
            f"}}"
        )

    complete = 88.0
    css.extend([
        f".farm-complete{{opacity:0;font-family:monospace;font-weight:900;letter-spacing:1.5px;"
        f"animation:farmComplete {LOOP_MS}ms steps(2,end) infinite}}",
        "@keyframes farmComplete{0%,88%{opacity:0}89%,97%{opacity:1}99.5%,100%{opacity:0}}",
        f".all-hearts{{opacity:0;animation:allHearts {LOOP_MS}ms steps(5,end) infinite}}",
        "@keyframes allHearts{0%,88%{opacity:0;transform:translateY(5px)}"
        "89%,94%{opacity:1;transform:translateY(-3px)}98%,100%{opacity:0;transform:translateY(-10px)}}",
        f".xp-fill{{transform-origin:left center;animation:xpFill {LOOP_MS}ms steps({len(feed_times)},end) infinite}}",
    ])

    xp = ["0%{transform:scaleX(.05)}"]
    for i, feed in enumerate(feed_times, start=1):
        xp.append(f"{fmt(feed)}%{{transform:scaleX({i/len(feed_times):.3f})}}")
    xp.extend(["99.5%{transform:scaleX(1)}", "100%{transform:scaleX(.05)}"])
    css.append("@keyframes xpFill{" + "".join(xp) + "}")

    scene = (
        '<g id="animal-farm-loop">'
        + farm_markup(panel_bg, panel_text)
        + '<g class="steven-route">' + steven_markup() + '</g>'
        + '<g id="farm-hud" aria-hidden="true">'
        + f'<rect x="280" y="164" width="568" height="17" rx="2" fill="{hud_bg}" stroke="#57534E" stroke-width="1.5"/>'
        + '<rect class="xp-fill" x="285" y="169" width="126" height="7" fill="#84CC16"/>'
        + f'<text x="417" y="176" font-family="monospace" font-size="10" font-weight="800" fill="{hud_text}">XP</text>'
        + f'<text class="scene-status" x="454" y="176" font-family="monospace" font-size="10" font-weight="800" fill="{hud_text}">'
          'CARROT → PIG   |   HAY → COW   |   GRASS → SHEEP</text>'
        + '</g>'
        + '<g class="all-hearts">'
          '<text x="88" y="54" font-size="15" fill="#FB7185">♥</text>'
          '<text x="130" y="48" font-size="18" fill="#F472B6">♥</text>'
          '<text x="173" y="54" font-size="15" fill="#FB7185">♥</text>'
        + '</g>'
        + '<text class="farm-complete" x="134" y="45" text-anchor="middle" font-size="13" fill="#A3E635">'
          'ANIMALS FED +XP</text>'
        + '</g>'
    )

    if "</style>" not in svg or "</svg>" not in svg:
        raise RuntimeError(f"Unexpected SVG structure in {path}")

    svg = svg.replace("</style>", "".join(css) + "</style>", 1)
    svg = svg.replace("</svg>", scene + "</svg>", 1)
    path.write_text(svg, encoding="utf-8")

    print(
        f"Added farm loop to {path}: {len(blocks)} trips, "
        "CARROT->PIG / HAY->COW / GRASS->SHEEP"
    )


def main() -> None:
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted(Path("dist").glob("*.svg"))
    if not paths:
        raise SystemExit("No SVG files found")
    for path in paths:
        minecraftify(path)


if __name__ == "__main__":
    main()
