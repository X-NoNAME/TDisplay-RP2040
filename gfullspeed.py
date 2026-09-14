# gfullspeed.py: мотогонка, портрет (порт "Full Speed" от Kuba & Stepan)
# A - влево, B - вправо. Обгоняй соперников, не вылетай с трассы.
import random
import time
import retro
from retro import fb, disp, WIDTH, HEIGHT, BLACK, WHITE, YELLOW, CYAN, RED

HORIZON = 56
ROAD_TOP = 60
MOTO_Y = HEIGHT - 44


def main():
    fb.fill(BLACK)
    retro.text2_center("SPEED", 80, YELLOW)
    retro.text2_center("A< >B", 120, WHITE)
    disp.show()
    time.sleep(1.5)

    x_pos = 0
    tilt = 0
    score = 0
    speed = 1
    accel = 1.0
    stripe = 0
    rival_y = -30          # вертикальная позиция соперника (ниже горизонта)
    rival_x = 0
    road_wobble = 0        # вираж трассы
    wob_dir = 1

    while True:
        retro.check_exit()

        fb.fill(BLACK)
        tilt = 0
        if retro.a_pressed():
            x_pos -= 4
            tilt = -6
        if retro.b_pressed():
            x_pos += 4
            tilt = 6

        cx = WIDTH // 2
        # счёт
        fb.text(str(score), 4, 2, WHITE)
        fb.text(str(score * 5) + "k", WIDTH - 8 * (len(str(score * 5)) + 1) - 2, 2, CYAN)

        # горизонт и вираж
        fb.hline(0, HORIZON, WIDTH, CYAN)
        road_c = cx + road_wobble

        # обочины (трапеция)
        fb.line(road_c - 8, ROAD_TOP, 2, HEIGHT - 1, WHITE)
        fb.line(road_c + 8, ROAD_TOP, WIDTH - 3, HEIGHT - 1, WHITE)

        # разметка
        for i in range(6):
            t = ((i * 40 + stripe) % 240) / 240.0
            y = int(ROAD_TOP + t * (HEIGHT - ROAD_TOP))
            w = 2 + int(t * 14)
            fb.rect(road_c - w // 2, y, w, 6, WHITE)
        stripe = (stripe + 6 + speed * 2) % 240

        # твой мото
        mx = cx + x_pos
        fb.rect(mx, MOTO_Y + 8, 6, 12, YELLOW)
        fb.rect(mx - 3 + tilt // 2, MOTO_Y, 12, 8, YELLOW)
        fb.rect(mx + tilt, MOTO_Y - 6, 6, 6, YELLOW)

        # соперник едет вниз
        rival_y += 2 + speed
        ry = int(ROAD_TOP + rival_y)
        if rival_y > 190:
            rival_y = -20
            rival_x = random.randint(-34, 34)
            score += 1
            accel += 0.06
            speed = int(accel)

        if rival_y > 0:
            # интерполяция ширины дороги для позиции соперника
            t = rival_y / 190.0
            spread = 4 + int(t * 44)
            rx = road_c + int(rival_x * t)
            fb.rect(rx - 3, ry, 12, 8, RED)
            fb.rect(rx, ry + 8, 6, 12, RED)

        # вираж трассы
        road_wobble += wob_dir
        if road_wobble > 18 or road_wobble < -18:
            wob_dir = -wob_dir

        # столкновения
        crashed = False
        if x_pos > 44 or x_pos < -44:
            crashed = True  # вылетел за обочину
        if (rival_y > 150 and abs(x_pos - int(rival_x * (rival_y / 190.0))) < 12):
            crashed = True

        if crashed:
            fb.fill(BLACK)
            retro.text2_center("GAME OVER", 90, RED)
            retro.text2_center("SCORE " + str(score), 120, WHITE)
            disp.show()
            time.sleep(1)
            retro.wait_press()
            return

        disp.show()
        time.sleep_ms(55)
