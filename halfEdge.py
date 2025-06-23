class Vertex:
    def __init__(self, idx, position):
        self.idx = idx            # index in OBJ (1-based)
        self.position = position  # (x, y, z)
        self.half_edge = None     # one outgoing half-edge

class HalfEdge:
    def __init__(self):
        self.origin = None        # Vertex
        self.twin = None          # HalfEdge
        self.next = None          # HalfEdge
        self.face = None          # Face

class Face:
    def __init__(self, idx):
        self.idx = idx            # face ID (1-based)
        self.half_edge = None     # one half-edge on its boundary

class HalfEdgeMesh:
    def __init__(self):
        self.vertices = []        # list of Vertex
        self.faces = []           # list of Face
        self.half_edges = []      # list of HalfEdge
        self.edge_map = {}        # map (origin, dest) -> half-edge

    def load_obj(self, filepath):
        positions = []
        face_indices = []
        with open(filepath, 'r') as f:
            for line in f:
                # remove comments
                line = line.split('#', 1)[0].strip()
                if not line:
                    continue
                parts = line.split()
                if parts[0] == 'v' and len(parts) >= 4:
                    x, y, z = map(float, parts[1:4])
                    positions.append((x, y, z))
                elif parts[0] == 'f' and len(parts) >= 4:
                    idxs = []
                    for p in parts[1:]:
                        idx = p.split('/')[0] if '/' in p else p
                        idxs.append(int(idx))
                    face_indices.append(idxs)

        # Create vertices
        self.vertices = [Vertex(i+1, pos) for i, pos in enumerate(positions)]

        # Build faces and half-edges
        for f_idx, idx_list in enumerate(face_indices, start=1):
            face = Face(f_idx)
            self.faces.append(face)
            n = len(idx_list)
            face_half_edges = [HalfEdge() for _ in range(n)]
            for he in face_half_edges:
                self.half_edges.append(he)
                he.face = face

            for i, he in enumerate(face_half_edges):
                origin_idx = idx_list[i]
                dest_idx = idx_list[(i+1) % n]
                v_origin = self.vertices[origin_idx-1]
                he.origin = v_origin
                if v_origin.half_edge is None:
                    v_origin.half_edge = he
                he.next = face_half_edges[(i+1) % n]

                key = (origin_idx, dest_idx)
                twin_key = (dest_idx, origin_idx)
                self.edge_map[key] = he
                if twin_key in self.edge_map:
                    twin_he = self.edge_map[twin_key]
                    he.twin = twin_he
                    twin_he.twin = he

            face.half_edge = face_half_edges[0]

    def faces_sharing_vertex(self, v_idx):
        v = self.vertices[v_idx-1]
        faces = []
        he = v.half_edge
        if not he:
            return faces
        start = he
        while True:
            faces.append(he.face)
            he = he.twin.next if he.twin else None
            if he == start or he is None:
                break
        return faces

    def edges_sharing_vertex(self, v_idx):
        v = self.vertices[v_idx-1]
        edges = []
        he = v.half_edge
        if not he:
            return edges
        start = he
        while True:
            edges.append((he.origin.idx, he.next.origin.idx))
            he = he.twin.next if he.twin else None
            if he == start or he is None:
                break
        return edges

    def faces_sharing_edge(self, origin_idx, dest_idx):
        he = self.edge_map.get((origin_idx, dest_idx))
        if not he:
            return []
        faces = [he.face]
        if he.twin:
            faces.append(he.twin.face)
        return faces

    def edges_sharing_face(self, f_idx):
        face = self.faces[f_idx-1]
        edges = []
        he = face.half_edge
        start = he
        while True:
            edges.append((he.origin.idx, he.next.origin.idx))
            he = he.next
            if he == start:
                break
        return edges

    def adjacent_faces(self, f_idx):
        face = self.faces[f_idx-1]
        neighbors = []
        he = face.half_edge
        start = he
        while True:
            if he.twin:
                neighbors.append(he.twin.face)
            he = he.next
            if he == start:
                break
        return neighbors

    def summary(self):
        num_he = len(self.half_edges)
        # Unique undirected edges
        unique = set(tuple(sorted(k)) for k in self.edge_map.keys())
        num_edges = len(unique)
        print(f"Loaded mesh with {len(self.vertices)} vertices, {len(self.faces)} faces, {num_he} half-edges ({num_edges} undirected edges).")

if __name__ == '__main__':
    mesh = HalfEdgeMesh()
    path = 'cube.obj'
    mesh.load_obj(path)
    mesh.summary()

    menu = '''\nEscolha uma opção:
1. Faces que compartilham um vértice
2. Arestas que compartilham um vértice
3. Faces que compartilham uma aresta
4. Arestas que compartilham uma face
5. Faces adjacentes a uma face
0. Sair\n'''
    while True:
        choice = input(menu)
        if choice == '0':
            break
        elif choice == '1':
            v = int(input("Índice do vértice: "))
            print([f.idx for f in mesh.faces_sharing_vertex(v)])
        elif choice == '2':
            v = int(input("Índice do vértice: "))
            print(mesh.edges_sharing_vertex(v))
        elif choice == '3':
            o = int(input("Origem da aresta: "))
            d = int(input("Destino da aresta: "))
            print([f.idx for f in mesh.faces_sharing_edge(o, d)])
        elif choice == '4':
            f = int(input("Índice da face: "))
            print(mesh.edges_sharing_face(f))
        elif choice == '5':
            f = int(input("Índice da face: "))
            print([nf.idx for nf in mesh.adjacent_faces(f)])
        else:
            print("Opção inválida.")
