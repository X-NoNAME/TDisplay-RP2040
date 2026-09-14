# Pico Games — LILYGO T-Display RP2040

Игровая консоль на 5 игр для платы **LILYGO T-Display RP2040** (встроенный экран
ST7789 1.14" 135×240, две кнопки на плате).

Порты игр из коллекции [PicoRetroGamingSystem](https://github.com/YouMakeTech/PicoRetroGamingSystem)
(она рассчитана на внешний OLED SSD1306 и 6 кнопок), переписанные под встроенный
экран и две кнопки T-Display RP2040.

- Портретное меню выбора игр (инверсная строка-курсор)
- Быстрый рендер: весь кадр рисуется в C-ускоренный `FrameBuffer` (RGB565)
  и уходит на экран **одной SPI-транзакцией** (~65 КБ) — без попиксельного Python
- Выход из любой игры — удержать обе кнопки ~1.2 с (плата перезагружается в меню)
- Официальный MicroPython, никаких кастомных прошивок

## Игры и управление

| Игра | Ориентация | Кнопка 1 (GP6) | Кнопка 2 (GP7) | Обе кнопки |
|------|-----------|----------------|----------------|------------|
| **Invaders** | альбом 240×135 | корабль вверх | корабль вниз | выход |
| **Pong** | портрет | ракетка влево | ракетка вправо | выход |
| **Snake** | портрет | поворот влево | поворот вправо | выход |
| **Speed** | портрет | руль влево | руль вправо | выход |
| **Lunar** | портрет | тяга влево | тяга вправо | тяга вверх + выход |

В меню: кнопка 1 — вверх, кнопка 2 — вниз, обе — запустить.
В Invaders и Pong стрельба автоматическая, как в оригиналах.

## Железо

- LILYGO T-Display RP2040 (проверено на v1.2)
- Кабель USB-C с передачей данных

Распиновка платы (зафиксирована в `fastdisplay.py`):

| Назначение | GPIO |
|------------|------|
| ST7789 SCLK (SPI0) | 2 |
| ST7789 MOSI (SPI0) | 3 |
| ST7789 DC | 1 |
| ST7789 CS | 5 |
| ST7789 RST | 0 |
| Подсветка | 4 |
| Питание панели | 22 |
| Кнопка 1 / 2 | 6 / 7 |
| Красный светодиод | 25 |

## Установка MicroPython

Нужен обычный MicroPython для Raspberry Pi Pico / RP2040 (тестировалось на
**v1.29.0**; подойдут и более поздние сборки RPI_PICO).

1. Скачайте свежий `*.uf2` со страницы <https://micropython.org/download/RPI_PICO/>
2. Зажмите кнопку **BOOTSEL** на плате и подключите USB-кабель
   (или из уже работающего MicroPython выполните `machine.bootloader()`)
3. Появится диск `RPI-RP2` — скопируйте на него скачанный `.uf2`
4. Плата сама перезагрузится с новой прошивкой

Проверка (REPL по USB):

```
python3 -m mpremote connect /dev/cu.usbmodem* exec "import sys; print(sys.version)"
```

## Установка игр

### Вариант 1: mpremote (рекомендуется)

```bash
pip install mpremote

# из папки проекта
mpremote cp . :
mpremote reset
```

После перезагрузки на экране появится меню.

## Структура проекта

```
main.py         автозапуск меню
menu.py         меню выбора игр
retro.py        общий слой: кнопки, шрифты, выход из игры
fastdisplay.py  драйвер ST7789 + быстрый FrameBuffer-рендер,
                set_mode() портрет/альбом
ginvaders.py    Space Invaders (альбомная, порт picoinvaders)
gpong.py        Pong
gsnake.py       Snake
gfullspeed.py   Speed (мотогонка)
glunar.py       Lunar Module (посадка лунного модуля)
```

## Как добавить свою игру

1. Создайте `gмоя_игра.py` с функцией `main()`:

```python
import retro
from retro import fb, disp, WIDTH, HEIGHT, BLACK, WHITE

def main():
    while True:
        retro.check_exit()          # выход: обе кнопки 1.2 c -> reset -> меню

        if retro.a_pressed():       # кнопка GP6
            pass
        if retro.b_pressed():       # кнопка GP7
            pass

        fb.fill(BLACK)
        fb.text("HELLO", 8, 8, WHITE)   # 8px текст — для динамических чисел
        retro.text2("GAME", 8, 30)      # 16px кэшируемый — для статичных надписей
        disp.show()                     # отправить кадр на экран
```

2. Добавьте строку в список `GAMES` в `menu.py`.

Правила хорошего тона:
- `retro.check_exit()` — в начале каждого прохода цикла
- координаты для `fb.*` — только целые числа (float роняет отрисовку)
- меняющиеся каждый кадр числа рисуйте `fb.text`/`retro.text1`,
  статичные надписи — `retro.text2` (кэш ограничен 40 записями)

## Используемые проекты и ссылки

Исходники игр и документация:

- **PicoRetroGamingSystem** (оригинальная коллекция игр) —
  <https://github.com/YouMakeTech/PicoRetroGamingSystem>
  (видео: [YouTube](https://youtu.be/VYeIR5n5Few),
  инструкция по сборке: [youmaketech.com](https://www.youmaketech.com/raspberry-pi-pico-retrogaming-system/))
- **Pico Invaders** — из коллекции
  [printnplay/Pico-MicroPython](https://github.com/printnplay/Pico-MicroPython)
- **Pong** — Vincent Mistler, [YouMakeTech](https://github.com/YouMakeTech)
- **Snake** — Twan37, [Twan37/PicoSnake](https://github.com/Twan37/PicoSnake)
- **Full Speed** и **Lunar Module** — Kuba & Stepan,
  [Hellmole/Raspberry-pi-pico-games](https://github.com/Hellmole/Raspberry-pi-pico-games)
- Инициализационная последовательность и тайминги ST7789 — по конфигам
  [russhughes/st7789py_mpy](https://github.com/russhughes/st7789py_mpy)
  (быстрая C-версия драйвера: [russhughes/st7789_mpy](https://github.com/russhughes/st7789_mpy))

Платформа и инструменты:

- Плата: [LILYGO T-Display RP2040](https://www.lilygo.cc/products/t-display-rp2040) —
  официальные примеры и схема:
  [Xinyuan-LilyGO/LILYGO-T-display-RP2040](https://github.com/Xinyuan-LilyGO/LILYGO-T-display-RP2040)
- Прошивка: [MicroPython для RP2040](https://micropython.org/download/RPI_PICO/)
- Загрузка файлов: [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)