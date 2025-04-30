import argparse
import pandas as pd
import os
from numpy import nan as NaN

def merge_processed_data(project_name):

    output_csv = f'../../../data/merge/{project_name}_link.csv'

    # 读取 CSV 文件
    df1 = pd.read_csv(f'../../../data/balancedata2/{project_name}_link_process.csv')
    df2 = pd.read_csv(f'../../../data/balancedata1/{project_name}_sub.csv')

    list1 = ['issue_id','summary_processed','description_processed','issuecode','hash','message_processed','changed_files','codelist_processed','label','train_flag']
    df = df1[list1]
    df.insert(len(df.columns),'Diff_processed',value=NaN)
    df.insert(len(df.columns),'labelist',value=NaN)
    df.insert(len(df.columns),'num',value=NaN)
    tg = df.label
    res = df.drop('label',axis=1)
    res.insert(len(res.columns),'target',tg)  
    flag = res.train_flag
    res = res.drop('train_flag',axis=1)
    res.insert(len(res.columns),'train_flag',flag)  
    res['Diff_processed'] = df2.Diff_processed
    res['labelist'] = df2.labelist
    res['num'] = df2.num
    res = res.loc[ : , ~res.columns.str.contains('Unnamed')]
    res.to_csv(output_csv)
    
    print(f"✅ merge over：{output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", type=str, help="")
    args = parser.parse_args()

    merge_processed_data(args.project_name)


