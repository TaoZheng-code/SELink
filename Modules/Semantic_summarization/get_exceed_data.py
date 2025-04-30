import pandas as pd
from transformers import RobertaTokenizer

# 初始化 tokenizer
tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")

def text2vec(seqs):
    texttoken_id = []
    max_seq_len = 35
    max_seq_len_50 = int(max_seq_len * 1.5)
    textoken = []

    for seq in seqs:
        textoken += [tokenizer.cls_token] + seq
    
    tokens_ids = tokenizer.convert_tokens_to_ids(textoken)

    original_length = len(tokens_ids)
    is_exceed = original_length > max_seq_len
    is_exceed_50 = original_length > max_seq_len_50

    texttoken_id = tokens_ids[:max_seq_len]

    texttoken_id.extend([0 for _ in range(max_seq_len - len(texttoken_id))])

    return texttoken_id, original_length, is_exceed

def count_exceeding_length(data, row_df):
    
    # 确保 'commit_use_llm' 和 'issue_use_llm' 列存在，初始化为 0
    for col in ['commit_use_llm', 'issue_use_llm']:
        if col not in row_df.columns:
            row_df[col] = 0
    
    for i, row in data.iterrows():
        try:
            # 提取 commit 和 issue 序列
            commit_seq = eval(row['message_processed'])
            issue_seq = eval(row['summary_processed']) + eval(row['description_processed'])

            # 调用 text2vec 并统计是否超过长度
            commit_token_id, commit_length, commit_exceed = text2vec(commit_seq)
            issue_token_id, issue_length, issue_exceed = text2vec(issue_seq)

            # 需要 LLM 处理的行
            if commit_exceed:
                row_df.loc[i, 'commit_use_llm'] = 1
            if issue_exceed:
                row_df.loc[i, 'issue_use_llm'] = 1

        except Exception as e:
            print(f"Error processing row {i}: {e}")

    return row_df

# 主程序
if __name__ == "__main__":

    projects=['ambari', 'calcite', 'groovy', 'ignite', 'isis', 'netbeans']
    for project in projects:
        print(project)
        file_path = f"../../../data/merge/{project}_link.csv"                      # 切词过的数据
        row_data_path = f"../../../data/{project}_link.csv"                   # 切词前原文件的数据
        write_to_csv_path = f"../../../data/select_csv/{project}_link.csv"

        row_df = pd.read_csv(row_data_path)
        # 加载数据
        try:
            df = pd.read_csv(file_path)
            
            # 确保包含所需的列
            required_columns = {'message_processed', 'summary_processed', 'description_processed'}
            if not required_columns.issubset(df.columns):
                print(f"Error: The dataset must contain the following columns: {required_columns}")
            else:
                # 调用统计函数，row_df 会在函数内被修改
                row_df = count_exceeding_length(df, row_df)
                
                print(f"原来有 {len(row_df)} 行")

                row_df.to_csv(write_to_csv_path, index=False)  
                print("数据已成功写入:", write_to_csv_path)


        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
