#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Controlador Mainframe
# Purpose:     Gerenciar conexão, recuperação e submissão de arquivos e JCLs
#
# Author:      Marcus Sacramento
#
# Created:     18/07/2019
# Copyright:   (c) dev89 2019
# Licence:     OpenSource
#-------------------------------------------------------------------------------

import ftplib
import sys
import time
import io


def initiate_mainframe_controller(arguments,configuration,handler_logger):
    """Inicialização de submodulo da aplicação

        Parameters
        ----------
            arguments : list, required
                Lista dos argumentos informados na linha de comando
            configuration : list, required
                Lista dos argumentos informados no arquivo de propriedades
            handler_logger : Object, required
                Objeto para gravação de Log
            Raises
            ------
                Nenhuma exceção lançada
            Returns
            -------
                Nenhum Retorno
    """
    global args
    global config
    global logger
    args = arguments
    config = configuration
    logger = handler_logger

    if args.ajuda:
        help(initiate_mainframe_controller)
    logger.debug('Inicializou o Módulo')


def connect_mainframe():
    """Conexão ao ambiente Mainframe conforme variável environment na linha de comando

        Parameters
        ----------
            Nenhum parâmetro para função. Dados obtidos da função initiate_mainframe_controller
        Raises
        ------
            Nenhuma exceção lançada
        Returns
        -------
            result: FTP, Object
                Objeto com a conexão FTP
    """
    if args.ajuda:
        help(connect_mainframe)
    logger.debug('Executando Connect Mainframe')

    result = None
    debug=0
    try:
        if args.ftp_debugger:
            debug=1
        hostname = config.get(args.environment,'hostname')
        port = config.getint(args.environment,'port')
        ftp_user = args.user
        ftp_pass = args.password
        ftp = ftplib.FTP()
        ftp.connect(hostname, port)
        ftp.set_debuglevel(debug)
        ftp.login(ftp_user, ftp_pass)
        logger.debug('Conectado ao FTP:'+hostname )
        logger.debug('Diretório atual:'+ftp.pwd())
        ftp.cwd('..')
        result = ftp
    except:
        logger.error('Falha ao conectar no FTP:\n{}'.format(sys.exc_info()[1]))
    return result

def disconnect_mainframe(ftp):
    if args.ajuda:
        help(disconnect_mainframe)
    logger.debug('Conexão ao Mainframe')
    try:
        ftp.close()
        logger.debug('Conexão FTP encerrada')
    except:
        logger.error('Falha ao desconectar:\n{}'.format(sys.exc_info()[1]))

def is_connection_alive(ftp):
    if args.ajuda:
        help(connection_is_alive)
    logger.debug('Validar se a conexão está ativa')

    result = True
    try:
        ftp.voidcmd("NOOP")
        logger.debug('Conexão FTP ativa')
    except:
        result = False
        logger.error('Conexão com FTP perdida:\n{}'.format(sys.exc_info()[1]))
    return result


