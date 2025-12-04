from Knapsack import area_salon, knapsack
from multiprocessing import Pool, Manager, cpu_count
import copy

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

    if start_row + height_t > class_h or start_col + width_t > class_w:
        return False

    for row in range(start_row, start_row + height_t):
        for col in range(start_col, start_col + width_t):
            if classroom[row][col] != 0:
                return False

    for row in range(start_row - 1, start_row + height_t + 1):
        for col in range(start_col - 1, start_col + width_t + 1):
            if start_row <= row < start_row + height_t and start_col <= col < start_col + width_t:
                continue
            if not (0 <= row < class_h and 0 <= col < class_w):
                continue
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
    return current_filled + min(remaining_area, free_cells)

def should_prune(classroom, table_sizes, table_index, best_value):
    upper_bound = compute_upper_bound(classroom, table_sizes, table_index)
    return upper_bound <= best_value

def backtrack_sequential(classroom, table_sizes, table_index, best_result):
    """Versión secuencial del backtracking para niveles profundos"""
    if table_index == len(table_sizes):
        filled_cells = sum(
            1 for row in classroom for cell in row if cell != 0
        )
        if filled_cells > best_result[0]:
            best_result[0] = filled_cells
            best_result[1] = [row[:] for row in classroom]
        return
    
    if should_prune(classroom, table_sizes, table_index, best_result[0]):
        return

    height_t, width_t = table_sizes[table_index]
    placed = False

    for row in range(1, len(classroom) - 1):
        for col in range(1, len(classroom[0]) - 1):
            if can_place(classroom, row, col, height_t, width_t):
                place(classroom, row, col, height_t, width_t, table_index + 1)
                placed = True
                backtrack_sequential(classroom, table_sizes, table_index + 1, best_result)
                place(classroom, row, col, height_t, width_t, 0)

    if not placed:
        return

def parallel_branch_worker(args):
    """Función worker para procesar una rama en paralelo"""
    classroom_copy, table_sizes, table_index, row, col = args
    
    height_t, width_t = table_sizes[table_index]
    
    # Colocar la mesa en esta posición
    place(classroom_copy, row, col, height_t, width_t, table_index + 1)
    
    # Continuar con backtracking secuencial desde aquí
    local_best = [0, None]
    backtrack_sequential(classroom_copy, table_sizes, table_index + 1, local_best)
    
    return local_best

def backtrack_parallel(classroom, table_sizes, table_index, best_result, parallel_depth=2):
    """Versión paralelizada del backtracking para los primeros niveles"""
    
    if table_index == len(table_sizes):
        filled_cells = sum(
            1 for row in classroom for cell in row if cell != 0
        )
        if filled_cells > best_result[0]:
            best_result[0] = filled_cells
            best_result[1] = [row[:] for row in classroom]
        return
    
    if should_prune(classroom, table_sizes, table_index, best_result[0]):
        return

    height_t, width_t = table_sizes[table_index]
    
    # Si estamos en los primeros niveles, paralelizamos
    if table_index < parallel_depth:
        # Recolectar todas las posiciones válidas
        valid_positions = []
        for row in range(1, len(classroom) - 1):
            for col in range(1, len(classroom[0]) - 1):
                if can_place(classroom, row, col, height_t, width_t):
                    # Crear una copia del classroom para cada posición
                    classroom_copy = [row[:] for row in classroom]
                    valid_positions.append((classroom_copy, table_sizes, table_index, row, col))
        
        if not valid_positions:
            return
        
        # Procesar en paralelo
        num_processes = min(cpu_count(), len(valid_positions))
        with Pool(processes=num_processes) as pool:
            results = pool.map(parallel_branch_worker, valid_positions)
        
        # Actualizar el mejor resultado
        for local_best in results:
            if local_best[0] > best_result[0]:
                best_result[0] = local_best[0]
                best_result[1] = local_best[1]
    else:
        # Para niveles más profundos, usar backtracking secuencial
        placed = False
        for row in range(1, len(classroom) - 1):
            for col in range(1, len(classroom[0]) - 1):
                if can_place(classroom, row, col, height_t, width_t):
                    place(classroom, row, col, height_t, width_t, table_index + 1)
                    placed = True
                    backtrack_sequential(classroom, table_sizes, table_index + 1, best_result)
                    place(classroom, row, col, height_t, width_t, 0)
        
        if not placed:
            return

if __name__ == "__main__":
    # ================== DATOS DEL PROBLEMA ==================
    class_h, class_w = 12, 15
    salon_area = area_salon(class_h, class_w)
    num_estudiantes = 40

    tipos_mesa = [
        ((2, 3), 4),
        ((1, 4), 6),
        ((2, 2), 2),
    ]

    estudiantes_por_mesa = [cap for (_, cap) in tipos_mesa]
    areas = [h * w for ((h, w), _) in tipos_mesa]

    # ================== FASE 1: KNAPSACK ==================
    print("=" * 60)
    print("FASE 1: SELECCIÓN DE MESAS (KNAPSACK)")
    print("=" * 60)
    
    max_estudiantes, seleccion_indices = knapsack(
        salon_area,
        estudiantes_por_mesa,
        areas
    )

    conteo_tipos = [0] * len(tipos_mesa)
    for idx in seleccion_indices:
        conteo_tipos[idx] += 1

    max_conteo_tipos = []
    for i, ((h, w), cap) in enumerate(tipos_mesa):
        max_rows = class_h // (h + 1)
        max_cols = class_w // (w + 1)
        max_geom = max_rows * max_cols
        limited_count = min(conteo_tipos[i], max_geom)
        max_conteo_tipos.append(limited_count)

    conteo_tipos = max_conteo_tipos
    mesas_necesarias_tipo1 = (num_estudiantes + estudiantes_por_mesa[1] - 1) // estudiantes_por_mesa[1]
    conteo_tipos[1] = min(conteo_tipos[1], mesas_necesarias_tipo1)

    print(f"Dimensiones del salón: {class_h}x{class_w}  (área = {salon_area})")
    print(f"Número de estudiantes a sentar: {num_estudiantes}")
    print(f"Capacidad máxima posible (según knapsack): {max_estudiantes}")
    print()
    print("Mesas seleccionadas por tipo:")
    for i, ((h, w), cap) in enumerate(tipos_mesa):
        print(f"  Tipo {i}: {conteo_tipos[i]} mesas, tamaño {h}x{w}, asientos por mesa = {cap}")

    table_sizes = []
    for i, count in enumerate(conteo_tipos):
        dims, _ = tipos_mesa[i]
        for _ in range(count):
            table_sizes.append(dims)

    # ================== FASE 2: COLOCACIÓN DE MESAS (PARALELIZADA) ==================
    print()
    print("=" * 60)
    print("FASE 2: BACKTRACKING PARALELIZADO - COLOCACIÓN DE MESAS")
    print("=" * 60)
    print(f"Usando {cpu_count()} núcleos de CPU")
    print()
    
    classroom = generate_zero_matrix(class_h, class_w)
    best_result = [0, None]

    # Ejecutar backtracking paralelizado (parallel_depth=2 significa que paraleliza los primeros 2 niveles)
    backtrack_parallel(classroom, table_sizes, 0, best_result, parallel_depth=2)

    best_value = best_result[0]
    best_matrix = best_result[1]
    best_choice = build_choice_vector(best_matrix, len(table_sizes))

    print("Matriz del salón (resultado):")
    for row in best_matrix:
        print(row)

    print()
    print(f"Espacios ocupados (celdas): {best_value}")
    print(f"Vector solución (0/1 por mesa colocada): {best_choice}")
    print()

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