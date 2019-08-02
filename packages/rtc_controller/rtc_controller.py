#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import re

import subprocess
import shlex
import configparser



config = configparser.ConfigParser()
config.read('arquivos/properties')

jazz_url = config.get('JAZZ','url')
user = config.get('JAZZ','user')
password = config.get('JAZZ','password')


class Changeset(object):
    def __init__(self, change_id,autor,comentario,data):
        self.change_id=change_id
        self.autor=autor
        self.comentario=comentario
        self.data=data

##class Changes(object):
##    def __init__(self,alteracao)

def login_rtc():
    """Realiza Login no RTC

    Parâmetros:
    """
    cmd='login -u '+user+' -P "'+password+'" -r "'+jazz_url+'"'
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    print(out)
    return out

def carrega_workspace(workspace,diretorio_local):
    """Carrega o worspace JAZZ para um diretório local

    Parâmetros:
    workspace -- Workspace Jazz criado para a matrícula que executa o comando (default Definido no arquivo properties)
    diretorio_local -- Diretório onde será manipulado o repositório JAZZ (default Definido no arquivo properties)
    """
    if not os.path.exists(diretorio_local):
        os.makedirs(diretorio_local)
    cmd='lscm load -f --all '+workspace+' -d '+diretorio_local+' -u '+user+' -P "'+password+'" -r '+jazz_url
    print(cmd)
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    print(out)
    return out

def descarrega_workspace(workspace,diretorio_local):
    """Descarrega o worspace JAZZ para um diretório local. Não realiza o delete do repositório, apenas desconecta do workspace

    Parâmetros:
    workspace -- Workspace Jazz criado para a matrícula que executa o comando (default Definido no arquivo properties)
    diretorio_local -- Diretório onde será manipulado o repositório JAZZ (default Definido no arquivo properties)
    """
    cmd='lscm unload --all '+workspace+' -d '+diretorio_local+' -u '+user+' -P '+password+' -r '+jazz_url
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    return out

def lista_changes(workspace,diretorio_local,change):
    """Lista os arquivos alterados e os WorkItens no repositório para um determinado changeset no worspace JAZZ para um diretório local

    Parâmetros:
    workspace -- Workspace Jazz criado para a matrícula que executa o comando (default Definido no arquivo properties)
    diretorio_local -- Diretório onde será manipulado o repositório JAZZ (default Definido no arquivo properties)
    change -- ID da mudança obtido pelo lista_changesets
    """
    cmd='lscm ls changes -w '+workspace+' '+change+' -u '+user+' -P '+password+' -r '+jazz_url
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    for linha in str(out).split('\\n'):
        change_id=''
        changes=re.search(r'[-]{3}[a-z][-][ ][(]([0-9]{4,5})[)][ ](.*)',linha)
        if(changes):
            change_id=changes.group(1)
            autor=changes.group(2)
            comentario=changes.group(3)
            data=changes.group(4)
            changes_result.append(Changeset(change_id,autor,comentario,data))
    for i in changes_result:
        print(i.data)
    return changes_result



    return out

def lista_changesets(diretorio_local):
    """Lista as mudanças pendentes no repositório para um determinado changeset no worspace JAZZ para um diretório local. Precisa ser atualizado com o carrega_workspace

    Parâmetros:
    diretorio_local -- Diretório onde será manipulado o repositório JAZZ (default Definido no arquivo properties)
    """
    cmd='lscm show status -d '+diretorio_local
    changes_result = []

    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    for linha in str(out).split('\\n'):
        changes=re.search(r'[(]([0-9]{4,5})[)][ ]{1,}[-]{1,}[$][ ](.*)[ ][""].*["<](.*)[>"].*([0-9]{2}[-][a-z]{3}[-][0-9]{4})',linha)
        if(changes):
            change_id=changes.group(1)
            autor=changes.group(2)
            comentario=changes.group(3)
            data=changes.group(4)
            changeset=Changeset(change_id,autor,comentario,data)
            changes_result.append(changeset)
            for i in changes_result:
                print(i.data)
    return changes_result

def aceita_changeset(workspace,changeset):
    cmd='lscm accept '+changeset+' -t '+workspace+' -u '+user+' -P '+password+' -r '+jazz_url
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    return out

def entrega_changeset(workspace_origem,workspace_destino,changeset):
    cmd='lscm deliver '+changeset+' -s '+workspace_origem+' -t '+workspace_destino+' -u '+user+' -P '+password+' -r '+jazz_url
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    return out


