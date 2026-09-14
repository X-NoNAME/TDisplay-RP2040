# retro.py: общий слой для игр на LILYGO T-Display RP2040
import time
import framebuf
from machine import Pin, reset
import fastdisplay as disp
from fastdisplay import BLACK, WHITE, RED, GREEN, YELLOW, CYAN, ORANGE


class _FBProxy:
    """Динамический доступ к текущему framebuf (после смены ориентации)."""
    def __getattr__(self, name):
        return getattr(disp.fb, name)


fb = _FBProxy()

WIDTH = disp.WIDTH    # портрет 135 (динамически из fastdisplay)
HEIGHT = disp.HEIGHT  # 240

A = Pin(6, Pin.IN, Pin.PULL_UP)   # кнопка 1
B = Pin(7, Pin.IN, Pin.PULL_UP)   # кнопка 2


def a_pressed():
    return A.value() == 0


def b_pressed():
    return B.value() == 0


def both():
    return A.value() == 0 and B.value() == 0


_exit_since = 0


def check_exit():
    """Выход из игры: держать обе кнопки ~1.2 c -> reset -> меню."""
    global _exit_since
    if both():
        now = time.ticks_ms()
        if _exit_since == 0:
            _exit_since = now
        elif time.ticks_diff(now, _exit_since) > 1200:
            reset()
    else:
        _exit_since = 0


def wait_release():
    """Ждать отпускания всех кнопок (чтобы запуск не считался нажатием)."""
    while A.value() == 0 or B.value() == 0:
        time.sleep_ms(10)


def wait_press():
    """Ждать нажатия любой кнопки, вернуть после отпускания."""
    while A.value() != 0 and B.value() != 0:
        time.sleep_ms(10)
    wait_release()


_text_cache = {}


def text2(s, x, y, color=WHITE, bg=None):
    """Текст с 2x масштабом (16px), кэшируется. bg=None -> прозрачный фон."""
    key = (s, color, bg)
    if len(_text_cache) > 40:
        _text_cache.clear()   # защита от переполнения RAM динамическими строками
    img = _text_cache.get(key)
    if img is None:
        w = 8 * len(s)
        b = bytearray(w)  # 8 строк по w пикселей, MONO_HLSB
        tmp = framebuf.FrameBuffer(b, w, 8, framebuf.MONO_HLSB)
        tmp.text(s, 0, 0, 1)
        img = disp.mono_rgb(b, w, 8, color, 2, bg=bg)
        _text_cache[key] = img
    fb.blit(img, x, y, 0 if bg is None else -1)


def text1(s, x, y, color=WHITE):
    """Обычный 8px текст — для часто меняющихся чисел (без кэша)."""
    fb.text(s, x, y, color)


def text2_center(s, y, color=WHITE):
    text2(s, (WIDTH - 16 * len(s)) // 2, y, color)


def game_over(score_text=""):
    fb.fill(BLACK)
    text2_center("GAME OVER", 44, RED)
    if score_text:
        text2_center(score_text, 68, WHITE)
    disp.show()
    time.sleep_ms(400)
    wait_press()
