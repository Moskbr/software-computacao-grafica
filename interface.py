import sys
import os
from halfEdge import HalfEdgeMesh
import tkinter as tk
from tkinter import filedialog
from MatrizResultante import Matrizes
import numpy as np

# Configuration\ nWINDOW_WIDTH = 800
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MENU_HEIGHT = 40
INPUT_HEIGHT = 30
BG_COLOR = (30, 30, 30)
MENU_COLOR = (50, 50, 50)
VERTEX_COLOR = (255, 200, 0)
EDGE_COLOR = (200, 200, 200)
BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
FPS = 60
INPUT_BG_COLOR = (40, 40, 40)
INPUT_BORDER_COLOR = (100, 100, 100)
MARGIN = 20

SCALE_FACTOR = (WINDOW_HEIGHT - MENU_HEIGHT - INPUT_HEIGHT - 2 * MARGIN)/max(WINDOW_HEIGHT-MARGIN, WINDOW_WIDTH - 2 * MARGIN)

# Primitive buttons configuration\ n

MENU_ITEMS = ["Open", "Triangle", "Rectangle", "Rotate", "Scale", "Apply"]
BUTTON_PADDING = 10
BUTTON_SPACING = 10


class Interface():
    def __init__(self, pygame):
        self.pygame = pygame
        self.input_values = {'UX': f"{3}", 'UY': f"{3}"}
        pass


    def load_mesh(self, filepath):
        mesh = HalfEdgeMesh()
        mesh.load_obj(filepath)
        return mesh

    def compute_extents(self, vertices, units_x = None, units_y = None):
        xs = [v.position[0] for v in vertices]
        ys = [v.position[1] for v in vertices]
        if not xs or not ys:
            return 3.0, 3.0
        
        span_x = max(xs) - min(xs) or 3.0
        span_y = max(ys) - min(ys) or 3.0
        
        if units_x and units_y:
            if span_x > units_x or span_y > units_y:
                return span_x, span_y
            else:
                return units_x, units_y
        return span_x, span_y


    def open_obj(self):
        file_path = filedialog.askopenfilename(title="Open OBJ File",
                                               filetypes=[("OBJ Files", "*.obj")])
        if file_path:
            try:
                mesh = self.load_mesh(file_path)
                return mesh
            except Exception as e:
                print(f"Failed to load mesh: {e}")

    def compute_projection(self, vertices, width, height, units_x, units_y):
        xs = [v.position[0] for v in vertices]
        ys = [v.position[1] for v in vertices]
        if not xs or not ys:
            return lambda v: (0, 0)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        # Escala para mapear 'units_x' ao espaço de desenho
        scale_x = (width - 2 * MARGIN) / (units_x)
        scale_y = (height - MENU_HEIGHT - INPUT_HEIGHT - 2 * MARGIN) / (units_y)

        def project(v):
            x, y, _ = v.position
            px = (x - min_x) * scale_x + MARGIN
            py = (y - min_y) * scale_y + MARGIN
            sx = int(px)
            sy = int(height - INPUT_HEIGHT - (py + MENU_HEIGHT))
            return sx, sy

        return project

    def screen_to_model(self, screen_pos, vertices, width, height, units_x, units_y, margin=MARGIN):
        """
        Converte uma posição de tela (pixels) para coordenadas do modelo.
        """
        # Calcula limites do modelo
        xs = [v.position[0] for v in vertices]
        ys = [v.position[1] for v in vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Escalas de projeção usadas
        scale_x = (width - 2*margin) / units_x
        scale_y = (height - MENU_HEIGHT - INPUT_HEIGHT - 2*margin) / units_y

        mx, my = screen_pos
        # Reverte X: remove margem e divide pela escala
        model_x = (mx - margin) / scale_x + min_x
        # Reverte Y: inverte o eixo, remove offset de menu+input e divide pela escala
        raw_y = (height - INPUT_HEIGHT - MENU_HEIGHT) - my
        model_y = raw_y / scale_y + min_y

        return (model_x, model_y)


    def screen_to_model(self, screen_pos, units_x=3, units_y=3, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, margin=MARGIN):
        mx, my = screen_pos
        scale_x = (width - 2*margin)/units_x
        scale_y = (height - MENU_HEIGHT - INPUT_HEIGHT - 2*margin)/units_y
        model_x = (mx - margin)/scale_x
        raw_y = (height - INPUT_HEIGHT - MENU_HEIGHT) - my
        model_y = raw_y/scale_y
        return (model_x, model_y)


    def create_buttons(self, font):
        buttons = []
        x = BUTTON_PADDING
        y = (MENU_HEIGHT - font.get_height()) // 2
        for name in MENU_ITEMS:
            text_surf = font.render(name, True, TEXT_COLOR)
            btn_rect = self.pygame.Rect(x, 0, text_surf.get_width() + 2 * BUTTON_PADDING, MENU_HEIGHT)
            buttons.append((name, btn_rect, text_surf))
            x += btn_rect.width + BUTTON_SPACING
        return buttons

    def recalculate_params(self, mesh, input_values):
        span_x, span_y = self.compute_extents(mesh.vertices)
        desired_x, desired_y = span_x, span_y
        input_values['UX'] = f"{desired_x:.2f}"
        input_values['UY'] = f"{desired_y:.2f}"
        first_focus = {'UX': True, 'UY': True}
                                
        project = self.compute_projection(mesh.vertices, WINDOW_WIDTH, WINDOW_HEIGHT,desired_x, desired_y*SCALE_FACTOR)
        return first_focus, project

    def compute_center(self, vertices):
        if not vertices:
            return (0, 0, 0)
        n = len(vertices)
        sum_x = sum(v.position[0] for v in vertices)
        sum_y = sum(v.position[1] for v in vertices)
        sum_z = sum(v.position[2] for v in vertices)
        return (sum_x / n, sum_y / n, sum_z / n)
    
    def reproject(self, input_values, mesh):
        desired_x = float(input_values['UX'])
        desired_y = float(input_values['UY'])
        # 3) recomputa projeção para redesenhar
        span_x, span_y = self.compute_extents(mesh.vertices, desired_x, desired_y)
        project = self.compute_projection(
            mesh.vertices,
            WINDOW_WIDTH, WINDOW_HEIGHT,
            span_x, span_y
        )

        input_values['UX'] = f"{span_x:.2f}"
        input_values['UY'] = f"{span_y:.2f}"
        return project, input_values