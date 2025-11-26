#funcion para definir el area del salon
def area_salon(largo, ancho):
    return largo * ancho

#knapsck modificado para seleccionar mesas por area
def knapsackRec(W, values, weights, n):
    # caso base
    if W <= 0 or n == 0:
        return 0, []

    # 1) opcion: NO tomar la mesa de indice n-1
    val_not, list_not = knapsackRec(W, values, weights, n - 1)
    best_val = val_not
    best_list = list_not

    # 2) opcion: SI tomar la mesa de indice n-1 (si cabe)
    if weights[n - 1] <= W:
        val_with, list_with = knapsackRec(W - weights[n - 1], values, weights, n)
        # sumamos el valor de esta mesa
        val_with = val_with + values[n - 1]
        # agregamos la mesa a la lista
        list_with = list_with + [n - 1]

        # nos quedamos con la mejor opcion
        if val_with > best_val:
            best_val = val_with
            best_list = list_with

    return best_val, best_list

def knapsack(area_salon, valores, areas):
    n = len(valores)
    max_valores, seleccion = knapsackRec(area_salon, valores, areas, n)
    return max_valores, seleccion


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
 

    

