import heapq
import random
import time
from config import MAZE_ROWS, MAZE_COLS, PATH
from .func_algorithm import simulate_move, MOVES, reconstruct_path_astar_ucs, heuristic

def astar_solve(maze, start_pos):
    """
    Giải quyết mê cung bằng A* Search và ghi lại log tuần tự.
    """
    total_path_tiles = sum(r.count(0) for r in maze)
    initial_painted = frozenset([tuple(start_pos)])
    start_state = (tuple(start_pos), initial_painted)

    pq = [(heuristic(initial_painted, total_path_tiles), 0, 0, start_state)]  # (f, g, tie_breaker, state)
    visited = {start_state: [0, None, None]}
    num_of_states = 0
    visited_count = 0
    start_time = time.time()

    explored = dict()
    stt = 0
    while pq:
        f, g, _, current_state = heapq.heappop(pq)
        current_pos, painted_tiles = current_state
        visited_count += 1

        if len(painted_tiles) == total_path_tiles:
            path = reconstruct_path_astar_ucs(visited, start_state, current_state)
            return {
                "path": path,
                "steps": len(path),
                "visited": visited_count,
                "states": num_of_states,
                "time": time.time() - start_time,
                "explored": explored
            }

        shuffled_moves = list(MOVES.keys())
        random.shuffle(shuffled_moves)

        possible_paint = []
        local_seen = set()

        for move in shuffled_moves:
            next_pos, newly_painted = simulate_move(
                current_pos, MAZE_ROWS, MAZE_COLS, move, maze
            )
            if next_pos == current_pos:
                continue

            dr, dc = MOVES.get(move, (0,0))
            r, c = current_pos
            slide_tiles = []
            while (0 <= r + dr < MAZE_ROWS and 0 <= c + dc < MAZE_COLS and
                   maze[r + dr][c + dc] == PATH):
                r += dr
                c += dc
                if (r, c) not in local_seen:
                    slide_tiles.append((r, c))
                    local_seen.add((r, c))

            for t in slide_tiles:
                if t not in possible_paint:
                    possible_paint.append(t)

            new_painted_set = painted_tiles.union(newly_painted)
            new_state = (next_pos, new_painted_set)
            g_new = g + 1
            f_new = g_new + heuristic(new_painted_set, total_path_tiles)
            if new_state not in visited or g_new < visited[new_state][0]:
                if new_state not in visited:
                    num_of_states += 1
                visited[new_state] = [g_new, current_state, move]
                heapq.heappush(pq, (f_new, g_new, stt, new_state))

        explored[stt] = possible_paint
        stt += 1

    return None