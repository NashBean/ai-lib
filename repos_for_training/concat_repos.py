# concat_repos.py – concatenates code files from cloned repos
import os
import argparse

def should_include(path):
    ext = os.path.splitext(path)[1].lower()
    name = os.path.basename(path).lower()
    # Focus on code; skip binaries, large data, venv, etc.
    good_exts = {'.py', '.cpp', '.h', '.hpp', '.c', '.kt', '.java', '.js', '.ts', '.html', '.css', '.sh', '.md', '.txt', '.yaml', '.json', '.toml'}
    skip_dirs = {'venv', '__pycache__', 'node_modules', '.git', 'build', 'dist', 'logs'}
    skip_files = {'package-lock.json', 'yarn.lock', '.min.js'}
    
    if any(s in path for s in skip_dirs):
        return False
    if name in skip_files:
        return False
    return ext in good_exts

def concat_repo(root_dir, output_file, prefix=""):
    for root, dirs, files in os.walk(root_dir):
        # Skip unwanted dirs
        dirs[:] = [d for d in dirs if d not in {'venv', '__pycache__', 'node_modules', '.git'}]
        
        for file in files:
            path = os.path.join(root, file)
            if should_include(path):
                rel_path = os.path.relpath(path, root_dir)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    output_file.write(f"\n\n===== {prefix}/{rel_path} =====\n\n")
                    output_file.write(content)
                    output_file.write("\n\n")
                except Exception as e:
                    print(f"Skipped {path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="input_code.txt")
    parser.add_argument("dirs", nargs="+", help="directories to process (e.g. repos_for_training/nanoGPT)")
    args = parser.parse_args()
    
    with open(args.output, "w", encoding="utf-8") as out:
        for d in args.dirs:
            if os.path.isdir(d):
                print(f"Processing {d}...")
                concat_repo(d, out, prefix=os.path.basename(d))
            else:
                print(f"Skipping {d} (not a dir)")
    
    print(f"Done. Wrote to {args.output}")
    print("Size:", os.path.getsize(args.output) / (1024*1024), "MB")

# Add more dirs as needed
# python concat_repos.py repos_for_training/nanoGPT repos_for_training/llm.c repos_for_training/LLMs-from-scratch
