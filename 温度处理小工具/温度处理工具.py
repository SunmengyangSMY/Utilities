import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import csv
import os

# ==================== 通用工具函数 ====================
def expand_range(text):
    result = []
    text = text.strip().replace("，", ",")
    parts = text.split(",")
    for p in parts:
        p = p.strip()
        if "-" in p:
            try:
                pre = p.split("-")[0].rstrip("0123456789")
                start = int(p.split("-")[0].replace(pre, ""))
                end = int(p.split("-")[1])
                for i in range(start, end + 1):
                    result.append(f"{pre}{i}")
            except:
                if p:
                    result.append(p)
        else:
            if p:
                result.append(p)
    return result

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

# ==================== 功能1：数据精简 ====================
def process_csv():
    try:
        input_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not input_path:
            return

        start_time = entry_start.get().strip()
        end_time = entry_end.get().strip()
        interval_min = entry_interval.get().strip()
        select_channels = entry_channels.get().strip()

        if not start_time or not end_time or not interval_min:
            messagebox.showwarning("提示", "请填写完整：开始时间、结束时间、间隔")
            return
        interval_min = int(interval_min)

        encodings = ['utf-8', 'gbk', 'gb2312', 'cp1252']
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(input_path, skiprows=7, header=None, encoding=enc)
                break
            except:
                continue
        if df is None:
            messagebox.showerror("错误", "无法读取文件编码")
            return

        max_ch = len(df.columns) - 2
        df.columns = ["序号", "记录时间"] + [f"CH{i}" for i in range(1, max_ch+1)]

        df["时间_分钟"] = pd.to_datetime(df["记录时间"], errors='coerce').dt.strftime("%H:%M")
        df = df.dropna(subset=["时间_分钟"])
        df = df[(df["时间_分钟"] >= start_time) & (df["时间_分钟"] <= end_time)]

        df["时间_分钟_dt"] = pd.to_datetime(df["时间_分钟"], format="%H:%M")
        start_dt = df["时间_分钟_dt"].iloc[0]

        def group_func(x):
            delta = (x - start_dt).total_seconds() / 60
            return delta // interval_min

        df = df.groupby(df["时间_分钟_dt"].apply(group_func)).first().reset_index(drop=True)

        use_cols = ["序号", "记录时间", "时间_分钟"]
        if select_channels.strip():
            ch_list = expand_range(select_channels)
            use_cols += [ch for ch in ch_list if ch in df.columns]
        else:
            use_cols += [f"CH{i}" for i in range(1, max_ch+1)]

        df_out = df[use_cols].copy()
        for col in df_out.columns:
            if col.startswith("CH"):
                df_out = df_out[df_out[col].astype(str).str.strip() != "---"]

        folder = os.path.dirname(input_path)
        name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(folder, f"{name}_精简结果.csv")
        df_out.to_csv(output_path, index=False, encoding="utf-8-sig")
        messagebox.showinfo("完成", f"已保存到：\n{output_path}")
    except Exception as e:
        messagebox.showerror("错误", f"失败：{str(e)}")

# ==================== 功能2：多文件顺序合并 ====================
def merge_csv_in_order():
    try:
        files = filedialog.askopenfilenames(title="按顺序选择CSV", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not files:
            return

        filenames = [os.path.basename(f) for f in files]
        info = "即将按顺序合并：\n\n" + "\n".join(f"{i+1}. {name}" for i, name in enumerate(filenames))
        if not messagebox.askyesno("确认顺序", info):
            return

        merged_rows = []
        for index, file_path in enumerate(files):
            rows = read_file_raw(file_path)
            if rows is None:
                messagebox.showerror("错误", f"读取失败：{os.path.basename(file_path)}")
                return

            if index == 0:
                merged_rows.extend(rows[:8])  # 1~8行表头只保留一次

            if len(rows) >= 9:
                merged_rows.extend(rows[8:])   # 所有文件从第9行开始取数据

        out_dir = os.path.dirname(files[0])
        out_path = os.path.join(out_dir, "合并完成.csv")

        with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(merged_rows)

        messagebox.showinfo("成功", f"合并完成！\n已保存到：\n{out_path}")
    except Exception as e:
        messagebox.showerror("失败", f"错误：{str(e)}")

# ==================== 统一界面 ====================
root = tk.Tk()
root.title("CSV 数据处理工具箱")
root.geometry("620x380")

# 标题
ttk.Label(root, text="优利德热电偶数据处理工具 ", font=("微软雅黑", 14, "bold"))\
    .grid(row=0, column=0, columnspan=2, pady=10)

# ========== 左侧：精简功能 ==========
lf1 = ttk.LabelFrame(root, text="数据精简")
lf1.grid(row=1, column=0, padx=10, pady=10, sticky="n")

ttk.Label(lf1, text="开始时间（例：13:29）").grid(row=0, column=0, padx=8, pady=4, sticky="w")
entry_start = ttk.Entry(lf1, width=14)
entry_start.grid(row=0, column=1, padx=8, pady=4)
entry_start.insert(0, "13:29")

ttk.Label(lf1, text="结束时间（例：13:50）").grid(row=1, column=0, padx=8, pady=4, sticky="w")
entry_end = ttk.Entry(lf1, width=14)
entry_end.grid(row=1, column=1, padx=8, pady=4)
entry_end.insert(0, "13:50")

ttk.Label(lf1, text="每隔几分钟保留一条").grid(row=2, column=0, padx=8, pady=4, sticky="w")
entry_interval = ttk.Entry(lf1, width=14)
entry_interval.grid(row=2, column=1, padx=8, pady=4)
entry_interval.insert(0, "2")

ttk.Label(lf1, text="通道（支持 CH1-24）").grid(row=3, column=0, padx=8, pady=4, sticky="w")
entry_channels = ttk.Entry(lf1, width=14)
entry_channels.grid(row=3, column=1, padx=8, pady=4)
entry_channels.insert(0, "CH1-24")

ttk.Button(lf1, text="选择CSV并精简", command=process_csv, width=20)\
    .grid(row=4, column=0, columnspan=2, pady=10)

# ========== 右侧：合并功能 ==========
lf2 = ttk.LabelFrame(root, text="多文件顺序合并")
lf2.grid(row=1, column=1, padx=10, pady=10, sticky="n")

ttk.Label(lf2, text="规则：").grid(row=0, column=0, padx=8, pady=4, sticky="w")
ttk.Label(lf2, text="• 仅保留第一个文件表头\n• 从第9行开始合并数据\n• 按选择顺序拼接", justify="left")\
    .grid(row=1, column=0, padx=8, pady=8)

ttk.Button(lf2, text="选择多个CSV并合并", command=merge_csv_in_order, width=25)\
    .grid(row=2, column=0, padx=10, pady=15)

root.mainloop()