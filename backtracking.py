from Knapsack import area_salon, knapsack

def generate_zero_matrix(height, width):
    return [[0 for _ in range(width)] for _ in range(height)]

def build_choice_vector(best_matrix, num_tables):
    choice = [0] * num_tables
    for i in range(num_tables):
        label = i + 1
        for row in best_matrix:
            if label in row:
                choice[i] = 1
                break
    return choice

def can_place(classroom, start_row, start_col, height_t, width_t):
    class_h, class_w = len(classroom), len(classroom[0])

    # Check bounds
    if start_row + height_t > class_h or start_col + width_t > class_w:
        return False

    # Check if the placement area is empty
    for row in range(start_row, start_row + height_t):
        for col in range(start_col, start_col + width_t):
            if classroom[row][col] != 0:
                return False

    # Check adjacency: ensure no neighboring cell around the area is occupied
    for row in range(start_row - 1, start_row + height_t + 1):
        for col in range(start_col - 1, start_col + width_t + 1):

            # Skip cells inside the table footprint (already checked above)
            if start_row <= row < start_row + height_t and start_col <= col < start_col + width_t:
                continue

            # Skip out-of-bounds
            if not (0 <= row < class_h and 0 <= col < class_w):
                continue

            # If ANY neighbor is not zero → adjacency violation
            if classroom[row][col] != 0:
                return False

    return True

def place(classroom, start_row, start_col, height_t, width_t, value):
    for row in range(start_row, start_row + height_t):
        for col in range(start_col, start_col + width_t):
            classroom[row][col] = value

def compute_upper_bound(classroom, table_sizes, table_index):
    current_filled = sum(
        1 for row in classroom for cell in row if cell != 0
    )
    remaining_area = sum(h * w for h, w in table_sizes[table_index:])
    free_cells = sum(
        1 for row in classroom for cell in row if cell == 0
    )
    # No puedes llenar más de las celdas libres
    return current_filled + min(remaining_area, free_cells)


"""def compute_upper_bound(classroom, table_sizes, table_index):
    current_filled = sum(sum(1 for cell in row if cell != 0) for row in classroom)
    remaining_area = sum(h * w for h, w in table_sizes[table_index:])
    return current_filled + remaining_area"""

def should_prune(classroom, table_sizes, table_index, best_result):
    upper_bound = compute_upper_bound(classroom, table_sizes, table_index)
    return upper_bound <= best_result[0]

def backtrack(classroom, table_sizes, table_index, best_result):
    # caso base: ya procesamos todas las mesas
    if table_index == len(table_sizes):
        filled_cells = sum(
            1 for row in classroom for cell in row if cell != 0
        )
        if filled_cells > best_result[0]:
            best_result[0] = filled_cells
            best_result[1] = [row[:] for row in classroom]
        return
    
    if should_prune(classroom, table_sizes, table_index, best_result):
        return

    height_t, width_t = table_sizes[table_index]
    placed = False

    # probar TODAS las posiciones para esta mesa
    for row in range(1, len(classroom) -1):
        for col in range(1, len(classroom[0]) -1):
            if can_place(classroom, row, col, height_t, width_t):
                place(classroom, row, col, height_t, width_t, table_index + 1)
                placed = True
                backtrack(classroom, table_sizes, table_index + 1, best_result)
                place(classroom, row, col, height_t, width_t, 0)

    # si no se pudo colocar esta mesa, simplemente paramos esta rama
    if not placed:
        return




