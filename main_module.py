#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Módulo Principal
# Purpose:     Orquestrar o upload e submissão de jobs de compilação ao mainframe
#
# Author:      Marcus Sacramento
#
# Created:     18/07/2019
# Copyright:   (c) dev89 2019
# Licence:     OpenSource
#-------------------------------------------------------------------------------
import configparser
import argparse
import datetime
import logging
import packages
import io
import os
import re

from packages.util.util import *
from packages.util.inutil import *
from packages.mainframe_controller.mainframe_controller import *

def program_uploader(ftp,args,config):
    """ Realiza o upload de programas para o Mainframe
            Os PDS devem ser configurados no arquivo de propriedades

        Parameters
        ----------
        ftp: FTP, required
            Conexão ftp
        args : list, required
            Lista dos argumentos informados na linha de comando
        config : list, required
            Lista da configuração definida no arquivo de propriedades
        Raises
        ------
            Nenhuma exceção lançada

        Returns
        -------
            Lista com o resultado da submissão
    """
    if args.ajuda:
        help(program_uploader)
    logger.debug('Executando Program Uploader')

    result = []
    with open('PROGRAMS.txt','rt') as p:
        logger.debug('Arquivo com lista de programas aberto')
        for program_compiler in p.read().split('\n'):
            if len(program_compiler)==0:
                continue
            program_result = []
            compiler = program_compiler.split(';')
            program = compiler[0]
            program_class = compiler[1].upper()
            try:
                program_compiler_jcl = compiler[2].upper() if compiler[2] else None
            except:
                program_compiler_jcl = None
            program_result.append(program)
            program_result.append(program_class)
            program_result.append(program_compiler_jcl)
            if program_class == 'BATCH' or program_class == 'CICS' or program_class == 'BOOKLIB':
                program_pds = ''
                program_extension = ''
                if program_class == 'BATCH':
                    program_pds = config.get(args.environment,'batch_program_pds')
                    program_extension = config.get('GENERAL','batch_extension')
                if program_class == 'CICS':
                    program_pds = config.get(args.environment,'cics_program_pds')
                    program_extension = config.get('GENERAL','cics_extension')
                if program_class == 'BOOKLIB':
                    program_pds = config.get(args.environment,'booklib_pds')
                    program_extension = config.get('GENERAL','booklib_extension')
                try:
                    file = open_file(args.sources+os.sep+args.subsystem+os.sep+program_class,program,program_extension)
                except:
                    file = None
                    result_submit = 'Falha ao ler arquivo'
                    logger.error('Falha ao ler arquivo:\n{}'.format(sys.exc_info()[1]))

                if file and program_pds:
                    try:
                        result_submit = submit_file(ftp,file,program,program_pds)
                        program_result.append(result_submit)
                    except:
                        result_submit = 'Falha na submissão do arquivo'
                        logger.error('Falha na submissão do arquivo:\n{}'.format(sys.exc_info()[1]))
                else:
                    program_result.append('Falha ao Carregar o arquivo')
                    logger.error('Falha ao Carregar o arquivo')
            else:
                program_result.append('Classe de Arquivo {} inválida'.format(program_class))
                logger.error('Classe de Arquivo {} inválida'.format(program_class))
            result.append(program_result)
    return result


