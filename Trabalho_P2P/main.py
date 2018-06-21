# coding: utf-8

import Config

import cliente as c
import servidor as s
import threading as thr
import os

portaServidor = Config.portaDefault
threadClienteExecutando = True;

def obterDiretorioDeUsuario():
    # Obtém o caminho completo do diretorio usado no compartilhamento
    diretorioPadrao = os.path.expanduser( Config.diretorioCompartilhado )

    ''' cria a pasta compartilhada se nao existir, se já existe 
    irá disparar uma  exceção e retornar o caminho de qualquer forma. '''
    try: os.mkdir(diretorioPadrao)
    finally: return diretorioPadrao


def main():
    global threadClienteExecutando

    diretorioPadrao = obterDiretorioDeUsuario()

    threadCliente = thr.Thread(target=c.cliente, args=(Config.portaDefault, diretorioPadrao), name='Thread_Cliente')
    threadServidor = thr.Thread(target=s.servidor, args=(Config.portaDefault, diretorioPadrao), name='Thread_Servidor', daemon=True)

    threadCliente.start()
    threadServidor.start()


if __name__ == '__main__':
	main()
