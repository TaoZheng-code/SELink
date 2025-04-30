import pandas as pd

def select_top_k_per_s_id(input_file, output_file, k=10):
    # 读取 CSV 文件
    df = pd.read_csv(input_file)

    # 只保留 s_id、t_id、label 三列
    df = df[['s_id', 't_id', 'label']]

    # 按 s_id 分组，并取每个分组的前 k 行
    df_top_k = df.groupby('s_id').head(k)

    # 保存到新的 CSV 文件
    df_top_k.to_csv(output_file, index=False)

projects=['ambari', 'calcite', 'groovy', 'ignite', 'isis', 'netbeans']
for project in projects:
    # relink的初结果
    input_csv = f"../../../data/res/res_{project}.csv"
    output_csv = f"../../../data/unique_res_10/{project}/res_10.csv"

    select_top_k_per_s_id(input_csv, output_csv)