def submit_compiler(program_list,ftp,args,config):
    """ Realiza a submissão de cartões de compilação JCL para o Mainframe

        Parameters
        ----------
        program_list: list, required
            Lista com os programas submetidos
        ftp: FTP, required
            Conexão ftp
        args : list, required
            Lista dos argumentos informados na linha de comando
        config : list, required
            Lista da configuração definida no arquivo de propriedades
        Raises
        ------
            Nenhuma exceção lançada

        Returns
        -------
            Lista com o resultado da submissão
    """
    if args.ajuda:
        help(submit_compiler)
    logger.debug('Executando Submit Compiler')

    result = []
    for program_compiler in program_list:
        if len(program_compiler)==0:
            continue
        program_result = []
        jcl_result = None
        program = program_compiler[0]
        program_class = program_compiler[1].lower()
        program_compiler_jcl = program_compiler[2].upper() if program_compiler[2] else None
        program_submit_result = program_compiler[3].upper() if program_compiler[3] else None
        program_result.append(program)
        program_result.append(program_class)
        program_result.append(program_compiler_jcl)
        program_result.append(program_submit_result)
        if not program_submit_result:
            continue

        if program_compiler_jcl and (program_submit_result.find('FALHA')<0):
            jcl_compiler=open_file('files/jcl/'+args.subsystem,program_compiler_jcl,'jcl')
            jcl_compiler=replace_string_parameter(jcl_compiler,'JOB_NAME',args.job_name)
            jcl_compiler=replace_string_parameter(jcl_compiler,'ACCOUNT',args.job_user)
            jcl_compiler=replace_string_parameter(jcl_compiler,'MAINFRAME_USER',args.job_user)
            jcl_compiler=replace_string_parameter(jcl_compiler,'MAINFRAME_PASSWORD',args.job_password)
            jcl_compiler=replace_string_parameter(jcl_compiler,'PROGRAM',program)
            jcl_compiler=replace_string_parameter(jcl_compiler,'DEMANDA_COMPILACAO',args.task)
            jcl_compiler=replace_string_parameter(jcl_compiler,'COMPILATION',program_compiler_jcl)
            jcl_compiler=replace_string_parameter(jcl_compiler,'DATA_HORA',datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
            jcl_compiler=replace_string_parameter(jcl_compiler,'EXTRA_PARAMETER',(','+args.jcl_extra_parameter if args.jcl_extra_parameter else ''))
            if jcl_compiler:
                try:
                    jcl_result = submit_file(ftp,jcl_compiler,config.get('GENERAL','jcl_program'),'','jes')
                    program_result.append(jcl_result)
                except:
                    program_result.append('Falha ao submeter JCL'+program)
                    logger.error('Falha ao submeter JCL'+program+':\n{}'.format(sys.exc_info()[1]))
        else:
            if program_compiler_jcl:
                program_result.append('Falha ao submeter JCL')
                logger.error('Falha ao submeter JCL para o programa {}'.format(program))
            else:
                program_result.append('')
        result.append(program_result)
    return result

def compiler_validator(job_list,ftp,args,config):
    """ Realiza a Validação do JOB submetido ao Mainframe.
            Necessário configurar a SYSOUT para saída em arquivo no Maiframe e
            alimentar no arquivo properties o padrão de JOB

        Parameters
        ----------
        job_list: list, required
            Lista com os JOBS submetidos
        ftp: FTP, required
            Conexão ftp
        args : list, required
            Lista dos argumentos informados na linha de comando
        config : list, required
            Lista da configuração definida no arquivo de propriedades
        Raises
        ------
            Nenhuma exceção lançada

        Returns
        -------
            Lista com o resultado da submissão
    """
    if args.ajuda:
        help(compiler_validator)
    logger.debug('Executando Compiler Validator')

    result = []
    for program_job in job_list:
        if len(program_job)==0:
            continue
        compiler_result = []
        program_compiler_result = None
        program = program_job[0]
        program_class = program_job[1].lower()
        program_compiler_jcl = program_job[2].upper() if program_job[2] else None
        program_submit_result = program_job[3].upper() if program_job[3] else None
        program_jcl_result = program_job[4].upper() if program_job[4] else None
        compiler_result.append(program)
        compiler_result.append(program_class)
        compiler_result.append(program_compiler_jcl)
        compiler_result.append(program_submit_result)
        compiler_result.append(program_jcl_result)
        if program_jcl_result and (program_submit_result.find('FALHA')<0):
            #program_jcl_result = input('Digite o JOBID('+program+'):') # Para testes noMVS 3.8j Tur(n)key 4. Usar OUTPUT JOBNAME(JOBID) PRINT(JOBNAME.JOBID) no TSO
            sysout_file = config.get(args.environment,'sysout_pattern')
            sysout_file = sysout_file.replace(args.delimiter+'JOB_NAME'+args.delimiter,args.job_name)
            sysout_file = sysout_file.replace(args.delimiter+'JOB_ID'+args.delimiter,program_jcl_result)
            sysout_file = sysout_file.replace(args.delimiter+'DATA'+args.delimiter,datetime.datetime.now().strftime("%y%m%d"))
            try:
                job_sysout = get_file(ftp,sysout_file).getvalue()
            except:
                job_sysout = 'Falha ao validar JOB {}'.format(program_jcl_result)
                logger.error('Falha ao validar JOB {}:\n{}'.format(program_jcl_result,sys.exc_info()[1]))
            for linha in job_sysout.split('\n'):
                max_rc = re.search(r''+args.job_name+'[ ]{1,}ENDED.*RC=([0-9]{4})',linha)
                jcl_error = re.search(r'(JCL ERROR)',linha)
                abend = re.search(r'(ABEND[ |=][A-Z0-9]{3,5})',linha)
            if max_rc:
                program_compiler_result = max_rc.group(1)
            elif jcl_error:
                program_compiler_result = jcl_error.group(1)
            elif abend:
                program_compiler_result = abend.group(1)
            else:
                program_compiler_result = 'N/A'
                logger.error('Não encontrado em nenhum padrão')
            compiler_result.append(program_jcl_result)
            compiler_result.append(program_compiler_result)
        result.append(compiler_result)
    return result


def get_exe(program_list,ftp,args,config):
    """ Realiza a submissão de cartões de compilação JCL para o Mainframe

        Parameters
        ----------
        program_list: list, required
            Lista com os programas submetidos
        ftp: FTP, required
            Conexão ftp
        args : list, required
            Lista dos argumentos informados na linha de comando
        config : list, required
            Lista da configuração definida no arquivo de propriedades
        Raises
        ------
            Nenhuma exceção lançada

        Returns
        -------
            Lista com o resultado da submissão
    """
    if args.ajuda:
        help(get_exe)
    logger.debug('Executando Get EXE')

    result = None
    for program_compiler in program_list:
        if len(program_compiler)==0 or not(program_compiler[1].lower() == 'batch' or program_compiler[1].lower() == 'cics'):
            continue
        result = io.BytesIO()
        program = program_compiler[0]
        program_class = program_compiler[1].lower()
        try:
            program_job_result = program_compiler[6].upper() if program_compiler[6] else None
        except:
            logger.error('Programa não submetido: {}:\n'.format(program))
            continue

        if not program_job_result.isnumeric():
            continue
        if int(program_job_result) <=4:
            pds = ''
            if program_class == 'batch':
                pds = config.get(args.environment,'exe_batch_pds')
            if program_class == 'cics':
                pds = config.get(args.environment,'exe_batch_pds')
            try:
                result = get_file(ftp,program,pds)
                if result:
                    file = open(os.path.normpath(args.exe_files)+os.sep+program,'wb')
                    file.write(result.getvalue().encode())
                    file.close()
            except:
                logger.error('Falha ao gravar arquivo {}:\n{}'.format(program,sys.exc_info()[1]))

def log_manager(args):
    """ Gerencia os logs da aplicação
            Deve-se informar o nível de log da aplicação de acordo com os argumentos
            * --cl: Console Log
            * --fl: File Log

            Os níeis de log para ambos:
            * CRITICAL
            * ERROR
            * WARNING
            * INFO
            * DEBUG
            * NOTSET

        Parameters
        ----------
            args : list, required
                Lista dos argumentos informados na linha de comando
        Raises
        ------
            Nenhuma exceção lançada

        Returns
        -------
            Objeto Logger
    """
    if args.ajuda:
        help(manager_log)

    global logger
    global fh
    global ch
    logger = logging.getLogger('JCL Compiler')
    fh = logging.FileHandler(args.log_file)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]' +
                                  '[%(module)s][%(threadName)s][%(funcName)s]' +
                                  '[%(lineno)d] %(message)s')

    logger.setLevel(logging.DEBUG)

    fh.setLevel(logging.ERROR)
    if args.file_log == 'NOTSET':
        fh.setLevel(logging.NOTSET)
    if args.file_log == 'CRITICAL':
        fh.setLevel(logging.CRITICAL)
    if args.file_log == 'WARNING':
        fh.setLevel(logging.WARNING)
    if args.file_log == 'INFO':
        fh.setLevel(logging.INFO)
    if args.file_log == 'DEBUG':
        fh.setLevel(logging.DEBUG)

    ch.setLevel(logging.ERROR)
    if args.console_log == 'NOTSET':
        ch.setLevel(logging.NOTSET)
    if args.console_log == 'CRITICAL':
        ch.setLevel(logging.CRITICAL)
    if args.console_log == 'WARNING':
        ch.setLevel(logging.WARNING)
    if args.console_log == 'INFO':
        ch.setLevel(logging.INFO)
    if args.console_log == 'DEBUG':
        ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger



