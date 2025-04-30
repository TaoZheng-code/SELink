**1. select_new_res_10.py**  
- Reads the top 10 rows of the EALink results.
- Selects the top 10 unique `s_id` entries from the relink result table, retrieving `s_id`, `t_id`, and `label`.
- The model name should be updated manually when running the script.
- Output:  
  `../../../data/unique_res_10/{project}/res_10.csv`

**2. select_new_res_data_10.py**  
- Based on the results obtained in the previous step, retrieves the fields `['s_id', 't_id', 'description', 'summary', 'message', 'label']`.
- The model name should be updated manually when running the script.
- Output:  
  `../../../data/unique_res_10/{project}/{project}_new_res_10.csv`

**3. relink_sort.py**  
- Performs re-linking using LLMs based on the issue and commit information and reorders the candidates.
- The model name and project name should be updated manually when running the script.
- Output:  
  `../../../data/unique_res_10/{project}/{project}_resorted_res.csv`

**4. resort_res.py**  
- Recalculates the evaluation metrics based on the new sorted results.
- Output: 
  `../../../data/model/resort_results.csv`