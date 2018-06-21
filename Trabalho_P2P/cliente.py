#coding: utf-8

from Config import pares
import socket
import threading as thr
import random


threadsClienteExecutando = 0
conectado = True


def cliente(portaServidor, diretorioPadrao):
    global threadsClienteExecutando

    while True:
        # Lê do usuário o nome do arquivo.
        busca = input("'Foneça o nome do arquivo para buscar. (digite 'exit' para sair)\nBusca: ")
        if busca == 'exit':
            break;

        # Envia o nome do arquivo para cada par em threads separadas.
        for par in pares.keys():
            thr.Thread(target=conectarComServidor, args=(par, portaServidor, busca), name='Conectar com Servidor').start()
            threadsClienteExecutando += 1

        #Espera por todas as threads que fazem a busca nos servidores.
        while True:
            if threadsClienteExecutando == 0: break

        hashesEncontrados = obterHashesEncontrados();
        if len(hashesEncontrados) > 0:
            opcao = solicitarAoUsuarioSelecionarHash(hashesEncontrados)
            listaHashes = list(hashesEncontrados.keys())

            # Se for um índice inválido continua para uma nova busca.
            if opcao < 0 or opcao >= len(listaHashes):
                print("-> A transferência não foi concluída.\n")
                continue

            hashEscolhido = listaHashes[opcao]
            servidores =  hashesEncontrados.get(hashEscolhido)
            requisitarArquivo(servidores, portaServidor, diretorioPadrao, busca)
        else:
            print("-> Nenhum arquivo '{}' foi encontrado!\n".format(busca))

    print("O cliente foi encerrado.")




'''
Envia a busca para o servidor que é passada por parametro.
'''
def conectarComServidor(servidor, portaServidor, busca):
    global threadsClienteExecutando

    try:
        socketCliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketCliente.settimeout(10)

        socketCliente.connect((servidor, portaServidor))
        print("-> '{}' - Servidor conectado com sucesso.".format(servidor))
        socketCliente.send(busca.encode('utf-8'))

        respostaHash = socketCliente.recv(2048).decode('utf-8');
        ##print("cliente recebeu o hash de {} = {} ".format(servidor, respostaHash))
        pares[servidor] = respostaHash;
    except ConnectionRefusedError:
        print("-> '{}' - Servidor não está disponível.".format(servidor))
    except OSError:
        print("-> '{}' - Destino nao foi encontrado.".format(servidor))
    finally:
        threadsClienteExecutando -= 1
        socketCliente.close()



def solicitarAoUsuarioSelecionarHash(hashesEncontrados):
    print("->\n-> Esolha uma opção para download:")
    for indice, hash in enumerate(hashesEncontrados.keys()):
        paresHash = hashesEncontrados.get(hash)
        print("\t{}. Hash '{}' encontrado em {} par(es)".format(indice + 1, hash, len(paresHash)))

    try:
        opcao = int(input("-> opção: "))
        return opcao-1
    except: return -1




def obterHashesEncontrados():
    hashesEncontrados = {}
    for par in pares.keys():
        hash  = pares[par]
        # Verifica se o par encontrou algum arquivo, se é diferente de None ou vazio.
        if(hash == 'None' or len(hash) == 0):
            continue

        # Verifica se o hash já existe no dicionario de hashes, se não, adiciona e cria uma lista vazia.
        if hashesEncontrados.get(hash) == None:
            hashesEncontrados[hash] = []

        # Adiciona o par no dicinario do hash.
        hashesEncontrados[hash].append(par)

    return hashesEncontrados




'''
Requisita o arquivo em algum dos hosts da lista. 
'''
def requisitarArquivo(hosts, portaServidor, diretorioPadrao,  nomeArquivo):
    indice = int(random.random() * len(hosts))

    socketCliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketCliente.connect((hosts[indice], portaServidor))
    socketCliente.send((nomeArquivo + '/get').encode('utf-8'))

    arquivo = open(diretorioPadrao + nomeArquivo, 'wb')

    print("-> Fazendo o download...")
    while True:
        # Recebe os dados do arquivo
        dados = socketCliente.recv(4096)

        # Verifica se acabou a transferencia
        if dados:
            arquivo.write(dados)
        else:
            break

    print("-> Transferencia concluída!\n")
    socketCliente.close()
    # Fecha o arquivo
    arquivo.close()


