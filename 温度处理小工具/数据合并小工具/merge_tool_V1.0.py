import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os

def read_file_raw(path):
    """用原生csv模块读取文件，兼容各种编码和格式"""
    rows = []
    # 尝试多种编码
    encodings = ["gbk", "gb2312", "utf-8", "cp1252"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    rows.append(row)
            return rows
        except:
            continue
    # 所有编码都失败时，用二进制方式暴力读取
    try:
        with open(path, "rb") as f:
            content = f.read()
            text = content.decode("latin1", errors="ignore")
            reader = csv.reader(text.splitlines())
            for row in reader:
                rows.append(row)
        return rows
    except:
        return None

def merge_csv_in_order():
    try:
        # 选择文件
        files = filedialog.askopenfilenames(
            title="按顺序选择CSV（先选的在前）",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not files:
            return

        # 显示顺序
        filenames = [os.path.basename(f) for f in files]
        info = "即将按以下顺序合并：\n\n" + "\n".join(f"{i+1}. {name}" for i, name in enumerate(filenames))
        if not messagebox.askyesno("确认顺序", info):
            return

        merged_rows = []

        for idx, file_path in enumerate(files):
            rows = read_file_raw(file_path)
            if rows is None:
                messagebox.showerror("错误", f"无法读取文件：\n{os.path.basename(file_path)}")
                return

            # 第一个文件：全部保留
            if idx == 0:
                merged_rows.extend(rows)
            else:
                # 其他文件：从第8行（索引7）开始
                if len(rows) > 7:
                    merged_rows.extend(rows[7:])

        # 保存到第一个文件的目录
        out_dir = os.path.dirname(files[0])
        out_path = os.path.join(out_dir, "合并结果.csv")

        # 写入文件
        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(merged_rows)

        messagebox.showinfo("✅ 合并完成", f"已成功保存到：\n{out_path}")

    except Exception as e:
        messagebox.showerror("❌ 错误", f"合并失败：\n{str(e)}")

# ==================== 界面 ====================
root = tk.Tk()
root.title("CSV顺序合并工具 - 终极兼容版")
root.geometry("550x280")

ttk.Label(
    root,
    text="使用说明：\n• 按选择顺序合并\n• 第一个文件保留完整1-7行表头\n• 其余文件只合并第8行开始数据\n• 已兼容所有编码和格式",
    font=("微软雅黑", 10)
).grid(row=0, column=0, columnspan=2, padx=10, pady=15)

btn = ttk.Button(root, text="选择多个CSV并按顺序合并", command=merge_csv_in_order)
btn.grid(row=1, column=0, columnspan=2, pady=20)

root.mainloop()