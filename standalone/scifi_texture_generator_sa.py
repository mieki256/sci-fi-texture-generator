#!python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2022/04/05 08:02:35 +0900>
"""
Sci-Fi texture generator with pycairo.

Author: mieki256
License: CC0 / Public Domain
require: Python, tkinter, pycairo, Pillow

* Windows10 x64 21H2 + Python 2.7.18 32bit + pycairo 1.8.10 + Pillow 6.2.2
* Windows10 x64 21H2 + Python 3.9.12 64bit + pycairo 1.21.0 + Pillow 9.0.1
"""

import sys
import platform

if sys.version_info.major == 2:
    # Python 2.7
    import Tkinter as tk
    import tkMessageBox as mbox
    import tkFileDialog as fdlg
else:
    # Python 3.x
    import tkinter as tk
    import tkinter.messagebox as mbox
    import tkinter.filedialog as fdlg

from PIL import Image, ImageTk, ImageOps
import cairo
import math
import random
import time
import datetime


class DividedRect:

    @staticmethod
    def get_div_rects(x0, y0, x1, y1, d, v, sftv):
        new_rect = []
        x0 = math.floor(x0)
        y0 = math.floor(y0)
        x1 = math.floor(x1)
        y1 = math.floor(y1)
        w0 = x1 - x0
        h0 = y1 - y0
        if w0 <= 0 or h0 <= 0:
            return new_rect

        rw = w0
        rh = h0
        tw = rw
        th = rh

        ydivide = True if tw <= th else False
        if v == 0:
            ydivide = False
        elif v == 1:
            ydivide = True

        if ydivide:
            h = float(h0) / d
            s = h * sftv / 2.0
            lst = []
            lst.append(y0)
            i = 1
            while i < d:
                y = math.floor(y0 + h * i + random.uniform(-s, s))
                if y <= y1:
                    lst.append(y)
                i += 1
            lst.append(y1)
            lst = list(set(lst))
            lst.sort()
            for i in range(len(lst) - 1):
                new_rect.append([int(x0), int(lst[i]), int(x1), int(lst[i + 1])])
        else:
            w = float(w0) / d
            s = w * sftv / 2
            lst = []
            lst.append(x0)
            i = 1
            while i < d:
                x = math.floor(x0 + w * i + random.uniform(-s, s))
                if x <= x1:
                    lst.append(x)
                i += 1
            lst.append(x1)
            lst = list(set(lst))
            lst.sort()
            for i in range(len(lst) - 1):
                new_rect.append([int(lst[i]), int(y0), int(lst[i + 1]), int(y1)])
        return new_rect

    @staticmethod
    def div_rect(rects, x0, y0, x1, y1, v, cnt, cntmax, dmin, dmax):
        if cnt > cntmax:
            return rects

        if dmin >= dmax:
            d = dmin
        elif cnt == 0:
            d = dmax
        else:
            d = random.randint(dmin, dmax)

        new_rects = DividedRect.get_div_rects(x0, y0, x1, y1, d, v, 0.6)

        if cnt == cntmax:
            rects.extend(new_rects)
        else:
            for r in new_rects:
                x0, y0, x1, y1 = r
                rects = DividedRect.div_rect(rects, x0, y0, x1, y1,
                                             2, cnt + 1, cntmax, dmin, dmax)
        return rects

    @staticmethod
    def get_divide_rectangles(w, h, dmin, dmax, cntmax):
        """Divide rectangle."""
        if dmin > dmax:
            dmax = dmin

        x0 = 0
        y0 = 0
        x1 = w - 1
        y1 = h - 1
        rects = []
        rects = DividedRect.div_rect(rects, x0, y0, x1, y1, 1, 0, cntmax, dmin, dmax)
        return rects

    @staticmethod
    def init_random_seed(seed, randomize):
        if randomize or randomize == 1:
            # seed = math.floor(time.time())
            seed = int(time.time() * 100)
        random.seed(seed)
        return seed