if __name__ == "__main__":
    # ================== DATOS DEL PROBLEMA ==================
    # Dimensiones del salón
    class_h, class_w = 12, 15
    salon_area = area_salon(class_h, class_w)

    # Número de estudiantes que queremos sentar
    num_estudiantes = 40

    # Tipos de mesas: ((alto, ancho), capacidad_alumnos)
    tipos_mesa = [
        ((2, 3), 4),   # mesa tipo 0, 4 alumnos, área 6
        ((1, 4), 6),   # mesa tipo 1, 6 alumnos, área 4
        ((2, 2), 2),   # mesa tipo 2, 2 alumnos, área 4
    ]

    # Extraemos de tipos_mesa lo que necesita knapsack
    estudiantes_por_mesa = [cap for (_, cap) in tipos_mesa]
    areas = [h * w for ((h, w), _) in tipos_mesa]

    # ================== FASE 1: KNAPSACK ==================
    max_estudiantes, seleccion_indices = knapsack(
        salon_area,
        estudiantes_por_mesa,
        areas
    )

    # Conteo por tipo de mesa
    conteo_tipos = [0] * len(tipos_mesa)
    for idx in seleccion_indices:
        conteo_tipos[idx] += 1

    # ====== Limitar las mesas por tipo según la geometría del salón ======
    max_conteo_tipos = []
    for i, ((h, w), cap) in enumerate(tipos_mesa):
        # Aprox: cuántas mesas de este tipo caben con al menos 1 celda de separación
        max_rows = class_h // (h + 1)  # bloques de h filas de mesa + 1 fila libre
        max_cols = class_w // (w + 1)  # bloques de w columnas de mesa + 1 col libre
        max_geom = max_rows * max_cols

        # Nos quedamos con lo que diga knapsack PERO sin pasar del máximo geométrico
        limited_count = min(conteo_tipos[i], max_geom)
        max_conteo_tipos.append(limited_count)

    # Actualizamos conteo_tipos con estos límites
    conteo_tipos = max_conteo_tipos

    print("Mesas seleccionadas (limitadas por geometría):")
    for i, ((h, w), cap) in enumerate(tipos_mesa):
        print(f"  Tipo {i}: {conteo_tipos[i]} mesas, tamaño {h}x{w}, asientos por mesa = {cap}")

    print()

    # ====== Limitar también por número de alumnos ======
    # Queremos solo las mesas necesarias para cubrir (más o menos) a los estudiantes
    mesas_necesarias_tipo1 = (num_estudiantes + estudiantes_por_mesa[1] - 1) // estudiantes_por_mesa[1]
    # si solo estás usando tipo 1, puedes hacer algo así:
    conteo_tipos[1] = min(conteo_tipos[1], mesas_necesarias_tipo1)


    print("=" * 60)
    print("FASE 1: SELECCIÓN DE MESAS (KNAPSACK)")
    print("=" * 60)
    print(f"Dimensiones del salón: {class_h}x{class_w}  (área = {salon_area})")
    print(f"Número de estudiantes a sentar: {num_estudiantes}")
    print(f"Capacidad máxima posible (según knapsack): {max_estudiantes}")
    print()

    if max_estudiantes >= num_estudiantes:
        print("Sí caben todos los estudiantes según knapsack.")
    else:
        print("No alcanza la capacidad teórica para todos los estudiantes.")
    print()

    print("Mesas seleccionadas por tipo:")
    for i, ((h, w), cap) in enumerate(tipos_mesa):
        print(f"  Tipo {i}: {conteo_tipos[i]} mesas, tamaño {h}x{w}, asientos por mesa = {cap}")

    print()

    # Construimos la lista de mesas individuales para el backtracking 
    table_sizes = []

    for i, count in enumerate(conteo_tipos):
        dims, _ = tipos_mesa[i]
        for _ in range(count):
         table_sizes.append(dims)

    # ================== FASE 2: COLOCACIÓN DE MESAS ==================
    classroom = generate_zero_matrix(class_h, class_w)
    best_result = [0, None]  # [mejor_celdas_ocupadas, mejor_matriz]

    backtrack(classroom, table_sizes, 0, best_result)

    best_value = best_result[0]
    best_matrix = best_result[1]
    best_choice = build_choice_vector(best_matrix, len(table_sizes))

    print()
    print("=" * 60)
    print("FASE 2: BACKTRACKING + BRANCH AND BOUND - COLOCACIÓN DE MESAS")
    print("=" * 60)
    print()
    print(f"Dimensiones del salón: {class_h}x{class_w}")
    print(f"Tamaños de mesas (instancias individuales): {table_sizes}")
    print()
    print("Matriz del salón (resultado):")
    for row in best_matrix:
        print(row)

    print()
    print(f"Espacios ocupados (celdas): {best_value}")
    print(f"Vector solución (0/1 por mesa colocada): {best_choice}")
    print()

    # ====== Resumen final de optimización ======
    print("=== Resumen de Optimización de Espacio ===")
    total_area = 0
    for i, usado in enumerate(best_choice):
        if usado == 1:
            h, w = table_sizes[i]
            area = h * w
            total_area += area
            print(f"- Mesa {i} colocada, tamaño {h}x{w}, área = {area} celdas")

    print()
    print(f"Número de mesas colocadas: {sum(best_choice)} de {len(table_sizes)}")
    print(f"Mejor optimización de espacio (geométrica): {best_value} celdas ocupadas")
    print(f"Capacidad teórica por knapsack: {max_estudiantes} estudiantes")
    print(f"Estudiantes objetivo: {num_estudiantes}")






"""

class_h, class_w = 6, 8
table_sizes = [(2,3), (1,4), (2,2), (2,3), (1,4), (2,2), (2,3), (1,4), (2,2), (2,3), (1,4), (2,2)]
classroom = generate_zero_matrix(class_h, class_w)
best_result = [0, None]
backtrack(classroom, table_sizes, 0, best_result)
best_value = best_result[0]
best_matrix = best_result[1]
best_choice = build_choice_vector(best_matrix, len(table_sizes))

print("=" * 60)
print("BACKTRACKING + BRANCH AND BOUND - COLOCACIÓN DE MESAS")    
print("=" * 60)
print()
print(f"Dimensiones del salón: {class_h}x{class_w}")
print(f"Tamaños de mesas: {table_sizes}")
print()
print("Matriz del salón (resultado):")
for row in best_matrix:
    print(row)

print()
print(f"Espacios ocupados: {best_value}")
print(f"Vector solución (0/1): {best_choice}")
print()

# ====== Optimización del espacio ======
print("=== Solución Branch & Bound - Optimización de Espacio ===")
total_area = 0
for i, usado in enumerate(best_choice):
    if usado == 1:
        h, w = table_sizes[i]
        area = h * w
        total_area += area
        print(f"- Mesa {i} seleccionada, tamaño {h}x{w}, área = {area} celdas")

print()
print(f"Número de mesas colocadas: {sum(best_choice)} de {len(table_sizes)}")
print(f"Mejor optimización de espacio: {best_value} celdas ocupadas")"""