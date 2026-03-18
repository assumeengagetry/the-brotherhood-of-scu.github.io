import subprocess
import json
import sys

# 配置项
ORG_NAME = "The-Brotherhood-of-SCU"
EXCLUDE_REPOS = [".github"]

def run_graphql(org_name):
    query = """
    query($org: String!) {
      organization(login: $org) {
        repositories(first: 100, privacy: PUBLIC) {
          nodes {
            name
            description
            url
            pushedAt
          }
        }
      }
    }
    """
    
    cmd = [
        "gh", "api", "graphql",
        "-f", f"org={org_name}",
        "-f", f"query={query}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None
    return json.loads(result.stdout)

def main():
    print(f"# 正在获取 {ORG_NAME} 的私有仓库并按更新时间排序...")
    
    data = run_graphql(ORG_NAME)
    
    if not data or 'data' not in data or not data['data']['organization']:
        print("未能获取数据。")
        return

    repo_nodes = data['data']['organization']['repositories']['nodes']
    
    filtered_repos = [r for r in repo_nodes if r['name'] not in EXCLUDE_REPOS]
    
    sorted_repos = sorted(filtered_repos, key=lambda x: x['pushedAt'], reverse=True)

    output_file = "./source/_data/internal_projects.yml"
    with open(output_file, "w", encoding="utf-8") as f:
        for repo in sorted_repos:
            name = repo['name']
            description = repo['description'] or "暂无描述"
            link = repo['url']
            
            f.write(f"- name: {name}\n")
            f.write(f"  en_name: {name}\n")
            f.write(f"  description: {description}\n")
            f.write(f"  link: {link}\n\n")
            print(f"已导出: {name} (更新时间: {repo['pushedAt']})")

    print(f"\n✅ 导出完成！共 {len(sorted_repos)} 个仓库，已保存至 {output_file}")

if __name__ == "__main__":
    main()