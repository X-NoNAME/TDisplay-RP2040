# menu.py: меню выбора игр для LILYGO T-Display RP2040 (портрет)
# A (GP6) - вверх, B (GP7) - вниз, обе кнопки - запустить
import time
import retro
from retro import fb, disp, WIDTH, HEIGHT, BLACK, WHITE, YELLOW, CYAN

GAMES = [
    ("INVADERS", "ginvaders"),
    ("PONG", "gpong"),
    ("SNAKE", "gsnake"),
    ("SPEED", "gfullspeed"),
    ("LUNAR", "glunar"),
]


def main():
    disp.init()
    disp.set_mode(False)   # меню всегда в портрете
    cur = 0
    prev_a = prev_b = 1
    last_move = 0

    while True:
        fb.fill(BLACK)
        retro.text2("PICO", (WIDTH - 64) // 2, 10, YELLOW)
        retro.text2("GAMES", (WIDTH - 80) // 2, 28, YELLOW)

        y = 66
        for i, (name, _) in enumerate(GAMES):
            x = (WIDTH - 16 * len(name)) // 2
            if i == cur:
                retro.text2(name, x, y, BLACK, bg=WHITE)
            else:
                retro.text2(name, x, y, WHITE)
            y += 26

        fb.text("A:up B:down", (WIDTH - 88) // 2, 212, CYAN)
        fb.text("BOTH:run|exit", (WIDTH - 104) // 2, 226, CYAN)
        disp.show()

        a = retro.A.value()
        b = retro.B.value()
        now = time.ticks_ms()

        # запуск: обе кнопки
        if a == 0 and b == 0:
            time.sleep_ms(30)  # антидребезг
            retro.wait_release()
            mod = __import__(GAMES[cur][1])
            mod.main()
            continue

        # навигация по фронту нажатия
        if now - last_move > 220:
            if a == 0 and prev_a == 1:
                cur = (cur - 1) % len(GAMES)
                last_move = now
            elif b == 0 and prev_b == 1:
                cur = (cur + 1) % len(GAMES)
                last_move = now
        prev_a, prev_b = a, b
        time.sleep_ms(10)
