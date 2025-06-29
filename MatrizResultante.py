import numpy as np

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            raise IndexError("Pilha vazia")

    def is_empty(self):
        return len(self.stack) == 0
class Matrizes:

    def translacao(self, tx, ty):
        return np.array([[1, 0, tx],
                        [0, 1, ty],
                        [0, 0, 1]])

    def rotacao(self, theta):
        return np.array([[np.cos(theta), -np.sin(theta), 0],
                        [np.sin(theta), np.cos(theta), 0],
                        [0, 0, 1]])

    def escalacao(self, sx, sy):
        return np.array([[sx, 0, 0],
                        [0, sy, 0],
                        [0, 0, 1]])

    def reflexao(self, eixo):
        if eixo == 'x':
            return np.array([[1, 0, 0],
                            [0, -1, 0],
                            [0, 0, 1]])
        elif eixo == 'y':
            return np.array([[-1, 0, 0],
                            [0, 1, 0],
                            [0, 0, 1]])
        elif eixo == 'xy':
            return np.array([[0, -1, 0],
                            [-1, 0, 0],
                            [0, 0, 1]])
        else:
            raise ValueError("Eixo inválido. Use 'x', 'y' ou 'xy'.")

    def pilha_transformacoes(self, ponto=(0, 0)):
        # Cria a pilha de transformações
        t = Stack()
        
        # Adiciona a translação para levar o ponto à origem
        translacao_origem = self.translacao(-ponto[0], -ponto[1]) # matriz de translação para levar o ponto à origem
        t.push(translacao_origem)  # Adiciona a translação à origem
        return t
        
    def resultante(self, transformacoes:Stack, ponto=(0, 0)):
        # Adiciona translação para devolver o ponto à sua posição original
        translacao_destino = self.translacao(ponto[0], ponto[1])
        transformacoes.push(translacao_destino)  # Adiciona a translação de volta
        
        resultado = np.eye(3)  # Matriz identidade 3x3
        
        while not transformacoes.is_empty():
            matriz = transformacoes.pop()
            resultado = np.dot(resultado, matriz)
        
        return resultado