#!/usr/bin/env python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2018/02/07 19:12:45 +0900>

u"""
Random boxes with cairo(pycairo).

usage: Filter -> Render -> Random boxes pycairo

Author : mieki256
License : CC0 / Public Domain

testing environment :
* GIMP 2.8.22 Portable + Windows10 x64
* GIMP 2.8.16 + Ubuntu Linux 16.04 LTS

Changelog

version 0.0.2 2018/02/07 by mieki256
    * update : get_rgba_str()

version 0.0.1 2018/02/07 by mieki256
    * first release.

"""

from gimpfu import *    # NOQA
import cairo
import struct
import random
import math
import time


def get_rgba_str(src):
    """Convert cairo surface data to RGBA."""
    u = struct.Struct('=L')
    p = struct.Struct('>L')
    lmax = len(src) / 4
    rgba_buf = [None] * lmax
    for i in xrange(lmax):
        argb = u.unpack_from(src, i * 4)[0]
        rgba = ((argb & 0x00ffffff) << 8) | ((argb >> 24) & 0x0ff)
        rgba_buf[i] = p.pack(rgba)
        if i & 0x3fff == 0:
            gimp.progress_update(0.5 + 0.5 * float(i + 1) / lmax)

    return ''.join(rgba_buf)


def draw_by_cairo_box_fill(surface, imgw, imgh, cnt, wmin, wmax, hmin, hmax):
    """Draw by cairo."""
    ctx = cairo.Context(surface)

    ctx.set_antialias(cairo.ANTIALIAS_NONE)
    ctx.set_line_width(0.0)
    ctx.set_line_cap(cairo.LINE_CAP_SQUARE)
    ctx.set_line_join(cairo.LINE_JOIN_MITER)

    # fill boxes
    for i in xrange(cnt):
        c = random.uniform(0.0, 1.0)
        ctx.set_source_rgb(c, c, c)
        w = random.randint(wmin, wmax)
        h = random.randint(hmin, hmax)
        x = random.randint(0 - w, imgw - 1)
        y = random.randint(0 - h, imgh - 1)
        ctx.rectangle(x, y, w, h)
        ctx.fill()
        gimp.progress_update(0.5 * float(i + 1) / cnt)

    return surface


def draw_by_cairo_box_line(surface, imgw, imgh, cnt, lwidth,
                           wmin, wmax, hmin, hmax):
    """Draw by cairo."""
    ctx = cairo.Context(surface)

    ctx.set_antialias(cairo.ANTIALIAS_NONE)
    ctx.set_line_width(float(lwidth))
    # ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.set_line_cap(cairo.LINE_CAP_SQUARE)
    ctx.set_line_join(cairo.LINE_JOIN_MITER)

    # draw line boxes
    for i in xrange(cnt):
        c = random.uniform(0.0, 1.0)
        ctx.set_source_rgb(c, c, c)
        w = random.randint(wmin, wmax)
        h = random.randint(hmin, hmax)
        x = random.randint(0 - w, imgw - 1)
        y = random.randint(0 - h, imgh - 1)
        ctx.move_to(x, y)
        ctx.line_to(x + w, y)
        ctx.line_to(x + w, y + h)
        ctx.line_to(x, y + h)
        ctx.line_to(x, y)
        ctx.stroke()
        gimp.progress_update(0.5 * float(i + 1) / cnt)

    return surface


def python_fu_random_boxes_main(img, layer,
                                cnt, fill_enable, lwidth,
                                wmin, wmax, hmin, hmax,
                                randomize, seed):
    """Main func."""
    cnt = int(cnt)
    fill_enable = True if int(fill_enable) == 1 else False
    lwidth = float(lwidth)
    wmin = int(wmin)
    wmax = int(wmax)
    if wmin > wmax:
        wmax = wmin
    hmin = int(hmin)
    hmax = int(hmax)
    if hmin > hmax:
        hmax = hmin
    randomize = True if int(randomize) == 1 else False
    seed = int(seed)

    w, h = img.width, img.height

    if randomize:
        seed = math.floor(time.time())
    random.seed(seed)

    pdb.gimp_image_undo_group_start(img)

    layer = gimp.Layer(img, "boxes", w, h, RGBA_IMAGE, 100, NORMAL_MODE)
    layer.fill(TRANSPARENT_FILL)
    img.add_layer(layer, 0)

    gimp.progress_init("Drawing rect. seed = %d" % (seed))

    # draw cairo
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    if fill_enable:
        draw_by_cairo_box_fill(surface, w, h, cnt, wmin, wmax, hmin, hmax)
    else:
        draw_by_cairo_box_line(
            surface, w, h, cnt, lwidth, wmin, wmax, hmin, hmax)

    # transfer gimp layer
    src = surface.get_data()
    dst = get_rgba_str(src)
    rgn = layer.get_pixel_rgn(0, 0, w, h, True, True)
    rgn[0:w, 0:h] = str(dst)

    layer.flush()
    layer.merge_shadow()
    layer.update(0, 0, w, h)

    pdb.gimp_progress_end()
    pdb.gimp_image_undo_group_end(img)
    pdb.gimp_displays_flush()

    # gimp.message("Done.")


register(
    "python_fu_random_boxes",     # proc_name
    "Random boxes with cairo (pycairo)",  # info
    "Random boxes with cairo (pycairo)",  # help
    "mieki256",    # author
    "mieki256",    # copyright
    "2018/02/06",  # date
    "Random boxes pycairo",  # menu name, menu label
    "RGB*",      # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    # params
    [
        # (type, name, description, default [, extra])
        (PF_IMAGE,    "image", "Input Image", None),
        (PF_DRAWABLE, "layer", "Inpu Layer",  None),
        (PF_INT,      "cnt",         "Number of boxes", 512),
        (PF_TOGGLE,   "fill_enable", "Fill",            1),
        (PF_FLOAT,    "lwidth",      "Line width",      1.0),
        (PF_INT,      "wmin",        "box width min",   16),
        (PF_INT,      "wmax",        "box width max",   64),
        (PF_INT,      "hmin",        "box height min",  16),
        (PF_INT,      "hmax",        "box height max",  128),
        (PF_TOGGLE,   "randomize",   "Randomize",       1),
        (PF_INT,      "seed",        "Random seed",     42)
    ],
    # return vals
    [],
    python_fu_random_boxes_main,  # function name
    menu="<Image>/Filters/Render"
)

main()
