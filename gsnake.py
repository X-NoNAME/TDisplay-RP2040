# gsnake.py: Змейка (порт PicoSnake от Twan37), управление относительное:
# кнопка A - поворот влево, кнопка B - поворот вправо
import random
import time
import retro
from retro import fb, disp, WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED

SEG = 8                      # размер клетки
COLS = WIDTH // SEG          # 30
ROWS = (HEIGHT - 16) // SEG  # 14 (верхние 16px под очки)
OFF_Y = 16

UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3


def main():
    snake = [[COLS // 2, ROWS // 2]]
    d = RIGHT
    food = [random.randrange(COLS), random.randrange(ROWS)]
    length = 3
    score = 0
    last = time.ticks_ms()
    speed = 160               # мс на шаг

    while True:
        retro.check_exit()

        now = time.ticks_ms()
        if time.ticks_diff(now, last) >= speed:
            last = now
            # повороты относительно направления
            if retro.a_pressed():
                d = (d + 3) % 4
            elif retro.b_pressed():
                d = (d + 1) % 4

            hx, hy = snake[-1]
            if d == UP:
                hy -= 1
            elif d == DOWN:
                hy += 1
            elif d == LEFT:
                hx -= 1
            else:
                hx += 1

            # столкновения
            if hx < 0 or hy < 0 or hx >= COLS or hy >= ROWS or [hx, hy] in snake:
                retro.game_over("LEN " + str(len(snake)))
                return

            snake.append([hx, hy])
            if [hx, hy] == food:
                score += 10
                if speed > 70:
                    speed -= 4
                while food in snake:
                    food = [random.randrange(COLS), random.randrange(ROWS)]
            else:
                snake.pop(0)

        fb.fill(BLACK)
        fb.text(str(score), 2, 4, WHITE)
        # еда
        fb.fill_rect(food[0] * SEG + 1, OFF_Y + food[1] * SEG + 1, SEG - 2, SEG - 2, RED)
        # змейка
        for i, (x, y) in enumerate(snake):
            c = GREEN if i < len(snake) - 1 else WHITE
            fb.fill_rect(x * SEG + 1, OFF_Y + y * SEG + 1, SEG - 2, SEG - 2, c)
        disp.show()
        time.sleep_ms(5)
