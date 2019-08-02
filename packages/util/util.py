#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Módulo de utilitários para a compilação
# Purpose:
#
# Author:      Marcus Sacramento
#
# Created:     18/07/2019
# Copyright:   (c) dev89 2019
# Licence:     OpenSource
#-------------------------------------------------------------------------------

import sys
import io
import platform
import os
import codecs

def initiate_util(arguments,configuration,handler_logger):
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
        help(initiate_util)
    logger.debug('Inicializou o Módulo')


def open_file(directory,filename,extension='txt'):
    """Substituição de parâmetro em um determinado arquivo
        Parameters
        ----------
            directory: str, required
                Diretório do arquivo local
            filename: str, required
                Nome do Arquivo
            extension: str, default=txt
                Extensão do arquivo. Informado no arquivo de Properties
        Raises
        ------
            Nenhuma exceção lançada
        Returns
        -------
            result: BytesIO
                Arquivo com texto substituído
    """
    if args.ajuda:
        help(open_file)
    logger.debug('Eexecutando Open File')

    result = None
    fp = None
    try:
        logger.debug('Tratando arquivo '+filename+' com encoding iso8859-1')
        fp=codecs.open(os.path.normpath(directory)+os.sep+filename.strip()+'.'+extension,'r',encoding='iso8859-1',errors='ignore')
    except:
        logger.debug('Tratando arquivo '+filename+' com encoding Original')
        fp=codecs.open(os.path.normpath(directory)+os.sep+filename.strip()+'.'+extension,'r')
    try:
        result=io.BytesIO(codecs.encode(fp.read(),'iso8859-1','ignore'))
    except:
        result=io.BytesIO(codecs.encode(fp.read()))
        logger.error('Falha ao tratar arquivo {}.{}\n{}'.format(filename,extension,sys.exc_info()[1]))

    return result


def replace_string_parameter(input_file,original_string,replace_string):
    """Substituição de parâmetro em um determinado arquivo
        Parameters
        ----------
            input_file: TextIoWrapper, required
                Arquivo de origem para substituição dos parâmetros
            original_string: str, required
                String original a ser substituída
            replace_string: str, required
                String que substituíra a antiga
        Raises
        ------
            Nenhuma exceção lançada
        Returns
        -------
            result: BytesIO
                Arquivo com texto substituído
    """
    if args.ajuda:
        help(replace_string_parameter)
    logger.debug('Executando Replace String Parameter')

    result = None
    try:
        tf=io.TextIOWrapper(input_file,encoding='iso8859-1',errors='ignore')
        result = io.BytesIO(tf.read().replace(args.delimiter+original_string+args.delimiter,replace_string).encode(encoding='iso8859-1',errors='ignore'))
        logger.debug('Substituiu a String {}{}{} por {}'.format(args.delimiter,original_string,args.delimiter,replace_string))
    except:
        logger.error('Falha ao substituir o texto:\n{}'.format(sys.exc_info()[1]))
    return result