from __future__ import annotations

import re
import sys
from pathlib import Path

LOOP_MS = 36000
TRIP_COUNT = 12
CANVAS_HEIGHT = 512

FOODS = (
    ("pig", "carrot", "#F97316"),
    ("cow", "wheat", "#FACC15"),
    ("sheep", "grass", "#65A30D"),
    ("chicken", "seeds", "#EAB308"),
)

HUB = (420.0, 278.0)

HARVEST_SPOTS = {
    "carrot": (82.0, 244.0),
    "wheat": (230.0, 244.0),
    "grass": (82.0, 374.0),
    "seeds": (230.0, 374.0),
}

FEED_SPOTS = {
    "pig": (565.0, 246.0),
    "cow": (718.0, 246.0),
    "sheep": (565.0, 377.0),
    "chicken": (718.0, 377.0),
}


def fmt(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


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
        '<rect x="-7" y="18" width="8" height="11" fill="#F97316"/>'
        '<rect x="-7" y="15" width="3" height="4" fill="#22C55E"/>'
        '<rect x="-3" y="14" width="3" height="5" fill="#16A34A"/>'
        '</g>'
        '<g class="food wheat-item">'
        '<rect x="-8" y="18" width="3" height="11" fill="#CA8A04"/>'
        '<rect x="-11" y="14" width="6" height="4" fill="#FACC15"/>'
        '<rect x="-5" y="12" width="6" height="4" fill="#FDE047"/>'
        '<rect x="-10" y="20" width="8" height="3" fill="#EAB308"/>'
        '</g>'
        '<g class="food grass-item">'
        '<rect x="-9" y="23" width="12" height="6" fill="#795548"/>'
        '<rect x="-9" y="17" width="12" height="7" fill="#65A30D"/>'
        '<rect x="-7" y="15" width="3" height="4" fill="#84CC16"/>'
        '<rect x="-2" y="14" width="3" height="5" fill="#4D7C0F"/>'
        '</g>'
        '<g class="food seeds-item">'
        '<rect x="-8" y="18" width="3" height="3" fill="#FDE047"/>'
        '<rect x="-3" y="22" width="3" height="3" fill="#CA8A04"/>'
        '<rect x="-10" y="25" width="3" height="3" fill="#EAB308"/>'
        '<rect x="-2" y="16" width="3" height="3" fill="#FACC15"/>'
        '</g>'
        '</g>'
        '</g>'
    )


def pig_markup(extra: str = "") -> str:
    return (
        f'<g class="animal-unit pig-unit {extra}">'
        '<rect x="0" y="8" width="29" height="17" fill="#F9A8D4"/>'
        '<rect x="21" y="3" width="17" height="18" fill="#F9A8D4"/>'
        '<rect x="24" y="11" width="14" height="7" fill="#F472B6"/>'
        '<rect x="27" y="13" width="2" height="2" fill="#7C2D12"/>'
        '<rect x="34" y="13" width="2" height="2" fill="#7C2D12"/>'
        '<rect x="25" y="6" width="2" height="2" fill="#111827"/>'
        '<rect x="34" y="6" width="2" height="2" fill="#111827"/>'
        '<rect x="23" y="1" width="5" height="5" fill="#F472B6"/>'
        '<rect x="33" y="1" width="5" height="5" fill="#F472B6"/>'
        '<rect x="4" y="24" width="5" height="8" fill="#F472B6"/>'
        '<rect x="21" y="24" width="5" height="8" fill="#F472B6"/>'
        '</g>'
    )


def cow_markup(extra: str = "") -> str:
    return (
        f'<g class="animal-unit cow-unit {extra}">'
        '<rect x="0" y="8" width="31" height="19" fill="#F5F5F4"/>'
        '<rect x="4" y="10" width="9" height="8" fill="#78350F"/>'
        '<rect x="19" y="17" width="9" height="8" fill="#78350F"/>'
        '<rect x="22" y="2" width="18" height="19" fill="#A16207"/>'
        '<rect x="26" y="11" width="14" height="8" fill="#D6D3D1"/>'
        '<rect x="26" y="6" width="2" height="2" fill="#111827"/>'
        '<rect x="36" y="6" width="2" height="2" fill="#111827"/>'
        '<path d="M24 4l-5-5h5zM38 4l5-5h-5z" fill="#FDE68A"/>'
        '<rect x="4" y="26" width="5" height="8" fill="#78350F"/>'
        '<rect x="23" y="26" width="5" height="8" fill="#78350F"/>'
        '</g>'
    )


