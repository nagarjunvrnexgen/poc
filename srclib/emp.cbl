       IDENTIFICATION DIVISION.
       PROGRAM-ID. EMP.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
           COPY EMPREC.
       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
           DISPLAY "USING COPYBOOK FOR EMPLOYEE RECORD".
           MOVE 1234 TO EMPNO.
           MOVE "John Doe" TO EMPNAME.
           MOVE "john@gmail.com" TO EMAIL.
           MOVE "KUM" TO LOC

           DISPLAY "Employee Number: " EMPNO.
           DISPLAY "Employee Name: " EMPNAME.
           DISPLAY "Employee Email: " EMAIL.
           DISPLAY "Employee Location: " LOC.

           DISPLAY "ALL FIELDS OF EMPLOYEE RECORD".
           DISPLAY EMPREC.
           STOP RUN.