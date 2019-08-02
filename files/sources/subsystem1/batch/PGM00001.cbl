       IDENTIFICATION DIVISION.
       PROGRAM-ID.                PGM00001.
       AUTHOR.                    MARCUS SACRAMENTO.
       INSTALLATION.              ESTUDO COBOL.
       DATE-WRITTEN.              03/05/2019.
       DATE-COMPILED.
       SECURITY.                  PROGRAMA DE ESTUDO.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER.           IBM-3083.
       OBJECT-COMPUTER.           IBM-3083.

       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EMPREGADOS    ASSIGN TO UT-S-EMPREGA.
           SELECT RELATORIO     ASSIGN TO UT-S-RELATOR.

       DATA DIVISION.
       FILE SECTION.
       FD  EMPREGADOS
           LABEL RECORDS ARE STANDARD
           RECORD CONTAINS 50 CHARACTERS
           BLOCK CONTAINS 0 RECORDS
           DATA RECORD IS REG-EMPREGADOS.
       01  REG-EMPREGADOS          PIC X(50).

       FD  RELATORIO
           LABEL RECORDS ARE STANDARD
           RECORD CONTAINS 80 CHARACTERS
           BLOCK CONTAINS 0 RECORDS
           DATA RECORD IS REG-RELATORIO.
       01  REG-RELATORIO           PIC X(80).

       WORKING-STORAGE SECTION.

       01  WS-AREAS-A-USAR.
           05 WS-REG-EMPREGADOS.
              10 WS-NUMERO-EMP     PIC 9(05).
              10 WS-NOME-EMP       PIC X(30).
              10 WS-STATUS-EMP     PIC 9(01).
              10 WS-DEPTO-EMP      PIC 9(03).
              10 WS-POSTO-EMP      PIC 9(02).
              10 WS-SALARIO-EMP    PIC 9(07)V99.
           05 WS-LIDOS-EMP         PIC 9(05)    VALUE ZEROS.
           05 WS-IMPRESSOS         PIC 9(05)    VALUE ZEROS.
           05 WS-TOT-SALARIOS      PIC 9(09)V99 VALUE ZEROS.
           05 SW-FIM               PIC X(03)    VALUE SPACES.

       01  WS-TITULO-1.
           05 FILLER               PIC X(30)    VALUE SPACES.
           05 WS-TIT-1             PIC X(15)
                                   VALUE 'ESTUDO DE COBOL'.
           05 FILLER               PIC X(35)    VALUE SPACES.

       01  WS-TITULO-2.
           05 FILLER               PIC X(08)    VALUE ' DATA: '.
           05 WS-TIT-2-DIA         PIC 9(02).
           05 FILLER               PIC X(01)    VALUE '/'.
           05 WS-TIT-2-MES         PIC 9(02).
           05 FILLER               PIC X(01)    VALUE '/'.
           05 WS-TIT-2-ANO         PIC 9(04).
           05 FILLER               PIC X(09)    VALUE SPACES.
           05 WS-TIT-2             PIC X(23)
                                   VALUE 'EMPREGADOS DA EMPRESA'.
           05 FILLER               PIC X(17)    VALUE SPACES.
           05 FILLER               PIC X(08)    VALUE 'PAGINA: '.
           05 WS-TIT-2-PAGINA      PIC ZZ9.
           05 FILLER               PIC X(02)    VALUE SPACES.

       01  WS-GUIA.
           05 FILLER               PIC X(01).
           05 FILLER               PIC X(78)    VALUE ALL '-'.
           05 FILLER               PIC X(01)    VALUE SPACES.

       01  WS-SUB-TITULO-1.
           05 FILLER               PIC X(04)    VALUE SPACES.
           05 FILLER               PIC X(06)    VALUE 'NUMERO'.
           05 FILLER               PIC X(12)    VALUE SPACES.
           05 FILLER               PIC X(06)    VALUE 'NOME'.
           05 FILLER               PIC X(15)    VALUE SPACES.
           05 FILLER               PIC X(06)    VALUE 'STATUS'.
           05 FILLER               PIC X(02)    VALUE SPACES.
           05 FILLER               PIC X(05)    VALUE 'DEPTO'.
           05 FILLER               PIC X(01)    VALUE SPACES.
           05 FILLER               PIC X(06)    VALUE 'POSTO'.
           05 FILLER               PIC X(04)    VALUE SPACES.
           05 FILLER               PIC X(07)    VALUE 'SALARIO'.
           05 FILLER               PIC X(06)    VALUE SPACES.
       01  WS-DETALHE.
           05 FILLER               PIC X(04)    VALUE SPACES.
           05 WS-DET-NUMERO        PIC ZZZZ9.
           05 FILLER               PIC X(04)    VALUE SPACES.
           05 WS-DET-NOME          PIC X(30).
           05 FILLER               PIC X(04)    VALUE SPACES.
           05 WS-DET-STATUS        PIC 9(01).
           05 FILLER               PIC X(04)    VALUE SPACES.
           05 WS-DET-DEPTO         PIC 9(03).
           05 FILLER               PIC X(04)    VALUE SPACES.
           05 WS-DET-POSTO         PIC 9(02).
           05 FILLER               PIC X(03)    VALUE SPACES.
           05 WS-DET-SALARIO       PIC Z,ZZZ,ZZ9.99.
           05 FILLER               PIC X(04)    VALUE SPACES.

       01  WS-DETALHE-LIDOS.
           05 FILLER               PIC X(01).
           05 FILLER               PIC X(29)
                             VALUE 'TOTAL DE EMPREGADOS LIDOS  : '.
           05 WS-TOT-LIDOS         PIC ZZ,ZZ9.
           05 FILLER               PIC X(44)    VALUE SPACES.

       01  WS-DETALHE-IMPRESSOS.
           05 FILLER               PIC X(01).
           05 FILLER               PIC X(31)
                             VALUE 'TOTAL DE EMPREGADOS IMPRESSOS: '.
           05 WS-TOT-IMPRESSOS     PIC ZZ,ZZ9.
           05 FILLER               PIC X(42)    VALUE SPACES.

       01  WS-DETALHE-SALARIOS.
           05 FILLER               PIC X(01).
           05 FILLER               PIC X(28)
                                   VALUE 'SOMA TOTAL DE SALARIOS    : '.
           05 WS-DET-SALARIO2      PIC $$$,$$$,$$9.99.
           05 FILLER               PIC X(37)    VALUE SPACES.

       LINKAGE SECTION.
       01  LK-FECHA.
           05 FILLER               PIC X(02).
           05 LK-DIA               PIC 9(02).
           05 LK-MES               PIC 9(02).
           05 LK-ANO               PIC 9(04).

       PROCEDURE DIVISION USING LK-FECHA.
           DISPLAY 'INICIO DA EXECUÇÃO'.
       010-INICIO.
           PERFORM 020-ABRE-ARQUIVOS THRU 020-FIM
           PERFORM 030-TITULOS       THRU 030-FIM
           PERFORM 040-LEE           THRU 040-FIM
           PERFORM 040-PROCESSO       THRU 040-FIM
                   UNTIL SW-FIM EQUAL 'FIM'
           PERFORM 050-FINAL         THRU 050-FIM
           GOBACK.

       020-ABRE-ARQUIVOS.
           OPEN INPUT  EMPREGADOS
                OUTPUT RELATORIO.
       020-FIM.  EXIT.

       030-TITULOS.
           WRITE REG-RELATORIO FROM WS-TITULO-1
           MOVE LK-DIA         TO WS-TIT-2-DIA
           MOVE LK-MES         TO WS-TIT-2-MES
           MOVE LK-ANO         TO WS-TIT-2-ANO
           MOVE 1              TO WS-TIT-2-PAGINA
           WRITE REG-RELATORIO FROM WS-TITULO-2
           WRITE REG-RELATORIO FROM WS-GUIA
           WRITE REG-RELATORIO FROM WS-SUB-TITULO-1
           WRITE REG-RELATORIO FROM WS-GUIA.
           DISPLAY 'DATA RELATORIO: ' WS-TIT-2-DIA '/' WS-TIT-2-MES
                                      '/' WS-TIT-2-ANO.
       030-FIM.  EXIT.

       040-PROCESSO.
           ADD 1                  TO WS-LIDOS-EMP
           ADD WS-SALARIO-EMP     TO WS-TOT-SALARIOS
           MOVE WS-NUMERO-EMP     TO WS-DET-NUMERO
           MOVE WS-NOME-EMP       TO WS-DET-NOME
           MOVE WS-STATUS-EMP     TO WS-DET-STATUS
           MOVE WS-DEPTO-EMP      TO WS-DET-DEPTO
           MOVE WS-POSTO-EMP      TO WS-DET-POSTO
           MOVE WS-SALARIO-EMP    TO WS-DET-SALARIO
           WRITE REG-RELATORIO    FROM WS-DETALHE
           ADD 1 TO WS-IMPRESSOS.
       040-LEE.
           READ EMPREGADOS INTO WS-REG-EMPREGADOS AT END
                MOVE 'FIM' TO SW-FIM.
       040-FIM.  EXIT.

       050-FINAL.
           MOVE WS-LIDOS-EMP      TO WS-TOT-LIDOS
           WRITE REG-RELATORIO    FROM WS-DETALHE-LIDOS
           MOVE WS-IMPRESSOS      TO WS-TOT-IMPRESSOS
           WRITE REG-RELATORIO    FROM WS-DETALHE-IMPRESSOS
           MOVE WS-TOT-SALARIOS   TO WS-DET-SALARIO2
           WRITE REG-RELATORIO    FROM WS-DETALHE-SALARIOS
           DISPLAY 'TOTAL LIDO: ' WS-TOT-LIDOS.
           DISPLAY 'TOTAL IMPRESSO: ' WS-TOT-IMPRESSOS.
           CLOSE EMPREGADOS RELATORIO.
       050-FIM.  EXIT.
