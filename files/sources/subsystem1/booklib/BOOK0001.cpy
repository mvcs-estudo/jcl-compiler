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
           05 WS-FIM               PIC X(03)    VALUE SPACES.
