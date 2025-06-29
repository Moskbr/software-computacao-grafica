import pygame
from interface import *


EVENTS = {
    "rect": False,
    "triangle": False,
    "polygon": False
}

class MouseEvent:
    
    def __init__(self):
        self.count = 0
        self.clickPositions = []
        pass
    
    def start_rect_event(self, event):
        self.clickPositions = []
        if event == "rect":
            self.count = 2
        if event == "triangle":
            self.count = 3    
    
    def add_click(self, click_position):
        if self.count > 0:
            self.clicks_positions.append(click_position)
            self.count-=1

    
    def showEvent(self):
        for i, point in self.clickPositions:
            print(f"ponto {i}: {point}")

        



def main():

    interface = Interface(pygame)

    mesh = None
    matriz = Matrizes()
    

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Half-Edge Mesh Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    
    posicoes = [None]*2
    arrastando = False
    rect_flag = False

    buttons = interface.create_buttons(font)

    # Campos de input (unidades)
    input_rects = {
        'UX': pygame.Rect(10, WINDOW_HEIGHT - INPUT_HEIGHT + 5, 120, INPUT_HEIGHT - 10),
        'UY': pygame.Rect(140, WINDOW_HEIGHT - INPUT_HEIGHT + 5, 120, INPUT_HEIGHT - 10)
    }
    #if mesh:
    input_values = {'UX': f"{3}", 'UY': f"{3}"}
    first_focus = {'UX': True, 'UY': True}
    active_input = True
    op_enable = False
    #project = compute_projection(mesh.vertices, WINDOW_WIDTH, WINDOW_HEIGHT)
    first_focus = {'SX': True, 'SY': True}
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if rect_flag and MENU_HEIGHT <= y <= (WINDOW_HEIGHT - INPUT_HEIGHT):
                    posicoes[0] = event.pos
                    posicoes[1] = event.pos
                    arrastando = True
                

                p = interface.screen_to_model(mouse_pos, float(input_values['UX']), float(input_values['UY']))
                print(p)
                for name, rect, _ in buttons:
                    if rect.collidepoint(mouse_pos):
                        match name:
                            case "Open":
                                mesh = interface.open_obj()
                                span_x, span_y = interface.compute_extents(mesh.vertices)
                                desired_x, desired_y = span_x, span_y
                                input_values['UX'] = f"{desired_x:.2f}"
                                input_values['UY'] = f"{desired_y:.2f}"
                                first_focus = {'UX': True, 'UY': True}
                                op_enable = True
                                center = interface.compute_center(mesh.vertices)
                                transformacoes = matriz.pilha_transformacoes(center)
                                project = interface.compute_projection(mesh.vertices, WINDOW_WIDTH, WINDOW_HEIGHT,desired_x, desired_y*SCALE_FACTOR)
                            case "Triangle":
                                print(f"Button '{name}' clicked - functionality not yet implemented")
                            case "Rectangle":
                                rect_flag =True
                                print(f"Button '{name}' clicked - functionality not yet implemented")
                            case "Rotate":
                                if op_enable:
                                    # Abre uma janela para entrada de ângulo
                                    root = tk.Tk()
                                    root.withdraw()  # Esconde a janela principal do Tkinter
                                    angle = tk.simpledialog.askfloat("Rotate", "Enter rotation angle (degrees):")
                                    if angle is not None and mesh:
                                        angle_rad = np.radians(angle)
                                        transformacoes.push(matriz.rotacao(angle_rad))
                                    else:
                                        print("Invalid angle or mesh not loaded.")
                            case "Apply":
                                if mesh and transformacoes:
                                    R = matriz.resultante(transformacoes, center)
                                    for v in mesh.vertices:
                                        x_new, y_new, _ = R @ np.array([v.position[0], v.position[1], 1])
                                        v.position = (x_new, y_new, v.position[2])    
                                    # Recalcula os parâmetros de entrada
                                    first_focus, project = interface.recalculate_params(mesh, input_values)
                                    print("Transformations applied.")

                # Input field focus
                active_input = None
                for key, rect in input_rects.items():
                    if rect.collidepoint(mouse_pos):
                        active_input = key
            
             # Input field focus
                active_input = None
                for key, rect in input_rects.items():
                    if rect.collidepoint(mouse_pos):
                        active_input = key
                        # Clear on first focus
                        if first_focus[key]:
                            input_values[key] = ''
                            first_focus[key] = False
            elif event.type == pygame.KEYDOWN and active_input:
                if event.key in [pygame.K_BACKSPACE, pygame.K_KP_ENTER]:
                    input_values[active_input] = input_values[active_input][:-1]
                    
                elif event.unicode.isdigit() or event.unicode == '.':
                    input_values[active_input] += event.unicode
                elif event.key == pygame.K_RETURN:
                    try:
                        desired_x = float(input_values['UX'])
                        desired_y = float(input_values['UY'])*SCALE_FACTOR
                        if mesh:
                            project = interface.compute_projection(mesh.vertices, WINDOW_WIDTH, WINDOW_HEIGHT, desired_x, desired_y)
                    except ValueError:
                        pass  # ignore invalid input
            #print(input_values)

            elif event.type == pygame.MOUSEMOTION and rect_flag:
                if arrastando:
                    posicoes[1] = event.pos  # Atualiza posição final
                
            
            elif event.type == pygame.MOUSEBUTTONUP and rect_flag:
                if arrastando:
                    arrastando = False
                    p1 =  interface.screen_to_model(posicoes[0], float(input_values['UX']), float(input_values['UY']))
                    p2 = interface.screen_to_model(posicoes[1], float(input_values['UX']), float(input_values['UY']))
                    print(f"Drag finalizado: Início={p1}, Fim={p2}")

                    
        # Draw background
        screen.fill(BG_COLOR)

        if mesh:
            # Draw edges
            for (o_idx, d_idx), he in mesh.edge_map.items():
                # Draw each directed edge once
                if o_idx < d_idx:
                    v1 = mesh.vertices[o_idx - 1]
                    v2 = mesh.vertices[d_idx - 1]
                    p1 = project(v1)
                    p2 = project(v2)
                    pygame.draw.line(screen, EDGE_COLOR, p1, p2, 2)

            # Draw vertices
            for v in mesh.vertices:
                p = project(v)
                pygame.draw.circle(screen, VERTEX_COLOR, p, 5)
            

            # Draw input area
            pygame.draw.rect(screen, INPUT_BG_COLOR, (0, WINDOW_HEIGHT - INPUT_HEIGHT, WINDOW_WIDTH, INPUT_HEIGHT))
            for key, rect in input_rects.items():
                pygame.draw.rect(screen, INPUT_BORDER_COLOR, rect, 2)
                txt = font.render(f"{key}: {input_values[key]}", True, TEXT_COLOR)
                screen.blit(txt, (rect.x + 5, rect.y + (rect.height - txt.get_height()) // 2))

        # Draw menu bar
        pygame.draw.rect(screen, MENU_COLOR, (0, 0, WINDOW_WIDTH, MENU_HEIGHT))
        for name, rect, text_surf in buttons:
            color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect)
            screen.blit(text_surf, (rect.x + BUTTON_PADDING, (MENU_HEIGHT - text_surf.get_height()) // 2))

        

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()