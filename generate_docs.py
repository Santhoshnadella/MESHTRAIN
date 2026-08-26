import os
import re

source_file = r"k:\meshtrAAin\addon prompt.txt"
output_dir = r"k:\meshtrAAin\docs\versions"

# Read the file
with open(source_file, "r", encoding="utf-8") as f:
    content = f.read()

# The versions start with "1. VERSION 0", "2. VERSION 1", etc.
pattern = re.compile(r"============================================================\n(?:\d+\.\s+VERSION\s+(\d+)\s+—\s+(.*?))\n============================================================\n(.*?)(?=\n============================================================|\Z)", re.DOTALL)

matches = pattern.findall(content)

file_mapping = {
    0: "V0_LOCAL.md",
    1: "V1_P2P.md",
    2: "V2_INTERNET.md",
    3: "V3_DHT.md",
    4: "V4_DISTRIBUTED_STORAGE.md",
    5: "V5_MESHSERVE.md",
    6: "V6_MESHTUNE.md",
    7: "V7_HIERARCHICAL.md",
    8: "V8_ELASTIC.md",
    9: "V9_VERIFIED.md",
    10: "V10_ZERO_TRUST.md",
    11: "V11_PRIVATE.md",
    12: "V12_COMMUNITY.md",
    13: "V13_WORKLOADS.md",
    14: "V14_MODEL_PARALLELISM.md",
    15: "V15_GLOBAL_FABRIC.md"
}

for match in matches:
    v_num = int(match[0])
    v_title = match[1].strip()
    v_content = match[2].strip()
    
    if v_num in file_mapping:
        filename = file_mapping[v_num]
        filepath = os.path.join(output_dir, filename)
        
        md_content = f"# VERSION {v_num} — {v_title}\n\n{v_content}\n"
        
        with open(filepath, "w", encoding="utf-8") as out_f:
            out_f.write(md_content)

print("Documentation generated successfully.")
