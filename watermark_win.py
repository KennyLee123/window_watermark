import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# Supported formats
SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
PADDING   = 20      # px gap from the edge
LOGO_MAX  = 0.20    # logo width capped at 20% of photo width

def pick_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return path

def pick_folder(title):
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    path = filedialog.askdirectory(title=title)
    root.destroy()
    return path

def alert(title, msg):
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    messagebox.showinfo(title, msg)
    root.destroy()

def stamp(photo_path, logo, output_dir):
    with Image.open(photo_path).convert("RGBA") as photo:
        pw, ph = photo.size

        # Scale logo based on the shorter side of the photo
        lw, lh = logo.size
        short_side = min(pw, ph)
        max_size   = int(short_side * LOGO_MAX)
        
        # Calculate scale to ensure width fits the max_size limit
        scale      = max_size / lw
        new_lw, new_lh = int(lw * scale), int(lh * scale)
        resized_logo = logo.resize((new_lw, new_lh), Image.LANCZOS)

        # Bottom-right corner position
        x = pw - new_lw - PADDING
        y = ph - new_lh - PADDING

        composite = photo.copy()
        composite.paste(resized_logo, (x, y), resized_logo)

        # Save in original format when possible, else PNG
        ext  = os.path.splitext(photo_path)[1].lower()
        name = os.path.basename(photo_path)
        if ext in {".jpg", ".jpeg"}:
            composite = composite.convert("RGB")
            out_path  = os.path.join(output_dir, name)
            composite.save(out_path, "JPEG", quality=95)
        else:
            out_name = os.path.splitext(name)[0] + ".png"
            out_path = os.path.join(output_dir, out_name)
            composite.save(out_path, "PNG")

def main():
    # ── Step 1: Pick logo ──────────────────────────────────────────────────────
    logo_path = pick_file(
        "Select your logo (PNG recommended)",
        [("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp")]
    )
    if not logo_path:
        return

    try:
        logo = Image.open(logo_path).convert("RGBA")
    except Exception as e:
        alert("Error", f"Could not open logo: {e}")
        return

    # ── Step 2: Pick photos folder ─────────────────────────────────────────────
    photos_dir = pick_folder("Select the folder containing your photos")
    if not photos_dir:
        return

    # ── Step 3: Create output folder ───────────────────────────────────────────
    output_dir = os.path.join(photos_dir, "watermarked")
    os.makedirs(output_dir, exist_ok=True)

    # ── Step 4: Process every supported image ──────────────────────────────────
    files = [
        f for f in os.listdir(photos_dir)
        if os.path.splitext(f)[1].lower() in SUPPORTED
    ]

    if not files:
        alert("No photos found", f"No supported images were found in:\n{photos_dir}")
        return

    errors = []
    for fname in files:
        try:
            stamp(os.path.join(photos_dir, fname), logo, output_dir)
        except Exception as e:
            errors.append(f"{fname}: {e}")

    # ── Step 5: Done! ──────────────────────────────────────────────────────────
    msg = f"✅ Done! {len(files) - len(errors)}/{len(files)} photos watermarked.\n\nSaved to:\n{output_dir}"
    if errors:
        msg += "\n\n⚠️ Errors:\n" + "\n".join(errors)
    alert("Watermark Complete", msg)

if __name__ == "__main__":
    main()