def sheep_markup(extra: str = "") -> str:
    return (
        f'<g class="animal-unit sheep-unit {extra}">'
        '<rect x="0" y="7" width="32" height="20" fill="#F8FAFC"/>'
        '<rect x="4" y="4" width="8" height="8" fill="#FFFFFF"/>'
        '<rect x="12" y="3" width="9" height="9" fill="#FFFFFF"/>'
        '<rect x="21" y="5" width="8" height="8" fill="#FFFFFF"/>'
        '<rect x="23" y="6" width="16" height="18" fill="#78716C"/>'
        '<rect x="26" y="10" width="2" height="2" fill="#111827"/>'
        '<rect x="35" y="10" width="2" height="2" fill="#111827"/>'
        '<rect x="27" y="18" width="8" height="3" fill="#A8A29E"/>'
        '<rect x="5" y="26" width="5" height="8" fill="#57534E"/>'
        '<rect x="23" y="26" width="5" height="8" fill="#57534E"/>'
        '</g>'
    )


def chicken_markup(extra: str = "") -> str:
    return (
        f'<g class="animal-unit chicken-unit {extra}">'
        '<rect x="5" y="8" width="24" height="20" fill="#F8FAFC"/>'
        '<rect x="20" y="3" width="17" height="17" fill="#FFFFFF"/>'
        '<rect x="34" y="11" width="8" height="5" fill="#F59E0B"/>'
        '<rect x="24" y="7" width="2" height="2" fill="#111827"/>'
        '<rect x="32" y="7" width="2" height="2" fill="#111827"/>'
        '<rect x="26" y="0" width="4" height="5" fill="#DC2626"/>'
        '<rect x="31" y="1" width="4" height="4" fill="#DC2626"/>'
        '<rect x="3" y="12" width="6" height="12" fill="#E5E7EB"/>'
        '<rect x="11" y="28" width="3" height="7" fill="#F59E0B"/>'
        '<rect x="23" y="28" width="3" height="7" fill="#F59E0B"/>'
        '</g>'
    )


def fence_box(x: int, y: int, w: int, h: int) -> str:
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#365314" opacity=".28"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="5" fill="#92400E"/>',
        f'<rect x="{x}" y="{y+h-5}" width="{w}" height="5" fill="#92400E"/>',
        f'<rect x="{x}" y="{y}" width="5" height="{h}" fill="#92400E"/>',
        f'<rect x="{x+w-5}" y="{y}" width="5" height="{h}" fill="#92400E"/>',
    ]
    for px in range(x, x + w, 24):
        out.append(f'<rect x="{px}" y="{y-3}" width="5" height="{h+6}" fill="#B45309"/>')
    for py in range(y + 18, y + h - 5, 26):
        out.append(f'<rect x="{x}" y="{py}" width="{w}" height="4" fill="#A16207"/>')
    return "".join(out)


def barn_markup() -> str:
    return (
        '<g id="voxel-barn" aria-hidden="true">'
        '<rect x="354" y="182" width="164" height="104" fill="#991B1B"/>'
        '<rect x="365" y="193" width="142" height="82" fill="#B91C1C"/>'
        '<path d="M340 185L436 126L532 185Z" fill="#292524"/>'
        '<path d="M352 181L436 137L520 181Z" fill="#44403C"/>'
        '<rect x="425" y="226" width="38" height="60" fill="#7F1D1D" stroke="#F8FAFC" stroke-width="5"/>'
        '<path d="M425 226L463 286M463 226L425 286" stroke="#F8FAFC" stroke-width="4"/>'
        '<rect x="382" y="210" width="27" height="27" fill="#0EA5E9" stroke="#F8FAFC" stroke-width="5"/>'
        '<rect x="472" y="210" width="27" height="27" fill="#0EA5E9" stroke="#F8FAFC" stroke-width="5"/>'
        '<rect x="426" y="157" width="22" height="22" fill="#0EA5E9" stroke="#F8FAFC" stroke-width="4"/>'
        '<rect x="351" y="178" width="170" height="7" fill="#F8FAFC"/>'
        '<rect x="370" y="268" width="36" height="18" fill="#EAB308"/>'
        '<rect x="477" y="268" width="30" height="18" fill="#FACC15"/>'
        '<path d="M373 274h30M480 274h24" stroke="#A16207" stroke-width="3"/>'
        '<rect x="411" y="288" width="53" height="8" fill="#795548"/>'
        '</g>'
    )


