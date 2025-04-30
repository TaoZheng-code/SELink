import pandas as pd
import math


def NDCG_at_K(data_frame, k=1):
    group_tops = data_frame.groupby('s_id')
    cnt = 0
    dcg_sum = 0
    for s_id, group in group_tops:
        rank = 0
        for index, row in group.head(k).iterrows():
            rank += 1
            if row['label'] == 1:
                dcg_sum += math.log(2)/math.log(rank+2) 
                break 
        cnt += 1
    return round(dcg_sum / cnt if cnt > 0 else 0, 4)

def recall_at_K(data_frame, k=1):
    group_tops = data_frame.groupby('s_id')
    sorted_df = data_frame.loc[data_frame['label']==1]
    cnt = 0
    recall = 0.0
    for s_id, group in group_tops:
        hits = 0
        tu = sorted_df.loc[sorted_df['s_id']==s_id]
        for index, row in group.head(k).iterrows():
            hits += 1 if row['label'] == 1 else 0      
        recall += round(hits / len(tu) if len(tu) > 0 else 0, 4)
        cnt +=1
    return recall/cnt

def precision_at_K(data_frame, k=1):
    group_tops = data_frame.groupby('s_id')
    cnt = 0
    hits = 0
    for s_id, group in group_tops:
        for index, row in group.head(k).iterrows():
            hits += 1 if row['label'] == 1 else 0      
        cnt += k
    return round(hits / cnt if cnt > 0 else 0, 4)
def Hit_at_K(data_frame, k=1):
    group_tops = data_frame.groupby('s_id')
    cnt = 0
    hits = 0
    for s_id, group in group_tops:
        for index, row in group.head(k).iterrows():
            if row['label'] == 1:
                hits += 1 
                break       
        cnt += 1
    return round(hits / cnt if cnt > 0 else 0, 4)

def MRR(data_frame):
    group_tops = data_frame.groupby('s_id')
    mrr_sum = 0
    for s_id, group in group_tops:
        rank = 0
        for i, (index, row) in enumerate(group.iterrows()):
            rank += 1
            if row['label'] == 1:
                mrr_sum += 1.0 / rank
                break
    return mrr_sum / len(group_tops)


def load_sorted_commits(sorted_commits_path):
    """ 读取 sorted_commits.csv，返回一个字典 {s_id: 排序列表} """
    sorted_commits_df = pd.read_csv(sorted_commits_path)
    sorted_commits_dict = {}

    for _, row in sorted_commits_df.iterrows():
        s_id = row['s_id']
        sort_order = list(map(int, row['sort'].split(',')))  # 解析排序列表
        sorted_commits_dict[s_id] = sort_order
    
    return sorted_commits_dict

def load_res_file(res_path):
    """ 读取 res.csv，去除 'pred' 列（如果存在） """
    res_df = pd.read_csv(res_path)
    if 'pred' in res_df.columns:
        res_df = res_df.drop(columns=['pred'])  # 删除 'pred' 列
    return res_df

def apply_sorting(res_df, sorted_commits_dict):
    """ 根据 sorted_commits_dict 对 res_df 进行排序 """
    sorted_rows = []

    for s_id, sort_order in sorted_commits_dict.items():
        # 获取当前 s_id 在 res_df 中的所有相关行
        s_id_rows = res_df[res_df['s_id'] == s_id].copy()

        if s_id_rows.empty:
            continue  # 跳过没有匹配项的 s_id

        # 仅对前 10 行进行重新排序
        top_rows = s_id_rows.iloc[:10].copy()

        # 处理排序索引（从 1-based 转为 0-based）
        sort_order = [x - 1 for x in sort_order if x - 1 < len(top_rows)]
        
        # 重新排序
        sorted_top_rows = top_rows.iloc[sort_order]

        # 存储排序后的数据
        sorted_rows.append(sorted_top_rows)

    if sorted_rows:
        return pd.concat(sorted_rows)[['s_id', 't_id', 'label']]
    else:
        return pd.DataFrame(columns=['s_id', 't_id', 'label'])  # 返回空 DataFrame 以防出错

