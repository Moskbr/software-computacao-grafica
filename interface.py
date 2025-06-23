import sys
import os
import pygame
from halfEdge import HalfEdgeMesh

# Configuration\ nWINDOW_WIDTH = 800
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MENU_HEIGHT = 40
BG_COLOR = (30, 30, 30)
MENU_COLOR = (50, 50, 50)
VERTEX_COLOR = (255, 200, 0)
EDGE_COLOR = (200, 200, 200)
BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
FPS = 60

# Primitive buttons configuration\ n

PRIMITIVES = ["Triangle", "Rectangle"]
BUTTON_PADDING = 10
BUTTON_SPACING = 10


def load_mesh(filepath):
    mesh = HalfEdgeMesh()
    mesh.load_obj(filepath)
    return mesh


def compute_projection(vertices, width, height, margin=20):
    """
    Compute 2D projection mapping for mesh vertices.
    """
    xs = [v.position[0] for v in vertices]
    ys = [v.position[1] for v in vertices]
    if not xs or not ys:
        return lambda v: (0, 0)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max_x - min_x if max_x - min_x != 0 else 1
    span_y = max_y - min_y if max_y - min_y != 0 else 1
    scale_x = (width - 2 * margin) / span_x
    scale_y = (height - 2 * margin - MENU_HEIGHT) / span_y
    scale = min(scale_x, scale_y)

    def project(v):
        x, y, _ = v.position
        sx = (x - min_x) * scale + margin
        sy = height - MENU_HEIGHT - ((y - min_y) * scale + margin)
        return int(sx), int(sy + MENU_HEIGHT)

    return project


def create_buttons(font):
    buttons = []
    x = BUTTON_PADDING
    y = (MENU_HEIGHT - font.get_height()) // 2
    for name in PRIMITIVES:
        text_surf = font.render(name, True, TEXT_COLOR)
        btn_rect = pygame.Rect(x, 0, text_surf.get_width() + 2 * BUTTON_PADDING, MENU_HEIGHT)
        buttons.append((name, btn_rect, text_surf))
        x += btn_rect.width + BUTTON_SPACING
    return buttons


def main():
    if len(sys.argv) < 2:
        print("Usage: python pygame_halfedge_ui.py <path_to_obj_file>")
        sys.exit(1)

    obj_path = sys.argv[1]
    if not os.path.exists(obj_path):
        print(f"File not found: {obj_path}")
        sys.exit(1)

    mesh = load_mesh(obj_path)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Half-Edge Mesh Viewer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    project = compute_projection(mesh.vertices, WINDOW_WIDTH, WINDOW_HEIGHT)
    buttons = create_buttons(font)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for name, rect, _ in buttons:
                    if rect.collidepoint(mouse_pos):
                        print(f"Button '{name}' clicked - functionality not yet implemented")

        # Draw background
        screen.fill(BG_COLOR)

        # Draw menu bar
        pygame.draw.rect(screen, MENU_COLOR, (0, 0, WINDOW_WIDTH, MENU_HEIGHT))
        for name, rect, text_surf in buttons:
            color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(screen, color, rect)
            screen.blit(text_surf, (rect.x + BUTTON_PADDING, (MENU_HEIGHT - text_surf.get_height()) // 2))

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

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
