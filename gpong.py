# gpong.py: Pong (порт PicoPong от YouMakeTech) на T-Display RP2040
import random
import time
import retro
from retro import fb, disp, WIDTH, HEIGHT, BLACK, WHITE, YELLOW, CYAN
from fastdisplay import RED


def main():
    BALL = 8                 # размер мяча
    PAD_W = 32               # ракетка
    PAD_H = 4
    PAD_Y = HEIGHT - 2 * PAD_H - 4

    ball_x = WIDTH // 2
    ball_y = 10
    ball_vx = 2.0
    ball_vy = 1.6

    pad_x = WIDTH // 2 - PAD_W // 2
    pad_v = 6
    score = 0

    while True:
        retro.check_exit()

        if retro.b_pressed():
            pad_x += pad_v
            if pad_x + PAD_W > WIDTH:
                pad_x = WIDTH - PAD_W
        elif retro.a_pressed():
            pad_x -= pad_v
            if pad_x < 0:
                pad_x = 0

        if abs(ball_vx) < 1:
            ball_vx = 1 if ball_vx >= 0 else -1

        ball_x = int(ball_x + ball_vx)
        ball_y = int(ball_y + ball_vy)

        if ball_x < 0:
            ball_x = 0
            ball_vx = -ball_vx
        if ball_x + BALL > WIDTH:
            ball_x = WIDTH - BALL
            ball_vx = -ball_vx
        if ball_y < 0:
            ball_y = 0
            ball_vy = -ball_vy

        if (ball_y + BALL > PAD_Y and ball_x > pad_x - BALL
                and ball_x < pad_x + PAD_W + BALL):
            ball_vy = -ball_vy
            ball_y = PAD_Y - BALL
            ball_vy -= 0.15
            ball_vx += (ball_x - (pad_x + PAD_W / 2)) / 12
            score += 10

        if ball_y + BALL > HEIGHT:
            retro.game_over("SCORE " + str(score))
            return

        fb.fill(BLACK)
        fb.fill_rect(pad_x, PAD_Y, PAD_W, PAD_H, CYAN)
        fb.fill_rect(ball_x, ball_y, BALL, BALL, YELLOW)
        fb.text(str(score), WIDTH - 8 * len(str(score)) - 2, 2, WHITE)
        disp.show()
        time.sleep_ms(12)
