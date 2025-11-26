from typing import List

class BranchAndBoundMaxSum:
    def __init__(self, values: List[int]):
        self.values = values      # valores de cada elemento
        self.n = len(values)

        self.best_value = 0       # mejor suma encontrada
        self.best_choice = [0] * self.n  # solución óptima (0/1)

    #  Cálculo de la cota superior
    def compute_upper_bound(self, index: int, current_value: int) -> int:
        remaining = sum(self.values[index:])   # suma de lo que falta
        return current_value + remaining       # cota optimista


    #  Verificación de poda
    def should_prune(self, index: int, current_value: int) -> bool:
        ub = self.compute_upper_bound(index, current_value)   # cota
        return ub <= self.best_value                         # si no supera al mejor, se poda

    #  Actualizar mejor solución
    def update_best_solution(self, current_value: int, current_choice: List[int]):
        if current_value > self.best_value:             # si mejora la actual
            self.best_value = current_value             # guardamos valor
            self.best_choice = current_choice.copy()    # copiamos solución

    # Simulsción de Backtracking + implementación de Branch & Bound
    def explore(self, index: int, current_value: int, current_choice: List[int]):
        if index == self.n:                       # caso base
            self.update_best_solution(current_value, current_choice)
            return

        if self.should_prune(index, current_value):   # poda
            return

        # ---- Rama 1: incluir elemento ----
        current_choice[index] = 1
        self.explore(index + 1,
                     current_value + self.values[index],
                     current_choice)

        # ---- Rama 2: excluir elemento ----
        current_choice[index] = 0
        self.explore(index + 1,
                     current_value,
                     current_choice)

    #  Función principal
    def solve(self):
        start_choice = [0] * self.n     # solución inicial
        self.explore(0, 0, start_choice)
        return self.best_value, self.best_choice



# Función que imprime la distribución
def imprimir_distribucion(values: List[int], best_choice: List[int]):
    print("=== Solución Branch & Bound (versión simple) ===")
    total_valor = 0

    for i, elegido in enumerate(best_choice):
        if elegido == 1:
            print(f"- Elemento {i} seleccionado, valor = {values[i]}")
            total_valor += values[i]

    print(f"\nNúmero de elementos seleccionados: {sum(best_choice)}")
    print(f"Suma total de valores: {total_valor}")


# Main 
if __name__ == "__main__":
    valores = [3, 5, 2, 8]
    
    solver = BranchAndBoundMaxSum(valores)
    best_value, best_choice = solver.solve()

    print("Valores:", valores)
    print("Mejor suma:", best_value)
    print("Vector solución (0/1):", best_choice)
    print()

    # Nueva forma de mostrar la solución
    imprimir_distribucion(valores, best_choice)
