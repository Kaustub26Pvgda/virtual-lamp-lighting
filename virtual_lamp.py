import tkinter as tk
import pygame
from PIL import Image, ImageTk
from itertools import cycle
pygame.mixer.init()
pygame.mixer.music.load("bgmusic.mp3")
pygame.mixer.music.play()  # play once, do not loop

root = tk.Tk()
root.title("Virtual Lamp Lighting Ceremony")

# wick coordinates for three levels 
coords1 = [(860, 2380), (1120, 2280), (1870, 2320), (2150, 2350), (1950, 2640), (1350, 2670)]
coords2 = [(945, 1565), (1230, 1440), (1840, 1400), (2150, 1520), (1950, 1700), (1280, 1750)]
coords3 = [(985, 805), (1210, 685), (1810, 685), (2110, 805), (1700, 820), (1300, 860)]
coords_levels = [coords1, coords2, coords3]  # store all levels here

# Load flame GIF
flame_gif = Image.open("flame-unscreen.gif")
pil_frames = []
gif_width, gif_height = flame_gif.size
try:
    while True:
        frame = flame_gif.copy().convert("RGBA")
        pil_frames.append(frame)
        flame_gif.seek(len(pil_frames))
except EOFError:
    pass

# Pre-converted Tkinter frames for animation
flame_frames = []
new_gif_width = int(gif_width * 0.13)
new_gif_height = int(gif_height * 0.13)
for f in pil_frames:
    flame_frames.append(ImageTk.PhotoImage(f.resize((new_gif_width, new_gif_height), Image.Resampling.LANCZOS)))
flame_frames_cycle = cycle(flame_frames)

# Maximize window
root.state('zoomed')
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Load lamp image
lamp_img_raw = Image.open("lamp.png")
img_width, img_height = lamp_img_raw.size
scale_factor = (screen_height * 0.8) / img_height
new_width = int(img_width * scale_factor)
new_height = int(img_height * scale_factor)
lamp_img_resized = lamp_img_raw.resize((new_width, new_height), Image.Resampling.LANCZOS)
lamp_img = ImageTk.PhotoImage(lamp_img_resized)

# Load and resize background image
bg_img_raw = Image.open("bg.png")
bg_img_resized = bg_img_raw.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
bg_img = ImageTk.PhotoImage(bg_img_resized)

# Create a blurred shadow under the lamp using PIL
from PIL import ImageDraw, ImageFilter
shadow_width = int(new_width * 0.7)
shadow_height = int(new_height * 0.18)
shadow_img = Image.new("RGBA", (shadow_width, shadow_height), (0, 0, 0, 0))
draw = ImageDraw.Draw(shadow_img)
draw.ellipse([(0, 0), (shadow_width, shadow_height)], fill=(30, 30, 30, 120))
shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(radius=10))
shadow_img_tk = ImageTk.PhotoImage(shadow_img)

# Canvas
canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_img, anchor="nw")  # Draw background first
canvas.create_image(screen_width // 2, screen_height // 2, image=lamp_img, anchor="center")  # Draw lamp on top

# Draw shadow below lamp
shadow_x = screen_width // 2 - shadow_width // 2
shadow_y = screen_height // 2 + new_height // 2 - int(shadow_height * 0.4)
canvas.create_image(shadow_x, shadow_y, image=shadow_img_tk, anchor="nw")

lamp_left = (screen_width - new_width) // 2
lamp_top = (screen_height - new_height) // 2

# 🔥 Store flames per level
flame_levels_ids = []   # list of lists, each level has its own image ids
flame_levels_refs = []  # keep PhotoImage refs
current_level = 0       # which click we’re on

def show_flame(event=None):
    global current_level
    if current_level >= len(coords_levels):
        return  # no more levels to light

    coords = coords_levels[current_level]
    flame_img_ids = []
    flame_img_refs = []

    duration = 500
    steps = 10
    step_delay = duration // steps

    def grow_flame(step=1):
        flame_img_refs.clear()
        for i, (wick_x_orig, wick_y_orig) in enumerate(coords):
            wick_x_scaled = int(wick_x_orig * scale_factor)
            wick_y_scaled = int(wick_y_orig * scale_factor)

            # Resize first frame for growth
            scaled_w = max(1, int(new_gif_width * step / steps))
            scaled_h = max(1, int(new_gif_height * step / steps))
            frame = pil_frames[0].resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(frame)

            x_pos = lamp_left + wick_x_scaled
            y_pos = lamp_top + wick_y_scaled - scaled_h // 2 + new_gif_height // 2

            if step == 1:
                flame_img_id = canvas.create_image(x_pos, y_pos, image=img, anchor="center")
                flame_img_ids.append(flame_img_id)
            else:
                canvas.coords(flame_img_ids[i], x_pos, y_pos)
                canvas.itemconfig(flame_img_ids[i], image=img)

            flame_img_refs.append(img)

        if step < steps:
            root.after(step_delay, lambda: grow_flame(step + 1))
        else:
            flame_levels_ids.append(flame_img_ids)
            flame_levels_refs.append(flame_img_refs)
            animate_flame()  # start animation once grown

    grow_flame()
    current_level += 1  # move to next level for next click

def animate_flame():
    frame = next(flame_frames_cycle)
    for flame_img_ids in flame_levels_ids:  # loop over all lit levels
        for flame_img_id in flame_img_ids:
            canvas.itemconfig(flame_img_id, image=frame)
    root.after(100, animate_flame)


# Remove canvas click binding
# Add buttons to trigger each lamp level
def trigger_level(level):
    global current_level
    if current_level == level:
        show_flame()

# Button positions (original image coordinates)
button_coords = [(4000, 2900), (4000, 2025), (4000, 1135)]
button_texts = ["Light Lamps", "Light Lamps", "Light Lamps"]
button_refs = []

# Load and resize diya image for buttons
diya_img_raw = Image.open("diya.png")
diya_img_resized = diya_img_raw.resize((60, 60), Image.Resampling.LANCZOS)
diya_img = ImageTk.PhotoImage(diya_img_resized)

button_refs = []
for i, (bx, by) in enumerate(button_coords):
    bx_scaled = int(bx * scale_factor)
    by_scaled = int(by * scale_factor)
    x_pos = lamp_left + bx_scaled
    y_pos = lamp_top + by_scaled
    btn = tk.Button(
        root,
        image=diya_img,
        command=lambda lvl=i: trigger_level(lvl),
        borderwidth=3,
        relief="ridge",
        highlightthickness=2,
        highlightbackground="#3a8dde",
        bg="#e0f7fa",
        activebackground="#b3e5fc"
    )
    button_window = canvas.create_window(x_pos, y_pos, window=btn)
    button_refs.append(btn)

# Keep a reference to the image to prevent garbage collection
root.diya_img = diya_img

root.mainloop()
