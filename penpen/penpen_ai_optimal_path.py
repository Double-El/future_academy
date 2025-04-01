import tkinter
import random
import numpy as np

DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

ANIMATION = [0, 1, 0, 2]
BLINK = ["#fff", "#ffc", "#ff8", "#fe4", "#ff8", "#ffc"]

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
replay_path = []
last_episode_log = ""

key = ""
koff = False
idx = 2  # <-- 최적 경로 재생 모드로 시작
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

# 🧠 최적 경로 (예시)
optimal_path = [(1, 1), (2, 1), (2, 2), (2, 3), (2, 2), (2, 1), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 3), (1, 4), (1, 3), (1, 2), (1, 1), (1, 2), (1, 3), (1, 4), (1, 3), (2, 3), (2, 2), (2, 1), (1, 1), (1, 2), (1, 3), (2, 3), (2, 2), (2, 3), (2, 4), (3, 4), (2, 4), (2, 3), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (5, 4), (5, 5), (6, 5), (6, 6), (6, 7), (6, 6), (6, 7), (6, 6), (5, 6), (6, 6), (5, 6), (5, 5), (5, 4), (6, 4), (6, 5), (6, 4), (6, 5), (6, 4), (6, 5), (6, 4), (6, 5), (6, 4), (6, 5), (6, 6), (6, 5), (6, 4), (6, 5), (6, 4), (6, 5), (6, 4), (6, 5), (6, 6), (6, 7), (7, 7), (8, 7), (7, 7), (6, 7), (7, 7), (6, 7), (7, 7), (6, 7), (7, 7), (6, 7), (7, 7), (6, 7), (5, 7), (5, 6), (5, 5), (6, 5), (6, 6), (6, 7), (5, 7), (5, 6), (5, 5), (6, 5), (6, 4), (5, 4), (5, 5), (5, 6), (6, 6), (6, 5), (6, 6), (5, 6), (5, 5), (5, 4), (5, 5), (6, 5), (6, 4), (5, 4), (6, 4), (6, 5), (5, 5), (6, 5), (6, 6), (6, 7), (6, 6), (6, 5), (5, 5), (6, 5), (6, 6), (6, 7), (6, 6), (6, 5), (5, 5), (5, 6), (5, 5), (5, 4), (5, 5), (5, 4), (6, 4), (6, 5), (6, 4), (5, 4), (6, 4), (6, 5), (5, 5), (5, 6), (5, 5), (5, 4), (4, 4), (5, 4), (6, 4), (6, 5), (6, 4), (5, 4), (5, 5), (6, 5), (6, 6), (6, 7), (5, 7), (6, 7), (6, 6), (5, 6), (5, 7), (5, 6), (5, 5), (5, 6), (5, 7), (4, 7), (3, 7), (4, 7), (5, 7), (5, 6), (5, 5), (6, 5), (6, 4), (6, 5), (5, 5), (5, 4), (6, 4), (6, 5), (6, 4), (6, 5), (6, 4), (5, 4), (5, 5), (5, 6), (5, 7), (6, 7), (7, 7), (8, 7), (7, 7), (6, 7), (6, 6), (5, 6), (5, 7), (6, 7), (5, 7), (6, 7), (5, 7), (6, 7), (7, 7), (8, 7), (7, 7), (8, 7), (9, 7), (9, 6), (9, 5), (9, 4), (10, 4), (11, 4), (12, 4), (13, 4), (14, 4), (14, 5), (14, 6), (14, 7), (15, 7), (16, 7), (17, 7), (17, 6), (17, 5), (17, 4), (17, 3), (18, 3), (18, 2), (18, 1), (19, 1), (20, 1), (21, 1), (22, 1)]
replay_queue = optimal_path.copy()

def draw_txt(txt, x, y, siz, col):
    fnt = ("Times New Roman", siz, "bold")
    canvas.create_text(x + 2, y + 2, text=txt, fill="black", font=fnt, tag="SCREEN")
    canvas.create_text(x, y, text=txt, fill=col, font=fnt, tag="SCREEN")

def key_down(e):
    global key, koff
    key = e.keysym
    koff = False

def key_up(e):
    global koff
    koff = True

def set_stage():
    global map_data, candy, red_sx, red_sy, kuma_sx, kuma_sy, kuma_sd
    map_data = [
        [0]*26,
        [0,2,2,2,2,2,2,0,0,2,2,0,0,2,2,0,0,2,2,2,2,2,4,0,0,0],
        [0,2,2,0,0,0,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
        [0,2,2,0,0,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
        [0,2,2,2,2,2,2,0,0,2,2,2,2,2,2,0,0,2,2,2,2,2,0,0,0,0],
        [0,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
        [0,0,0,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,2,2,0,0,0],
        [0,2,2,2,2,2,2,2,2,2,2,0,0,2,2,2,2,2,2,2,2,2,0,0,0,0],
        [0]*26,
    ]
    candy = 0
    red_sx = 630
    red_sy = 450
    kuma_sd = -1

def set_chara_pos():
    global pen_x, pen_y, pen_d, pen_a, red_x, red_y, red_d, red_a, kuma_x, kuma_y, kuma_d, kuma_a
    pen_x = optimal_path[0][0] * 60
    pen_y = optimal_path[0][1] * 60
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

def replay_optimal_path(path):
    global pen_x, pen_y, pen_d, pen_a, idx, tmr
    if not path:
        idx = 4
        return
    next_x, next_y = path.pop(0)
    cur_x, cur_y = get_state()
    dx = next_x - cur_x
    dy = next_y - cur_y
    if dx == 1:
        pen_d = DIR_RIGHT
        pen_x += 60
    elif dx == -1:
        pen_d = DIR_LEFT
        pen_x -= 60
    elif dy == 1:
        pen_d = DIR_DOWN
        pen_y += 60
    elif dy == -1:
        pen_d = DIR_UP
        pen_y -= 60
    pen_a = pen_d * 3 + ANIMATION[tmr % 4]
    replay_path.append((next_x, next_y))

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

def draw_screen():
    canvas.delete("SCREEN")
    for y in range(len(map_data)):
        for x in range(len(map_data[0])):
            tile = map_data[y][x]
            canvas.create_image(x * 60 + 30, y * 60 + 30, image=img_bg[tile], tag="SCREEN")
    for (x, y) in replay_path:
        canvas.create_rectangle(x*60+10, y*60+10, x*60+50, y*60+50, fill="cyan", stipple="gray50", tag="SCREEN")
    canvas.create_image(pen_x, pen_y, image=img_pen[pen_a], tag="SCREEN")
    canvas.create_image(red_x, red_y, image=img_red[red_a], tag="SCREEN")
    draw_txt("Episode: " + str(episode), 720, 30, 20, "yellow")
    draw_txt("Reward: " + str(total_reward), 720, 60, 20, "orange")
    draw_txt("Steps: " + str(steps), 720, 90, 20, "aqua")
    draw_txt("Best: " + (str(shortest_steps) if shortest_steps != float('inf') else "-"), 720, 120, 20, "violet")
    if idx == 4:
        draw_txt(" 목표 도달 완료!", 720, 180, 24, "lime")

def main():
    global tmr
    tmr += 1
    draw_screen()
    if idx == 2 and tmr % 5 == 0:
        replay_optimal_path(replay_queue)
    root.after(100, main)

root = tkinter.Tk()
root.title("신한은행이 나아가야 할 길")
root.resizable(False, False)
root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)
canvas = tkinter.Canvas(width=1430, height=540)
canvas.pack()

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

set_stage()
set_chara_pos()
main()
root.mainloop()
