def generate_zero_matrix(height, width):
    return [[0 for _ in range(width)] for _ in range(height)]

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

def backtrack(classroom, table_sizes, table_index, best_result):
    if table_index == len(table_sizes):
        filled_cells = sum(sum(1 for cell in row if cell != 0) for row in classroom)
        if filled_cells > best_result[0]:
            best_result[0] = filled_cells
            best_result[1] = [row[:] for row in classroom]
        return
    height_t, width_t = table_sizes[table_index]
    for row in range(1, len(classroom) -1):
        for col in range(1, len(classroom[0]) -1):
            if can_place(classroom, row, col, height_t, width_t):
                place(classroom, row, col, height_t, width_t, table_index + 1)
                backtrack(classroom, table_sizes, table_index + 1, best_result)
                place(classroom, row, col, height_t, width_t, 0)
    backtrack(classroom, table_sizes, table_index + 1, best_result)

class_h, class_w = 6, 8
table_sizes = [(2,3), (1,4), (2,2)]
classroom = generate_zero_matrix(class_h, class_w)
best_result = [0, None]
backtrack(classroom, table_sizes, 0, best_result)
for row in best_result[1]:
    print(row)