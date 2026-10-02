import json
from pathlib import Path
import unicodedata
import Exercicios
import Palavras

json_Lista = Path(__file__).parent / "JSON" / "ListaLicao.json"
json_Index = Path(__file__).parent / "JSON" / "IndexLicao.json"

class Node:

    def __init__(self, codigo, posicao = None, esq = None, dir = None):
        self.codigo = codigo
        self.posicao = posicao
        self.esq = esq
        self.dir = dir

    def __repr__(self):
        return f"Node({self.codigo})"  

class Licao:

    def __innit__(self):
        self.raiz = None

    def montagem(self):
        lista = Licao.load_json(json_Lista)
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

    def limpar(self, texto):
        decompor = unicodedata.normalize('NFD', texto)
        acento = "".join(c for c in decompor if unicodedata.category(c) != 'Mn')
        return acento.casefold()

    def inserir(self):
        x = self.gerar_codigo()
        descricao = input("Pergunta da licao: ")
        cod_idioma = int(input("Qual idioma? "))
        Palavras.Palavra().busca(cod_idioma)
        trad = input("Traducao:  ")
        nvl = int(input("Qual nivel? "))
        lista = Licao.load_json(json_Index)
        index = {"palavras": [{"codigo": item["codigo"],
                               "cod_idioma": item["cod_idioma"],
                               "nivel": item["nivel"],
                               "descricao": item["descricao"],
                               "traducao": item["traducao"]} for item in lista]}
        pos = len(index["palavras"]) 
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
            novo = {"codigo": x, "cod_idioma": cod_idioma, "nivel": nvl,
                     "descricao": descricao, "traducao": trad}
            index["licoes"].append(novo)
            with open(json_Index, "w", encoding="utf-8") as g:
                json.dump(index, g, indent=4, ensure_ascii=False)
            self.save_json()
        else:
            print("Op cancelada")      

        return None

    def exercicio(self, idioma, nivel):
        ex1 = Exercicios.Exercicio().pergunta(idioma, nivel)
        ex2 = Exercicios.Exercicio().pergunta(idioma, nivel)
        ex3 = Exercicios.Exercicio().pergunta(idioma, nivel)
        return ex1 + ex2 + ex3

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
        dados = {"licoes": self.dicionario(self.raiz)}
        with open(json_Lista, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent = 4, ensure_ascii = False) 
        print("Arquivo salvo")

    def load_json(caminho):
        with open(caminho, "r", encoding = "utf-8") as f:
            dados = json.load(f)  
        return dados["licoes"]


#text = input("Digite:  ")
#limpo = Licao.limpar(text)
#print(limpo)
