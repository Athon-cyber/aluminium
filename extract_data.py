import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

base_dir = r"D:\abaqus_working_directory\Abaqus_Buckling_Results"

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 12

def read_csv_extract(csv_path):
    df_raw = pd.read_csv(csv_path, header=None)
    first_val = str(df_raw.iloc[0, 0]).strip()
    try:
        float(first_val)
        has_header = False
    except ValueError:
        has_header = True

    if has_header:
        data = pd.read_csv(csv_path, header=0)
        disp = data.iloc[:, 1]
        load = data.iloc[:, 3]
    else:
        disp = df_raw.iloc[:, 1]
        load = df_raw.iloc[:, 3]

    disp = pd.to_numeric(disp, errors='coerce').dropna().reset_index(drop=True)
    load = pd.to_numeric(load, errors='coerce').dropna().reset_index(drop=True)
    min_len = min(len(disp), len(load))
    return disp.iloc[:min_len], load.iloc[:min_len]

def filter_negative_growth(disp, load):
    if len(disp) < 2:
        return disp, load
    diff = disp.diff().iloc[1:]
    neg_indices = diff[diff < 0].index
    if len(neg_indices) > 0:
        cut_idx = neg_indices[0] + 1
        disp = disp.iloc[:cut_idx]
        load = load.iloc[:cut_idx]
    return disp, load

def process_first_level(first_dir):
    print(f"处理第一层子目录: {first_dir}")
    second_dirs = [
        d for d in os.listdir(first_dir)
        if os.path.isdir(os.path.join(first_dir, d))
    ]
    if not second_dirs:
        print("  没有第二层子目录，跳过")
        return

    all_data_filtered = []
    all_data_peak = []
    max_load_records = []

    plt.figure(1, figsize=(10, 6))
    plt.figure(2, figsize=(10, 6))

    for sub in sorted(second_dirs):
        sub_path = os.path.join(first_dir, sub)
        csv_files = glob.glob(os.path.join(sub_path, "*.csv"))
        if not csv_files:
            print(f"  子目录 {sub} 中没有 CSV 文件，跳过")
            continue
        csv_file = csv_files[0]
        try:
            disp, load = read_csv_extract(csv_file)
        except Exception as e:
            print(f"  读取 {csv_file} 失败: {e}")
            continue

        if len(load) == 0:
            print(f"  子目录 {sub} 的数据为空，跳过")
            continue

        disp_f, load_f = filter_negative_growth(disp, load)
        if len(load_f) == 0:
            print(f"  子目录 {sub} 负增长筛选后无数据，跳过")
            continue

        idx_max = load_f.idxmax()
        max_load_val = load_f.iloc[idx_max]
        disp_peak = disp_f.iloc[:idx_max+1]
        load_peak = load_f.iloc[:idx_max+1]

        print(f"    {sub}: Max Load = {max_load_val:.2f} N")
        max_load_records.append([sub, max_load_val])

        for d, l in zip(disp_f, load_f):
            all_data_filtered.append([sub, d, l])
        for d, l in zip(disp_peak, load_peak):
            all_data_peak.append([sub, d, l])

        plt.figure(1)
        plt.plot(disp_f, load_f, label=sub, linewidth=1.0)
        plt.figure(2)
        plt.plot(disp_peak, load_peak, label=sub, linewidth=1.0)

    if all_data_filtered:
        df_filtered = pd.DataFrame(all_data_filtered, columns=["subfolder", "Displacement_U3(mm)", "Abs_Load(N)"])
        csv_filtered = os.path.join(first_dir, "summary_load_displacement.csv")
        df_filtered.to_csv(csv_filtered, index=False, encoding='utf-8-sig')
        print(f"  位移负增长筛选后汇总数据已保存: {csv_filtered}")

        df_peak = pd.DataFrame(all_data_peak, columns=["subfolder", "Displacement_U3(mm)", "Abs_Load(N)"])
        csv_peak = os.path.join(first_dir, "summary_load_displacement_to_peak.csv")
        df_peak.to_csv(csv_peak, index=False, encoding='utf-8-sig')
        print(f"  峰值前数据汇总已保存: {csv_peak}")

        df_max = pd.DataFrame(max_load_records, columns=["subfolder", "Max_Load(N)"])
        max_csv = os.path.join(first_dir, "max_load_summary.csv")
        df_max.to_csv(max_csv, index=False, encoding='utf-8-sig')
        print(f"  最大荷载汇总已保存: {max_csv}")
    else:
        print("  没有有效数据，不生成汇总文件")
        plt.close('all')
        return

    plt.figure(1)
    plt.xlabel("Displacement U3 (mm)")
    plt.ylabel("Abs Load (N)")
    plt.title(f"Load-Displacement Curves (Negative Growth Removed) - {os.path.basename(first_dir)}")
    plt.legend(fontsize=8, loc='best')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    img1_path = os.path.join(first_dir, "load_displacement_curves.png")
    plt.savefig(img1_path, dpi=300)
    plt.close(1)

    plt.figure(2)
    plt.xlabel("Displacement U3 (mm)")
    plt.ylabel("Abs Load (N)")
    plt.title(f"Load-Displacement Curves (Up to Peak Load) - {os.path.basename(first_dir)}")
    plt.legend(fontsize=8, loc='best')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    img2_path = os.path.join(first_dir, "load_displacement_curves_to_peak.png")
    plt.savefig(img2_path, dpi=300)
    plt.close(2)

    print(f"  曲线图已保存: {img1_path} 和 {img2_path}")

def main():
    base = os.path.abspath(base_dir)
    print(f"工作根目录: {base}")
    first_levels = [
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d))
    ]
    if not first_levels:
        print("没有找到第一层子目录。")
        return

    for fdir in sorted(first_levels):
        process_first_level(os.path.join(base, fdir))

if __name__ == "__main__":
    main()