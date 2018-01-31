;
; Mechanical bump texture generator
;
; ----------------------------------------
; Changelog
;
; version 0.0.2  2014/07/13 mieki256
;     - add option "Merge Layer"
;     - use mecha-bump-tex-gen-parts.scm
;
; version 0.0.1  2014/07/06 mieki256
;     - first release
;

; divide rect
(define (script-fu-mecha-bump-tex-gen-divide-rect vlst x y w h dmax cnt cntmax)
  (if (>= cnt cntmax)
      (cons (vector x y w h) vlst)
    (if (or (= cnt 0) (> h w))
        (let* ((bh (/ h (+ 1 (rand dmax)))) (yend (+ y h -1)))
          (let loop ((y0 y) (h0 bh))
            (set! h0 (* bh (+ (/ (rand 40) 100) 0.6)))
            (set! h0 (if (<= (+ y0 h0) yend) h0 (- yend y0)))
            (if (>= y0 yend)
                vlst
              (begin
                (set! vlst (script-fu-mecha-bump-tex-gen-divide-rect vlst x y0 w h0 dmax (+ cnt 1) cntmax))
                (loop (+ y0 h0) bh)))))
      (let* ((bw (/ w (+ 1 (rand dmax)))) (xend (+ x w -1)))
        (let loop ((x0 x) (w0 bw))
          (set! w0 (* bw (+ (/ (rand 40) 100) 0.6)))
          (set! w0 (if (<= (+ x0 w0) xend) w0 (- xend x0)))
          (if (>= x0 xend)
              vlst
            (begin
              (set! vlst (script-fu-mecha-bump-tex-gen-divide-rect vlst x0 y w0 h dmax (+ cnt 1) cntmax))
              (loop (+ x0 w0) bw)))))
      )))

(define (script-fu-mecha-bump-tex-gen image layer dmax cntmax spacing rr merge-enable)
  (srand (realtime))
  (gimp-image-undo-group-start image)
  (let* (
         (old-fg-color  (car (gimp-palette-get-foreground)))
         (old-brush (car (gimp-brushes-get-brush)))
         (width (car (gimp-image-width image)))
         (height (car (gimp-image-height image)))
         (bg-layer (car (gimp-layer-new image width height RGBA-IMAGE "bg fill" 100 NORMAL)))
         (n-layer (car (gimp-layer-new image width height RGBA-IMAGE "box fill" 100 NORMAL)))
         (l-layer (car (gimp-layer-new image width height RGBA-IMAGE "line" 100 NORMAL)))
         (r-layer (car (gimp-layer-new image width height RGBA-IMAGE "rivet" 100 NORMAL)))
         (next-layer 0)
         (c 64)
         (type-cnt 0)
         (type-list '(0 1 0 1 0 1 2))
         
         ; get divide rect
         (vlst (reverse (script-fu-mecha-bump-tex-gen-divide-rect '() 0 0 width height dmax 0 cntmax)))
         )
    ; gray BG fill
    (gimp-image-add-layer image bg-layer -1)
    (gimp-selection-all image)
    (gimp-palette-set-foreground (list c c c))
    (gimp-drawable-fill bg-layer FOREGROUND-FILL)
    (gimp-selection-none image)

    (gimp-image-add-layer image n-layer -1) ; add box fill layer
    (gimp-image-add-layer image l-layer -1) ; add line layer
    (gimp-image-add-layer image r-layer -1) ; add rivet layer
    (let loop ((ls vlst))
      (if (null? ls)
          #f
        (let* ((a spacing)
               (rect (car ls))
               (x0 (+ (vector-ref rect 0) a))
               (y0 (+ (vector-ref rect 1) a))
               (w0 (- (vector-ref rect 2) (* a 2)))
               (h0 (- (vector-ref rect 3) (* a 2)))
               (fc (+ c 24 (rand 80)))
               (lc (if (< (rand 100) 50) 0 255))
               (line-color (list lc lc lc))
               (line-count (+ (rand 4) 3))
               (dir-fg (if (< (rand 100) 50) 0 1))
               )
          (if (or (<= w0 0) (<= h0 0) (>= x0 width) (>= y0 height)) 
              #f
            (begin
              (gimp-image-select-round-rectangle image 2 x0 y0 w0 h0 rr rr)
              (if (equal? (car (gimp-selection-is-empty image)) FALSE)
                  (let* ((rivet-chk 36)
                         (line-chk 28)
                         (kind (list-ref type-list (modulo type-cnt (length type-list))))
                         )
                    
                    ; fill box
                    (gimp-palette-set-foreground (list fc fc fc))
                    (gimp-edit-fill n-layer FOREGROUND-FILL)

                    (cond
                     ((= kind 0)
                      ; draw line
                      (script-fu-mecha-bump-tex-gen-parts image l-layer 2 0 rr line-color (list fc fc fc)
                                                          rivet-chk 6 TRUE dir-fg line-chk 12 line-count)
                      )
                     ((= kind 1)
                      ; draw box
                      (script-fu-mecha-bump-tex-gen-parts image l-layer 4 0 rr '(32 32 32) (list fc fc fc)
                                                          rivet-chk 6 TRUE dir-fg line-chk 12 line-count)
                      )
                     (#t
                      ; draw grid
                      (script-fu-mecha-bump-tex-gen-parts image l-layer 3 0 rr '(0 0 0) (list fc fc fc)
                                                          rivet-chk 6 TRUE dir-fg line-chk 12 line-count)
                      )
                     )
                     
                    ; draw rivet
                    (script-fu-mecha-bump-tex-gen-parts image r-layer 1 0 rr '(255 255 255) (list fc fc fc)
                                                        rivet-chk 6 TRUE dir-fg line-chk 12 line-count)
                    
                    (set! type-cnt (+ type-cnt 1))
                    )
                #f)
              ))
          (loop (cdr ls)))))

    (if (equal? merge-enable TRUE)
        (begin
          ; layer merge
          (gimp-image-merge-down image n-layer 1)
          (gimp-image-merge-down image l-layer 1)
          (gimp-image-merge-down image r-layer 1)
          (set! next-layer (car (gimp-image-get-active-layer image)))
          (gimp-layer-set-name next-layer "Mecha Bump")
          )
      #f)
    
    (gimp-palette-set-foreground old-fg-color)
    (gimp-brushes-set-brush old-brush)
    )
  (gimp-selection-none image)
  (gimp-displays-flush)
  (gimp-image-undo-group-end image)
  )

(script-fu-register
 "script-fu-mecha-bump-tex-gen"
 "Mecha bump tex gen"
 "Mechanical bump texture generator"
 "mieki256"
 "Copyright 2014"
 "2014-07-06"
 "RGB*"
 SF-IMAGE      "Image"         0
 SF-DRAWABLE   "Drawable"      0
 SF-ADJUSTMENT "Divide max"    '(3 1 10 1 2 0 1)
 SF-ADJUSTMENT "Repeat"        '(4 1 10 1 2 0 1)
 SF-ADJUSTMENT "Spacing"       '(2 1 10 1 2 0 1)
 SF-ADJUSTMENT "Border Radius" '(2 1 10 1 2 0 1)
 SF-TOGGLE     "Merge Layer"   TRUE
 )

(script-fu-menu-register
 "script-fu-mecha-bump-tex-gen"
 "<Image>/Script-Fu/Utils")

