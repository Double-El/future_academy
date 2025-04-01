import tkinter
import random
import numpy as np

# 방향 상수 정의
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

# 애니메이션과 색상 효과
ANIMATION = [0, 1, 0, 2]
BLINK = ["#fff", "#ffc", "#ff8", "#fe4", "#ff8", "#ffc"]

# 강화학습 변수
Q = {}
visit_count = {}
alpha = 0.1
gamma = 0.9
epsilon = 0.2

actions = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
goal_state = (22, 1)

episode = 0
steps = 0
total_reward = 0
shortest_steps = float('inf')

# 게임 전역 변수
key = ""
koff = False
idx = 0
tmr = 0
stage = 1
score = 0
nokori = 3
candy = 0
pen_x = 0
pen_y = 0
pen_d = 0
pen_a = 0
red_x = 0
red_y = 0
red_d = 0
red_a = 0
red_sx = 0
red_sy = 0
kuma_x = 0
kuma_y = 0
kuma_d = 0
kuma_a = 0
kuma_sx = 0
kuma_sy = 0
kuma_sd = 0
map_data = []

def key_down(e):
    global key, koff
    key = e.keysym
    koff = False

def key_up(e):
    global koff
    koff = True

def set_stage():
    global map_data, candy, red_sx, red_sy, kuma_sx, kuma_sy, kuma_sd
    if stage == 1:
        map_data = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,2,2,2,2,2,2,0,0,2,2,0,0,2,2,0,0,2,2,2,2,2,4,0,0,0,0],
            [0,2,2,0,0,0,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0],
            [0,2,2,0,0,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0],
            [0,2,2,2,2,2,2,0,0,2,2,2,2,2,2,0,0,2,2,2,2,2,0,0,0,0,0],
            [0,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0],
            [0,2,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0,0],
            [0,2,2,2,2,2,2,2,0,2,2,0,0,2,2,2,2,2,2,2,2,2,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        ]
        candy = 0
        red_sx = 630
        red_sy = 450
        kuma_sd = -1

def set_chara_pos():
    global pen_x, pen_y, pen_d, pen_a, red_x, red_y, red_d, red_a, kuma_x, kuma_y, kuma_d, kuma_a
    pen_x = 90
    pen_y = 90
    pen_d = DIR_DOWN
    pen_a = 3
    red_x = red_sx
    red_y = red_sy
    red_d = DIR_DOWN
    red_a = 3
    kuma_x = kuma_sx
    kuma_y = kuma_sy
    kuma_d = kuma_sd
    kuma_a = 0