class SciFiTex:

    PAT_KIND = [
        "All",  # 0
        "Rect only",  # 1
        "Lines",  # 2
        "Box",  # 3
        "Box fill",  # 4
        "Box fill b",  # 5
        "Grid",  # 6
        "Angle line a",  # 7
        "Angle line b",  # 8
        "Angle line c"  # 9
    ]

    RIVET_KIND = [
        "Box",
        "Circle"
    ]

    @staticmethod
    def draw_rounder_rectangle(ctx, x, y, w, h, ra):
        """Set sub path rounded rectangle."""
        deg = math.pi / 180.0
        ctx.new_sub_path()
        ctx.arc(x + w - ra, y + ra, ra, -90 * deg, 0 * deg)
        ctx.arc(x + w - ra, y + h - ra, ra, 0 * deg, 90 * deg)
        ctx.arc(x + ra, y + h - ra, ra, 90 * deg, 180 * deg)
        ctx.arc(x + ra, y + ra, ra, 180 * deg, 270 * deg)
        ctx.close_path()

    @staticmethod
    def set_rounder_rectangle(ctx, x0, y0, x1, y1, borderradius=0):
        """Set rouder rectangle path."""
        w, h = x1 - x0, y1 - y0
        r = borderradius
        d = r * 2
        if d > w or d > h:
            r = math.floor(float(min([w, h])) / 2.0)

        if r <= 0:
            ctx.rectangle(x0, y0, w, h)
        else:
            SciFiTex.draw_rounder_rectangle(ctx, x0, y0, w, h, r)

    @staticmethod
    def draw_rect(ctx, x0, y0, x1, y1, fillcol=None, linecol=None,
                  linewidth=None, borderradius=0):
        """Draw rectangle."""
        # w, h = x1 - x0, y1 - y0
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_width(linewidth if linewidth is not None else 0)

        if fillcol is not None:
            ctx.set_source_rgba(fillcol, fillcol, fillcol, 1.0)

        if fillcol is not None or linecol is not None:
            SciFiTex.set_rounder_rectangle(ctx, x0, y0, x1, y1, borderradius)

        if fillcol is not None:
            if linecol is None:
                ctx.fill()
                return
            else:
                ctx.fill_preserve()

        if linecol is not None:
            ctx.set_source_rgba(linecol, linecol, linecol, 1.0)
            ctx.stroke()

    @staticmethod
    def draw_lines(area, spacing, linecol, linespc, horizontal, count, area_chk):
        _, _, _, _, w, h = area
        if w < area_chk or h < area_chk:
            return None

        brushsize = 5
        if linecol >= 0.5:
            linespc = linespc * 1.6
            brushsize = 7
        dd = 18

        data = []
        if horizontal == 0:
            # Vertical line
            h1 = math.floor(h * random.uniform(0.3, 0.8))
            px0 = dd + random.randint(0, int(w / 3))
            py0 = random.randint(0, int((h - h1) + 16)) - 8
            px1 = w - dd
            py1 = py0 + (h * 0.4)
            x = px0
            for i in range(count):
                if x >= px1:
                    break
                data.append([x, py0, x, py1, brushsize, linecol])
                x = x + linespc
        else:
            # Horizontal Line
            w1 = math.floor(w * random.uniform(0.3, 0.8))
            px0 = random.randint(0, int((w - w1) + 16)) - 8
            py0 = dd + random.randint(0, int(h / 3))
            px1 = px0 + (w * 0.4)
            py1 = h - dd
            y = py0
            for i in range(count):
                if y >= py1:
                    break
                data.append([px0, y, px1, y, brushsize, linecol])
                y = y + linespc

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(ims)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        for x0, y0, x1, y1, brushsize, col in data:
            ctx.set_line_width(brushsize)
            ctx.set_source_rgba(col, col, col)
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
            ctx.stroke()

        return ims

    @staticmethod
    def draw_box(area, spacing, linecol, area_chk):
        _, _, _, _, w, h = area
        if w < area_chk or h < area_chk:
            return None

        w1 = math.floor(w * 0.4)
        h1 = math.floor(h * 0.4)
        aw = w1 + random.randint(0, w1)
        ah = h1 + random.randint(0, h1)
        px0 = random.randint(0, (w - aw) + 16) - 8
        py0 = random.randint(0, (h - ah) + 16) - 8

        brushsize = random.randint(1, 2)
        # bsize = 1

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(ims)
        ctx.set_source_rgba(linecol, linecol, linecol)
        ctx.set_line_width(brushsize)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        ctx.rectangle(px0, py0, aw, ah)
        ctx.stroke()

        return ims

    @staticmethod
    def draw_box_fill(area, spacing, bgcol, area_chk):
        x0, y0, x1, y1, sw, sh = area
        if sw < area_chk or sh < area_chk:
            return None

        col_add_fg = True if random.random() <= 0.5 else False

        d = random.randint(2, 4)
        rects = DividedRect.get_div_rects(0, 0, x1 - x0, y1 - y0, d, 2, 0.6)
        data = []
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
                v = bgcol
                col = bgcol - random.uniform(bgcol * 0.05, bgcol * 0.3)
            else:
                v = 1.0 - bgcol
                col = bgcol + random.uniform(v * 0.05, v * 0.3)

            w = math.floor(random.randint(3, 7) * aw / 10.0)
            h = math.floor(random.randint(3, 7) * ah / 10.0)
            px0 = x0 + aa + random.randint(0, int(aw - w))
            py0 = y0 + aa + random.randint(0, int(ah - h))
            data.append([px0, py0, w, h, col])

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_width(0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        for x, y, w, h, col in data:
            ctx.set_source_rgba(col, col, col)
            ctx.rectangle(x, y, w, h)
            ctx.fill()

        return ims

    @staticmethod
    def draw_box_fill_b(area, spacing, bg_col, area_chk):
        x0, y0, x1, y1, sw, sh = area
        if sw < area_chk or sh < area_chk:
            return None

        aa = 8
        x0 = math.floor(x0 + aa)
        y0 = math.floor(y0 + aa)
        x1 = math.floor(x1 - aa)
        y1 = math.floor(y1 - aa)
        w0 = x1 - x0
        h0 = y1 - y0
        if w0 <= 0 or h0 <= 0:
            return None

        col_add_fg = True if random.random() <= 0.5 else False

        # divide rect
        d = random.randint(2, 3)
        rects = DividedRect.get_div_rects(0, 0, x1 - x0, y1 - y0, d, 2, 0.6)
        fill_rects = []
        for rect in rects:
            x0, y0, x1, y1 = rect
            w0 = math.floor(x1 - x0)
            h0 = math.floor(y1 - y0)
            if w0 <= 0 or h0 <= 0:
                continue

            d = random.randint(2, 3)
            nrects = DividedRect.get_div_rects(x0, y0, x1, y1, d, 2, 0.6)
            for rect in nrects:
                x0, y0, x1, y1 = rect
                aa = 3
                x0 = math.floor(x0 + aa)
                y0 = math.floor(y0 + aa)
                x1 = math.floor(x1 - aa)
                y1 = math.floor(y1 - aa)
                w = math.floor(x1 - x0)
                h = math.floor(y1 - y0)
                if w <= aa * 2 or h <= aa * 2:
                    continue
                fill_rects.append([x0, y0, w, h])

        if len(fill_rects) <= 0:
            return None

        # colors setting
        col_cnt = 0
        cols = []
        while col_cnt == 0:
            col_cnt = 0
            cols = []
            for i in range(len(fill_rects)):
                if random.random() <= 0.6:
                    cols.append(bg_col)
                else:
                    if col_add_fg:
                        v = bg_col
                        col = bg_col - random.uniform(v * 0.1, v * 0.5)
                    else:
                        v = 1.0 - bg_col
                        col = bg_col + random.uniform(v * 0.1, v * 0.5)
                    cols.append(col)
                    col_cnt += 1

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_width(0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        for i, rect in enumerate(fill_rects):
            x, y, w, h = rect
            col = cols[i]
            ctx.set_source_rgba(col, col, col)
            ctx.rectangle(x, y, w, h)
            ctx.fill()

        return ims

    @staticmethod
    def draw_grid(area, spacing, fgcol, bgcol, linespc, area_chk):
        x0, y0, x1, y1, sw, sh = area
        if sw < area_chk or sh < area_chk:
            return None

        count = random.randint(3, 6)

        data = []
        brushsize = 5
        xd, yd = 12, 8
        px0, py0 = xd, yd
        px1, py1 = sw - xd, sh - yd
        y = py0 + 3.5
        while y < py1 + 3.5:
            data.append([px0, y, px1, y, brushsize, fgcol])
            y = y + linespc

        brushsize = 3
        px0 = px0 - 3
        px1 = px1 + 3
        pw = px1 - px0
        dd = float(pw) / count
        x = px0 + dd
        for i in range(count - 1):
            data.append([x, 0, x, sh, brushsize, bgcol])
            x = x + dd

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        for x0, y0, x1, y1, brushsize, col in data:
            ctx.set_line_width(brushsize)
            ctx.set_source_rgba(col, col, col)
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
            ctx.stroke()

        return ims

    @staticmethod
    def draw_angled_line(area, spacing, fgcol, area_chk):
        x0, y0, x1, y1, sw, sh = area
        if sw < area_chk or sh < area_chk:
            return None

        px0 = -spacing * 2
        px1 = sw + spacing * 2
        py0 = -spacing * 2
        py1 = sh + spacing * 2
        w = px1 - px0
        h = py1 - py0

        count = 3
        aa = 10
        if w >= h:
            px1 = math.floor(px0 + random.randint(2, 6) * w / 10)
            px0 = math.floor(px0 + random.randint(2, 6) * w / 10)
            dx, dy = aa, 0
        else:
            py1 = math.floor(py0 + random.randint(2, 6) * h / 10)
            py0 = math.floor(py0 + random.randint(2, 6) * h / 10)
            dx, dy = 0, aa

        brushsize = 2
        # brushsize = random.randint(2, 3)

        data = []
        for i in range(count):
            data.append([px0, py0, px1, py1])
            px0 += dx
            px1 += dx
            py0 += dy
            py1 += dy

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        ctx.set_line_width(brushsize)
        ctx.set_source_rgba(fgcol, fgcol, fgcol)
        for x0, y0, x1, y1 in data:
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
            ctx.stroke()

        return ims

    @staticmethod
    def draw_angled_line_b(area, spacing, fgcol, lw, area_chk):
        x0, y0, x1, y1, sw, sh = area
        if sw <= area_chk or sh <= area_chk:
            return None

        ph0 = lw
        py0 = math.floor(random.randint(3, 5) * sh / 8)
        py1 = py0 + ph0

        pw0 = sw * 3 / 12
        px0 = -spacing * 2
        px1 = pw0
        px2 = px1 + ph0

        px5 = sw + spacing * 2
        px4 = sw - pw0
        px3 = px4 - ph0
        if px2 > px3:
            px2, px3 = px3, px2

        if random.random() < 0.5:
            py0, py1 = py1, py0

        brushsize = 3
        # brushsize = random.randint(2, 3)

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        ctx.set_line_width(brushsize)
        ctx.set_source_rgba(fgcol, fgcol, fgcol)
        ctx.move_to(px0, py0)
        ctx.line_to(px1, py0)
        ctx.line_to(px2, py1)
        ctx.line_to(px3, py1)
        ctx.line_to(px4, py0)
        ctx.line_to(px5, py0)
        ctx.stroke()

        return ims

    @staticmethod
    def draw_angled_line_c(area, spacing, fgcol, area_chk):
        _, _, _, _, sw, sh = area
        if sw <= area_chk or sh <= area_chk:
            return None

        px0 = math.floor(-spacing * 2)
        py0 = math.floor(random.randint(2, 6) * sh / 10)
        ang = 0
        if random.random() > 0.5:
            px0 = math.floor(sw + spacing * 2)
            ang = 180

        if py0 <= sh / 2:
            add_ang = 45 if ang == 0 else -45
        else:
            add_ang = -45 if ang == 0 else 45

        dists = []
        d0 = math.floor(random.randint(3, 5) * sw / 10)
        dists.append([d0, ang])
        d1 = math.floor((sw if sw <= sh else sh) / 4)
        dists.append([d1, add_ang])
        dists.append([sh, add_ang])

        x, y = px0, py0
        ang = 0
        pnts = []
        pnts.append([x, y])
        for dt in dists:
            d, add_ang = dt
            ang += add_ang
            r = math.radians(ang)
            x = math.floor(x + d * math.cos(r))
            y = math.floor(y + d * math.sin(r))
            pnts.append([x, y])

        brushsize = 3
        # brushsize = random.randint(2, 3)

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        ctx.set_line_width(brushsize)
        ctx.set_source_rgba(fgcol, fgcol, fgcol)
        x, y = pnts.pop(0)
        ctx.move_to(x, y)
        for x, y in pnts:
            ctx.line_to(x, y)
        ctx.stroke()

        return ims

    @staticmethod
    def draw_rivet_box(area, rivetsize, rivetspc, chk):
        _, _, _, _, sw, sh = area
        if sw < chk or sh < chk:
            return None

        px0 = math.floor(rivetspc / 2)
        py0 = math.floor(rivetspc)
        px1 = math.floor(sw - rivetspc / 2)
        py1 = math.floor(sh - rivetspc - 1)
        place_list = [[px0, py0], [px1, py0], [px1, py1], [px0, py1]]

        # rivet box
        col = 0.0
        w = max([2, math.floor(rivetsize / 4)])
        h = rivetsize
        data = []
        for x, y in place_list:
            x0 = x - math.floor(w / 2.0)
            y0 = y - math.floor(h / 2.0)
            data.append([x0, y0, w, h])

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        ctx.set_line_width(0)
        ctx.set_source_rgba(col, col, col)
        for x, y, w, h in data:
            ctx.rectangle(x, y, w, h)
            ctx.fill()

        return ims

    @staticmethod
    def draw_rivet(area, bgcol, rivetsize, rivetspc, rivet_h, bg_enable, chk):
        x0, y0, x1, y1, sw, sh = area
        if sw < chk or sh < chk:
            return

        height_max = (rivet_h / 256.0)

        px0 = math.floor(rivetspc)
        py0 = math.floor(rivetspc)
        px1 = math.floor(sw - rivetspc - 1)
        py1 = math.floor(sh - rivetspc - 1)
        place_lst = [[px0, py0], [px1, py0], [px1, py1], [px0, py1]]

        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
        ctx = cairo.Context(ims)
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
        ctx.set_line_join(cairo.LINE_JOIN_MITER)
        ctx.set_line_width(0)

        if bg_enable:
            # fill rivet background
            ctx.set_source_rgba(bgcol, bgcol, bgcol)
            r = rivetsize / 2.0 + 3.0
            for x, y in place_lst:
                ctx.arc(x, y, r, 0, 2 * math.pi)
                ctx.fill()

            # bgcol = (32.0 / 256.0)
            bgcol = max([0.0, (bgcol - height_max)])
            ctx.set_source_rgba(bgcol, bgcol, bgcol)
            r = rivetsize / 2.0 + 1.0
            for x, y in place_lst:
                ctx.arc(x, y, r, 0, 2 * math.pi)
                ctx.fill()

        # rivet circle fuzzy
        rr = rivetsize / 2.0
        cx = rr
        while cx >= 1.0:
            col = bgcol + (math.sqrt(rr * rr - cx * cx) * height_max / rr)
            col = min([1.0, col])
            ctx.set_source_rgba(col, col, col)
            for x, y in place_lst:
                ctx.arc(x, y, cx, 0, 2 * math.pi)
                ctx.fill()
            cx = cx - 1.0

        return ims

    @staticmethod
    def generate(imgw, imgh, rects, spc, borderradius,
                 rivet_enable, rivet_spc, rivet_size, rivet_h, rivet_bg, rivet_type,
                 fill_col=None, drawtype="All", bordercol=64):
        """Fill rectangles."""

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, imgw, imgh)
        ctx = cairo.Context(surface)

        # fill backgorund
        bg_col = min([1.0, (float(bordercol) / 256.0)])
        # bg_col = 0.25
        x0, y0 = 0, 0
        x1, y1 = imgw - 1, imgh - 1
        SciFiTex.draw_rect(ctx, x0, y0, x1, y1, bg_col, None, None, 0)

        pat_kind_lst = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]

        for rect in rects:
            bx0, by0, bx1, by1 = rect
            x0 = math.floor(bx0 + spc)
            y0 = math.floor(by0 + spc)
            x1 = math.floor(bx1 - spc)
            y1 = math.floor(by1 - spc)
            w0 = x1 - x0
            h0 = y1 - y0

            if w0 <= 0 or h0 <= 0 or x0 >= imgw or y0 >= imgh:
                continue

            col = fill_col
            if col is None:
                col = 0.25 + random.uniform((24.0 / 256.0), (80.0 / 256.0))

            SciFiTex.draw_rect(ctx, x0, y0, x1, y1, col, None, None, borderradius)

            if drawtype == "Rect only":
                continue

            kind = drawtype
            if drawtype == "All":
                idx = pat_kind_lst[random.randint(0, len(pat_kind_lst) - 1)] + 2
                kind = SciFiTex.PAT_KIND[idx]

            # draw pattern
            area = (x0, y0, x1, y1, int(w0), int(h0))
            newsurf = None
            rsurf = None

            if kind == "Lines":
                # draw lines
                fgcol = 0.0 if random.random() <= 0.5 else random.uniform(col * 1.05, col * 1.2)
                fgcol = min([fgcol, 1.0])
                count = random.randint(3, 8)
                horizontal = False if random.random() < 0.5 else True
                linespc = 12
                chk = 28
                newsurf = SciFiTex.draw_lines(
                    area, spc, fgcol, linespc, horizontal, count, chk)
            elif kind == "Box":
                # draw box
                # col = (32.0 / 256.0)
                fgcol = col - random.uniform(col * 0.3, col * 0.7)
                fgcol = min([max([0.0, fgcol]), 1.0])
                chk = 20
                newsurf = SciFiTex.draw_box(area, spc, fgcol, chk)
            elif kind == "Box fill":
                # draw box fill
                bspc = spc + 8
                newsurf = SciFiTex.draw_box_fill(area, bspc, col, 28)
            elif kind == "Box fill b":
                # draw box fill b
                bspc = spc + 8
                newsurf = SciFiTex.draw_box_fill_b(area, bspc, col, 28)
            elif kind == "Grid":
                # draw grid
                newsurf = SciFiTex.draw_grid(area, spc, 0.0, col, 12, 60)
            elif kind == "Angle line a":
                # draw angled line a
                newsurf = SciFiTex.draw_angled_line(area, spc, bg_col, 28)
            elif kind == "Angle line b":
                # draw angled line b
                newsurf = SciFiTex.draw_angled_line_b(area, spc, bg_col, 12, 12 * 4)
            elif kind == "Angle line c":
                # draw angled line c
                newsurf = SciFiTex.draw_angled_line_c(area, spc, bg_col, 12 * 4)

            if newsurf is not None:
                ctx.save()
                SciFiTex.set_rounder_rectangle(ctx, x0, y0, x1, y1, borderradius)
                ctx.clip()
                ctx.set_source_surface(newsurf, x0, y0)
                ctx.paint()
                ctx.restore()
                newsurf.finish()

            if rivet_enable:
                # draw rivet
                if rivet_type == "Box":
                    rsurf = SciFiTex.draw_rivet_box(area, rivet_size, rivet_spc, 64)
                elif rivet_type == "Circle":
                    rsurf = SciFiTex.draw_rivet(area, col, rivet_size,
                                                rivet_spc, rivet_h, rivet_bg, 36)

                if rsurf is not None:
                    ctx.save()
                    SciFiTex.set_rounder_rectangle(ctx, x0, y0, x1, y1, borderradius)
                    ctx.clip()
                    ctx.set_source_surface(rsurf, x0, y0)
                    ctx.paint()
                    ctx.restore()
                    rsurf.finish()

        return surface


