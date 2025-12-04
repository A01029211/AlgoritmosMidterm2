from functools import lru_cache

# Función para definir el área del salón
def area_salon(largo, ancho):
    return largo * ancho

def knapsackRec(W, values, weights, n):
    # Use a wrapper that supports memoization
    return _knapsackRec(W, n, tuple(values), tuple(weights))

@lru_cache(None)
def _knapsackRec(W, n, values, weights):
    # Caso base
    if W <= 0 or n == 0:
        return 0, ()

    # NO tomar la mesa
    val_not, list_not = _knapsackRec(W, n - 1, values, weights)
    best_val = val_not
    best_list = list_not

    # SI tomar la mesa (si cabe)
    if weights[n - 1] <= W:
        val_with, list_with = _knapsackRec(W - weights[n - 1], n, values, weights)
        val_with += values[n - 1]
        list_with = list_with + (n - 1,)

        if val_with > best_val:
            best_val = val_with
            best_list = list_with

    return best_val, best_list


def knapsack(area, valores, areas):
    valores_t = tuple(valores)
    areas_t = tuple(areas)
    n = len(valores)
    best, chosen_tuple = knapsackRec(area, valores_t, areas_t, n)
    return best, list(chosen_tuple)

"""
if __name__ =="__main__":
    largo_salon = 15
    ancho_salon=50

    area_salon = area_salon(largo_salon, ancho_salon)


    estudiantes_por_mesa = [4,6,8]
    areas = [9,12,20]

    num_estudiantes = 40

    resultado, mesas = knapsack(area_salon, estudiantes_por_mesa, areas)

    conteo_tipos = [0] * len(estudiantes_por_mesa)
    for idx in mesas:
        conteo_tipos[idx] += 1

    print("Largo del salon: ", largo_salon)
    print("ancho del salon: ", ancho_salon)

    print("Numero de estudiantes:" ,num_estudiantes)

    if resultado > num_estudiantes:
        print("Si caben todos los estudiantes!")
    else:
        print("No caben todos los estudiantes")

    print("\nMesas seleccionadas por tipo:")
    for i in range(len(estudiantes_por_mesa)):
        print("  Tipo", i, "- mesas:", conteo_tipos[i], "- asientos por mesa:", estudiantes_por_mesa[i], "- area:", areas[i])
 
"""
    

