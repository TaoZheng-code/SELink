import pandas as pd
from transformers import RobertaTokenizer

# 初始化 tokenizer
tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")

def text2vec(seqs):
    """
    将文本序列转换为 token ID 列表，并统计长度。
    :param seqs: 文本序列列表
    :return: token ID 列表, 原始长度, 是否超过最大长度, 是否超过最大长度的 1.5 倍
    """
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

    return texttoken_id, original_length, is_exceed, is_exceed_50

def code2vec(codes, isdiff):
    """
    将代码序列转换为 token ID 列表，并统计长度。
    :param codes: 代码序列列表（字符串形式）
    :param isdiff: 是否为 diff 类型
    :return: token ID 列表, 原始长度, 是否超过最大长度, 是否超过最大长度的 1.5 倍
    """
    codetoken_id = []
    max_code_len = 300
    max_diff_len = 500
    max_code_len_50 = int(max_code_len * 1.5)
    max_diff_len_50 = int(max_diff_len * 1.5)
    codes = eval(codes)
    code_tokens = []

    if isdiff:
        for code in codes:
            code_id = tokenizer.convert_tokens_to_ids([tokenizer.cls_token] + code)
            code_id = code_id[:80]
            code_id.extend([0 for _ in range(80 - len(code_id))])
            codetoken_id.extend(code_id)
        original_length = len(codetoken_id)
        is_exceed = original_length > max_diff_len
        is_exceed_50 = original_length > max_diff_len_50
        codetoken_id = codetoken_id[:max_diff_len]
        codetoken_id.extend([0 for _ in range(max_diff_len - len(codetoken_id))])
    else:
        for code in codes:
            code_tokens += [tokenizer.cls_token] + code[:80]
        tokens_ids = tokenizer.convert_tokens_to_ids(code_tokens)
        original_length = len(tokens_ids)
        is_exceed = original_length > max_code_len
        is_exceed_50 = original_length > max_code_len_50
        codetoken_id = tokens_ids[:max_code_len]
        codetoken_id.extend([0 for _ in range(max_code_len - len(codetoken_id))])

    return codetoken_id, original_length, is_exceed, is_exceed_50

def count_exceeding_length(data):
    """
    统计 commit 和 issue 超过长度限制及其 1.5 倍的数量和比例。
    """
    total_count = len(data)
    commit_exceed_count = 0
    commit_exceed_50_count = 0
    issue_exceed_count = 0
    issue_exceed_50_count = 0
    max_seq_len = 35

    for i, row in data.iterrows():
        try:
            # 提取 commit 和 issue 序列
            commit_seq = eval(row['message_processed'])
            issue_seq = eval(row['summary_processed']) + eval(row['description_processed'])

            # 调用 text2vec 并统计是否超过长度
            i, commit_length, commit_exceed, commit_exceed_50 = text2vec(commit_seq)
            i, issue_length, issue_exceed, issue_exceed_50 = text2vec(issue_seq)

            if commit_exceed:
                commit_exceed_count += 1
            if commit_exceed_50:
                commit_exceed_50_count += 1
            if issue_exceed:
                issue_exceed_count += 1
            if issue_exceed_50:
                issue_exceed_50_count += 1

        except Exception as e:
            print(f"Error processing row: {e}")

    # 计算比例
    commit_exceed_ratio = commit_exceed_count / total_count if total_count > 0 else 0
    commit_exceed_50_ratio = commit_exceed_50_count / total_count if total_count > 0 else 0
    issue_exceed_ratio = issue_exceed_count / total_count if total_count > 0 else 0
    issue_exceed_50_ratio = issue_exceed_50_count / total_count if total_count > 0 else 0

    # 打印统计结果
    print(f"\nTotal rows: {total_count}")
    print(f"Commit exceeding {max_seq_len} tokens: {commit_exceed_count} ({commit_exceed_ratio:.2%})")
    print(f"Commit exceeding {int(max_seq_len * 1.5)} tokens: {commit_exceed_50_count} ({commit_exceed_50_ratio:.2%})")
    print(f"Issue exceeding {max_seq_len} tokens: {issue_exceed_count} ({issue_exceed_ratio:.2%})")
    print(f"Issue exceeding {int(max_seq_len * 1.5)} tokens: {issue_exceed_50_count} ({issue_exceed_50_ratio:.2%})")

    return (commit_exceed_count, commit_exceed_ratio, commit_exceed_50_count, commit_exceed_50_ratio,
            issue_exceed_count, issue_exceed_ratio, issue_exceed_50_count, issue_exceed_50_ratio)

# 主程序
if __name__ == "__main__":
    file_path = "data/merge/ambari_link.csv"  # 修改为你的实际文件路径

    # 加载数据
    try:
        df = pd.read_csv(file_path)

        # 确保包含所需的列
        required_columns = {'message_processed', 'summary_processed', 'description_processed'}
        if not required_columns.issubset(df.columns):
            print(f"Error: The dataset must contain the following columns: {required_columns}")
        else:
            # 调用统计函数
            stats = count_exceeding_length(df)
            

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