def get_state():
    return (pen_x // 60, pen_y // 60)

def get_valid_actions(x, y):
    valid = []
    for a in actions:
        cx, cy = x * 60 + 30, y * 60 + 30
        if not check_wall(cx, cy, a, 20):
            valid.append(a)
    return valid

def take_action(action):
    global pen_x, pen_y, pen_d
    pen_d = action
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

def move_penpen_ai():
    global Q, visit_count, idx, tmr, total_reward, steps, shortest_steps, episode
    state = get_state()
    if state not in Q:
        Q[state] = [0] * len(actions)
    if state not in visit_count:
        visit_count[state] = 0
    visit_count[state] += 1
    valid = get_valid_actions(*state)
    if not valid:
        return
    if random.random() < epsilon:
        action = random.choice(valid)
    else:
        q_vals = Q[state]
        action = max(valid, key=lambda a: q_vals[a])
    prev_state = state
    take_action(action)
    new_state = get_state()
    if new_state not in Q:
        Q[new_state] = [0] * len(actions)
    reward = get_reward(*new_state)
    total_reward += reward
    steps += 1
    Q[prev_state][action] += alpha * (reward + gamma * max(Q[new_state]) - Q[prev_state][action])
    pen_a = pen_d * 3 + ANIMATION[tmr % 4]
    if new_state == goal_state:
        idx = 4
        tmr = 0
        if steps < shortest_steps:
            shortest_steps = steps
        episode += 1
        steps = 0
        total_reward = 0

        # 다음 에피소드로 넘어가기 위한 재시작 처리
        set_chara_pos()  # 캐릭터 위치 초기화
        idx = 1  # 다시 AI 동작 시작

def check_wall(cx, cy, di, dot):
    chk = False
    if di == DIR_UP:
        mx = int((cx - 30) / 60)
        my = int((cy - 30 - dot) / 60)
        if map_data[my][mx] <= 1:
            chk = True
        mx = int((cx + 29) / 60)
        if map_data[my][mx] <= 1:
            chk = True
    if di == DIR_DOWN:
        mx = int((cx - 30) / 60)
        my = int((cy + 29 + dot) / 60)
        if map_data[my][mx] <= 1:
            chk = True
        mx = int((cx + 29) / 60)
        if map_data[my][mx] <= 1:
            chk = True
    if di == DIR_LEFT:
        mx = int((cx - 30 - dot) / 60)
        my = int((cy - 30) / 60)
        if map_data[my][mx] <= 1:
            chk = True
        my = int((cy + 29) / 60)
        if map_data[my][mx] <= 1:
            chk = True
    if di == DIR_RIGHT:
        mx = int((cx + 29 + dot) / 60)
        my = int((cy - 30) / 60)
        if map_data[my][mx] <= 1:
            chk = True
        my = int((cy + 29) / 60)
        if map_data[my][mx] <= 1:
            chk = True
    return chk

def draw_txt(txt, x, y, siz, col):
    fnt = ("Times New Roman", siz, "bold")
    canvas.create_text(x + 2, y + 2, text=txt, fill="black", font=fnt, tag="SCREEN")
    canvas.create_text(x, y, text=txt, fill=col, font=fnt, tag="SCREEN")

def draw_screen():
    canvas.delete("SCREEN")
    for y in range(len(map_data)):
        for x in range(len(map_data[0])):
            tile = map_data[y][x]
            canvas.create_image(x * 60 + 30, y * 60 + 30, image=img_bg[tile], tag="SCREEN")
            state = (x, y)
            if state in visit_count:
                count = visit_count[state]
                if count > 0:
                    color = f"#{min(255, count*5):02x}00{255 - min(255, count*5):02x}"
                    canvas.create_rectangle(x*60, y*60, x*60+60, y*60+60, fill=color, stipple="gray25", tag="SCREEN")
    canvas.create_image(pen_x, pen_y, image=img_pen[pen_a], tag="SCREEN")
    canvas.create_image(red_x, red_y, image=img_red[red_a], tag="SCREEN")
    draw_txt("Episode: " + str(episode), 720, 30, 20, "yellow")
    draw_txt("Reward: " + str(total_reward), 720, 60, 20, "orange")
    draw_txt("Steps: " + str(steps), 720, 90, 20, "aqua")
    draw_txt("Best: " + (str(shortest_steps) if shortest_steps != float('inf') else "-"), 720, 120, 20, "violet")

def main():
    global tmr
    tmr += 1
    draw_screen()
    if idx == 1:
        move_penpen_ai()
    root.after(100, main)

# Tkinter GUI 세팅
root = tkinter.Tk()
root.title("신한은행이 나아가야 할 길")
root.resizable(False, False)
root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)
canvas = tkinter.Canvas(width=1430, height=540)
canvas.pack()

# 이미지 로딩
img_bg = [
    tkinter.PhotoImage(file="image_penpen/chip00.png"),
    tkinter.PhotoImage(file="image_penpen/chip01.png"),
    tkinter.PhotoImage(file="image_penpen/chip02.png"),
    tkinter.PhotoImage(file="image_penpen/chip03.png"),
    tkinter.PhotoImage(file="image_penpen/sol.png")
]
img_pen = [tkinter.PhotoImage(file=f"image_penpen/pen{str(i).zfill(2)}.png") for i in range(12)] + [tkinter.PhotoImage(file="image_penpen/pen_face.png")]
img_red = [tkinter.PhotoImage(file=f"image_penpen/red{str(i).zfill(2)}.png") for i in range(12)]
img_kuma = [tkinter.PhotoImage(file=f"image_penpen/kuma{str(i).zfill(2)}.png") for i in range(3)]
img_title = tkinter.PhotoImage(file="image_penpen/title.png")
img_ending = tkinter.PhotoImage(file="image_penpen/ending.png")

# 게임 시작
set_stage()
set_chara_pos()
idx = 1  # 바로 시작되도록 설정
main()
root.mainloop()