def plot_markup(plot_id: str, label: str, x: int, y: int, crop: str) -> str:
    soil = (
        f'<rect x="{x}" y="{y}" width="132" height="104" fill="#3F2A1D"/>'
        f'<rect x="{x+5}" y="{y+5}" width="122" height="94" fill="#6B4423"/>'
        f'<rect x="{x+61}" y="{y+5}" width="10" height="94" fill="#0EA5E9"/>'
        f'<rect x="{x+64}" y="{y+5}" width="4" height="94" fill="#38BDF8"/>'
    )
    fence = fence_box(x - 5, y - 5, 142, 114)
    rows = []
    for row in range(3):
        cy = y + 20 + row * 24
        for col in range(4):
            cx = x + 13 + col * 12
            rows.append(crop_sprite(crop, cx, cy))
        for col in range(4):
            cx = x + 82 + col * 12
            rows.append(crop_sprite(crop, cx, cy))

    return (
        f'<g id="plot-{plot_id}" class="crop-plot crop-{crop}">'
        + fence
        + soil
        + "".join(rows)
        + f'<rect x="{x+36}" y="{y-16}" width="60" height="14" fill="#78350F"/>'
        + f'<text x="{x+66}" y="{y-6}" text-anchor="middle" font-family="monospace" '
          f'font-size="9" font-weight="900" fill="#FDE68A">{label}</text>'
        + '</g>'
    )


def crop_sprite(crop: str, x: int, y: int) -> str:
    if crop == "carrot":
        return (
            f'<g transform="translate({x},{y})"><g class="crop-sprout">'
            '<rect class="crop-stem" x="3" y="-10" width="3" height="10" fill="#16A34A"/>'
            '<rect class="crop-stem" x="7" y="-8" width="3" height="8" fill="#22C55E"/>'
            '<rect class="ripe-part" x="4" y="0" width="5" height="10" fill="#F97316"/>'
            '</g></g>'
        )
    if crop == "wheat":
        return (
            f'<g transform="translate({x},{y})"><g class="crop-sprout">'
            '<rect x="5" y="-17" width="2" height="17" fill="#A16207"/>'
            '<rect class="ripe-part" x="1" y="-17" width="5" height="4" fill="#FACC15"/>'
            '<rect class="ripe-part" x="6" y="-14" width="5" height="4" fill="#FDE047"/>'
            '<rect class="ripe-part" x="1" y="-10" width="5" height="4" fill="#EAB308"/>'
            '</g></g>'
        )
    if crop == "grass":
        return (
            f'<g transform="translate({x},{y})"><g class="crop-sprout">'
            '<rect x="1" y="-12" width="3" height="12" fill="#4D7C0F"/>'
            '<rect x="6" y="-17" width="3" height="17" fill="#65A30D"/>'
            '<rect x="10" y="-10" width="3" height="10" fill="#84CC16"/>'
            '<rect class="ripe-part" x="3" y="-18" width="3" height="5" fill="#A3E635"/>'
            '</g></g>'
        )
    return (
        f'<g transform="translate({x},{y})"><g class="crop-sprout">'
        '<rect x="5" y="-15" width="2" height="15" fill="#65A30D"/>'
        '<rect class="ripe-part" x="1" y="-16" width="4" height="4" fill="#FACC15"/>'
        '<rect class="ripe-part" x="7" y="-13" width="4" height="4" fill="#EAB308"/>'
        '<rect class="ripe-part" x="2" y="-9" width="4" height="4" fill="#FDE047"/>'
        '</g></g>'
    )

