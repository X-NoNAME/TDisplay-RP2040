"""Быстрый вывод на LILYGO T-Display RP2040 (ST7789 240x135).

Отрисовка идёт в C-ускоренный FrameBuffer (RGB565), на экран кадр
уходит одной большой SPI-записью. Без Python-циклов на пиксель.
"""
import time
import framebuf
from machine import Pin, SPI

WIDTH = 135
HEIGHT = 240

_landscape = False

BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
YELLOW = 0xFFE0
CYAN = 0x07FF
ORANGE = 0xFC10

# Пины T-Display RP2040
_dc = Pin(1, Pin.OUT)
_cs = Pin(5, Pin.OUT)
_rst = Pin(0, Pin.OUT)
_bl = Pin(4, Pin.OUT, value=1)      # подсветка
_pwr = Pin(22, Pin.OUT, value=1)    # питание панели
_spi = SPI(0, baudrate=62_500_000, polarity=0, phase=0,
           sck=Pin(2), mosi=Pin(3), miso=None)

# Экранный буфер: все рисуем сюда, потом show()
buf = bytearray(WIDTH * HEIGHT * 2)
fb = framebuf.FrameBuffer(buf, WIDTH, HEIGHT, framebuf.RGB565)

# Окно (пересчитывается в set_mode)
_CASET = bytes((0x00, 52, (52 + WIDTH - 1) >> 8, (52 + WIDTH - 1) & 0xFF))
_RASET = bytes((0x00, 40, (40 + HEIGHT - 1) >> 8, (40 + HEIGHT - 1) & 0xFF))


def _apply_window(madctl, xs, ys, w, h):
    global _CASET, _RASET, WIDTH, HEIGHT, _landscape, fb
    _cmd(0x36, bytes((madctl,)))
    _CASET = bytes((0x00, xs, (xs + w - 1) >> 8, (xs + w - 1) & 0xFF))
    _RASET = bytes((0x00, ys, (ys + h - 1) >> 8, (ys + h - 1) & 0xFF))
    WIDTH, HEIGHT = w, h
    _landscape = WIDTH > HEIGHT
    fb = framebuf.FrameBuffer(buf, WIDTH, HEIGHT, framebuf.RGB565)


def set_mode(landscape=False):
    """Портрет (по умолчанию) или альбом 240x135 (как любили в Invaders)."""
    _apply_window(0xA0 if landscape else 0x00,
                  40 if landscape else 52,
                  52 if landscape else 40,
                  240 if landscape else 135,
                  135 if landscape else 240)

# Известно-рабочая init-последовательность (как в st7789py)
_INIT = (
    (b'\x11', b'', 120),                     # SLPOUT
    (b'\x13', b'', 0),                       # NORON
    (b'\xb6', b'\x0a\x82', 0),
    (b'\x3a', b'\x55', 10),                  # RGB565
    (b'\xb2', b'\x0c\x0c\x00\x33\x33', 0),
    (b'\xb7', b'\x35', 0),
    (b'\xbb', b'\x28', 0),
    (b'\xc0', b'\x0c', 0),
    (b'\xc2', b'\x01\xff', 0),
    (b'\xc3', b'\x10', 0),
    (b'\xc4', b'\x20', 0),
    (b'\xc6', b'\x0f', 0),
    (b'\xd0', b'\xa4\xa1', 0),
    (b'\xe0', b'\xd0\x00\x02\x07\x0a\x28\x32\x44\x42\x06\x0e\x12\x14\x17', 0),
    (b'\xe1', b'\xd0\x00\x02\x07\x0a\x28\x31\x54\x47\x0e\x1c\x17\x1b\x1e', 0),
    (b'\x21', b'', 0),                       # INVON
    (b'\x29', b'', 120),                     # DISPON
)


def _cmd(c, data=b'', delay=0):
    if not isinstance(c, bytes):
        c = bytes((c,))
    _cs(0)
    _dc(0)
    _spi.write(c)
    _dc(1)
    if data:
        _spi.write(data)
    _cs(1)
    if delay:
        time.sleep_ms(delay)


def init():
    _rst(0)
    time.sleep_ms(50)
    _rst(1)
    time.sleep_ms(120)
    _cmd(0x01, delay=150)        # SWRESET
    for c, d, delay in _INIT:
        _cmd(c, d if d else b'', delay)
    set_mode(False)


def show():
    """Отправить кадр на экран."""
    _cs(0)
    _dc(0)
    _spi.write(b'\x2a')          # CASET
    _dc(1)
    _spi.write(_CASET)
    _dc(0)
    _spi.write(b'\x2b')          # RASET
    _dc(1)
    _spi.write(_RASET)
    _dc(0)
    _spi.write(b'\x2c')          # RAMWR
    _dc(1)
    _spi.write(buf)
    _cs(1)


def mono_rgb(data, w, h, color, scale=1, bg=None, transpose=False):
    """MONO_HLSB спрайт -> RGB565 FrameBuffer (0 = прозрачный, если bg=None)."""
    if not isinstance(data, bytearray):
        data = bytearray(data)  # FrameBuffer требует изменяемый буфер
    src = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
    if transpose:
        W, H = h * scale, w * scale
        out = framebuf.FrameBuffer(bytearray(W * H * 2), W, H, framebuf.RGB565)
        if bg is not None:
            out.fill(bg)
        for y in range(h):
            for x in range(w):
                if src.pixel(x, y):
                    tx, ty = (h - 1 - y) * scale, x * scale
                    if scale == 1:
                        out.pixel(tx, ty, color)
                    else:
                        out.rect(tx, ty, scale, scale, color)
        return out
    W, H = w * scale, h * scale
    out = framebuf.FrameBuffer(bytearray(W * H * 2), W, H, framebuf.RGB565)
    if bg is not None:
        out.fill(bg)
    for y in range(h):
        for x in range(w):
            if src.pixel(x, y):
                if scale == 1:
                    out.pixel(x, y, color)
                else:
                    out.rect(x * scale, y * scale, scale, scale, color)
    return out
