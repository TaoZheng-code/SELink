import subprocess
import sys

projects = ['ambari', 'calcite', 'groovy', 'ignite', 'isis', 'netbeans']

def run_script(script_name, args):
    cmd = [sys.executable, script_name] + args
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ {script_name} run error：")
        print(result.stderr)
    else:
        print(f"✅ {script_name} run successful：")
        print(result.stdout)

for project in projects:
    print(f"Processing project: {project}")

    print("Step 1: Processing Diff Tokens...")
    run_script("0_subdata.py", [project])

    print("Step 2: Processing Issue & Commit Links...")
    run_script("1_splitword.py", [project])

    print("Step 3: Merging Processed Data...")
    run_script("2_sub_merge.py", [project])