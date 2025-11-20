import tkinter as tk
from tkinter import ttk, colorchooser
import math


def rgb_to_cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 1
    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255
    k = min(c, m, y)
    c = (c - k) / (1 - k) if (1 - k) != 0 else 0
    m = (m - k) / (1 - k) if (1 - k) != 0 else 0
    y = (y - k) / (1 - k) if (1 - k) != 0 else 0
    return c, m, y, k


def cmyk_to_rgb(c, m, y, k):
    r = 255 * (1 - c) * (1 - k)
    g = 255 * (1 - m) * (1 - k)
    b = 255 * (1 - y) * (1 - k)
    return int(round(r)), int(round(g)), int(round(b))


def rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    diff = max_val - min_val

    # Hue calculation
    if diff == 0:
        h = 0
    elif max_val == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif max_val == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:  # max_val == b
        h = (60 * ((r - g) / diff) + 240) % 360

    # Saturation calculation
    s = 0 if max_val == 0 else (diff / max_val)

    # Value calculation
    v = max_val

    return h, s, v


def hsv_to_rgb(h, s, v):
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:  # 300 <= h < 360
        r, g, b = c, 0, x

    r = int(round((r + m) * 255))
    g = int(round((g + m) * 255))
    b = int(round((b + m) * 255))

    return r, g, b


class ColorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Конвертер цветов: CMYK ↔ RGB ↔ HSV')
        self.resizable(False, False)

        # Переменные для хранения значений цветов
        self.rgb = {c: tk.IntVar(value=128) for c in 'RGB'}
        self.cmyk = {c: tk.DoubleVar(value=0.0) for c in 'CMYK'}
        self.hsv = {'H': tk.DoubleVar(value=0.0),
                    'S': tk.DoubleVar(value=0.5),
                    'V': tk.DoubleVar(value=0.5)}

        # Флаг для предотвращения рекурсивных обновлений
        self.updating = False

        self.build_ui()
        self.update_from_rgb()

    def build_ui(self):
        main = ttk.Frame(self, padding=8)
        main.grid(row=0, column=0)

        # RGB Frame
        rgb_f = ttk.LabelFrame(main, text='RGB (0–255)')
        rgb_f.grid(row=0, column=0, padx=5, sticky='nsew')
        self.rgb_entries = {}
        self.rgb_scales = {}
        for i, c in enumerate('RGB'):
            ttk.Label(rgb_f, text=c).grid(row=i, column=0, padx=2, pady=2)

            scale = ttk.Scale(rgb_f, from_=0, to=255, variable=self.rgb[c])
            scale.grid(row=i, column=1, padx=2, pady=2, sticky='ew')
            scale.bind('<ButtonPress-1>', lambda e, cc=c: self.on_rgb_scale_press(cc))
            scale.bind('<ButtonRelease-1>', lambda e, cc=c: self.on_rgb_scale_release(cc))
            self.rgb_scales[c] = scale

            entry = ttk.Entry(rgb_f, width=6, textvariable=self.rgb[c])
            entry.grid(row=i, column=2, padx=2, pady=2)
            entry.bind('<Return>', lambda e, cc=c: self.on_rgb_entry_change(cc))
            self.rgb_entries[c] = entry

        # HSV Frame
        hsv_f = ttk.LabelFrame(main, text='HSV (H 0–360, S/V 0–1)')
        hsv_f.grid(row=0, column=1, padx=5, sticky='nsew')
        ranges = {'H': (0, 360), 'S': (0, 1), 'V': (0, 1)}
        labels = {'H': 'H', 'S': 'S', 'V': 'V'}
        self.hsv_entries = {}
        self.hsv_scales = {}
        for i, c in enumerate(['H', 'S', 'V']):
            lo, hi = ranges[c]
            ttk.Label(hsv_f, text=labels[c]).grid(row=i, column=0, padx=2, pady=2)

            scale = ttk.Scale(hsv_f, from_=lo, to=hi, variable=self.hsv[c])
            scale.grid(row=i, column=1, padx=2, pady=2, sticky='ew')
            scale.bind('<ButtonPress-1>', lambda e, cc=c: self.on_hsv_scale_press(cc))
            scale.bind('<ButtonRelease-1>', lambda e, cc=c: self.on_hsv_scale_release(cc))
            self.hsv_scales[c] = scale

            entry = ttk.Entry(hsv_f, width=7, textvariable=self.hsv[c])
            entry.grid(row=i, column=2, padx=2, pady=2)
            entry.bind('<Return>', lambda e, cc=c: self.on_hsv_entry_change(cc))
            self.hsv_entries[c] = entry

        # CMYK Frame
        cmyk_f = ttk.LabelFrame(main, text='CMYK (0–1)')
        cmyk_f.grid(row=0, column=2, padx=5, sticky='nsew')
        self.cmyk_entries = {}
        self.cmyk_scales = {}
        for i, c in enumerate('CMYK'):
            ttk.Label(cmyk_f, text=c).grid(row=i, column=0, padx=2, pady=2)

            scale = ttk.Scale(cmyk_f, from_=0.0, to=1.0, variable=self.cmyk[c])
            scale.grid(row=i, column=1, padx=2, pady=2, sticky='ew')
            scale.bind('<ButtonPress-1>', lambda e, cc=c: self.on_cmyk_scale_press(cc))
            scale.bind('<ButtonRelease-1>', lambda e, cc=c: self.on_cmyk_scale_release(cc))
            self.cmyk_scales[c] = scale

            entry = ttk.Entry(cmyk_f, width=7, textvariable=self.cmyk[c])
            entry.grid(row=i, column=2, padx=2, pady=2)
            entry.bind('<Return>', lambda e, cc=c: self.on_cmyk_entry_change(cc))
            self.cmyk_entries[c] = entry

        # Bottom controls
        bottom = ttk.Frame(main)
        bottom.grid(row=1, column=0, columnspan=3, pady=6, sticky='ew')

        self.swatch = ttk.Label(bottom, text='   ', width=24, relief='sunken', background='#808080')
        self.swatch.grid(row=0, column=0, padx=6, pady=2)

        ttk.Button(bottom, text='Выбрать цвет', command=self.pick_color).grid(row=0, column=1, padx=6, pady=2)

        self.warn = ttk.Label(bottom, text='', foreground='orange')
        self.warn.grid(row=0, column=2, padx=6, pady=2)

    # RGB handlers
    def on_rgb_scale_press(self, c):
        self.rgb_scales[c].bind('<Motion>', lambda e, cc=c: self.on_rgb_scale_drag(cc))

    def on_rgb_scale_release(self, c):
        self.rgb_scales[c].unbind('<Motion>')
        self.update_from_rgb()

    def on_rgb_scale_drag(self, c):
        if not self.updating:
            self.update_from_rgb()

    def on_rgb_entry_change(self, c):
        if not self.updating:
            try:
                value = int(self.rgb[c].get())
                value = max(0, min(255, value))
                self.rgb[c].set(value)
                self.update_from_rgb()
            except ValueError:
                pass

    # HSV handlers
    def on_hsv_scale_press(self, c):
        self.hsv_scales[c].bind('<Motion>', lambda e, cc=c: self.on_hsv_scale_drag(cc))

    def on_hsv_scale_release(self, c):
        self.hsv_scales[c].unbind('<Motion>')
        self.update_from_hsv()

    def on_hsv_scale_drag(self, c):
        if not self.updating:
            self.update_from_hsv()

    def on_hsv_entry_change(self, c):
        if not self.updating:
            try:
                value = float(self.hsv[c].get())
                ranges = {'H': (0, 360), 'S': (0, 1), 'V': (0, 1)}
                lo, hi = ranges[c]
                value = max(lo, min(hi, value))
                self.hsv[c].set(value)
                self.update_from_hsv()
            except ValueError:
                pass

    # CMYK handlers
    def on_cmyk_scale_press(self, c):
        self.cmyk_scales[c].bind('<Motion>', lambda e, cc=c: self.on_cmyk_scale_drag(cc))

    def on_cmyk_scale_release(self, c):
        self.cmyk_scales[c].unbind('<Motion>')
        self.update_from_cmyk()

    def on_cmyk_scale_drag(self, c):
        if not self.updating:
            self.update_from_cmyk()

    def on_cmyk_entry_change(self, c):
        if not self.updating:
            try:
                value = float(self.cmyk[c].get())
                value = max(0.0, min(1.0, value))
                self.cmyk[c].set(value)
                self.update_from_cmyk()
            except ValueError:
                pass

    def update_from_rgb(self):
        if self.updating:
            return

        self.updating = True
        r, g, b = [self.rgb[x].get() for x in 'RGB']

        # RGB → HSV
        h, s, v = rgb_to_hsv(r, g, b)
        self.hsv['H'].set(round(h, 1))
        self.hsv['S'].set(round(s, 3))
        self.hsv['V'].set(round(v, 3))

        # RGB → CMYK
        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.cmyk['C'].set(round(c, 3))
        self.cmyk['M'].set(round(m, 3))
        self.cmyk['Y'].set(round(y, 3))
        self.cmyk['K'].set(round(k, 3))

        self.set_swatch(r, g, b)
        self.warn.config(text='')
        self.updating = False

    def update_from_hsv(self):
        if self.updating:
            return

        self.updating = True
        h = float(self.hsv['H'].get())
        s = float(self.hsv['S'].get())
        v = float(self.hsv['V'].get())

        r, g, b = hsv_to_rgb(h, s, v)

        # Проверка на выход за границы RGB
        clipped = not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255)
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

        self.rgb['R'].set(r)
        self.rgb['G'].set(g)
        self.rgb['B'].set(b)

        # RGB → CMYK
        c, m, y, k = rgb_to_cmyk(r, g, b)
        self.cmyk['C'].set(round(c, 3))
        self.cmyk['M'].set(round(m, 3))
        self.cmyk['Y'].set(round(y, 3))
        self.cmyk['K'].set(round(k, 3))

        self.set_swatch(r, g, b)
        self.warn.config(text='RGB усечён!' if clipped else '')
        self.updating = False

    def update_from_cmyk(self):
        if self.updating:
            return

        self.updating = True
        c, m, y, k = [float(self.cmyk[x].get()) for x in 'CMYK']

        r, g, b = cmyk_to_rgb(c, m, y, k)
        self.rgb['R'].set(r)
        self.rgb['G'].set(g)
        self.rgb['B'].set(b)

        # RGB → HSV
        h, s, v = rgb_to_hsv(r, g, b)
        self.hsv['H'].set(round(h, 1))
        self.hsv['S'].set(round(s, 3))
        self.hsv['V'].set(round(v, 3))

        self.set_swatch(r, g, b)
        self.warn.config(text='')
        self.updating = False

    def pick_color(self):
        if self.updating:
            return

        current_rgb = f'#{self.rgb["R"].get():02x}{self.rgb["G"].get():02x}{self.rgb["B"].get():02x}'

        col = colorchooser.askcolor(color=current_rgb, title='Выберите цвет')
        if col and col[0]:
            self.updating = True
            r, g, b = [int(round(x)) for x in col[0]]
            self.rgb['R'].set(r)
            self.rgb['G'].set(g)
            self.rgb['B'].set(b)

            # Обновляем все значения из RGB
            h, s, v = rgb_to_hsv(r, g, b)
            self.hsv['H'].set(round(h, 1))
            self.hsv['S'].set(round(s, 3))
            self.hsv['V'].set(round(v, 3))

            c, m, y, k = rgb_to_cmyk(r, g, b)
            self.cmyk['C'].set(round(c, 3))
            self.cmyk['M'].set(round(m, 3))
            self.cmyk['Y'].set(round(y, 3))
            self.cmyk['K'].set(round(k, 3))

            self.set_swatch(r, g, b)
            self.warn.config(text='')
            self.updating = False

    def set_swatch(self, r, g, b):
        color_hex = f'#{int(r):02x}{int(g):02x}{int(b):02x}'
        self.swatch.config(background=color_hex)


if __name__ == '__main__':
    app = ColorApp()
    app.mainloop()