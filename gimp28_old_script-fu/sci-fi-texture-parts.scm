;
; Generate Sci-Fi bump mapping texture parts.
;
; require rectangle selection.
;
; usage :
; 1. Create new image.
; 2. Script-Fu -> Utils -> Sci-Fi texture parts
;
; tested : gimp 2.8.22
;
; License : CC0 / Public Domain
;
; ----------------------------------------
; Changelog
;
; version 0.0.2  2018/01/30 mieki256
;     - fix : brush name and size in GIMP 2.8
;
; version 0.0.1  2014/07/11 mieki256
;     - first release
;

(define
  (script-fu-scifi-tex-gen-parts image layer draw-type
                                 spacing rr
                                 line-color bg-color
                                 rivet-chk rivet-spc rivet-size rivet-bg-enable
                                 line-dir line-chk line-spc line-count
                                 randomize)

  (if (equal? randomize TRUE) (srand (realtime)) #f)

  (gimp-image-undo-group-start image)
  (if (equal? 0 (car (gimp-selection-bounds image))) (gimp-selection-all image) #f)

  (let* (
         (old-fg-color  (car (gimp-palette-get-foreground)))
         (old-brush (car (gimp-brushes-get-brush)))
         (width (car (gimp-image-width image)))
         (height (car (gimp-image-height image)))
         (bounds (gimp-selection-bounds image))
         (boundn (list-ref bounds 0))
         (bx0 (list-ref bounds 1))
         (by0 (list-ref bounds 2))
         (bx1 (list-ref bounds 3))
         (by1 (list-ref bounds 4))
         (bw0 (- bx1 bx0))
         (bh0 (- by1 by0))
         (a spacing)
         (x0 (+ bx0 a))
         (y0 (+ by0 a))
         (w0 (- bw0 (* a 2)))
         (h0 (- bh0 (* a 2)))
         )
    (if (or (<= w0 0) (<= h0 0) (>= x0 width) (>= y0 height))
      #f
      (if (equal? (car (gimp-selection-is-empty image)) FALSE)
        (begin
          (gimp-image-select-round-rectangle image 2 x0 y0 w0 h0 rr rr)

          (cond

           ; fill bg

           ((equal? draw-type 0)
            (begin
              (gimp-palette-set-foreground bg-color)
              (gimp-edit-fill layer FOREGROUND-FILL)))

           ; draw rivet

           ((equal? draw-type 1)
            (let* (
                   )
              (if (and (> w0 rivet-chk) (> h0 rivet-chk))
                (let* (
                       (px0 (+ x0 rivet-spc))
                       (py0 (+ y0 rivet-spc))
                       (px1 (- (+ x0 w0) (+ rivet-spc 1)))
                       (py1 (- (+ y0 h0) (+ rivet-spc 1)))
                       )
                  (if (equal? rivet-bg-enable TRUE)
                    (begin
                      ; rivet bg circle
                      ; (gimp-palette-set-foreground bg-color)
                      (gimp-palette-set-foreground '(32 32 32))

                      ; (gimp-brushes-set-brush "Circle (13)")
                      (gimp-context-set-brush "2. Hardness 100")
                      (gimp-context-set-brush-size rivet-size)

                      (gimp-paintbrush-default layer 2 (vector px0 py0))
                      (gimp-paintbrush-default layer 2 (vector px1 py0))
                      (gimp-paintbrush-default layer 2 (vector px1 py1))
                      (gimp-paintbrush-default layer 2 (vector px0 py1))
                      )
                    #f)
                  ; rivet circle fuzzy
                  (gimp-palette-set-foreground '(255 255 255))

                  ; (gimp-brushes-set-brush "Circle Fuzzy (11)")
                  (gimp-context-set-brush "2. Hardness 075")
                  (gimp-context-set-brush-size rivet-size)

                  (gimp-paintbrush-default layer 2 (vector px0 py0))
                  (gimp-paintbrush-default layer 2 (vector px1 py0))
                  (gimp-paintbrush-default layer 2 (vector px1 py1))
                  (gimp-paintbrush-default layer 2 (vector px0 py1))

                  (gimp-paintbrush-default layer 2 (vector px0 py0))
                  (gimp-paintbrush-default layer 2 (vector px1 py0))
                  (gimp-paintbrush-default layer 2 (vector px1 py1))
                  (gimp-paintbrush-default layer 2 (vector px0 py1))
                  )
                #f)))

           ; draw line

           ((equal? draw-type 2)
            (if (and (> w0 line-chk) (> h0 line-chk))
              (let* ((lc (car line-color))
                     (dv (if (< lc 128) line-spc (* line-spc 1.6)))
                     (dd 18)
                     (x1 (+ x0 w0))
                     (y1 (+ y0 h0))
                     (i 0))
                (gimp-palette-set-foreground line-color)

                ; (gimp-brushes-set-brush (if (< lc 128) "Circle (05)" "Circle (07)"))
                (gimp-context-set-brush "2. Hardness 100")
                (gimp-context-set-brush-size (if (< lc 128) 5 7))

                (if (equal? line-dir 0)
                  (let* (
                         (h1 (* h0 (/ (+ 30 (rand 50)) 100)))
                         (px0 (+ x0 dd (rand (/ w0 3))))
                         (py0 (+ y0 (- (rand (+ (- h0 h1) 16)) 8)))
                         (px1 (- x1 dd))
                         (py1 (+ py0 (* h0 0.4)))
                         (x px0)
                         )
                    (while (and (< i line-count) (< x px1))
                      (gimp-paintbrush-default layer 4 (vector x py0 x py1))
                      (set! x (+ x dv))
                      (set! i (+ i 1)))
                    )
                  (let* (
                         (w1 (* w0 (/ (+ 30 (rand 50)) 100)))
                         (px0 (+ x0 (- (rand (+ (- w0 w1) 16)) 8)))
                         (py0 (+ y0 dd (rand (/ h0 3))))
                         (px1 (+ px0 (* w0 0.4)))
                         (py1 (- y1 dd))
                         (y py0)
                         )
                    (while (and (< i line-count) (< y py1))
                      (gimp-paintbrush-default layer 4 (vector px0 y px1 y))
                      (set! y (+ y dv))
                      (set! i (+ i 1)))
                    )
                  )
                )
              #f)
            )

           ; draw grid

           ((equal? draw-type 3)
            (if (and (> w0 60) (> h0 60))
              (let* ((x1 (+ x0 w0))
                     (y1 (+ y0 h0))
                     (xd 12)
                     (yd 8)
                     (px0 (+ x0 xd))
                     (px1 (- x1 xd))
                     (py0 (+ y0 yd))
                     (py1 (- y1 yd))
                     )
                (gimp-palette-set-foreground line-color)

                ; (gimp-brushes-set-brush "Circle (05)")
                (gimp-context-set-brush "2. Hardness 100")
                (gimp-context-set-brush-size 5)

                (let* ((i 0) (y (+ py0 3.5)))
                  (while (< y (+ py1 3.5))
                    (gimp-paintbrush-default layer 4 (vector px0 y px1 y))
                    (set! y (+ y line-spc)))
                  )
                (gimp-palette-set-foreground bg-color)

                ; (gimp-brushes-set-brush "Circle (03)")
                (gimp-context-set-brush "2. Hardness 100")
                (gimp-context-set-brush-size 3)

                (let* ((i 0) (dv (/ w0 4)) (x (+ x0 dv)))
                  (while (< x px1)
                    (gimp-paintbrush-default layer 4 (vector x y0 x y1))
                    (set! x (+ x dv)))
                  )))
            )

           ; draw box

           ((equal? draw-type 4)
            (if (and (> w0 line-chk) (> h0 line-chk))
              (let* (
                     (w1 (* w0 0.4))
                     (h1 (* h0 0.4))
                     (aw (+ w1 (rand w1)))
                     (ah (+ h1 (rand h1)))
                     (x1 (+ x0 w0))
                     (y1 (+ y0 h0))
                     (px0 (+ x0 (- (rand (+ (- w0 aw) 16)) 8)))
                     (py0 (+ y0 (- (rand (+ (- h0 ah) 16)) 8)))
                     (px1 (+ px0 aw))
                     (py1 (+ py0 ah))
                     )
                (gimp-palette-set-foreground line-color)
                ; (gimp-brushes-set-brush "Circle (01)")
                (gimp-context-set-brush "2. Hardness 100")
                (gimp-context-set-brush-size 1)

                (gimp-paintbrush-default layer 10 (vector px0 py0 px1 py0 px1 py1 px0 py1 px0 py0))
                )
              #f)
            )

           ; draw angled line

           ((equal? draw-type 5)
            (if (and (> w0 line-chk) (> h0 line-chk))
              (let* (
                     (aa 12)
                     (x1 (- bx0 aa))
                     (x2 (+ bx1 aa))
                     (y1 (- by0 aa))
                     (y2 (+ by1 aa))
                     )
                (begin
                  (if (>= bw0 bh0)
                    (begin
                      (set! x1 (+ bx0 (/ (* (+ (rand 6) 2) bw0) 10.0)))
                      (set! x2 (+ bx0 (/ (* (+ (rand 6) 2) bw0) 10.0)))
                      )
                    (begin
                      (set! y1 (+ by0 (/ (* (+ (rand 6) 2) bh0) 10.0)))
                      (set! y2 (+ by0 (/ (* (+ (rand 6) 2) bh0) 10.0)))
                      )
                    )
                  (gimp-context-set-foreground bg-color)
                  ; (gimp-brushes-set-brush "Circle (03)")
                  (gimp-context-set-brush "2. Hardness 100")
                  (gimp-context-set-brush-size 2)
                  (gimp-paintbrush-default layer 4 (vector x1 y1 x2 y2))
                  )
                )
              #f)
            )
           )
          (gimp-palette-set-foreground old-fg-color)
          ; (gimp-brushes-set-brush old-brush)
          (gimp-context-set-brush old-brush)
          )
        #f)
      )
    )
  (gimp-image-undo-group-end image)
  (gimp-displays-flush)
  )

(script-fu-register
 "script-fu-scifi-tex-gen-parts"
 "Sci-Fi texture parts"
 "Generate Sci-Fi bump mapping txeture parts"
 "mieki256"
 "Copyright 2014"
 "2014-07-11"
 "RGB*"
 SF-IMAGE      "Image"         0
 SF-DRAWABLE   "Drawable"      0
 SF-OPTION     "Draw type"     '("Fill BG" "Rivet" "Line" "Grid" "Box" "Angled line")
 SF-ADJUSTMENT "Spacing"       '(2 0 64 1 2 0 1)
 SF-ADJUSTMENT "Border Radius" '(3 0 64 1 2 0 1)
 SF-COLOR      "Line color"    '(0 0 0)
 SF-COLOR      "BG color"      '(64 64 64)
 SF-ADJUSTMENT "Rivet enable width" '(26 0 2048 1 2 0 1)
 SF-ADJUSTMENT "Rivet space"        '(8 1 64 1 2 0 1)
 SF-ADJUSTMENT "Rivet size"         '(9 1 64 1 2 0 1)
 SF-TOGGLE     "Rivet BG fill"      FALSE
 SF-OPTION     "Line Dir"          '("x" "y")
 SF-ADJUSTMENT "Line enable width"  '(28 1 64 1 2 0 1)
 SF-ADJUSTMENT "Line space"         '(12 1 64 1 2 0 1)
 SF-ADJUSTMENT "Line count"         '(3 1 256 1 2 0 1)
 ; SF-VALUE      "Random seed"   "42"
 SF-TOGGLE     "Randomize"     TRUE
 )

(script-fu-menu-register
 "script-fu-scifi-tex-gen-parts"
 "<Image>/Script-Fu/Utils")

