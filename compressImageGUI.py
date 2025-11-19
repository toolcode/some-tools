import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

VALID_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")

def compress_to_target_size(input_path, output_path, target_mb):
    target_bytes = target_mb * 1024 * 1024

    with Image.open(input_path) as img:
        # 如果是 PNG 并且有透明通道
        if img.format == "PNG" and ("A" in img.getbands() or "transparency" in img.info):
            # 尝试用 optimize 压缩
            img.save(output_path, format="PNG", optimize=True)
            # 不能精确控制大小，可能需要多次尝试或外部工具
        else:
            # 其他格式或无透明
            if img.format == "PNG":
                img = img.convert("RGB")  # 转 JPEG
            # 二分法寻找最佳 JPEG 质量
            low, high = 5, 95
            best_quality = 95
            while low <= high:
                q = (low + high) // 2
                img.save(output_path, "JPEG", quality=q)
                if os.path.getsize(output_path) > target_bytes:
                    high = q - 1
                else:
                    best_quality = q
                    low = q + 1
            img.save(output_path, "JPEG", quality=best_quality)


def process_directory(input_dir, output_dir, target_mb, min_mb):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(input_dir)
    count = 0

    for name in files:
        ext = os.path.splitext(name)[1].lower()
        if ext not in VALID_EXT:
            continue  # 跳过非图片

        input_path = os.path.join(input_dir, name)
        size_mb = os.path.getsize(input_path) / (1024 * 1024)

        if size_mb < min_mb:
            continue  # 跳过小于阈值的图片

        output_path = os.path.join(output_dir, name)
        compress_to_target_size(input_path, output_path, target_mb)
        count += 1

    return count


# ---------------- GUI 部分 ----------------
def select_input():
    folder = filedialog.askdirectory()
    if folder:
        input_var.set(folder)

def select_output():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)

def run():
    input_dir = input_var.get()
    output_dir = output_var.get()

    try:
        target_mb = float(target_var.get())
        min_mb = float(min_var.get())
    except ValueError:
        messagebox.showerror("错误", "请输入正确的数字")
        return

    if not os.path.isdir(input_dir):
        messagebox.showerror("错误", "输入路径无效")
        return

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    count = process_directory(input_dir, output_dir, target_mb, min_mb)
    messagebox.showinfo("完成", f"压缩完成，共处理 {count} 张图片。")


# ---------------- Tkinter 界面 ----------------
root = tk.Tk()
root.title("图片压缩器（按目标大小 MB）")

input_var = tk.StringVar()
output_var = tk.StringVar()
target_var = tk.StringVar(value="1")  # 默认压缩到 1MB
min_var = tk.StringVar(value="1")     # 默认只压缩大于 1MB 的文件

tk.Label(root, text="输入文件夹：").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=input_var, width=40).grid(row=0, column=1)
tk.Button(root, text="选择", command=select_input).grid(row=0, column=2)

tk.Label(root, text="输出文件夹：").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=output_var, width=40).grid(row=1, column=1)
tk.Button(root, text="选择", command=select_output).grid(row=1, column=2)

tk.Label(root, text="压缩目标大小 (MB)：").grid(row=2, column=0, sticky="e")
tk.Entry(root, textvariable=target_var, width=10).grid(row=2, column=1, sticky="w")

tk.Label(root, text="只压缩超过 (MB)：").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=min_var, width=10).grid(row=3, column=1, sticky="w")

tk.Button(root, text="开始压缩", command=run).grid(row=4, column=1, pady=10)

root.mainloop()