def load_config(args):
    """ Carrega Arquivo de configuração
            Carrega o arquivo de configuração informado nos parametros.

            Parameters
            ----------
            args : list, required
                Lista dos argumentos informados na linha de comando

            Raises
            ------
            Nenhuma exceção lançada

            Returns
            -------
            Lista de configurações
    """
    if args.ajuda:
        help(load_config)
    logger.debug('Executando Load Config')

    global config
    config=configparser.ConfigParser()
    config.read(args.properties)
    logger.debug('Sections into '+args.properties+':'+str(config.sections()))
    for i in (config['GENERAL']):
        logger.debug(i+'='+config.get('GENERAL',i))
    logger.info('Config loaded')

    return config



def arguments_application():
    """Carregamento dos argumentos passados por linha de comando"""
    parser = argparse.ArgumentParser(description='Programa para testar os \
    argumentos passados')
    parser._action_groups.pop()
    required = parser.add_argument_group('Obrigatorio')
    optional = parser.add_argument_group('Opcional')
    required.add_argument("-E", "--environment",
                        help="Ambiente para conexão no mainframe",required=True)
    required.add_argument("-S", "--subsystem",
                        help="Subsistema de aplicações",required=True)
    required.add_argument("-U", "--user",
                        help="Usuário para conexão ao Mainframe",required=True)
    required.add_argument("-P", "--password",
                        help="Senha do usuário para conexão ao mainframe",required=True)
    required.add_argument("-T", "--task",
                        help="Identificação da atividade de submissão(Tarefa)",required=True)
    optional.add_argument("-p", "--properties", default='files/properties',
                        help="Arquivo de propriedades")
    optional.add_argument("-d", "--delimiter", default='#',
                        help="Delimitador de string para substituição")
    optional.add_argument("-j", "--jcl_extra_parameter",
                        help="Parametro extra na execucao do JCL: RESTART,TYPRUN")
    optional.add_argument("-s", "--sources", default='files/sources',
                        help="Diretório onde se encontram os fontes")
    optional.add_argument("-jn", "--job_name",
                        help="Nome do JobName de submissão")
    optional.add_argument("-ju", "--job_user",
                        help="Usuário para execução no Job(Se necessário)")
    optional.add_argument("-jp", "--job_password",
                        help="Senha para execução no Job(Se necessário)")
    optional.add_argument("-t", "--time_out", default=5,
                        help="timeout para tentativas de conexão no FTP")
    optional.add_argument("-e", "--exe_files", default='files/exe',
                        help="Diretório para guardar os executáveis")
    optional.add_argument("-a","--ajuda", help="Exibe ajuda para o script",
                        action="store_true")
    optional.add_argument("-l", "--log_file", default='files/logs/application.log',
                        help="Arquivo de log")
    optional.add_argument("-cl", "--console_log", default='ERROR',
                        help="Definicao de log de console da aplicacao: DEBUG,"+
                              "INFO, WARNING, ERROR, CRITICAL")
    optional.add_argument("-fl", "--file_log", default='ERROR',
                        help="Definicao de log em arquivo da aplicacao: DEBUG,"+
                             "INFO, WARNING, ERROR, CRITICAL")
    optional.add_argument("-fd", "--ftp_debugger",
                        help="Liga o debug do FTP",
                        action="store_true")


    return parser.parse_args()


if __name__ == '__main__':
    inicio()
    args = arguments_application()
    log_manager(args)
    logger.info('Aplicação Iniciada')
    config = load_config(args)
    initiate_mainframe_controller(args,config,logger)
    initiate_util(args,config,logger)
    logger.info('Conectando ao Servidor')
    ftp=connect_mainframe()
    logger.info('Submissão de Programas')
    submitted_files = program_uploader(ftp,args,config)
    logger.info('Submissão de JOBS de Compilação')
    submitted_jobs = submit_compiler(submitted_files,ftp,args,config)
    logger.info('Avaliação de Compilações')
    compilation_result = compiler_validator(submitted_jobs,ftp,args,config)
    for i in compilation_result:
        print(i)
    logger.info('Recuperação de Executáveis')
    get_exe(compilation_result,ftp,args,config)
    logger.info('Desconectando do servidor')
    disconnect_mainframe(ftp)
    logger.info('Aplicação Encerrada')

    fh.close()