def herd_markup(kind: str, x: int, y: int, w: int, h: int) -> str:
    sprite = {
        "pig": pig_markup,
        "cow": cow_markup,
        "sheep": sheep_markup,
        "chicken": chicken_markup,
    }[kind]
    sign = {
        "pig": "PIGS",
        "cow": "COWS",
        "sheep": "SHEEP",
        "chicken": "CHICKENS",
    }[kind]
    return (
        f'<g id="{kind}-pen">'
        + fence_box(x, y, w, h)
        + f'<rect x="{x+40}" y="{y-16}" width="{w-80}" height="14" fill="#78350F"/>'
        + f'<text x="{x+w/2}" y="{y-6}" text-anchor="middle" font-family="monospace" '
          f'font-size="9" font-weight="900" fill="#FDE68A">{sign}</text>'
        + f'<g class="{kind}-herd">'
        + f'<g transform="translate({x+18},{y+36}) scale(.82)">{sprite("wander-a")}</g>'
        + f'<g transform="translate({x+70},{y+66}) scale(.68)">{sprite("wander-b")}</g>'
        + '</g>'
        + f'<rect x="{x+12}" y="{y+h-20}" width="42" height="10" fill="#78350F"/>'
        + f'<rect x="{x+14}" y="{y+h-18}" width="38" height="4" fill="#A16207"/>'
        + f'<g class="{kind}-heart"><text x="{x+w/2}" y="{y+24}" text-anchor="middle" '
          f'font-size="18" fill="#FB7185">♥</text></g>'
        + '</g>'
    )


def route_and_times() -> tuple[str, list[float], list[float], list[tuple[str, str, str]]]:
    start = 2.0
    end = 90.0
    span = (end - start) / TRIP_COUNT
    hx, hy = HUB
    points: list[tuple[float, float, float]] = [(0.0, hx, hy), (start, hx, hy)]
    pickup_times: list[float] = []
    feed_times: list[float] = []
    assignments: list[tuple[str, str, str]] = []

    for i in range(TRIP_COUNT):
        animal, food, color = FOODS[i % len(FOODS)]
        source_x, source_y = HARVEST_SPOTS[food]
        target_x, target_y = FEED_SPOTS[animal]
        trip = start + i * span

        arrive_source = trip + span * 0.24
        pickup = trip + span * 0.38
        arrive_target = trip + span * 0.66
        feed = trip + span * 0.78
        return_home = trip + span * 0.96

        points.extend([
            (arrive_source, source_x, source_y),
            (pickup, source_x, source_y),
            (arrive_target, target_x, target_y),
            (feed, target_x, target_y),
            (return_home, hx, hy),
        ])
        pickup_times.append(pickup)
        feed_times.append(feed)
        assignments.append((animal, food, color))

    points.extend([(96.0, hx, hy), (99.5, hx, hy), (100.0, hx, hy)])

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
            f"{fmt(feed - .12)}%{{transform:translateY(0) scale(1)}}",
            f"{fmt(feed + .18)}%{{transform:translateY(-7px) scale(1.04)}}",
            f"{fmt(feed + .65)}%{{transform:translateY(0) scale(1)}}",
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
            f"{fmt(feed + .12)}%{{opacity:1;transform:translateY(0) scale(1)}}",
            f"{fmt(feed + .72)}%{{opacity:0;transform:translateY(-10px) scale(1.2)}}",
        ])
    frames.append("100%{opacity:0}")
    return f"@keyframes {name}" + "{" + "".join(frames) + "}"


def crop_css(
    crop: str,
    pickup_times: list[float],
    assignments: list[tuple[str, str, str]],
) -> str:
    matching = [p for p, (_, food, _) in zip(pickup_times, assignments) if food == crop]
    if len(matching) < 2:
        crop_ms = 11000
    else:
        delta_pct = matching[1] - matching[0]
        crop_ms = round(LOOP_MS * delta_pct / 100)

    first_ms = LOOP_MS * matching[0] / 100
    delay_ms = round(first_ms - crop_ms * 0.88)

    return (
        f".crop-{crop} .crop-sprout{{transform-box:fill-box;transform-origin:center bottom;"
        f"animation:{crop}Grow {crop_ms}ms steps(4,end) infinite;"
        f"animation-delay:{delay_ms}ms}}"
        f".crop-{crop} .ripe-part{{animation:{crop}Ripe {crop_ms}ms steps(1,end) infinite;"
        f"animation-delay:{delay_ms}ms}}"
        f"@keyframes {crop}Grow{{"
        "0%,12%{transform:scaleY(.22)}"
        "32%{transform:scaleY(.45)}"
        "55%{transform:scaleY(.7)}"
        "72%,87%{transform:scaleY(1)}"
        "88%,94%{transform:scaleY(.05)}"
        "100%{transform:scaleY(.22)}}"
        f"@keyframes {crop}Ripe{{"
        "0%,54%{opacity:.3}"
        "55%,87%{opacity:1}"
        "88%,100%{opacity:.15}}}"
    )