def submit_file(ftp,file,name,lib,filetype='seq'):
    """Conexão ao ambiente Mainframe conforme variável environment na linha de comando

        Parameters
        ----------
            ftp: FTP, required
                Conexão ftp
            file : BytesIO, required
                Arquivo a ser submitido no FTP para o Mainframe
            name: str, required
                Nome do arquivo para o Mainframe
            lib: str, required
                Biblioteca Mainframe onde o arquivo será armazenado
            filetype: str, default=seq
                Forma de conexão ao Mainframe:
                    * seq: Sequencial para upload de arquivos
                    * jes: Para manipulação de JCL
        Raises
        ------
            Excedeu as Tentaivas de reconexão
            FTP filetype deve ser seq(uential) ou jes
        Returns
        -------
            result: str, String
                Informação de retorno do comando FTP de submissão
    """
    if args.ajuda:
        help(submit_file)
    logger.debug('Executando Submit File')

    result = None
    retry = is_connection_alive(ftp)
    attempt = 1
    while not retry:
        logger.error('Conexão Inativa')
        logger.debug('Tentativa de reconectar #'+str(attempt))
        attempt+=1
        ftp=connect_mainframe()
        retry = is_connection_alive(ftp)
        if not retry:
            retry = not retry
        if attempt == 3:
            logger.error('Excedeu as Tentaivas de reconexão')
            raise Exception('Excedeu as Tentaivas de reconexão')
    try:
        if filetype=='seq':
            ftp.voidcmd('site filetype=seq')
        elif filetype=='jes':
            ftp.voidcmd('site filetype=jes')
        else:
            logger.debug('FTP filetype='+filetype+'inválido')
            raise Exception('FTP filetype deve ser seq(uential) ou jes')
        logger.debug('Filetype alterado para '+filetype)
    except:
        logger.debug('Servidor FTP não suporta filetype')
    logger.debug('filetype={}'.format(filetype))
    try:
        ftp.cwd(lib)
        logger.debug('Diretório atual: {}'.format(ftp.pwd()))
        result = ftp.storlines('STOR '+name.strip(), file)
        logger.debug('Arquivo {} enviado com sucesso'.format(name))
        ftp.cwd('..')
    except:
        result = None
        logger.error('Falha ao enviar arquivo:\n{}'.format(sys.exc_info()[1]))
        disconnect_mainframe(ftp)
    return result


def get_file(ftp,file_name,lib=None,filetype='seq'):
    """Conexão ao ambiente Mainframe conforme variável environment na linha de comando

        Parameters
        ----------
            ftp: FTP, required
                Conexão ftp
            file_name : str, required
                Nome do arquivo a ser recuperado do Mainframe
            lib: str, required
                Biblioteca Mainframe onde o arquivo está armazenado
            filetype: str, default=seq
                Forma de conexão ao Mainframe:
                    * seq: Sequencial para upload de arquivos
                    * jes: Para manipulação de JCL
        Raises
        ------
            Excedeu as Tentaivas de reconexão
            FTP filetype deve ser seq(uential) ou jes
        Returns
        -------
            result: str, String
                Informação de retorno do comando FTP de submissão
    """
    if args.ajuda:
        help(get_file)
    logger.debug('Executando Get File')

    result = None

    retry = is_connection_alive(ftp)
    attempt = 1
    while not retry:
        logger.error('Conexão Inativa')
        logger.debug('Tentativa de reconectar #{}'.format(str(attempt)))
        attempt+=1
        ftp=connect_mainframe()
        retry = is_connection_alive(ftp)
        if not retry:
            retry = not retry
        if attempt == 3:
            logger.error('Excedeu as Tentaivas de reconexão')
            raise Exception('Excedeu as Tentaivas de reconexão')
    try:
        if filetype=='seq':
            ftp.voidcmd('site filetype=seq')
        elif filetype=='jes':
            ftp.voidcmd('site filetype=jes')
        else:
            logger.error('FTP filetype={} inválido'.format(filetype))
            raise Exception('FTP filetype deve ser seq(uential) ou jes')
        logger.debug('Filetype alterado para {}'.format(filetype))
    except:
        logger.debug('Servidor FTP não suporta filetype')
    try:
        if lib:
             teste =  ftp.cwd(lib)
        file_not_exists = True
        attempt_get_file = 1
        while file_not_exists:
            result = io.StringIO()
            try:
                teste = ftp.retrlines('RETR '+file_name,result.write)
                file_not_exists = False
            except:
                logger.error('Falha ao recuperar arquivo(#{}) {}:\n{}'.format(attempt_get_file,file_name,sys.exc_info()[1]))
                result = None
                if attempt_get_file == 3:
                    file_not_exists = False
                attempt_get_file += 1
                time.sleep(args.time_out)
    except:
        result = None
        logger.error('Falha ao conectar no FTP:\n{}'.format(sys.exc_info()[1]))

    return result
