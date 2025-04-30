import csv
import sys
import re
import time
import openai
from tqdm import tqdm

# OpenAI API
openai.api_base = "API"
openai.api_key = "key"


csv.field_size_limit(sys.maxsize)

# 处理单条文本的函数
def compress_text(text, run):
    if not text.strip():
        return text, run

    word_count = len(re.findall(r'\b\w+\b', text))
    if word_count < 40:
        return text, run

    prompt = (
        "Summarize the key details from the following text. "
        "Ensure the summary is between 35 and 45 words." 
        "Keep the summary clear, concise, and informative." 
        "Please Output only the summary:\n\n"
        f"{text}"
    )

    max_retries = 3  # 最大重试次数
    timeout = 30  # 请求超时时间

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(  # 使用 openai 直接调用 API
                # deepseek  chatgpt    claude
                model="deepseek-v3",
                messages=[
                    {"role": "system", "content": "You are an AI assistant who is good at summarizing text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                request_timeout=timeout  # 修改 timeout 关键字
            )

            result = response["choices"][0]["message"]["content"].strip()  # 获取返回内容
            run = "0"
            break  # 请求成功，跳出循环

        except openai.error.RateLimitError as e:  # 速率限制
            print(f"\n⚠️ 速率限制错误 (第 {attempt+1}/{max_retries} 次)，等待 5 秒后重试，错误信息: {e}")
            time.sleep(5)  # 速率限制时等待 5 秒

        except openai.error.Timeout as e:  # 超时错误
            print(f"\n⚠️ API 请求超时 (第 {attempt+1}/{max_retries} 次)，错误信息: {e}")

        except openai.error.APIError as e:  # OpenAI API 相关错误
            print(f"\n⚠️ OpenAI API 发生错误: {e}")
            result = text  # 发生 API 错误，返回原始文本
            break  # 不再重试，直接退出

        except Exception as e:
            print(f"\n⚠️ 未知错误: {e}")
            result = text
            break  # 发生未知错误，直接退出

        time.sleep(2)  # 除速率限制外，其它情况重试前等待 2 秒

    else:
        print("\n❌ API 请求失败，返回原始文本")
        result = text  # 如果重试 max_retries 次后仍失败，返回原文本

    return result, run  # 确保始终返回有效数据

# CSV 文件路径
input_csv = "../../../data/select_csv/netbeans_link.csv"
output_csv = "../../../data/llm/netbeans_llm_link.csv"

# **先统计总行数**
with open(input_csv, newline='', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    total_rows = sum(1 for row in reader if any(field.strip() for field in row)) - 1  # 过滤掉空行，并减去标题行

print(f"📊 Total rows to process: {total_rows}")


# **开始处理 CSV**
with open(input_csv, newline='', encoding='utf-8') as infile, open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    
    # 确保存在需要的列
    required_fields = ["compressed_llm_message", "compressed_llm_summary", "compressed_llm_description"]
    for field in required_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    # 使用 tqdm 显示进度条
    with tqdm(total=total_rows, desc="Processing", unit="row") as pbar:
        for row in reader:
            commit_use_llm = row.get("commit_use_llm", "")
            issue_use_llm = row.get("issue_use_llm", "")

            original_message = row.get("message", "")
            original_summary = row.get("summary", "")
            original_description = row.get("description", "")

            # **只处理需要 LLM 处理的字段**
            if commit_use_llm == "1":
                row["compressed_llm_message"], row["commit_use_llm"] = compress_text(original_message, commit_use_llm)
                time.sleep(1)  # 避免 API 速率限制
            else:
                row["compressed_llm_message"] = original_message  # 不变

            if issue_use_llm == "1":
                row["compressed_llm_summary"], row["issue_use_llm"] = compress_text(original_summary, issue_use_llm)
                row["compressed_llm_description"], row["issue_use_llm"] = compress_text(original_description, issue_use_llm)
                time.sleep(1)  # 避免 API 速率限制
            else:
                row["compressed_llm_summary"] = original_summary  # 不变
                row["compressed_llm_description"] = original_description  # 不变

            writer.writerow(row)
            pbar.update(1)  # 更新进度条

print("\n✅ 压缩完成，结果已保存到", output_csv)