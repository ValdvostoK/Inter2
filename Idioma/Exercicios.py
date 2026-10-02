import json
from pathlib import Path
import random
import Palavras
import Idiomas

json_Lista = Path(__file__).parent / "JSON" / "ListaExercicio.json"
json_Index = Path(__file__).parent / "JSON" / "IndexExercicio.json"

class Node:

    def __init__(self, codigo, posicao = None, esq = None, dir = None):
        self.codigo = codigo
        self.posicao = posicao
        self.esq = esq
        self.dir = dir

    def __repr__(self):
        return f"Node({self.codigo})"  

class Exercicio:

    def __innit__(self):
        self.raiz = None
        self.montagem()

    def montagem(self):
        lista = Exercicio.load_json(json_Lista)
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

    def inserir(self):
        #x = self.gerar_codigo()
        descricao = input("Qual nome? ")
        x = descricao
        lista = self.load_json(json_Index)
        index = {"exercicios": [{"codigo": item["codigo"], "descricao": item["descricao"]} for item in lista]}
        pos = len(index["exercicios"]) 
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

    def pergunta(self, idioma, nivel):
        lista = Palavras.Palavra().exercicio(nivel, idioma)
        dados = self.load_json(json_Index)
        pergunta = dados[0]["pergunta"]
        traducao = random.randint(0, 3)
        print(pergunta, lista[traducao][1], "?")

        for x, y in lista:
            print(x)
        resposta = input()

        if resposta.lower() == lista[traducao][0].lower():
            print("Correto")
            return dados[0]["pontos"]
        else:
            print(f'Incorreto a resposta certa era {lista[traducao][0]}')
            return (dados[0]["pontos"]*(-0.1))

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

    def save_json(self):
        dados = {"exercicios": self.dicionario(self.raiz)}
        with open(json_Lista, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent = 4, ensure_ascii = False) 
        print("Arquivo salvo")

    def load_json(self, caminho):
        with open(caminho, "r", encoding = "utf-8") as f:
            dados = json.load(f)  
        return dados["exercicios"]

#ex = Exercicio()
#massa = 1
#ex.inserir()
#ex.exercicios(massa)