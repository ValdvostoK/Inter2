import json
from pathlib import Path
import random

json_Lista = Path(__file__).parent / "JSON" / "ListaIdioma.json"
json_Index = Path(__file__).parent / "JSON" / "IndexIdioma.json"

class Node:

    def __init__(self, codigo, posicao = None, esq = None, dir = None):
        self.codigo = codigo
        self.posicao = posicao
        self.esq = esq
        self.dir = dir

    def __repr__(self):
        return f"Node({self.codigo})"    

class Idioma:

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

    def gerar_codigo(self):
        while True:
            novo = random.randint(1, 1000000)
            if self.busca(novo) is None:
                return novo     

    def inserir(self):
        #x = self.gerar_codigo()
        descricao = input("Qual nome? Idioma")
        x = descricao
        lista = self.load_json(json_Index)
        index = {"idiomas": [{"codigo": item["codigo"], "descricao": item["descricao"]} for item in lista]}
        pos = len(index["idiomas"]) 
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
            novo = {"codigo": x, "descricao": descricao}
            index["idiomas"].append(novo)
            with open(json_Index, "w", encoding="utf-8") as g:
                json.dump(index, g, indent=4, ensure_ascii=False)
            self.save_json()
        else:
            print("Op cancelada")      

        return None

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
            dados["idiomas"] = index

            with open(json_Index, "w", encoding="utf-8") as g:
                json.dump(dados, g, indent=4, ensure_ascii=False)


            self.save_json()
        else:
            print("Nao existe")

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
        return dados["idiomas"]  

    def save_json(self):
        dados = {"idiomas": self.dicionario(self.raiz)}
        with open(json_Lista, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent = 4, ensure_ascii = False) 
        print("Arquivo salvo") 


#arvore = Idioma()

#arvore.montagem() 
#print("Resultado do print", lista)

#x = int(input("Qual numero"))
#mouse = arvore.busca(x)
#print("mouse: ", mouse)

#desc = input("descricao  ")
#arvore.inserir()
#print(arvore)
#arvore.remover()
