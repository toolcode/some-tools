import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ExifTags
from datetime import datetime
import os
import threading
from queue import Queue

class BatchWatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量图片水印工具")
        self.root.geometry("900x650")
        
        # 初始化变量
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.font_path = tk.StringVar()
        self.status = tk.StringVar(value="准备就绪")
        self.position = tk.StringVar(value="右下")
        self.custom_text = tk.StringVar()
        self.font_size = tk.IntVar(value=0)
        self.margin = tk.IntVar(value=20)
        self.progress = tk.DoubleVar()
        self.file_queue = Queue()
        self.running = False

        # 创建界面组件
        self.create_widgets()
        
        # 设置默认字体路径
        self.set_default_font()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 输入目录选择
        ttk.Label(main_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1)
        ttk.Button(main_frame, text="浏览...", command=self.select_input_dir).grid(row=0, column=2)

        # 输出目录选择
        ttk.Label(main_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1)
        ttk.Button(main_frame, text="浏览...", command=self.select_output_dir).grid(row=1, column=2)

        # 字体选择
        ttk.Label(main_frame, text="选择字体:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.font_path, width=50).grid(row=2, column=1)
        ttk.Button(main_frame, text="浏览...", command=self.select_font).grid(row=2, column=2)

        # 水印设置
        settings_frame = ttk.LabelFrame(main_frame, text="水印设置", padding=10)
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        ttk.Label(settings_frame, text="位置:").grid(row=0, column=0)
        ttk.Combobox(settings_frame, textvariable=self.position, 
                    values=["右下", "左下", "左上", "右上"]).grid(row=0, column=1)

        ttk.Label(settings_frame, text="自定义文字:").grid(row=1, column=0)
        ttk.Entry(settings_frame, textvariable=self.custom_text, width=30).grid(row=1, column=1)

        ttk.Label(settings_frame, text="字体大小（0=自动）:").grid(row=2, column=0)
        ttk.Spinbox(settings_frame, from_=0, to=100, textvariable=self.font_size).grid(row=2, column=1)

        ttk.Label(settings_frame, text="边距:").grid(row=3, column=0)
        ttk.Spinbox(settings_frame, from_=0, to=100, textvariable=self.margin).grid(row=3, column=1)

        # 进度条
        ttk.Progressbar(main_frame, variable=self.progress, length=600).grid(row=4, column=0, columnspan=3, pady=15)

        # 控制按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=3)
        ttk.Button(btn_frame, text="开始处理", command=self.start_processing).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="停止处理", command=self.stop_processing).pack(side=tk.LEFT)

        # 状态栏
        ttk.Label(main_frame, textvariable=self.status).grid(row=6, column=0, columnspan=3)

    def set_default_font(self):
        # 常见系统字体路径检测
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",  # Windows 雅黑
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux
        ]
        for path in font_paths:
            if os.path.exists(path):
                self.font_path.set(path)
                break

    def select_input_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.input_dir.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def select_font(self):
        path = filedialog.askopenfilename(filetypes=[("字体文件", "*.ttf *.ttc")])
        if path:
            self.font_path.set(path)

    def validate_inputs(self):
        required = [
            (self.input_dir, "请选择输入目录"),
            (self.output_dir, "请选择输出目录"),
            (self.font_path, "请选择字体文件")
        ]

        for var, msg in required:
            if not var.get():
                messagebox.showerror("错误", msg)
                return False

        if not os.path.isdir(self.input_dir.get()):
            messagebox.showerror("错误", "输入目录不存在")
            return False

        return True

    def start_processing(self):
        if not self.validate_inputs():
            return

        # 获取所有图片文件
        supported_formats = ('.jpg', '.jpeg', '.png', '.webp')
        input_files = []
        for root, _, files in os.walk(self.input_dir.get()):
            for file in files:
                if file.lower().endswith(supported_formats):
                    input_files.append(os.path.join(root, file))

        if not input_files:
            messagebox.showwarning("警告", "没有找到支持的图片文件")
            return

        # 准备队列和进度
        for file in input_files:
            self.file_queue.put(file)
        self.progress.set(0)
        self.running = True

        # 启动处理线程
        threading.Thread(target=self.process_images, daemon=True).start()

    def stop_processing(self):
        self.running = False
        self.status.set("正在停止...")

    def process_images(self):
        total = self.file_queue.qsize()
        processed = 0
        success_count = 0
        fail_count = 0

        while not self.file_queue.empty() and self.running:
            try:
                input_path = self.file_queue.get()
                output_path = self.get_output_path(input_path)
                self.process_single_image(input_path, output_path)
                success_count += 1
            except Exception as e:
                fail_count += 1
                print(f"处理失败：{str(e)}")
            finally:
                processed += 1
                self.progress.set(processed / total * 100)
                self.status.set(f"正在处理：{os.path.basename(input_path)} ({processed}/{total})")

        # 处理完成后的统计
        result_msg = f"处理完成！成功：{success_count} 张，失败：{fail_count} 张"
        self.status.set(result_msg)
        messagebox.showinfo("完成", result_msg)
        self.running = False

    def get_output_path(self, input_path):
        # 保持目录结构
        relative_path = os.path.relpath(input_path, self.input_dir.get())
        output_fullpath = os.path.join(self.output_dir.get(), relative_path)
        
        # 创建输出目录
        os.makedirs(os.path.dirname(output_fullpath), exist_ok=True)
        return output_fullpath
    def parse_exposure_time(self,exposure_value):
        print(exposure_value,'limiande')
        exposure_value = float(exposure_value)
    # """专业处理快门速度的多种数据格式"""
        if isinstance(exposure_value, tuple):
            # 处理有理数格式 (分子, 分母)
            if exposure_value[1] == 0:
                return ""
            if exposure_value[0] / exposure_value[1] < 1:
                return f"1/{round(exposure_value[1]/exposure_value[0])}s"
            else:
                return f"{exposure_value[0]/exposure_value[1]:.1f}s"
        elif isinstance(exposure_value, (float, int)):
            # 处理直接数值型快门速度
            if exposure_value < 1:
                # 精确转换分数并约分
                denominator = round(1/exposure_value)
                return f"1/{denominator}s"
            else:
                # 显示小数后一位，并移除无效的.0
                formatted = f"{exposure_value:.1f}".rstrip('0').rstrip('.')
                return f"{formatted}s"
        else:
            return ""

    def process_single_image(self, input_path, output_path):
        try:
            img = Image.open(input_path)
            exif_data = img._getexif() or {}
            exif = {ExifTags.TAGS.get(tag, tag): value for tag, value in exif_data.items()}
            print(exif)

            # 构建水印文本
            watermark_lines = []
            if self.custom_text.get():
                watermark_lines.append(self.custom_text.get())
            
            # 添加拍摄时间
            if date_str := exif.get('DateTimeOriginal'):
                try:
                    date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                    watermark_lines.append(date_obj.strftime("拍摄时间：%Y-%m-%d %H:%M:%S"))
                except:
                    pass

            # 添加相机参数
            params = []
            # if model := exif.get('Model'):
            #     params.append(f"设备：{model}")
            if fnum := exif.get('FNumber'):
                params.append(f"光圈：f/{fnum[0]/fnum[1]:.1f}" if isinstance(fnum, tuple) else f"光圈：f/{fnum}")
            if exposure := exif.get('ExposureTime'):
                shutter = self.parse_exposure_time(exposure) if exposure else ""
                if isinstance(shutter, str):
                    params.append(f"快门速度：{shutter}")
            if iso := exif.get('ISOSpeedRatings'):
                params.append(f"ISO：{iso}")
            print(params)
            if params:
                watermark_lines.append(" | ".join(params))

            watermark_text = "\n".join(watermark_lines)

            # 绘制水印
            draw = ImageDraw.Draw(img)
            font_size = self.font_size.get() or min(img.size) // 40
            font = ImageFont.truetype(self.font_path.get(), font_size)

            # 计算位置
            text_bbox = draw.multiline_textbbox((0, 0), watermark_text, font=font)
            text_size = (text_bbox[2]-text_bbox[0], text_bbox[3]-text_bbox[1])
            position = self.calculate_position(img.size, text_size, self.margin.get())

            # 添加阴影
            shadow_offset = 2
            draw.multiline_text(
                (position[0]+shadow_offset, position[1]+shadow_offset),
                watermark_text,
                font=font,
                fill=(0, 0, 0))
            draw.multiline_text(
                position,
                watermark_text,
                font=font,
                fill=(255, 255, 255))

            # 保存图片
            img.save(output_path)

        except Exception as e:
            raise RuntimeError(f"{os.path.basename(input_path)} 处理失败：{str(e)}")

    def calculate_position(self, img_size, text_size, margin):
        positions = {
            "右下": (img_size[0] - text_size[0] - margin, img_size[1] - text_size[1] - margin),
            "左下": (margin, img_size[1] - text_size[1] - margin),
            "左上": (margin, margin),
            "右上": (img_size[0] - text_size[0] - margin, margin)
        }
        return positions.get(self.position.get(), positions["右下"])

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchWatermarkApp(root)
    root.mainloop()