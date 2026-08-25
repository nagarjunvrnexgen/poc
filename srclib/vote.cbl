       IDENTIFICATION DIVISION.
       PROGRAM-ID. VOTE.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-AGE            PIC 9(3) VALUE 20.
       01 WS-VOTING-AGE     PIC 9(2) VALUE 18.

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           DISPLAY "Current Age: " WS-AGE
           
           IF WS-AGE >= WS-VOTING-AGE
               DISPLAY "Status: Eligible to vote."
           ELSE
               DISPLAY "Status: Not eligible to vote."
           END-IF.
           
           STOP RUN.
