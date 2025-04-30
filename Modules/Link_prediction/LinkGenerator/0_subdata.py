import argparse
import pandas as pd
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import preprocessor
import re
import csv
from tree_sitter import Language, Parser
from parser_lang import tree_to_token_index, index_to_code_token, tree_to_variable_index
from dgl.data.utils import save_graphs, load_graphs
from tkinter import _flatten

csv.field_size_limit(500 * 1024 * 1024)


def process_diff_tokens(project_name):
    
    lang = 'java'
    LANGUAGE = Language('parser_lang/my-languages.so', lang)
    parser = Parser()
    parser.set_language(LANGUAGE)
    newlist = []

    input_csv = f'../../../data/{project_name}_llm_link.csv'
    output_csv = f'../../../data/balancedata1/{project_name}_sub.csv'

    dummy_link = pd.read_csv(input_csv, engine='python')
    for index, row in dummy_link.iterrows():
        labelist = []
        Diff_processed = []
        difflist = eval(row['Diff'])
        tg = row['label']
        num = len(difflist)
        if tg == 0:
            labelist = [0] * num
        elif tg == 1:
            text = str(row['comment']) + str(row['compressed_llm_summary']) + str(row['compressed_llm_description'])
            text = text.lower()
            cf = eval(row['changed_files'])
            len1 = len(cf)
            if len1 == num:
                for i in range(len1):
                    func_name = cf[i].split('.')[0].split('/')[-1].lower()
                    if text.find(func_name) != -1:
                        labelist.append(1)
                    else:
                        labelist.append(0)
            else:
                labelist = [1] * num
        for d in difflist:
            diff = re.sub(r'\<ROW.[0-9]*\>', "", str(d))
            diff = re.sub(r'\<CODE.[0-9]*\>', "", diff)
            diff = re.sub(r'@.*[0-9].*@', "", diff)
            try:
                dl = preprocessor.extract_codetoken(diff, parser, lang)
            except:
                print(dl)
            if len(dl) == 0:
                dl = preprocessor.processDiffCode(diff)
            Diff_processed.append(dl)
        list1 = [Diff_processed, labelist, num]
        newlist.append(list1)
        # print(index)
    pd.DataFrame(newlist, columns=['Diff_processed', 'labelist', 'num']).to_csv(output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", type=str, help="")
    args = parser.parse_args()

    process_diff_tokens(args.project_name)