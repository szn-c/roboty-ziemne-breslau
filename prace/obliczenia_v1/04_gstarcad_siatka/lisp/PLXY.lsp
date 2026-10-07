;;; PLXY.lsp - eksport wierzcholkow JEDNEJ polilinii (LWPOLYLINE) do pliku tekstowego
;;; Uzycie: APPLOAD -> PLXY.lsp -> Zaladuj. Wpisz PLXY i wskaz polilinie.
;;; Plik "wierzcholki_polilinii.txt" powstaje w folderze rysunku (zapisz rysunek wczesniej!).
;;; Dwie kolumny rozdzielone tabulatorem: E (X) i N (Y). Bez naglowka. Wklej do Excela w komorke B2 arkusza Obrys.
(defun c:PLXY ( / e ed f fn k)
  (setq e (car (entsel "\nWskaz polilinie (LWPOLYLINE): ")))
  (if (and e (= (cdr (assoc 0 (entget e))) "LWPOLYLINE"))
    (progn
      (setq ed (entget e))
      (setq fn (strcat (getvar "DWGPREFIX") "wierzcholki_polilinii.txt"))
      (setq f (open fn "w") k 0)
      (foreach p ed
        (if (= (car p) 10)
          (progn
            (setq k (1+ k))
            (write-line (strcat (rtos (cadr p) 2 3) "\t" (rtos (caddr p) 2 3)) f))))
      (close f)
      (princ (strcat "\nZapisano " (itoa k) " wierzcholkow: " fn)))
    (princ "\nNie wskazano polilinii typu LWPOLYLINE."))
  (princ))
(princ "\nPLXY zaladowane. Wpisz PLXY.")
(princ)
