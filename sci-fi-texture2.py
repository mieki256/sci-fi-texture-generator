#!/usr/bin/env python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2018/02/05 05:20:57 +0900>

u"""
Generate Scif-Fi bump mapping texture.

usage :
Filter -> Render -> Sci-Fi texture 2

Author : mieki256
License : CC0 / Public Domain

testing environment :
* GIMP 2.8.22 Portable + Windows10 x64

Changelog :

version 0.0.3 2018/02/05 by mieki256
    * add : draw pattern
    * add : progress bar

version 0.0.2 2018/02/04 by mieki256
    * add : draw pattern

version 0.0.1 2018/02/03 by mieki256
    * first release.

"""

from gimpfu import *    # NOQA
import random
import math


def get_div_rects(x0, y0, x1, y1, d, v, sftv):
    rw = x1 - x0
    rh = y1 - y0
    tw = rw
    th = rh

    ydiv_enable = True
    if v == 0:
        ydiv_enable = False
    elif v == 1:
        ydiv_enable = True
    else:
        ydiv_enable = False if tw > th else True

    if ydiv_enable:
        th = float(rh) / d
    else:
        tw = float(rw) / d

    new_rect = []
    rx0, ry0, rx1, ry1 = x0, y0, x1, y1
    if ydiv_enable:
        for i in range(d):
            rv = random.random() * th * sftv - th * (sftv / 2.0)
            ry1 = math.floor(ry0 + th + rv) if i < (d - 1) else y1
            new_rect.append([rx0, ry0, rx1, ry1])
            ry0 = ry1
    else:
        for i in range(d):
            rv = random.random() * tw * sftv - tw * (sftv / 2.0)
            rx1 = math.floor(rx0 + tw + rv) if i < (d - 1) else x1
            new_rect.append([rx0, ry0, rx1, ry1])
            rx0 = rx1
    return new_rect


def div_rect(rects, x0, y0, x1, y1, d, v, cnt, cntmax, divide_num):
    if cnt <= cntmax:
        new_rects = get_div_rects(x0, y0, x1, y1, d, v, 0.6)
        if cnt == cntmax:
            rects.extend(new_rects)
        else:
            for r in new_rects:
                tx0, ty0, tx1, ty1 = r
                d = random.randint(1, divide_num)
                rects = div_rect(rects, tx0, ty0, tx1, ty1,
                                 d, 2, cnt + 1, cntmax, divide_num)
    return rects


def get_scifi_draw_area(image, spacing):
    non_empty, bx0, by0, bx1, by1 = pdb.gimp_selection_bounds(image)
    x0 = bx0 + spacing
    y0 = by0 + spacing
    x1 = bx1 - spacing
    y1 = by1 - spacing
    w0 = x1 - x0
    h0 = y1 - y0
    return x0, y0, x1, y1, w0, h0


