import json
from pathlib import Path
import random
import Idiomas
import Licaos

json_Lista = Path(__file__).parent / "JSON" / "ListaUsuario.json"
json_Index = Path(__file__).parent / "JSON" / "IndexUsuario.json"
json_IndexIdioma = Path(__file__).parent / "JSON" / "IndexIdioma.json"

class Node:

    def __init__(self, codigo, posicao = None, esq = None, dir = None):
        self.codigo = codigo
        self.posicao = posicao
        self.esq = esq
        self.dir = dir

    def __repr__(self):
        return f"Node({self.codigo})"   

class Usuario:

    def __init__(self):
        self.raiz = None
        self.montagem()

    def montagem(self):
        lista = self.load_json(json_Lista)
        nodes = {}
        for item in lista:
            codigo = item["codigo"]
            posicao = item["posicao"]
            nodes[codigo] = Node(codigo, posicao) 

        for item in lista:
            atual = nodes[item["codigo"]]
            atual_esq = item.get("esq")  
            atual_dir = item.get("dir")  
            if atual_esq is not None:
                atual.esq = nodes.get(atual_esq)
            if atual_dir is not None:
                atual.dir = nodes.get(atual_dir)  

        raiz_codigo = lista[0]["codigo"]
        self.raiz = nodes[raiz_codigo]  

        return nodes 

    def busca(self, codigo):
        atual = self.raiz
        while atual is not None and atual.codigo != codigo:
            if codigo < atual.codigo:
                atual = atual.esq
            elif codigo > atual.codigo:
                atual = atual.dir
        if atual is not None:
            return atual.posicao
        else:            
            return None

    def inserir(self):
        #x = self.gerar_codigo()
        nome = input("Qual nome? Usuario")
        x = nome
        senha = input("Senha: ")
        checagem = None
        while checagem is None:
            cod_idioma = input("Qual idioma deseja aprender? ")
            checagem = Idiomas.Idioma().busca(cod_idioma)
            if checagem is None:
                print("Codigo invalido")
        lista = self.load_json(json_Index)
        index = {"usuarios": [{"codigo": item["codigo"], "nome": item["nome"],
                               "senha": item["senha"],
                               "cod_idioma": item["cod_idioma"],
                               "nivel": item["nivel"],
                               "pontos_atual": item["pontos_atual"]} for item in lista]}
        pos = len(index["usuarios"]) 
        y = Node(x, pos)
        atual = self.raiz
        while True:
            if  x < atual.codigo:
                if atual.esq is None:
                    atual.esq = y
                    break
                atual = atual.esq

            elif x > atual.codigo:
                if atual.dir is None:
                    atual.dir = y
                    break
                atual = atual.dir  

        conf = input("Confirmar insercao(S/N)")
        if conf.lower() == "s":
            novo = {"codigo": x, "nome": nome, "senha": senha, "cod_idioma": cod_idioma,
                    "nivel": 1, "pontos_atual": 0}
            index["usuarios"].append(novo)
            with open(json_Index, "w", encoding="utf-8") as g:
                json.dump(index, g, indent=4, ensure_ascii=False)
            self.save_json()
        else:
            print("Op cancelada")      

        return None

    def aula(self, user):
        pos = self.busca(user)
        lista = self.load_json(json_Index)
        idioma = lista[pos]["cod_idioma"]
        nivel = lista[pos]["nivel"]
        pontos = int(Licaos.Licao().exercicio(idioma, nivel))
        lista[pos]["pontos_atual"] += pontos
        level = str(lista[pos]["pontos_atual"])
        antiga = int(level)
        if len(level) > 2:
            level = int(level[:-2])
            lista[pos]["nivel"] = level + 1

        if antiga > lista[pos]["nivel"]:
            print(f'Subiu para o nivel {lista[pos]["nivel"]}')
        elif antiga < lista[pos]["nivel"]:
            print(f'Caiu para o nivel {lista[pos]["nivel"]}')

        if lista[pos]["nivel"] == 5:
            print(f'Parabens {user}, voce concluiu o curso e tem direito a seu certificado')

        with open(json_Index, "r", encoding="utf-8") as f:
            dados = json.load(f)
        dados["usuarios"] = lista
                
        with open(json_Index, "w", encoding="utf-8") as g:
            json.dump(dados, g, indent=4, ensure_ascii=False)

    def certificado(self, nome):
        pos = self.busca(nome)
        lista = self.load_json(json_Index)
        if lista[pos]["nivel"] == 5:
            print(f'Parabens {nome} voce concluiu o curso de {lista[pos]["cod_idioma"]}!')
        else:
            print(f'{nome} ainda esta no nivel {lista[pos]["nivel"]} e não pode obter o certificado ainda')


    def ranking(self, user):
        dados = self.load_json(json_Index)
        proprio = dados[self.busca(user)]["cod_idioma"]
        modo = int(input(f'Idioma que esta estudando(1) {proprio} ou geral(2)'))
        if modo == 1:
            lista = [p for p in dados if p["cod_idioma"] == proprio and p["codigo"] != 0]
            lista.sort(key=lambda usuario: usuario['pontos_atual'], reverse=True)

            for x, y in enumerate(lista, start = 1):
                nome = y['nome']
                pontos = y["pontos_atual"]
                print(f'{x}° Lugar: {nome} - {pontos} pontos')   
            
        else:
            dados = [p for p in dados if p["codigo"] != 0]
            dados.sort(key=lambda usuario: usuario['pontos_atual'], reverse=True)

            for x, y in enumerate(dados, start = 1):
                nome = y['nome']
                pontos = y["pontos_atual"]
                print(f'{x}° Lugar: {nome} - {pontos} pontos')

    def minimo(self, cod):
        while cod.esq:
            cod = cod.esq
        return cod

    def excluir(self, codigo, atual = None):

        if atual is None:
            atual = self.raiz    

        if codigo < atual.codigo:
                atual.esq = self.excluir(codigo, atual.esq)

        elif codigo > atual.codigo:
                atual.dir = self.excluir(codigo, atual.dir)
        else:
            if atual.esq is None:
                return atual.dir
                    
            elif atual.dir is None:
                return atual.esq

            sucessor = atual.dir
            sucessor = self.minimo(sucessor)
            atual.codigo = sucessor.codigo  
            atual.posicao = sucessor.posicao  
            atual.dir = self.excluir(atual.codigo, atual.dir)     

        return atual

    def remover(self):
        codigo = input("Qual codigo: ")
        x = self.busca(codigo)
        if x:
            self.excluir(codigo)
            index = self.load_json(json_Index)
            index[x]["codigo"] = 0

            with open(json_Index, "r", encoding = "utf-8") as f:
                dados = json.load(f)
            dados["usuarios"] = index

            with open(json_Index, "w", encoding="utf-8") as g:
                json.dump(dados, g, indent=4, ensure_ascii=False)


            self.save_json()
        else:
            print("Nao existe")

    def alterar(self, nome):
        x = self.busca(nome)
        lista = self.load_json(json_Index)

        print(f'Usuario: {nome} || Idioma atual: {lista[x]["cod_idioma"]}')

        y = input('\nDeseja alterar o idioma aprendido? (s/n)')

        if y == 's':
            idiomas = Idiomas.Idioma().load_json(json_IndexIdioma)
            dupla = [(p["codigo"]) for p in idiomas]

            for w in dupla:
                print(w)

            check = None

            while check is None:
                y = input('\nQual idioma gostaria?')
                check = Idiomas.Idioma().busca(y)

                if check is None:
                    print('Idioma invalido')

            lista[x]["cod_idioma"] = y
            lista[x]["nivel"] = 1
            lista[x]["pontos_atual"] = 0

            with open(json_Index, "r", encoding="utf-8") as f:
                dados = json.load(f)
            dados["usuarios"] = lista

            with open(json_Index, "w", encoding="utf-8") as g:
                json.dump(dados, g, indent=4, ensure_ascii=False)

            print(f'Alterado idioma para {y}')

        else:
            print("Alteracao cancelada")


    def dicionario(self, node, lista = None):

        if lista is None:
            lista = []

        if node is None:
            return lista
         
        lista.append({
            "codigo": node.codigo,
            "posicao": node.posicao,
            "esq": node.esq.codigo if node.esq else None,
            "dir": node.dir.codigo if node.dir else None
        })

        self.dicionario(node.esq, lista)       
        self.dicionario(node.dir, lista)

        return lista

    def load_json(self, caminho):
        with open(caminho, "r", encoding = "utf-8") as f:
            dados = json.load(f)  
        return dados["usuarios"]  

    def save_json(self):
        dados = {"usuarios": self.dicionario(self.raiz)}
        with open(json_Lista, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent = 4, ensure_ascii = False) 
        print("Arquivo salvo") 


#arvore = Usuario()
#arvore.ranking()
#arvore.aula("Valdrei") 
#arvore.inserir()
#arvore.alterar("Valdrei")