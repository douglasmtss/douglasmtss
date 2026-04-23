import requests
import os
from collections import Counter
from urllib.parse import quote

GITHUB_API = "https://api.github.com"
USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

LANG_CONFIG = {
    "HTML":             {"color": "E34F26", "logo": "html5",      "logoColor": "white"},
    "Java":             {"color": "007396", "logo": "openjdk",    "logoColor": "white"},
    "TypeScript":       {"color": "3178C6", "logo": "typescript", "logoColor": "white"},
    "JavaScript":       {"color": "F7DF1E", "logo": "javascript", "logoColor": "black"},
    "CSS":              {"color": "1572B6", "logo": "css3",       "logoColor": "white"},
    "Jupyter Notebook": {"color": "F37626", "logo": "jupyter",    "logoColor": "white"},
    "Dart":             {"color": "0175C2", "logo": "dart",       "logoColor": "white"},
    "C++":              {"color": "00599C", "logo": "cplusplus",  "logoColor": "white"},
    "C":                {"color": "A8B9CC", "logo": "c",          "logoColor": "black"},
    "CMake":            {"color": "064F8C", "logo": "cmake",      "logoColor": "white"},
    "Python":           {"color": "3776AB", "logo": "python",     "logoColor": "white"},
    "MDX":              {"color": "1B1F24", "logo": "markdown",   "logoColor": "white"},
    "Shell":            {"color": "4EAA25", "logo": "gnubash",    "logoColor": "white"},
    "Hack":             {"color": "878787", "logo": "php",        "logoColor": "white"},
    "SCSS":             {"color": "CC6699", "logo": "sass",       "logoColor": "white"},
    "Ruby":             {"color": "CC342D", "logo": "ruby",       "logoColor": "white"},
}


def format_bytes(b):
    if b >= 1_000_000:
        return f"{b / 1_000_000:.1f} MB"
    elif b >= 1_000:
        return f"{b / 1_000:.1f} KB"
    return f"{b} B"


def make_badge(lang, bytes_count):
    config = LANG_CONFIG.get(lang, {"color": "555555", "logo": "code", "logoColor": "white"})
    color = config["color"]
    logo = config["logo"]
    logo_color = config.get("logoColor", "white")
    size = format_bytes(bytes_count)
    label = quote(lang, safe="")
    return (
        f'<img src="https://img.shields.io/badge/{label}-{color}'
        f'?style=flat-square&logo={logo}&logoColor={logo_color}" alt="{lang}" />'
    )

def get_repositories(username):
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API}/users/{username}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_languages(repo_full_name):
    url = f"{GITHUB_API}/repos/{repo_full_name}/languages"
    response = requests.get(url, headers=headers)
    return response.json()

def update_readme(languages):
    start_tag = "<!-- LANGUAGES-START -->"
    end_tag = "<!-- LANGUAGES-END -->"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    before = content.split(start_tag)[0]
    after = content.split(end_tag)[-1]

    cols = 4
    rows = []
    for i in range(0, len(languages), cols):
        chunk = languages[i:i + cols]
        cells = "".join(
            f'\n<td align="center">{make_badge(lang, b)}<br/><sub><b>{format_bytes(b)}</b></sub></td>'
            for lang, b in chunk
        )
        rows.append(f"<tr>{cells}\n</tr>")

    table = "<table>\n" + "\n".join(rows) + "\n</table>"
    new_content = f"{before}{start_tag}\n{table}\n{end_tag}{after}"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    repos = get_repositories(USERNAME)
    language_counter = Counter()

    for repo in repos:
        if repo.get("fork"):
            continue
        languages = get_languages(repo["full_name"])
        for lang, count in languages.items():
            language_counter[lang] += count

    sorted_languages = language_counter.most_common()
    update_readme(sorted_languages)

if __name__ == "__main__":
    main()
