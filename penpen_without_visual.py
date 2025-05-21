import random
import numpy as np

DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

actions = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
Q = {}
alpha = 0.2
gamma = 0.99
epsilon = 0.3

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

goal_state = (22, 1)  # (x, y)
pen_start = (1, 1)

def get_valid_actions(x, y):
    valid = []
    for a in actions:
        nx, ny = x, y
        if a == DIR_UP: ny -= 1
        elif a == DIR_DOWN: ny += 1
        elif a == DIR_LEFT: nx -= 1
        elif a == DIR_RIGHT: nx += 1
        if 0 <= ny < len(map_data) and 0 <= nx < len(map_data[0]):
            if map_data[ny][nx] > 1:
                valid.append(a)
    return valid

def take_action(x, y, action):
    nx, ny = x, y
    if action == DIR_UP: ny -= 1
    elif action == DIR_DOWN: ny += 1
    elif action == DIR_LEFT: nx -= 1
    elif action == DIR_RIGHT: nx += 1
    if 0 <= ny < len(map_data) and 0 <= nx < len(map_data[0]) and map_data[ny][nx] > 1:
        return (nx, ny)
    return (x, y)

def get_reward(x, y):
    if (x, y) == goal_state:
        return 100
    elif map_data[y][x] <= 1:
        return -10
    return -0.1  # Smaller penalty for each step to encourage shorter paths

def train_q_learning(episodes=5000):
    global epsilon
    for ep in range(episodes):
        x, y = pen_start
        steps = 0
        total_reward = 0
        epsilon = max(0.01, epsilon * 0.999)

        while (x, y) != goal_state and steps < 5000:
            state = (x, y)
            if state not in Q:
                Q[state] = [0] * len(actions)

            valid = get_valid_actions(x, y)
            if not valid:
                break

            if random.random() < epsilon:
                action = random.choice(valid)
            else:
                max_q = max([Q[state][a] for a in valid])
                best_actions = [a for a in valid if Q[state][a] == max_q]
                action = random.choice(best_actions)

            new_x, new_y = take_action(x, y, action)
            new_state = (new_x, new_y)

            reward = get_reward(new_x, new_y)
            if new_state not in Q:
                Q[new_state] = [0] * len(actions)

            Q[state][action] += alpha * (reward + gamma * max(Q[new_state]) - Q[state][action])

            x, y = new_x, new_y
            total_reward += reward
            steps += 1

            print(f"Episode {ep+1}: Steps={steps}, Total Reward={total_reward:.1f}, Epsilon={epsilon:.4f}")

def print_optimal_path():
    print("\n최적 경로:")
    x, y = pen_start
    path = [(x, y)]
    visited = {(x, y): 1}
    max_steps = 10000

    for _ in range(max_steps):
        state = (x, y)
        if state not in Q:
            print("Q값 없는 상태에 도달, 종료")
            break

        valid = get_valid_actions(x, y)
        if not valid:
            print("더 이상 유효한 행동 없음, 종료")
            break

        max_q = max([Q[state][a] for a in valid])
        best_actions = [a for a in valid if Q[state][a] == max_q]
        action = random.choice(best_actions)

        new_x, new_y = take_action(x, y, action)
        if (new_x, new_y) == (x, y) or visited.get((new_x, new_y), 0) > 100:
            print("루프 또는 정지 상태 감지됨, 종료")
            break

        path.append((new_x, new_y))
        visited[(new_x, new_y)] = visited.get((new_x, new_y), 0) + 1
        x, y = new_x, new_y

        if (x, y) == goal_state:
            print("목표 도달!")
            break

    print(", ".join(map(str, path)))

# 실행
train_q_learning(episodes=5000)
print_optimal_path()