def world_markup(bg: str, text: str) -> str:
    return (
        '<g id="minecraft-farm-world">'
        f'<rect x="-16" y="112" width="880" height="356" fill="{bg}" opacity=".98"/>'
        '<rect x="-16" y="112" width="880" height="22" fill="#14532D"/>'
        '<rect x="-16" y="134" width="880" height="12" fill="#365314"/>'
        '<rect x="-16" y="444" width="880" height="24" fill="#4D7C0F"/>'
        '<rect x="-16" y="460" width="880" height="8" fill="#795548"/>'
        + barn_markup()
        + plot_markup("carrot", "CARROTS", 24, 172, "carrot")
        + plot_markup("wheat", "WHEAT", 174, 172, "wheat")
        + plot_markup("grass", "GRASS", 24, 302, "grass")
        + plot_markup("seeds", "SEEDS", 174, 302, "seeds")
        + herd_markup("pig", 535, 168, 142, 112)
        + herd_markup("cow", 696, 168, 142, 112)
        + herd_markup("sheep", 535, 299, 142, 112)
        + herd_markup("chicken", 696, 299, 142, 112)
        + '<path d="M326 314H535M438 296V444" stroke="#A16207" stroke-width="12"/>'
        + '<path d="M326 314H535M438 296V444" stroke="#CA8A04" stroke-width="4"/>'
        + '<rect x="326" y="429" width="518" height="15" fill="#78350F"/>'
        + '<rect x="330" y="432" width="510" height="7" fill="#A16207"/>'
        + f'<text x="436" y="118" text-anchor="middle" font-family="monospace" '
          f'font-size="11" font-weight="900" fill="{text}">GITHUB FARM LIFE</text>'
        + '</g>'
    )


