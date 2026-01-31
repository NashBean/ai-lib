# github_to_text.py
import requests
import base64
import sys

def get_tree(owner, repo, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    r = requests.get(url)
    if r.status_code != 200:
        print("Error:", r.json())
        sys.exit(1)
    return r.json()["tree"]

def dump_file(owner, repo, path, out):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        if data.get("encoding") == "base64":
            content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
            out.write(f"\n\n===== {path} =====\n\n{content}\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python github_to_text.py owner/repo output.txt")
        sys.exit(1)
    
    repo_full = sys.argv[1]
    out_path = sys.argv[2]
    owner, repo = repo_full.split("/")
    
    tree = get_tree(owner, repo)
    with open(out_path, "w", encoding="utf-8") as out:
        for item in tree:
            if item["type"] == "blob" and should_include(item["path"]):  # reuse should_include from above
                print(f"Fetching {item['path']}")
                dump_file(owner, repo, item["path"], out)

