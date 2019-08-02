# JCL Compiler

## Propósito

Script em python para submissão de programas COBOL e compilação por meio de JCL's de maneira massiva a partir da baixa plataforma. Permitindo a integração com versionadores e aplicações de controle de demandas.

### Configuração Necessária

* Python 3.2.5 ou superior
* Permissão para utilizaçãop de FTP no servidor Mainframe(INTERFACELEVEL=1)

Preencher o arquivo de propriedades conforme abaixo:

```txt
[GENERAL]
batch_extension=extensão para arquivos de programas COBOL, Geralmente cbl
cics_extension=extensão para arquivos de programas COBOL Online, Geralmente cbl
booklib_extension=extensão para arquivos de COPYBOOK COBOL, Geralmente cpy
jcl_program=Nome para submissão de JOB. No MVS é usado AAINTRDR para execução automática
# Cada ambiente possui sua seção de configuração
[PRODUCAO]
hostname=Hostname no ambiente Mainframe
port=prota para conexão FTP no Mainframe
sysout_pattern=Padrão para o DS com a SYSOUT. Aceita #JOB_NAME#, #JOB_ID# e #DATA#("%y%m%d") como curingas na substituição
batch_program_pds=PDS para onde serão enviados os programas COBOL
cics_program_pds=PDS para onde serão enviados os programas COBOL Online
booklib_pds=PDS para onde serão enviados os COPYBOOK COBOL
exe_batch_pds=PDS onde se encontram os executáveis COBOL para recuperação
exe_cics_pds=PDS onde se encontram os executáveis COBOL Online para recuperação
```

## Uso

* A aplicação foi testada no [MVS 3.8j Tur(n)key 4](http://wotho.ethz.ch/tk4-/). Portanto para utilização como ZOS pode ser necessário adaptação.
* A aplicação funciona por linha de parâmetro podendo ser acionada: ```python main_module.py -h```

A aplicação funciona com as seguintes etapas:

![Alt text](https://g.gravizo.com/svg?%20digraph%20G%20{%20%20%20%20"Program%20Upload"%20[shape=box];%20%20%20%20"JCL%20Submission"%20[shape=box];"SYSOUT%20Check"%20[shape=box];"Get%20EXE%20Program"%20[shape=box];%20%20%20%20"Program%20Upload"->%20"JCL%20Submission";%20%20%20"JCL%20Submission"->%20"SYSOUT%20Check";%20%20%20"SYSOUT%20Check"->%20"Get%20EXE%20Program";%20})

Um exemplo de linha de comando: ```python main_module.py -E PRODUCAO -S subsystem1 -U HERC01 -P CUL8TR -T 123456 -jn HERC010A -ju HERC01 -jp CUL8TR -fl ERROR -cl ERROR -j USER=HERC01,PASSWORD=CUL8TR```

## Testes no MVS

A versão atual pode ser testada no MVS com as seguintes premissas:

* Criação  dos seguintes PDS:
	* HERC01.PRIVLIB.SOURCE: FB/80/19040///T/300/5/5
	* HERC01.PRIVLIB.CICS: FB/80/19040///T/300/5/5
	* HERC01.PRIVLIB.LOAD: U/////T/300/5/5
* Informação dos programas a serem compilados no arquivo PROGRAMS.txt no seguinte padrão: PROGRAMA;TIPO(BATCH,CICS ou BOOKLIB);FORMA DE COMPILAÇÂO(CARTÃO), conforme exemplo abaixo:
```txt
 PGM00003;BATCH;CP2
 PGM00001;BATCH;CP2
 PGM00002;BATCH;CP2
 PGM00002;CICS;CP1
 BOOK0001;BOOKLIB
```
* Descomentar a linha ```#program_jcl_result``` no main module. Para o MVS não há o retorno do JOBID
	* A cada programa submetido será necessário informar o JobID para que seja buscado o DS com o resultado da SYSOUT. Antes de informar, verificar a SYSOUT no mainframe por meio do comando ```ST``` e executar ```OUTPUT JOBNAME(JOBID) PRINT(JOBNAME.JOBID)```. Com isso será criado um arquivo HERC01.#JOB_NAME#.#JOB_ID#.OUTLIST que poderá ser pesqusado pelo script. Em Mainframes Corporativos ferramentas automatizadas realizam essa cópia automaticamente.
