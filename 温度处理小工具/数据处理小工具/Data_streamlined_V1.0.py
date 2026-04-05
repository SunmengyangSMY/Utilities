import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

def process_csv():
    try:
        # 选择原始CSV
        input_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not input_path:
            return

        # 读取界面参数
        start_time = entry_start.get().strip()
        end_time = entry_end.get().strip()
        interval_min = entry_interval.get().strip()
        select_channels = entry_channels.get().strip()

        if not start_time or not end_time or not interval_min:
            messagebox.showwarning("提示", "请填写完整：开始时间、结束时间、间隔")
            return

        interval_min = int(interval_min)

        # 尝试多种编码读取
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

        # 构造列名
        max_ch = len(df.columns) - 2
        df.columns = ["序号", "记录时间"] + [f"CH{i}" for i in range(1, max_ch+1)]

        # 时间只保留到分钟
        df["时间_分钟"] = pd.to_datetime(df["记录时间"], errors='coerce').dt.strftime("%H:%M")
        df = df.dropna(subset=["时间_分钟"])

        # 时间范围筛选
        df = df[(df["时间_分钟"] >= start_time) & (df["时间_分钟"] <= end_time)]

        # 按间隔分钟采样
        df["时间_分钟_dt"] = pd.to_datetime(df["时间_分钟"], format="%H:%M")
        start_dt = df["时间_分钟_dt"].iloc[0]

        def group_func(x):
            delta = (x - start_dt).total_seconds() / 60
            return delta // interval_min

        df = df.groupby(df["时间_分钟_dt"].apply(group_func)).first().reset_index(drop=True)

        # 选择通道
        use_cols = ["序号", "记录时间", "时间_分钟"]
        if select_channels.strip():
            ch_list = [c.strip() for c in select_channels.replace("，", ",").split(",")]
            use_cols += [ch for ch in ch_list if ch in df.columns]
        else:
            use_cols += [f"CH{i}" for i in range(1, max_ch+1)]

        df_out = df[use_cols].copy()

        # 过滤 --- 无效数据
        for col in df_out.columns:
            if col.startswith("CH"):
                df_out = df_out[df_out[col].astype(str).str.strip() != "---"]

        # ===================== 关键修改 =====================
        # 自动生成输出路径：和原文件同目录
        folder = os.path.dirname(input_path)
        name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(folder, f"{name}_精简结果.csv")
        # ====================================================

        df_out.to_csv(output_path, index=False, encoding="utf-8-sig")
        messagebox.showinfo("完成", f"已保存到：\n{output_path}")

    except Exception as e:
        messagebox.showerror("错误", f"失败：{str(e)}")

# ==================== 界面 ====================
root = tk.Tk()
root.title("CSV数据精简工具")
root.geometry("520x300")

ttk.Label(root, text="开始时间（例：13:29）").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_start = ttk.Entry(root, width=15)
entry_start.grid(row=0, column=1, padx=10, pady=5)
entry_start.insert(0, "13:29")

ttk.Label(root, text="结束时间（例：13:50）").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_end = ttk.Entry(root, width=15)
entry_end.grid(row=1, column=1, padx=10, pady=5)
entry_end.insert(0, "13:50")

ttk.Label(root, text="每隔几分钟保留一条").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_interval = ttk.Entry(root, width=15)
entry_interval.grid(row=2, column=1, padx=10, pady=5)
entry_interval.insert(0, "2")

ttk.Label(root, text="需要的通道（逗号分隔 CH1,CH3）").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_channels = ttk.Entry(root, width=30)
entry_channels.grid(row=3, column=1, padx=10, pady=5)
entry_channels.insert(0, "CH1,CH2,CH3,CH4")

btn_run = ttk.Button(root, text="选择CSV并开始处理", command=process_csv)
btn_run.grid(row=4, column=0, columnspan=2, pady=20)

root.mainloop()