import re
import openai
import pandas as pd
import csv


class CommitRelinker:
    def __init__(self, api_base, api_key):
        # 配置 OpenAI API
        openai.api_base = api_base
        openai.api_key = api_key
        self.prompt_template = """Analyze the correlation between this issue and all given commits. Return a sorted list of all commit IDs (1-{n}) in descending relevance order.

# Issue Context
[Title]: {issue_summary}
[Description]: {issue_description}

# Candidate Commits:
{commit_list}

# Scoring Criteria:
1. Semantic alignment (0.3 weight)
2. Technical term match (0.4 weight)
3. Action consistency (0.3 weight)
4. Penalize non-functional changes (-0.2)

### Output Format
- Return **all** commit IDs (1 to {n}) in a single comma-separated list.
- Do **not** skip any commits.
- Ensure the list contains exactly {n} numbers.
- Example output format (if there are {n} commits): 3,5,4,1,2,6,7,8,9,10
- Do **not** include explanations, extra text, or brackets."""

    def generate_commit_list(self, commits):
        """将 commit messages 格式化为带编号的列表"""
        return "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(commits)])

    def relink_commits(self, issue_summary, issue_description, commit_messages):
        """主函数：对 commit messages 进行 relink 排序"""
        try:
            # 格式化 commit 列表
            formatted_commits = self.generate_commit_list(commit_messages)
            prompt = self.prompt_template.format(
                n=len(commit_messages),
                issue_summary=issue_summary,
                issue_description=issue_description,
                commit_list=formatted_commits
            )
            
            # 调用 OpenAI API
            response = openai.ChatCompletion.create(
                # deepseek  chatgpt    claude
                model="deepseek-v3",
                messages=[
                {"role": "system", "content": "You are an AI assistant specialized in analyzing software development issues and commit messages. Your task is to evaluate the relevance between issues and commits, and return the most likely linked commit IDs in descending order of relevance."},
                {"role": "user", "content": prompt}
            ],
                temperature=0.2,
                max_tokens=50
            )
            
            # 解析响应
            return self.parse_response(response.choices[0].message.content)
        except Exception as e:
            print(f"API Error: {str(e)}")
            return sorted(range(1, len(commit_messages)+1))  # 异常时返回默认顺序

    def parse_response(self, response_text):
        """解析 API 响应，提取排序后的 commit IDs"""
        try:
            # 预处理：移除可能的 Markdown 代码块或多余字符
            response_text = re.sub(r"[^\d,]", "", response_text)  # 只保留数字和逗号

            # 解析 ID 列表
            sorted_ids = [int(id.strip()) for id in response_text.split(",") if id.strip().isdigit()]
            
            # 确保所有 ID 在合法范围内
            if not sorted_ids or not all(1 <= id <= 10 for id in sorted_ids):
                raise ValueError("Invalid ID range")

            return sorted_ids

        except Exception as e:
            print(f"Failed to parse response: {e}, using fallback sorting")
            return list(range(1, len(sorted_ids)+1))  # 兜底返回默认排序


def process_csv_for_relink(input_file):
    # 读取 CSV
    df = pd.read_csv(input_file)

    # 结果存储
    relink_inputs = {}

    # 遍历每个唯一的 s_id
    for s_id, group in df.groupby('s_id'):
        issue_summary = group['summary'].iloc[0] if pd.notna(group['summary'].iloc[0]) else ""  
        issue_description = group['description'].iloc[0] if pd.notna(group['description'].iloc[0]) else ""
        commit_messages = group['message'].dropna().tolist()  # 过滤掉 NaN
        # 存储数据
        relink_inputs[s_id] = (issue_summary, issue_description, commit_messages)

    return relink_inputs



if __name__ == "__main__":
    # OpenAI API
    api_base = "API"
    api_key = "key"

    relinker = CommitRelinker(api_base, api_key)
    
input_csv = "../../../data/unique_res_10/ignite/ignite_new_res_10.csv"
output_csv = "../../../data/unique_res_10/ignite/ignite_resorted_res.csv"

input_data = process_csv_for_relink(input_csv)

# 打开 CSV 文件进行写操作
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # 写入表头
    writer.writerow(['s_id', 'sort'])
    
    # 遍历 input_data 并将结果写入 CSV 文件
    for s_id, (summary, description, messages) in input_data.items():
        sorted_commit_ids = relinker.relink_commits(summary, description, messages)
        print(f"s_id: {s_id}, Sorted Commits: {sorted_commit_ids}")
        # 将列表转换为字符串并写入 CSV 文件
        sorted_commit_ids_str = str(sorted_commit_ids).replace('[', '').replace(']', '')
        writer.writerow([s_id, sorted_commit_ids_str])