def draw_scifi_lines(image, layer, spacing, lcol, lspc, ldir, lcnt, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 < area_chk or h0 < area_chk:
        return

    dv = lspc if lcol < 0.5 else (lspc * 1.6)
    bsize = 5 if lcol < 0.5 else 7
    dd = 18
    gimp.set_foreground(lcol, lcol, lcol)
    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(bsize)

    if ldir == 0:
        h1 = math.floor(h0 * random.uniform(0.3, 0.8))
        px0 = x0 + dd + random.randint(0, w0 / 3)
        py0 = y0 + random.randint(0, (h0 - h1) + 16) - 8
        px1 = x1 - dd
        py1 = py0 + (h0 * 0.4)
        x = px0
        for i in range(lcnt):
            if x >= px1:
                break
            pdb.gimp_paintbrush_default(layer, 4, [x, py0, x, py1])
            x = x + dv
    else:
        w1 = math.floor(w0 * random.uniform(0.3, 0.8))
        px0 = x0 + random.randint(0, (w0 - w1) + 16) - 8
        py0 = y0 + dd + random.randint(0, h0 / 3)
        px1 = px0 + (w0 * 0.4)
        py1 = y1 - dd
        y = py0
        for i in range(lcnt):
            if y >= py1:
                break
            pdb.gimp_paintbrush_default(layer, 4, [px0, y, px1, y])
            y = y + dv


def draw_scifi_box(image, layer, spacing, lcol, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 < area_chk or h0 < area_chk:
        return

    w1 = math.floor(w0 * 0.4)
    h1 = math.floor(h0 * 0.4)
    aw = w1 + random.randint(0, w1)
    ah = h1 + random.randint(0, h1)
    px0 = x0 + random.randint(0, (w0 - aw) + 16) - 8
    py0 = y0 + random.randint(0, (h0 - ah) + 16) - 8
    px1 = px0 + aw
    py1 = py0 + ah

    bsize = random.randint(1, 2)
    # bsize = 1
    gimp.set_foreground(lcol, lcol, lcol)
    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(bsize)
    pdb.gimp_paintbrush_default(layer, 10, [px0, py0, px1, py0,
                                            px1, py1, px0, py1,
                                            px0, py0])


def draw_scifi_box_fill(image, layer, spacing, bg_col, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 < area_chk or h0 < area_chk:
        return

    # save selection to channel
    channel = pdb.gimp_selection_save(image)

    col_add_fg = True if random.random() <= 0.5 else False

    d = random.randint(2, 4)
    rects = get_div_rects(x0, y0, x1, y1, d, 2, 0.6)
    for rect in rects:
        x0, y0, x1, y1 = rect
        w0 = math.floor(x1 - x0)
        h0 = math.floor(y1 - y0)
        aa = 4
        if w0 <= aa * 2 or h0 <= aa * 2:
            continue

        aw = w0 - aa * 2
        ah = h0 - aa * 2
        if aw <= 10 or ah <= 10:
            continue

        col = 0.0
        if col_add_fg:
            v = bg_col
            col = bg_col - random.uniform(v * 0.05, v * 0.3)
        else:
            v = 1.0 - bg_col
            col = bg_col + random.uniform(v * 0.05, v * 0.3)

        w = math.floor(random.randint(3, 7) * aw / 10)
        h = math.floor(random.randint(3, 7) * ah / 10)
        px0 = x0 + aa + random.randint(0, (aw - w))
        py0 = y0 + aa + random.randint(0, (ah - h))

        # fill box
        pdb.gimp_image_select_rectangle(image, 2, px0, py0, w, h)
        gimp.set_foreground(col, col, col)
        pdb.gimp_edit_fill(layer, FOREGROUND_FILL)

    # load selection from channel
    pdb.gimp_selection_none(image)
    pdb.gimp_selection_load(channel)

    # remove channel
    pdb.gimp_image_remove_channel(image, channel)


def draw_scifi_box_fill_b(image, layer, spacing, bg_col, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 < area_chk or h0 < area_chk:
        return

    # save selection to channel
    channel = pdb.gimp_selection_save(image)

    aa = 8
    x0 += aa
    y0 += aa
    x1 -= aa
    y1 -= aa
    w0 = math.floor(x1 - x0)
    h0 = math.floor(y1 - y0)
    if w0 <= 0 or h0 <= 0:
        return

    col_add_fg = True if random.random() <= 0.5 else False

    d = random.randint(2, 3)
    rects = get_div_rects(x0, y0, x1, y1, d, 2, 0.6)
    for rect in rects:
        x0, y0, x1, y1 = rect
        w0 = math.floor(x1 - x0)
        h0 = math.floor(y1 - y0)
        if w0 <= 0 or h0 <= 0:
            continue

        d = random.randint(2, 3)
        nrects = get_div_rects(x0, y0, x1, y1, d, 2, 0.6)
        for rect in nrects:
            x0, y0, x1, y1 = rect
            aa = 3
            x0 += aa
            y0 += aa
            x1 -= aa
            y1 -= aa
            w = math.floor(x1 - x0)
            h = math.floor(y1 - y0)
            if w <= aa * 2 or h <= aa * 2:
                continue

            if random.random() <= 0.6:
                continue

            col = 0.0
            if col_add_fg:
                v = bg_col
                col = bg_col - random.uniform(v * 0.1, v * 0.75)
            else:
                v = 1.0 - bg_col
                col = bg_col + random.uniform(v * 0.1, v * 0.75)

            # fill box
            pdb.gimp_image_select_rectangle(image, 2, x0, y0, w, h)
            gimp.set_foreground(col, col, col)
            pdb.gimp_edit_fill(layer, FOREGROUND_FILL)

    # load selection from channel
    pdb.gimp_selection_none(image)
    pdb.gimp_selection_load(channel)

    # remove channel
    pdb.gimp_image_remove_channel(image, channel)


def draw_scifi_grid(image, layer, spacing, lcol, bg_col, lspc, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 < area_chk or h0 < area_chk:
        return

    xd = 12
    yd = 8
    px0 = x0 + xd
    px1 = x1 - xd
    py0 = y0 + yd
    py1 = y1 - yd

    gimp.set_foreground(lcol, lcol, lcol)
    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(5)

    y = py0 + 3.5
    while y < py1 + 3.5:
        pdb.gimp_paintbrush_default(layer, 4, [px0, y, px1, y])
        y = y + lspc

    gimp.set_foreground(bg_col, bg_col, bg_col)
    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(3)

    px0 = px0 - 3
    px1 = px1 + 3
    dv = (px1 - px0) / 4
    x = px0 + dv
    for i in range(3):
        x = px0 + (px1 - px0) * (i + 1) / 4
        pdb.gimp_paintbrush_default(layer, 4, [x, y0, x, y1])


def draw_scifi_angled_line(image, layer, spacing, lcol, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 < area_chk or h0 < area_chk:
        return

    px0 = x0 - spacing * 2
    px1 = x1 + spacing * 2
    py0 = y0 - spacing * 2
    py1 = y1 + spacing * 2
    w = px1 - px0
    h = py1 - py0

    aa = 10
    if w >= h:
        px1 = math.floor(px0 + random.randint(2, 6) * w / 10)
        px0 = math.floor(px0 + random.randint(2, 6) * w / 10)
        dx = aa
        dy = 0
    else:
        py1 = math.floor(py0 + random.randint(2, 6) * h / 10)
        py0 = math.floor(py0 + random.randint(2, 6) * h / 10)
        dx = 0
        dy = aa

    bsize = 2
    # bsize = random.randint(2, 3)
    gimp.set_foreground(lcol, lcol, lcol)
    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(bsize)

    for i in range(3):
        pdb.gimp_paintbrush_default(layer, 4, [px0, py0, px1, py1])
        px0 += dx
        px1 += dx
        py0 += dy
        py1 += dy


def draw_scifi_angled_line_b(image, layer, spacing, lcol, lw, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 <= area_chk or h0 <= area_chk:
        return

    ph0 = lw
    py0 = math.floor(y0 + random.randint(3, 5) * h0 / 8)
    py1 = py0 + ph0

    pw0 = w0 * 3 / 12
    px0 = x0 - spacing * 2
    px1 = x0 + pw0
    px2 = px1 + ph0

    px5 = x1 + spacing * 2
    px4 = x1 - pw0
    px3 = px4 - ph0
    if px2 > px3:
        px2, px3 = px3, px2

    if random.random() < 0.5:
        py0, py1 = py1, py0

    bsize = 3
    # bsize = random.randint(2, 3)
    gimp.set_foreground(lcol, lcol, lcol)
    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(bsize)
    pdb.gimp_paintbrush_default(layer, 12, [px0, py0, px1, py0,
                                            px2, py1, px3, py1,
                                            px4, py0, px5, py0])


def draw_scifi_angled_line_c(image, layer, spacing, lcol, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 <= area_chk or h0 <= area_chk:
        return

    px0 = math.floor(x0 - spacing * 2)
    py0 = math.floor(y0 + random.randint(2, 6) * h0 / 10)
    ang = 0
    if random.random() > 0.5:
        px0 = math.floor(x1 + spacing * 2)
        ang = 180

    if py0 <= (y0 + y1) / 2:
        add_ang = 45 if ang == 0 else -45
    else:
        add_ang = -45 if ang == 0 else 45

    dists = []
    d0 = math.floor(random.randint(3, 5) * w0 / 10)
    dists.append([d0, ang])
    d1 = math.floor((w0 if w0 <= h0 else h0) / 4)
    dists.append([d1, add_ang])
    dists.append([h0, add_ang])

    x, y = px0, py0
    ang = 0
    pnts = []
    pnts.append(x)
    pnts.append(y)
    for dt in dists:
        d, add_ang = dt
        ang += add_ang
        r = math.radians(ang)
        x = math.floor(x + d * math.cos(r))
        y = math.floor(y + d * math.sin(r))
        pnts.append(x)
        pnts.append(y)

    bsize = 3
    # bsize = random.randint(2, 3)
    gimp.set_foreground(lcol, lcol, lcol)
    pdb.gimp_context_set_brush("2. Hardness 100")
    pdb.gimp_context_set_brush_size(bsize)
    pdb.gimp_paintbrush_default(layer, len(pnts), pnts)


def draw_scifi_rivet(image, layer, spacing, rsize, rspc, rbg, area_chk):
    x0, y0, x1, y1, w0, h0 = get_scifi_draw_area(image, spacing)
    if w0 < area_chk or h0 < area_chk:
        return

    px0 = x0 + rspc
    py0 = y0 + rspc
    px1 = x1 - rspc - 1
    py1 = y1 - rspc - 1
    pnt_lst = [[px0, py0], [px1, py0], [px1, py1], [px0, py1]]

    if rbg:
        # draw rivet background
        col = (32.0 / 256.0)
        gimp.set_foreground(col, col, col)
        pdb.gimp_context_set_brush("2. Hardness 100")
        pdb.gimp_context_set_brush_size(rsize)

        for pnt in pnt_lst:
            x, y = pnt
            pdb.gimp_paintbrush_default(layer, 2, [x, y])

    # rivet circle fuzzy
    col = 1.0
    gimp.set_foreground(col, col, col)
    pdb.gimp_context_set_brush("2. Hardness 075")
    pdb.gimp_context_set_brush_size(rsize)

    for i in range(2):
        for pnt in pnt_lst:
            x, y = pnt
            pdb.gimp_paintbrush_default(layer, 2, [x, y])


def generate_scifi_texture(img, layer,
                           dmax, cntmax, spacing, borderradius,
                           rivet_enable, rivet_spc, rivet_size, rivet_bg,
                           merge_enable, seed, randomize):
    """Main func."""

    dmax = int(dmax)
    cntmax = int(cntmax)
    spacing = int(spacing)
    borderradius = int(borderradius)
    rivet_enable = True if int(rivet_enable) == 1 else False
    rivet_spc = int(rivet_spc)
    rivet_size = int(rivet_size)
    rivet_bg = True if int(rivet_bg) == 1 else False
    merge_enable = True if int(merge_enable) == 1 else False
    seed = int(seed)
    randomize = int(randomize)

    if randomize == 1:
        random.seed()
    else:
        random.seed(seed)

    w, h = img.width, img.height
    pdb.gimp_image_undo_group_start(img)
    old_color = gimp.get_foreground()
    old_brush = pdb.gimp_context_get_brush()

    bg_layer = gimp.Layer(img, "bg fill", w, h, RGBA_IMAGE, 100, NORMAL_MODE)
    box_layer = gimp.Layer(img, "box fill", w, h, RGBA_IMAGE, 100, NORMAL_MODE)
    line_layer = gimp.Layer(img, "line", w, h, RGBA_IMAGE, 100, NORMAL_MODE)
    rivet_layer = gimp.Layer(img, "rivet", w, h, RGBA_IMAGE, 100, NORMAL_MODE)

    bg_layer.fill(TRANSPARENT_FILL)
    box_layer.fill(TRANSPARENT_FILL)
    line_layer.fill(TRANSPARENT_FILL)
    rivet_layer.fill(TRANSPARENT_FILL)

    img.add_layer(bg_layer, 0)
    img.add_layer(box_layer, 0)
    img.add_layer(line_layer, 0)
    img.add_layer(rivet_layer, 0)

    # fill bg layer
    bg_col = 0.25
    pdb.gimp_selection_all(img)
    gimp.set_foreground(bg_col, bg_col, bg_col)
    bg_layer.fill(FOREGROUND_FILL)
    pdb.gimp_selection_none(img)

    # divide rect
    rects = []
    rects = div_rect(rects, 0, 0, w - 1, h - 1, dmax, 1, 0, cntmax, dmax)

    kind_cnt = 0
    # kind_lst = [4, 4, 4]
    kind_lst = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]

    gimp.progress_init("Draw rect...")

    for i, rect in enumerate(rects):
        bx0, by0, bx1, by1 = rect
        x0 = bx0 + spacing
        y0 = by0 + spacing
        x1 = bx1 - spacing
        y1 = by1 - spacing
        w0 = x1 - x0
        h0 = y1 - y0

        if w0 <= 0 or h0 <= 0 or x0 >= w or y0 >= h:
            continue

        pdb.gimp_image_select_round_rectangle(img, 2, x0, y0, w0, h0,
                                              borderradius, borderradius)

        if pdb.gimp_selection_is_empty(img) == 1:
            continue

        # box fill
        fillcol = bg_col + (24.0 / 256.0) + random.uniform(0, (80.0 / 256.0))
        gimp.set_foreground(fillcol, fillcol, fillcol)
        pdb.gimp_edit_fill(box_layer, FOREGROUND_FILL)

        kind = kind_lst[random.randint(0, len(kind_lst) - 1)]

        if kind == 0:
            # draw line
            col = 0.0 if random.random() <= 0.5 else 1.0
            cnt = random.randint(3, 8)
            ldir = 0 if random.random() < 0.5 else 1
            lspc = 12
            chk = 28
            draw_scifi_lines(img, line_layer, spacing,
                             col, lspc, ldir, cnt, chk)
        elif kind == 1:
            # draw box
            # col = (32.0 / 256.0)
            col_range = max([fillcol - (8.0 / 256.0), (8.0 / 256.0)])
            col = random.uniform(0, col_range)
            chk = 20
            draw_scifi_box(img, line_layer, spacing, col, chk)
        elif kind == 2:
            # draw box fill
            bspc = spacing + 8
            chk = 28
            draw_scifi_box_fill(img, line_layer, bspc, fillcol, chk)
        elif kind == 3:
            # draw box fill b
            bspc = spacing + 8
            chk = 28
            draw_scifi_box_fill_b(img, line_layer, bspc, fillcol, chk)
        elif kind == 4:
            # draw grid
            col = 0.0
            lspc = 12
            chk = 60
            draw_scifi_grid(img, line_layer, spacing, col, fillcol, lspc, chk)
        elif kind == 5:
            # draw angled line
            chk = 28
            draw_scifi_angled_line(img, line_layer, spacing, bg_col, chk)
        elif kind == 6:
            # draw angled line b
            lw = 12
            chk = lw * 4
            draw_scifi_angled_line_b(img, line_layer, spacing, bg_col, lw, chk)
        elif kind == 7:
            # draw angled line c
            lw = 12
            chk = lw * 4
            draw_scifi_angled_line_c(img, line_layer, spacing, bg_col, chk)

        if rivet_enable:
            # draw rivet
            chk = 36
            draw_scifi_rivet(img, rivet_layer, spacing,
                             rivet_size, rivet_spc, rivet_bg, chk)

        gimp.displays_flush()
        gimp.progress_update(float(i + 1) / len(rects))

    # merge layer
    if merge_enable:
        pdb.gimp_image_merge_down(img, box_layer, 1)
        pdb.gimp_image_merge_down(img, line_layer, 1)
        pdb.gimp_image_merge_down(img, rivet_layer, 1)
        next_layer = pdb.gimp_image_get_active_layer(img)
        next_layer.name = "scifi-bump"

    pdb.gimp_progress_end()

    pdb.gimp_selection_none(img)
    gimp.set_foreground(old_color)
    pdb.gimp_context_set_brush(old_brush)
    pdb.gimp_image_undo_group_end(img)
    gimp.displays_flush()
    # gimp.message("Done.")


register(
    "python-fu-generate-scifi-texture",  # proc_name
    "Generate Sci-Fi texture",           # info
    "Generate Sci-Fi bump mapping texture with Python-fu",  # help
    "mieki256",    # author
    "mieki256",    # copyright
    "2018/02/01",  # date
    "Sci-Fi texture 2",  # menu name, menu label
    "RGB*",        # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    # params
    [
        # (type, name, description, default [, extra])
        (PF_IMAGE,    "img",          "Input image",    None),
        (PF_DRAWABLE, "layer",        "Input drawable", None),
        (PF_SPINNER,  "dmax",         "Divide Max",     3, (1, 10, 1)),
        (PF_SPINNER,  "cntmax",       "Repeat",         4, (1, 10, 1)),
        (PF_SPINNER,  "spacing",      "Spacing",        2, (1, 10, 1)),
        (PF_SPINNER,  "borderradius", "Border radius",  2, (1, 10, 1)),
        (PF_TOGGLE,   "rivet_enable", "Draw rivet",     1),
        (PF_SPINNER,  "rivet_spc",    "Rivet spacing",  8, (1, 64, 1)),
        (PF_SPINNER,  "rivet_size",   "Rivet size",     9, (1, 64, 1)),
        (PF_TOGGLE,   "rivet_bg",     "Draw rivet bg",  0),
        (PF_TOGGLE,   "merge_enable", "Merge Layer",    1),
        (PF_INT,      "seed",         "Random seed",    42),
        (PF_TOGGLE,   "randomize",    "Randomize",      1)
    ],
    [],                           # return vals
    generate_scifi_texture,  # function name
    menu="<Image>/Filters/Render"
)

main()