class MyApp(tk.Tk, object):
    """MyApp class."""

    IMG_W, IMG_H = 512, 512
    # IMG_W, IMG_H = 1024, 1024

    WIDGET_LIST = [
        ["Spinbox", "imgsize", "Image size (pixel)", 512, 256, 2048, 256],
        ["Spinbox", "dmin", "Divide min", 1, 1, 10, 1],
        ["Spinbox", "dmax", "Divide max", 3, 1, 10, 1],
        ["Spinbox", "cntmax", "Repeat", 4, 1, 10, 1],
        ["Spinbox", "spc", "Spacing", 2, 0, 16, 1],
        ["Spinbox", "borderradius", "Border radius", 2, 0, 16, 1],
        ["Checkbutton", "rivet_enable", "Draw rivet", True],
        ["OptionMenu", "rivet_type", "Rivet type", 0, SciFiTex.RIVET_KIND],
        ["Checkbutton", "rivet_bg", "Draw rivet bg", False],
        ["Spinbox", "rivet_spc", "Rivet spacing", 8, 1, 64, 1],
        ["Spinbox", "rivet_size", "Rivet size", 9, 1, 64, 1],
        ["Spinbox", "rivet_h", "Rivet height", 12, 1, 255, 1],
        ["Checkbutton", "colrandomize", "Fill color randomize", True],
        ["Spinbox", "fillcol", "Fill color", 160, 0, 160, 1],
        ["Spinbox", "bordercol", "Border color", 64, 0, 255, 1],
        ["Checkbutton", "randomize", "Randomize", True],
        ["Entry", "seed", "Random seed", 42],
        ["OptionMenu", "drawtype", "Draw type", 0, SciFiTex.PAT_KIND]
    ]

    def __init__(self):
        super(MyApp, self).__init__()
        # self.geometry("{}x{}".format(cv.W, cv.H))
        self.title("Sci-Fi texture generator with pycairo (Python %s)" % platform.python_version())

        self.reserve_param_variable()
        self.reset_param()

        self.zoomfit = False

        frm = tk.Frame(self)
        frm.pack(side=tk.LEFT, anchor=tk.NW)

        self.frmr = tk.Frame(self)
        self.frmr.pack(expand=1, fill=tk.BOTH)
        self.frmr.rowconfigure(1, weight=1)
        self.frmr.columnconfigure(0, weight=1)

        self.frmvb = tk.Frame(self.frmr)
        self.frmvb.grid(row=0, column=0, sticky=tk.W)

        vb0 = tk.Button(self.frmvb, text="View Fit", command=lambda: self.set_zoomfit())
        vb1 = tk.Button(self.frmvb, text="View 1:1", command=lambda: self.set_zoomfull())
        vb0.pack(side=tk.LEFT, padx=4, ipadx=8)
        vb1.pack(side=tk.LEFT, padx=4, ipadx=8)

        self.frmc = tk.Frame(self.frmr)
        self.frmc.grid(row=1, column=0, sticky=tk.N + tk.S + tk.W + tk.E)
        self.frmc.rowconfigure(0, weight=1)
        self.frmc.columnconfigure(0, weight=1)

        # reserve canvas
        _w = self.IMG_W + 16
        _h = self.IMG_H + 16
        self.canvas = tk.Canvas(self.frmc, width=_w, height=_h, bg="#cccccc")
        self.canvas.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

        # create Scrollbar
        self.xbar = tk.Scrollbar(self.frmc, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.ybar = tk.Scrollbar(self.frmc, orient=tk.VERTICAL, command=self.canvas.yview)
        self.xbar.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.ybar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.canvas.config(xscrollcommand=self.xbar.set)
        self.canvas.config(yscrollcommand=self.ybar.set)

        # set drag scroll
        self.canvas.bind("<ButtonPress-1>", lambda e: self.canvas.scan_mark(e.x, e.y))
        self.canvas.bind("<B1-Motion>", lambda e: self.canvas.scan_dragto(e.x, e.y, gain=1))

        # reserve button
        btnfrm = tk.Frame(frm)
        btnfrm.grid(row=0, column=0, columnspan=2)

        b1 = tk.Button(btnfrm, text="Generate", height=3, command=self.clicked_generate)
        b2 = tk.Button(btnfrm, text="Save Image", command=self.clicked_save_button, padx=8)
        b3 = tk.Button(btnfrm, text="Reset Parameter", command=self.clicked_reset_button, padx=8)
        b4 = tk.Button(btnfrm, text="Exit", command=self.clicked_exit_button, padx=8)

        b1.grid(row=0, column=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=3, pady=3)
        b2.grid(row=1, column=0, padx=4, pady=4)
        b3.grid(row=1, column=1, padx=4, pady=4)
        b4.grid(row=1, column=2, padx=4, pady=4)

        # create widget and layout
        r = 1
        for d in self.WIDGET_LIST:
            kind, name, lbl, = d[0], d[1], d[2]
            if kind == "Spinbox":
                fromv, tov, incv = d[4], d[5], d[6]
                tk.Label(frm, text=lbl).grid(row=r, column=0, sticky=tk.W, padx=8)
                s = tk.Spinbox(frm, textvariable=self.param[name],
                               from_=fromv, to=tov, increment=incv, width=6)
                s.grid(row=r, column=1, sticky=tk.W)
            elif kind == "Checkbutton":
                c = tk.Checkbutton(frm, variable=self.param[name], text=lbl)
                c.grid(row=r, column=0, columnspan=2)
            elif kind == "Entry":
                tk.Label(frm, text=lbl).grid(row=r, column=0, sticky=tk.W, padx=8)
                e = tk.Entry(frm, textvariable=self.param[name], width=24)
                e.grid(row=r, column=1, sticky=tk.W)
            elif kind == "OptionMenu":
                lst = d[4]
                tk.Label(frm, text=lbl).grid(row=r, column=0, sticky=tk.W, padx=8)
                tk.OptionMenu(frm, self.param[name], *lst).grid(row=r, column=1, sticky=tk.W)
            else:
                print("Error: not found param type. [%s]" % kind)
            r = r + 1

        # draw canvas
        self.generate_image()

    def reserve_param_variable(self):
        self.param = {}
        for d in self.WIDGET_LIST:
            kind, name = d[0], d[1]
            if kind == "Spinbox":
                self.param[name] = tk.IntVar(self)
            elif kind == "Checkbutton":
                self.param[name] = tk.BooleanVar(self)
            elif kind == "Entry" or kind == "OptionMenu":
                self.param[name] = tk.StringVar(self)
            else:
                print("Error: not found param type. [%s]" % kind)

    def reset_param(self):
        """Reset parameter."""
        for d in self.WIDGET_LIST:
            kind, name, v = d[0], d[1], d[3]
            if kind == "Spinbox" or kind == "Checkbutton" or kind == "Entry":
                self.param[name].set(v)
            elif kind == "OptionMenu":
                lst = d[4]
                self.param[name].set(lst[v])
            else:
                print("Error: not found param type. [%s]" % kind)

    def conv_surface_to_pil_image(self, surface):
        """Convert pycairo surface to PIL Image."""
        w, h = surface.get_width(), surface.get_height()
        m = surface.get_data()

        if sys.version_info.major == 2:
            # Python 2.7
            im = Image.frombuffer("RGBA", (w, h), m, "raw", "BGRA", 0, 1)
        else:
            # Python 3.x
            im = Image.frombuffer("RGBA", (w, h), m, "raw", "RGBA", 0, 1)

            # BGRA -> RGBA
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))

        return im

    def generate_image(self):
        """Set image to Tk canvas."""
        # get parameter
        imgsize = int(self.param["imgsize"].get())
        w, h = imgsize, imgsize
        dmin = int(self.param["dmin"].get())
        dmax = int(self.param["dmax"].get())
        cntmax = int(self.param["cntmax"].get())
        spc = int(self.param["spc"].get())
        borderradius = int(self.param["borderradius"].get())

        seed = int(self.param["seed"].get())
        randomize = self.param["randomize"].get()
        colrandomize = self.param["colrandomize"].get()
        fillcol = None if colrandomize else (float(self.param["fillcol"].get()) / 256.0)
        bordercol = int(self.param["bordercol"].get())
        drawtype = self.param["drawtype"].get()

        rivet_enable = self.param["rivet_enable"].get()
        rivet_bg = self.param["rivet_bg"].get()
        rivet_type = self.param["rivet_type"].get()
        rivet_spc = int(self.param["rivet_spc"].get())
        rivet_size = int(self.param["rivet_size"].get())
        rivet_h = int(self.param["rivet_h"].get())

        nseed = DividedRect.init_random_seed(seed, randomize)
        self.param["seed"].set("%d" % nseed)

        rects = DividedRect.get_divide_rectangles(w, h, dmin, dmax, cntmax)

        self.nsurf = SciFiTex.generate(w, h, rects, spc, borderradius,
                                       rivet_enable, rivet_spc, rivet_size, rivet_h,
                                       rivet_bg, rivet_type, fillcol, drawtype, bordercol)

        self.im = self.conv_surface_to_pil_image(self.nsurf)
        self.set_image()

    def set_image(self):
        if self.zoomfit:
            # view fit
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            self.im_pad = ImageOps.pad(self.im, (cw - 20, ch - 20), method=Image.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(image=self.im_pad)
        else:
            # view 1:1
            self.photo_image = ImageTk.PhotoImage(self.im)

        self.canvas.create_image(8, 8, image=self.photo_image, anchor=tk.NW)

        # set scroll region
        w = self.photo_image.width()
        h = self.photo_image.height()
        self.region = (0, 0, w + 16, h + 16)
        self.canvas.config(scrollregion=self.region)

    def save_image(self):
        """Save image."""
        n = datetime.datetime.now()
        initfname = "output_%s" % n.strftime("%Y%m%d_%H%M%S")
        # initfname = "output"

        filename = fdlg.asksaveasfilename(
            initialdir="./",
            initialfile=initfname,
            defaultextension=".png",
            filetypes=[("PNG", ".png"), ("Bitmap", ".bmp"), ("All Files", ".*")]
        )
        if filename:
            # save png image with pil
            self.im.convert("RGB").save(filename)
            mbox.showinfo("Save image", "Save %s" % filename)

    def clicked_generate(self):
        """Generate button clicked."""
        self.generate_image()

    def clicked_reset_button(self):
        """Reset button clicked."""
        self.reset_param()

    def clicked_save_button(self):
        """Save image button clicked."""
        self.save_image()

    def clicked_exit_button(self):
        """Exit button clicked."""
        if mbox.askyesno("Exit", "Are You Sure You Want to Exit?"):
            self.destroy()
            # sys.exit()

    def set_zoomfit(self):
        """Set view zoom fit."""
        self.zoomfit = True
        self.set_image()

    def set_zoomfull(self):
        """Set view zoom 1:1."""
        self.zoomfit = False
        self.set_image()

    def run(self):
        """Start main loop."""
        self.mainloop()


def main():
    """Main."""
    app = MyApp()
    app.run()


if __name__ == "__main__":
    main()
