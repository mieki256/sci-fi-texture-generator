;
; Makeup Sci-Fi bump mapping texture.
;
; usage:
; Script-Fu -> Utils -> Sci-Fi texture makeup
;
; License : CC0 / Public Domain
;
; ----------------------------------------
; Changelog
;
; version 0.0.2  2014/07/13 mieki256
;     - add option "Merge Layer"
;
; version 0.0.1  2014/07/06 mieki256
;     - first release
;

(define (script-fu-scifi-tex-make-up image layer merge-enable)
  (gimp-image-undo-group-start image)
  (let*
      (
       (width (car (gimp-image-width image)))
       (height (car (gimp-image-height image)))
       (g-layer (car (gimp-layer-copy layer TRUE)))
       (gd-layer (car (gimp-layer-copy layer TRUE)))
       (m-layer (car (gimp-layer-copy layer TRUE)))
       (l-layer (car (gimp-layer-copy layer TRUE)))
       (c-layer (car (gimp-layer-new image width height 1 "solid noise 0" 25 17)))
       (d-layer (car (gimp-layer-new image width height 1 "solid noise 1" 25 4)))
       (e-layer (car (gimp-layer-new image width height 1 "solid noise 2" 25 17)))
       (next-layer 0)
       )

    ; emboss
    (gimp-image-add-layer image m-layer -1)
    (plug-in-emboss 1 image m-layer 120 40 6 1)
    (gimp-layer-set-mode m-layer MULTIPLY-MODE)

    ; gauss and divide-mode
    (gimp-image-add-layer image gd-layer -1)
    (plug-in-gauss 1 image gd-layer 6 6 1)
    (gimp-layer-set-mode gd-layer DIVIDE-MODE)
    (gimp-layer-set-opacity gd-layer 50)

    ; gauss and softlight-mode
    (gimp-image-add-layer image g-layer -1)
    (plug-in-gauss 1 image g-layer 6 6 1)
    (gimp-layer-set-mode g-layer SOFTLIGHT-MODE)
    (gimp-layer-set-opacity g-layer 50)

    ; edge
    (gimp-image-add-layer image l-layer -1)
    (plug-in-edge 1 image l-layer 2 2 5)
    (gimp-invert l-layer)
    (gimp-layer-set-mode l-layer MULTIPLY-MODE)

    ; solid noise 2
    (gimp-image-add-layer image e-layer -1)
    (plug-in-solid-noise 1 image e-layer TRUE FALSE 3767556749 1 4 4)
    (gimp-colorize e-layer 200 35 10)
    (plug-in-hsv-noise 1 image e-layer 3 13 24 30) ; HSV noise
    
    ; solid noise 1
    (gimp-image-add-layer image d-layer -1)
    (plug-in-solid-noise 1 image d-layer TRUE FALSE 436305492 1 4 4)
    (gimp-colorize d-layer 126 28 0)
    (plug-in-rotate 1 image d-layer 2 FALSE) ; layer rotate 180
    
    ; solid noise 0
    (gimp-image-add-layer image c-layer -1)
    (plug-in-solid-noise 1 image c-layer TRUE FALSE 3442539593 1 4 4)
    (gimp-colorize c-layer 37 30 0)
    
    (if (equal? merge-enable TRUE)
        (begin
          (gimp-image-merge-down image m-layer 1)
          (gimp-image-merge-down image gd-layer 1)
          (gimp-image-merge-down image g-layer 1)
          (gimp-image-merge-down image l-layer 1)
          (gimp-image-merge-down image e-layer 1)
          (gimp-image-merge-down image d-layer 1)
          (gimp-image-merge-down image c-layer 1)
          (set! next-layer (car (gimp-image-get-active-layer image)))
          (gimp-layer-set-name next-layer "Mecha Texture")
          )
      #f)
    )
  
  (gimp-displays-flush)
  (gimp-image-undo-group-end image)
  )

(script-fu-register
 "script-fu-scifi-tex-make-up"
 "Sci-Fi texture makeup"
 "Makeup Sci-Fi bump mapping texture"
 "mieki256"
 "mieki256"
 "2014-07-06"
 "RGB*"
 SF-IMAGE    "Image"    0
 SF-DRAWABLE "Drawable" 0
 SF-TOGGLE   "Merge Layer"  TRUE
 )

(script-fu-menu-register
 "script-fu-scifi-tex-make-up"
 "<Image>/Script-Fu/Utils")

