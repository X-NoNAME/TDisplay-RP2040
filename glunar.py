# glunar.py: Лунный модуль (порт "Lunar Module" от Kuba & Stepan)
# A или B - тяга двигателя. Посадись на площадку медленно!
import time
import retro
from retro import fb, disp, WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED, YELLOW, CYAN


def main():
    fb.fill(BLACK)
    retro.text2_center("LUNAR MODULE", 30, CYAN)
    retro.text2_center("A< >B", 60, WHITE)
    retro.text2_center("BOTH:THRUST", 80, WHITE)
    disp.show()
    time.sleep(1.5)

    def new_level(lvl):
        return dict(x=4, y=4, vx=1 + lvl, gravity=1, fuel=25 + lvl * 5)

    st = new_level(1)
    level = 1
    pad_x = 20 + (level * 17) % 90   # позиция площадки (0..110)

    while True:
        retro.check_exit()

        fire = False
        a = retro.a_pressed()
        b = retro.b_pressed()
        if a and b and st["fuel"] > 0:
            fire = True
            st["gravity"] -= 5
            st["fuel"] -= 1
        elif a:
            st["vx"] -= 0.4
        elif b:
            st["vx"] += 0.4
        if st["vx"] > 4:
            st["vx"] = 4
        if st["vx"] < -4:
            st["vx"] = -4

        fb.fill(BLACK)
        fb.text("FUEL " + str(st["fuel"]), 2, HEIGHT - 10, YELLOW)
        fb.text("v" + str(st["gravity"]), WIDTH - 40, 4, WHITE)

        x = int(st["x"])   # framebuf требует целые
        y = int(st["y"])
        # модуль
        fb.rect(12 + x, 6 + y, 10, 10, WHITE)
        fb.vline(10 + x, 10 + y, 10, WHITE)
        fb.vline(22 + x, 10 + y, 10, WHITE)
        fb.rect(14 + x, 2 + y, 6, 8, WHITE)
        if fire:
            fb.vline(16 + x, 22 + y, 14, RED)
            fb.vline(18 + x, 22 + y, 10, YELLOW)

        # площадка
        fb.rect(pad_x, HEIGHT - 8, 28, 4, GREEN)

        # физика
        st["x"] += st["vx"]
        st["y"] = int(st["y"]) + 2 + st["gravity"] // 10
        st["gravity"] += 1

        # отскок от краёв по горизонтали
        if st["x"] < 0 or st["x"] > WIDTH - 30:
            st["vx"] = -st["vx"]

        # посадка
        if st["y"] >= HEIGHT - 22:
            if pad_x - 4 <= st["x"] <= pad_x + 22 and st["gravity"] < 4:
                fb.fill(BLACK)
                retro.text2_center("LANDING OK!", 40, GREEN)
                retro.text2_center("LEVEL " + str(level + 1), 64, WHITE)
                disp.show()
                time.sleep(2)
                level += 1
                st = new_level(level)
                pad_x = 20 + (level * 17) % 90
                retro.wait_release()
            else:
                fb.fill(BLACK)
                retro.text2_center("GAME OVER", 44, RED)
                retro.text2_center("LEVEL " + str(level), 68, WHITE)
                disp.show()
                time.sleep(1)
                retro.wait_press()
                return

        disp.show()
        time.sleep_ms(90)
