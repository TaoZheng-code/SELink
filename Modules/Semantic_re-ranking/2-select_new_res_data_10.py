import pandas as pd

def filter_and_match(input_file1, input_file2, output_file):
    # 读取 CSV 文件
    df1 = pd.read_csv(input_file1)
    df2 = pd.read_csv(input_file2)

    # 初始化列表存储结果
    results = []

    for _, row in df1.iterrows():
        s_id, t_id, label = row['s_id'], row['t_id'], row['label']
        
        # 查找 description 和 summary（issue_id == s_id）
        df2_issue_match = df2[df2['issue_id'] == s_id]
        description = df2_issue_match['description'].iloc[0] if not df2_issue_match.empty else None
        summary = df2_issue_match['summary'].iloc[0] if not df2_issue_match.empty else None

        # 查找 message（commitid == t_id）
        df2_commit_match = df2[df2['commitid'] == t_id]
        message = df2_commit_match['message'].iloc[0] if not df2_commit_match.empty else None

        # 存入结果
        results.append([s_id, t_id, description, summary, message, label])

    # 转换为 DataFrame
    df_result = pd.DataFrame(results, columns=['s_id', 't_id', 'description', 'summary', 'message', 'label'])

    # 保存到 CSV
    df_result.to_csv(output_file, index=False)

projects=['ambari', 'calcite', 'groovy', 'ignite', 'isis', 'netbeans']

for project in projects:
    # 文件路径     
    input_csv1 = f"../../../data/unique_res_10/{project}/res_10.csv"
    input_csv2 = f"../../../data/{project}_link.csv"

    output_csv = f"../../../data/unique_res_10/{project}/{project}_new_res_10.csv"

    # 运行函数
    filter_and_match(input_csv1, input_csv2, output_csv)