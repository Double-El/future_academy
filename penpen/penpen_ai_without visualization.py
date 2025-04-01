import random
import numpy as np

# 방향 정의
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3
actions = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

# Q-learning 파라미터
Q = {}
visit_count = {}
alpha = 0.1
gamma = 0.9
epsilon = 0.2

goal_state = (1, 22)
replay_path = []

map_data = [
    [0]*26,
    [0,2,2,2,2,2,2,0,0,2,2,0,0,2,2,0,0,2,2,2,2,2,4,0,0,0],
    [0,2,2,0,0,0,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
    [0,2,2,0,0,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
    [0,2,2,2,2,2,2,0,0,2,2,2,2,2,2,0,0,2,2,2,2,2,0,0,0,0],
    [0,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
    [0,2,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
    [0,2,2,2,2,2,2,2,2,2,2,0,0,2,2,2,2,2,2,2,2,2,0,0,0,0],
    [0]*26,
]

# agent position (pixel-based)
pen_x = 0
pen_y = 0

def set_chara_pos():
    global pen_x, pen_y
    pen_x = 90
    pen_y = 90

def get_state():
    return (pen_x // 60, pen_y // 60)

def check_wall(cx, cy, di, dot):
    try:
        if di == DIR_UP:
            mx = int((cx - 30) / 60)
            my = int((cy - 30 - dot) / 60)
            if map_data[my][mx] <= 1: return True
            mx = int((cx + 29) / 60)
            if map_data[my][mx] <= 1: return True
        elif di == DIR_DOWN:
            mx = int((cx - 30) / 60)
            my = int((cy + 29 + dot) / 60)
            if map_data[my][mx] <= 1: return True
            mx = int((cx + 29) / 60)
            if map_data[my][mx] <= 1: return True
        elif di == DIR_LEFT:
            mx = int((cx - 30 - dot) / 60)
            my = int((cy - 30) / 60)
            if map_data[my][mx] <= 1: return True
            my = int((cy + 29) / 60)
            if map_data[my][mx] <= 1: return True
        elif di == DIR_RIGHT:
            mx = int((cx + 29 + dot) / 60)
            my = int((cy - 30) / 60)
            if map_data[my][mx] <= 1: return True
            my = int((cy + 29) / 60)
            if map_data[my][mx] <= 1: return True
        return False
    except:
        return True

def get_valid_actions(x, y):
    valid = []
    for a in actions:
        cx, cy = x * 60 + 30, y * 60 + 30
        if not check_wall(cx, cy, a, 20):
            valid.append(a)
    return valid

def take_action(action):
    global pen_x, pen_y
    if action == DIR_UP:
        pen_y -= 60
    elif action == DIR_DOWN:
        pen_y += 60
    elif action == DIR_LEFT:
        pen_x -= 60
    elif action == DIR_RIGHT:
        pen_x += 60

def get_reward(x, y):
    if (x, y) == goal_state:
        return 100
    elif map_data[y][x] <= 1:
        return -10
    else:
        return -1

def train_q_learning(episodes=500):
    global pen_x, pen_y, Q, visit_count, replay_path
    for ep in range(episodes):
        set_chara_pos()
        steps = 0
        while True:
            state = get_state()
            if state not in Q:
                Q[state] = [0] * len(actions)
            if state not in visit_count:
                visit_count[state] = 0
            visit_count[state] += 1
            valid = get_valid_actions(*state)
            if not valid:
                break
            if random.random() < epsilon:
                action = random.choice(valid)
            else:
                action = max(valid, key=lambda a: Q[state][a])
            prev_state = state
            take_action(action)
            new_state = get_state()
            if new_state not in Q:
                Q[new_state] = [0] * len(actions)
            reward = get_reward(*new_state)
            Q[prev_state][action] += alpha * (reward + gamma * max(Q[new_state]) - Q[prev_state][action])
            steps += 1
            if new_state == goal_state:
                break

def get_best_path(start_state):
    path = [start_state]
    state = start_state
    visited = set()
    while state != goal_state:
        if state not in Q or state in visited:
            break
        visited.add(state)
        best_action = np.argmax(Q[state])
        x, y = state
        if best_action == DIR_UP: y -= 1
        elif best_action == DIR_DOWN: y += 1
        elif best_action == DIR_LEFT: x -= 1
        elif best_action == DIR_RIGHT: x += 1
        next_state = (x, y)
        if map_data[y][x] <= 1:
            break
        path.append(next_state)
        state = next_state
    return path

# 실행
train_q_learning(episodes=500)
best_path = get_best_path((1, 1))
print("최적 경로:")
print(", ".join(str(p) for p in best_path))
