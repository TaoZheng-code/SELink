import argparse
import pandas as pd
import preprocessor
import re
import csv
from tree_sitter import Language, Parser
from parser_lang import tree_to_token_index, index_to_code_token, tree_to_variable_index
from dgl.data.utils import save_graphs, load_graphs
from tkinter import _flatten

csv.field_size_limit(500 * 1024 * 1024)


def process_link_data(project_name, model_name):
    
    lang = 'java'
    LANGUAGE = Language('parser_lang/my-languages.so', lang)
    parser = Parser()
    parser.set_language(LANGUAGE)
    process = []

    input_csv = f'../../../data/{project_name}_llm_link.csv'
    output_csv = f'../../../data/balancedata2/{project_name}_link_process.csv'
    
    dummy_link = pd.read_csv(input_csv, engine='python')
    dummy_link.rename(columns={'commitid': 'hash'}, inplace=True)
    
    for index, row in dummy_link.iterrows():
        summary_processed = preprocessor.preprocessNoCamel(str(row['compressed_llm_summary']).strip('[]'))
        description_processed = preprocessor.preprocessNoCamel(str(row['compressed_llm_description']).strip('[]'))
        message_processed = preprocessor.preprocessNoCamel(str(row['compressed_llm_message']).strip('[]'))
        
        diff = re.sub(r'\<ROW.[0-9]*\>', "", str(row['Diff']))
        diff = re.sub(r'\<CODE.[0-9]*\>', "", diff)
        Diff_processed = preprocessor.processDiffCode(diff)
        
        changed_files = [f.split('/')[-1] for f in eval(row['changed_files'])]
        codelist_processed = [preprocessor.extract_codetoken(code, parser, lang) for code in eval(row['codelist'])]
        
        issue_text = str(row['compressed_llm_summary']) + str(row['compressed_llm_description']) + str(row['comment'])
        issuecode = preprocessor.getIssueCode(issue_text)
        
        list1 = [row['source'], row['product'], row['issue_id'], row['component'], row['creator_key'],
                 row['create_date'], row['update_date'], row['last_resolved_date'], summary_processed,
                 description_processed, issuecode, row['issue_type'], row['status'], row['repo'], row['hash'],
                 row['parents'], row['author'], row['committer'], row['author_time_date'],
                 row['commit_time_date'], message_processed, row['commit_issue_id'],
                 changed_files, Diff_processed, codelist_processed, row['label'],
                 row['train_flag']]
        
        process.append(list1)
        # print(index)
    
    pd.DataFrame(process, columns=['source', 'product', 'issue_id', 'component', 'creator_key',
                                   'create_date', 'update_date', 'last_resolved_date', 'summary_processed',
                                   'description_processed', 'issuecode', 'issue_type', 'status', 'repo', 'hash',
                                   'parents', 'author', 'committer', 'author_time_date',
                                   'commit_time_date', 'message_processed', 'commit_issue_id',
                                   'changed_files', 'Diff_processed', 'codelist_processed', 'label',
                                   'train_flag']).to_csv(output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", type=str, help="")
    args = parser.parse_args()

    process_link_data(args.project_name)