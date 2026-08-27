       IDENTIFICATION DIVISION.
       PROGRAM-ID. WLCME.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
           COPY USER.
          01 WS-WLCM-MSG PIC X(80) VALUE SPACES.
       PROCEDURE DIVISION.
           MOVE "Welcome to the COBOL program!" TO WS-WLCM-MSG.
           MOVE "USR001"             TO USER-ID.
           MOVE "Nagarjun"           TO USER-NAME.
           MOVE "nagarjun@example.com" TO USER-EMAIL.
           DISPLAY WS-WLCM-MSG.
           DISPLAY "User ID:   " USER-ID.
           DISPLAY "User Name: " USER-NAME.
           DISPLAY "User Email:" USER-EMAIL.
           STOP RUN.
