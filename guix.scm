;;; Package recipe for linux-desktop-gremlin

;; Copyright (C) 2025  Thanos Apollo

;; Permission is hereby granted, free of charge, to any person obtaining a copy
;; of this software and associated documentation files (the "Software"), to deal
;; in the Software without restriction, including without limitation the rights
;; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
;; copies of the Software, and to permit persons to whom the Software is
;; furnished to do so, subject to the following conditions:

;; The above copyright notice and this permission notice shall be included in all
;; copies or substantial portions of the Software.

;; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
;; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
;; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
;; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
;; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
;; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
;; SOFTWARE.

;;; Commentary:

;; Example using guix shell:
;;   guix shell -f guix.scm -- linux-desktop-gremlin [character]

;;; Code:

(define-module (linux-desktop-gremlin-package)
  #:use-module (guix packages)
  #:use-module (guix gexp)
  #:use-module (guix utils)
  #:use-module (guix git)
  #:use-module (guix git-download)
  #:use-module (guix build-system copy)
  #:use-module ((guix licenses) #:prefix license:)
  #:use-module (gnu packages bash)
  #:use-module (gnu packages python)
  #:use-module (gnu packages qt))

(define-public linux-desktop-gremlin
  (package
    (name "linux-desktop-gremlin")
    (version "0.0.1")
    (source (local-file
             "." "linux-desktop-gremlin-checkout"
             #:recursive? #t
             #:select? (or (git-predicate (dirname (current-filename)))
                           (const #t))))
    (build-system copy-build-system)
    (arguments
     (list
      #:install-plan
      #~'(("ilgwg_desktop_gremlins.py" "share/linux-desktop-gremlin/")
          ("gremlin.py" "share/linux-desktop-gremlin/")
          ("sprite_manager.py" "share/linux-desktop-gremlin/")
          ("settings.py" "share/linux-desktop-gremlin/")
          ("movement_handler.py" "share/linux-desktop-gremlin/")
          ("hotspot_geometry.py" "share/linux-desktop-gremlin/")
          ("config_manager.py" "share/linux-desktop-gremlin/")
          ("config.json" "share/linux-desktop-gremlin/")
          ("spritesheet/" "share/linux-desktop-gremlin/spritesheet"
           #:include-regexp (".*"))
          ("sounds/" "share/linux-desktop-gremlin/sounds"
           #:include-regexp (".*")))
      #:modules '((guix build copy-build-system)
                  (guix build utils))
      #:phases
      #~(modify-phases %standard-phases
          (add-after 'install 'wrap-program
            (lambda* (#:key outputs inputs #:allow-other-keys)
              (use-modules (guix build utils))
              (let* ((out (assoc-ref outputs "out"))
                     (bin (string-append out "/bin"))
                     (share (string-append out "/share/linux-desktop-gremlin"))
                     (python (search-input-file inputs "/bin/python3"))
                     (bash (search-input-file inputs "/bin/bash"))
                     (pyside-site (string-append
                                   #$(this-package-input "python-pyside-6")
                                   "/lib/python3.11/site-packages"))
                     (shiboken-site (string-append
                                     #$(this-package-input "python-shiboken-6")
                                     "/lib/python3.11/site-packages")))
                (mkdir-p bin)
                ;; Create launcher script
                (call-with-output-file (string-append bin "/linux-desktop-gremlin")
                  (lambda (port)
                    (format port "#!~a
# Wrapper script for linux-desktop-gremlin
export GUIX_PYTHONPATH=~a:~a:$GUIX_PYTHONPATH
cd ~a
exec ~a ~a/ilgwg_desktop_gremlins.py \"$@\"~%"
                            bash
                            pyside-site
                            shiboken-site
                            share
                            python
                            share)))
                (chmod (string-append bin "/linux-desktop-gremlin") #o755)))))))
    (inputs
     (list bash-minimal python))
    (propagated-inputs
     ;; Python dependencies need to be propagated so they're available at runtime
     (list python-pyside-6 python-shiboken-6))
    (home-page "https://github.com/iluvgirlswithglasses/linux-desktop-gremlin")
    (synopsis "Animated desktop mascots for Linux")
    (description
     "Linux Desktop Gremlins brings animated character mascots to your Linux desktop.")
    (license license:expat)))

linux-desktop-gremlin
