from flask import Flask, request, jsonify
from flask_cors import CORS
from ortools.sat.python import cp_model

app = Flask(__name__)
CORS(app)  # Allow requests from your Vercel frontend

@app.route('/solve', methods=['POST'])
def solve_queens():
    try:
        data = request.get_json()
        n = data['n']
        color_groups = data['colorGroups']

        # Convert color strings to numeric indices
        color_map = {}
        numeric_grid = []
        for row in color_groups:
            numeric_row = []
            for color in row:
                if color not in color_map:
                    color_map[color] = len(color_map)
                numeric_row.append(color_map[color])
            numeric_grid.append(numeric_row)

        if len(color_map) != n:
            return jsonify({"error": f"Must use exactly {n} colors"}), 400

        solution = solve_queens_cp_sat(n, numeric_grid)
        return jsonify({"solution": solution}) if solution else jsonify({"error": "No solution"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def solve_queens_cp_sat(n, color_groups):
    model = cp_model.CpModel()
    x = {}
    for i in range(n):
        for j in range(n):
            x[(i, j)] = model.NewBoolVar(f'x_{i}_{j}')

    # Row/column/color constraints
    for i in range(n):
        model.AddExactlyOne(x[(i, j)] for j in range(n))
    for j in range(n):
        model.AddExactlyOne(x[(i, j)] for i in range(n))
    color_to_cells = {}
    for i in range(n):
        for j in range(n):
            color = color_groups[i][j]
            color_to_cells.setdefault(color, []).append(x[(i, j)])
    for cells in color_to_cells.values():
        model.AddExactlyOne(cells)

    # Diagonal constraints
    for i1 in range(n):
        for j1 in range(n):
            for i2 in range(i1 + 1, n):
                j2 = j1 + (i2 - i1)
                if j2 < n:
                    model.AddAtMostOne([x[(i1, j1)], x[(i2, j2)]])
                j2_alt = j1 - (i2 - i1)
                if j2_alt >= 0:
                    model.AddAtMostOne([x[(i1, j1)], x[(i2, j2_alt)]])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return [[int(solver.Value(x[(i, j)])) for j in range(n)] for i in range(n)]
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)