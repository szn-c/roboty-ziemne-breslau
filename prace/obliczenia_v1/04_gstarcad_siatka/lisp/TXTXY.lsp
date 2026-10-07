;;; TXTXY.lsp - eksport zaznaczonych napisow (TEXT, MTEXT) z polozeniem do pliku tekstowego
;;; Uzycie: APPLOAD -> TXTXY.lsp -> Zaladuj. Wpisz TXTXY, zaznacz napisy (np. pikiety wysokosciowe z mapy), Enter.
;;; Plik "teksty_xy.txt" powstaje w folderze rysunku. Trzy kolumny (tabulator): E (X), N (Y), tekst. Bez naglowka.
;;; Wklej do Excela w komorke A2 arkusza Pikiety.
(defun c:TXTXY ( / ss i ed f fn p s)
  (setq ss (ssget '((0 . "TEXT,MTEXT"))))
  (if ss
    (progn
      (setq fn (strcat (getvar "DWGPREFIX") "teksty_xy.txt"))
      (setq f (open fn "w"))
      (setq i 0)
      (repeat (sslength ss)
        (setq ed (entget (ssname ss i)))
        (setq p (cdr (assoc 10 ed)))
        (setq s (cdr (assoc 1 ed)))
        (if (and p s)
          (write-line (strcat (rtos (car p) 2 3) "\t" (rtos (cadr p) 2 3) "\t" s) f))
        (setq i (1+ i)))
      (close f)
      (princ (strcat "\nZapisano: " fn))))
  (princ))
(princ "\nTXTXY zaladowane. Wpisz TXTXY.")
(princ)
