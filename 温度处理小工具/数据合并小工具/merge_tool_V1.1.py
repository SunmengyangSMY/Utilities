import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os

def read_file_raw(path):
    rows = []
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
    try:
        with open(path, "rb") as f:
            text = f.read().decode("latin1", errors="ignore")
            reader = csv.reader(text.splitlines())
            for row in reader:
                rows.append(row)
        return rows
    except:
        return None

def merge_csv_in_order():
    try:
        files = filedialog.askopenfilenames(
            title="按顺序选择CSV（先选的在前）",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not files:
            return

        filenames = [os.path.basename(f) for f in files]
        info = "即将按以下顺序合并：\n\n" + "\n".join(f"{i+1}. {name}" for i, name in enumerate(filenames))
        if not messagebox.askyesno("确认顺序", info):
            return

        merged_rows = []

        for index, file_path in enumerate(files):
            rows = read_file_raw(file_path)
            if rows is None:
                messagebox.showerror("错误", f"读取失败：{os.path.basename(file_path)}")
                return

            # ===================== 核心逻辑 =====================
            # 第一个文件：保留 1~8 行（完整表头）
            if index == 0:
                merged_rows.extend(rows[:8])

            # 所有文件：都只取 第9行开始的数据（跳过第8行表头）
            if len(rows) >= 9:
                merged_rows.extend(rows[8:])
            # ====================================================

        # 保存
        out_dir = os.path.dirname(files[0])
        out_path = os.path.join(out_dir, "合并完成_.csv")

        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(merged_rows)

        messagebox.showinfo("成功", f"合并完成！\n已保存到：\n{out_path}")

    except Exception as e:
        messagebox.showerror("失败", f"错误：{str(e)}")

# ==================== 界面 ====================
root = tk.Tk()
root.title("CSV多文件合并工具")
root.geometry("550x260")

ttk.Label(
    root,
    text="使用说明：\n• 按选择顺序合并\n• 仅保留【第一个文件】的 1~8 行表头\n• 所有文件从第9行开始取数据\n• 自动去重所有多余表头",
    font=("微软雅黑", 10)
).grid(row=0, column=0, columnspan=2, padx=10, pady=15)

btn = ttk.Button(root, text="选择多个CSV并按顺序合并", command=merge_csv_in_order)
btn.grid(row=1, column=0, columnspan=2, pady=20)

root.mainloop()