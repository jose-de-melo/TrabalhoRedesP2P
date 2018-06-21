#coding: utf-8

import threading as thr
import socket
import os
import hashlib


def servidor(portaServidor, diretorioPadrao):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind(('', portaServidor))
    serverSocket.listen(5)


    while True:
        connectionSocket, addr = serverSocket.accept()
        connectionSocket.settimeout(60)

        # Cria uma thread para atender o cliente.
        thr.Thread(target=atenderCliente, args=((connectionSocket, diretorioPadrao, addr)), name="Atender Cliente").start()


    print('O servidor será encerrado.')
    serverSocket.close()



'''
Recebe a requisição do cliente com o nome do arquivo para
busca ou já para a sua trânsferencia. No caso de busca apenas 
envia o hash para o cliente se o arquivo for encontrado.
'''
def atenderCliente(connectionSocket, diretorioPadrao, addr):
    try:
        # Recebe uma requisição com o nome do arquivo a ser buscado.
        busca = connectionSocket.recv(1024).decode('utf-8')

        # verifica se é uma solicitação de transferência (/get), se não é apenas uma pesquisa.
        if busca.__contains__('/get'):
            solicitacaoDeTransferencia(connectionSocket, diretorioPadrao, busca)
        else:
            hashArquivo = pesquisarArquivo(busca.encode('utf-8'), diretorioPadrao)
            hashArquivo = str(hashArquivo)

            #print("servidor {} vai enviar o hash {}".format(addr[0], hashArquivo))
            connectionSocket.send(hashArquivo.encode('utf-8'))
    finally:
        connectionSocket.close



'''
Envia pelo socket conectado passado por parâmetro o arquivo solicitado.
'''
def solicitacaoDeTransferencia(connectionSocket, diretorioPadrao, nomeArquivo):
    nomeArquivo = nomeArquivo.replace('/get', '')

    #procura o nome do arquivo novamente para evitar letras maiuscula e minuscula.
    caminhoArquivo = findFile(diretorioPadrao, nomeArquivo)
    if(caminhoArquivo != None):
	    arquivo = open(caminhoArquivo, 'rb')

	    # Le os bytes de cada linha e envia para o servidor
	    # Poderia pensar que o procedimento abaixo está criando varios pacotes e enviando um por um?
	    linhasArquivo = arquivo.readlines()
	    for line in linhasArquivo:
	        connectionSocket.send(line)

    connectionSocket.close()
    arquivo.close()



'''
Verifica se um arquivo existe, se existe retorna seu camimnho completo
'''
def findFile( absolutePath, fileName ):
    for path, diretorios, arquivos in os.walk(absolutePath):
        for arquivo in arquivos:
            if fileName.lower() == arquivo.lower():
                return path + arquivo

                

'''
Pesquisa o nome do arquivo no sistema de arquivos e
retorna o hash caso tenha sido encontrado.
'''
def pesquisarArquivo( busca, diretorioPadrao ):
    # print("A busca eh {}".format(busca))
    caminhoArquivo = findFile( diretorioPadrao, busca.decode('utf-8'))
    if caminhoArquivo != None:
        return geraHash(caminhoArquivo)

    return None

'''
Gera o hash do arquivo. O hash do arquivo é um hash MD5.
'''
def geraHash (caminhoArquivo):
	hash = hashlib.md5()
	arquivo = open(caminhoArquivo, 'rb')
	hash.update(arquivo.read())
	return hash.hexdigest()