def sort_res_by_commit_order(sorted_commits_path, res_path, output_path=None):
    """ 
    读取 sorted_commits.csv 和 res.csv，按 commit 排序后返回排序后的 DataFrame
    如果提供了 output_path，则同时保存文件 
    """
    sorted_commits_dict = load_sorted_commits(sorted_commits_path)
    res_df = load_res_file(res_path)
    sorted_res_df = apply_sorting(res_df, sorted_commits_dict)
    
    if output_path:
        sorted_res_df.to_csv(output_path, index=False)
        print(f"Sorted data saved to {output_path}")

    return sorted_res_df  # 返回排序后的 DataFrame

def main():
        projects = ['ambari', 'calcite', 'groovy', 'ignite', 'isis', 'netbeans']
        for project in projects:
            # 文件路径
            sorted_commits_file = f"../../../data/unique_res_10/{project}/{project}_resorted_res.csv"
            res_file = f"../../../data/unique_res_10/{project}/res_10.csv"
            output_file = f"../../../data/unique_res_10/{project}/{project}_res_sorted.csv"
            resort_result_path = f"../../../data/model/resort_results.csv"

            # 获取排序后的 DataFrame
            sorted_df = sort_res_by_commit_order(sorted_commits_file, res_file, output_file)
            Hit = Hit_at_K(sorted_df, 1)
            print("  Final test Hit@1 %f" % (Hit) )
            Hit5 = Hit_at_K(sorted_df, 5)
            print("  Final test Hit@5 %f" % (Hit5) )
            Hit10 = Hit_at_K(sorted_df, 10)
            print("  Final test Hit@10 %f" % (Hit10) )
            Hit20 = Hit_at_K(sorted_df, 20)
            print("  Final test Hit@20 %f" % (Hit20) )
            precision = precision_at_K(sorted_df, 1)
            print("  Final test precision@1 %f" % (precision) )  
            precision5 = precision_at_K(sorted_df, 5)
            print("  Final test precision@5 %f" % (precision5))
            precision10 = precision_at_K(sorted_df, 10)
            print("  Final test precision@10 %f" % (precision10))
            precision20 = precision_at_K(sorted_df, 20)
            print("  Final test precision@20 %f" % (precision20))
            recall = recall_at_K(sorted_df, 1)
            print("  Final test recall@1 %f" % (recall))  
            recall5 = recall_at_K(sorted_df, 5)
            print("  Final test recall@5 %f" % (recall5))  
            recall10 = recall_at_K(sorted_df, 10)
            print("  Final test recall@10 %f" % (recall10))
            recall20 = recall_at_K(sorted_df, 20)
            print("  Final test recall@20 %f" % (recall20))
            mrr = MRR(sorted_df)
            print("  Final test MRR %f" % (mrr)) 
            ndcg = NDCG_at_K(sorted_df, k=1)
            print("  Final test ndcg@1 %f" % (ndcg))
            ndcg5 = NDCG_at_K(sorted_df, k=5)
            print("  Final test ndcg@5 %f" % (ndcg5))
            ndcg10 = NDCG_at_K(sorted_df, k=10)
            print("  Final test ndcg@10 %f" % (ndcg10))  
            ndcg20 = NDCG_at_K(sorted_df, k=20)
            print("  Final test ndcg@20 %f" % (ndcg20))   

            # 结果存入字典
            result_dict = {
                "project": [project],  # 这里填入具体的路径或标识
                "Hit@1": [Hit],
                "Hit@5": [Hit5],
                "Hit@10": [Hit10],
                "Hit@20": [Hit20],
                "Precision@1": [precision],
                "Precision@5": [precision5],
                "Precision@10": [precision10],
                "Precision@20": [precision20],
                "Recall@1": [recall],
                "Recall@5": [recall5],
                "Recall@10": [recall10],
                "Recall@20": [recall20],
                "MRR": [mrr],
                "NDCG@1": [ndcg],
                "NDCG@5": [ndcg5],
                "NDCG@10": [ndcg10],
                "NDCG@20": [ndcg20],
            }

            # 转换为 DataFrame
            result_df = pd.DataFrame(result_dict)

            result_df.to_csv(resort_result_path, mode="a", index=False, header=not pd.io.common.file_exists(resort_result_path))

            print("Results appended to", resort_result_path)

if __name__ == "__main__":
    main()
