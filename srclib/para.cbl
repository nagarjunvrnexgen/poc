       IDENTIFICATION DIVISION.
       PROGRAM-ID. PARA.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-COUNTER           PIC 9(2) VALUE ZEROS.
       01  WS-MESSAGE           PIC X(30) VALUE SPACES.

       PROCEDURE DIVISION.
           DISPLAY "Starting COBOL program with loop and conditional...".

           PERFORM VARYING WS-COUNTER FROM 1 BY 1 UNTIL WS-COUNTER > 5
               DISPLAY "Current counter value: " WS-COUNTER
               IF WS-COUNTER = 3
                   MOVE "Reached the middle!" TO WS-MESSAGE
                   DISPLAY WS-MESSAGE
               ELSE
                   MOVE "Continuing loop..." TO WS-MESSAGE
                   DISPLAY WS-MESSAGE
               END-IF
           END-PERFORM.

           DISPLAY "Loop finished."
           DISPLAY "Program execution complete."

           STOP RUN.
