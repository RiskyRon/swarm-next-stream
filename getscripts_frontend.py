import os
import re

def generate_md_from_tsx_ts(output_file='output.md'):
    excluded_dirs = {'node_modules', '.next', '.git', 'ui', 'backend'}
    excluded_files = {'next-env.d.ts', 'get_scripts.py'}

    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if file.endswith(('.tsx', '.ts', '.py', '.css')) and file not in excluded_files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path)
                    
                    f.write(f"## {relative_path}\n\n")
                    f.write("```typescript\n")
                    
                    with open(file_path, 'r', encoding='utf-8') as script_file:
                        content = script_file.read()
                        # Remove BOM if present
                        content = re.sub(r'^\ufeff', '', content)
                        f.write(content)
                    
                    f.write("\n```\n\n")

    print(f"Markdown file '{output_file}' has been generated.")

# Usage
generate_md_from_tsx_ts()