def minecraftify(path: Path) -> None:
    svg = path.read_text(encoding="utf-8")
    if 'id="minecraft-farm-world"' in svg:
        return

    svg = re.sub(
        r'<svg viewBox="-16 -32 880 [0-9.]+" width="880" height="[0-9.]+"',
        f'<svg viewBox="-16 -32 880 {CANVAS_HEIGHT}" width="880" height="{CANVAS_HEIGHT}"',
        svg,
        count=1,
    )

    route_css, pickup_times, feed_times, assignments = route_and_times()

    is_dark = "dark" in path.name
    world_bg = "#0F172A" if is_dark else "#DCFCE7"
    world_text = "#E5E7EB" if is_dark else "#1F2937"
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
        f".wheat-item{{opacity:0;animation:wheatCarry {LOOP_MS}ms steps(1,end) infinite}}",
        f".grass-item{{opacity:0;animation:grassCarry {LOOP_MS}ms steps(1,end) infinite}}",
        f".seeds-item{{opacity:0;animation:seedsCarry {LOOP_MS}ms steps(1,end) infinite}}",
        visibility_keyframes("carrotCarry", pickup_times, feed_times, assignments, "carrot"),
        visibility_keyframes("wheatCarry", pickup_times, feed_times, assignments, "wheat"),
        visibility_keyframes("grassCarry", pickup_times, feed_times, assignments, "grass"),
        visibility_keyframes("seedsCarry", pickup_times, feed_times, assignments, "seeds"),
        crop_css("carrot", pickup_times, assignments),
        crop_css("wheat", pickup_times, assignments),
        crop_css("grass", pickup_times, assignments),
        crop_css("seeds", pickup_times, assignments),
        ".wander-a{animation:animalWalkA 5400ms steps(7,end) infinite;animation-delay:-900ms}",
        ".wander-b{animation:animalWalkB 6700ms steps(8,end) infinite;animation-delay:-2800ms}",
        "@keyframes animalWalkA{0%,100%{transform:translate(0,0)}15%{transform:translate(5px,0)}30%{transform:translate(8px,-2px)}45%{transform:translate(3px,0)}60%{transform:translate(-5px,0)}76%{transform:translate(-8px,-1px)}90%{transform:translate(-2px,0)}}",
        "@keyframes animalWalkB{0%,100%{transform:translate(0,0)}14%{transform:translate(-4px,0)}28%{transform:translate(-7px,-1px)}42%{transform:translate(-2px,0)}58%{transform:translate(5px,0)}74%{transform:translate(7px,-2px)}89%{transform:translate(2px,0)}}",
    ]

    for animal in ("pig", "cow", "sheep", "chicken"):
        css.append(
            f".{animal}-herd{{transform-origin:center bottom;"
            f"animation:{animal}React {LOOP_MS}ms steps(5,end) infinite}}"
        )
        css.append(reaction_keyframes(f"{animal}React", feed_times, assignments, animal))
        css.append(
            f".{animal}-heart{{opacity:0;"
            f"animation:{animal}Heart {LOOP_MS}ms steps(5,end) infinite}}"
        )
        css.append(heart_keyframes(f"{animal}Heart", feed_times, assignments, animal))

    css.extend([
        f".farm-complete{{opacity:0;font-family:monospace;font-weight:900;letter-spacing:1.2px;"
        f"animation:farmComplete {LOOP_MS}ms steps(2,end) infinite}}",
        "@keyframes farmComplete{0%,92%{opacity:0}93%,98%{opacity:1}99.5%,100%{opacity:0}}",
        f".all-hearts{{opacity:0;animation:allHearts {LOOP_MS}ms steps(5,end) infinite}}",
        "@keyframes allHearts{0%,92%{opacity:0;transform:translateY(5px)}"
        "93%,97%{opacity:1;transform:translateY(-4px)}99%,100%{opacity:0;transform:translateY(-11px)}}",
        f".xp-fill{{transform-origin:left center;animation:xpFill {LOOP_MS}ms steps({len(feed_times)},end) infinite}}",
    ])

    xp = ["0%{transform:scaleX(.04)}"]
    for i, feed in enumerate(feed_times, start=1):
        xp.append(f"{fmt(feed)}%{{transform:scaleX({i/len(feed_times):.3f})}}")
    xp.extend(["99.5%{transform:scaleX(1)}", "100%{transform:scaleX(.04)}"])
    css.append("@keyframes xpFill{" + "".join(xp) + "}")

    scene = (
        '<g id="minecraft-farm-loop">'
        + world_markup(world_bg, world_text)
        + '<g class="steven-route">' + steven_markup() + '</g>'
        + '<g id="farm-hud" aria-hidden="true">'
        + f'<rect x="18" y="446" width="826" height="22" fill="{hud_bg}" stroke="#57534E" stroke-width="2"/>'
        + '<rect class="xp-fill" x="25" y="453" width="165" height="8" fill="#84CC16"/>'
        + f'<text x="198" y="461" font-family="monospace" font-size="10" font-weight="900" fill="{hud_text}">XP</text>'
        + f'<text x="238" y="461" font-family="monospace" font-size="9" font-weight="800" fill="{hud_text}">'
          'CARROT→PIG  |  WHEAT→COW  |  GRASS→SHEEP  |  SEEDS→CHICKEN</text>'
        + '</g>'
        + '<g class="all-hearts">'
          '<text x="575" y="151" font-size="16" fill="#FB7185">♥</text>'
          '<text x="735" y="151" font-size="18" fill="#F472B6">♥</text>'
          '<text x="575" y="289" font-size="16" fill="#FB7185">♥</text>'
          '<text x="735" y="289" font-size="18" fill="#F472B6">♥</text>'
        + '</g>'
        + '<text class="farm-complete" x="436" y="438" text-anchor="middle" font-size="14" fill="#A3E635">'
          'FARM DAY COMPLETE +XP</text>'
        + '</g>'
    )

    if "</style>" not in svg or "</svg>" not in svg:
        raise RuntimeError(f"Unexpected SVG structure in {path}")

    svg = svg.replace("</style>", "".join(css) + "</style>", 1)
    svg = svg.replace("</svg>", scene + "</svg>", 1)
    path.write_text(svg, encoding="utf-8")

    print(
        f"Added Minecraft-style farm world to {path}: "
        "12 harvest/feed trips, 4 crops, 4 animal pens"
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
