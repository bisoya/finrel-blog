import feedparser
import os
import re
from markdownify import markdownify
import html

BLOG_URI = "https://finrel.tistory.com/"
GITHUB_URI = "https://github.com/jectgenius/finrel-blog/tree/main/"


def update(feeds: list):
    for feed in feeds:
        category = feed["tags"][0]["term"]
        title = feed["title"]
        content = create_content(title, feed["summary"])

        file_name = get_file_name(category, title)
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        update_readme(category)

    # 최근 10개 포스팅을 README에 업데이트
    update_readme_with_recent_posts(feeds)


def create_content(title: str, summary: str) -> str:
    summary = html.unescape(summary)
    contents = summary.split("<pre>")

    for i in range(len(contents)):
        code_block = re.search(r'<code\s+class="([^"]+)"', contents[i])
        if code_block:
            language = code_block.group(1)
            if "language-" in language:
                language = language.replace("language-", "")
            contents[i] = attach_language(language, "<pre>" + contents[i])
        else:
            contents[i] = markdownify(contents[i])
    return f"{title}\n=\n" + "".join(contents)


def attach_language(language: str, content: str) -> str:
    content = markdownify(content).split("```")
    return "\n```" + language + content[1] + "```\n" + "".join(content[2:])


def get_file_name(category: str, title: str) -> str:
    file_path = f"{category}/{title}/".replace(" ", "_")
    os.makedirs(file_path, exist_ok=True)
    return file_path + "README.md"


def update_readme(category: str):
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    if readme.find(category) == -1:
        with open("README.md", "a", encoding="utf-8") as f:
            f.write(f"\n- [{category}]({GITHUB_URI + category})")

    sort_toc()


def sort_toc():
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    start = readme.find("## 📌 카테고리")
    toc = readme[start:].strip()
    toc_lines = sorted(toc.split("\n")[1:])
    sort_toc = "\n".join(["## 📌 카테고리"] + toc_lines)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme.replace(toc, sort_toc))


def update_readme_with_recent_posts(feeds: list, post_count: int = 10):
    # :zap: 최근 발행 포스트 가져오기
    recent_posts = feeds[:post_count]
    
    # :zap: 최근 발행 포스트 목록을 Markdown 형식으로 구성
    recent_posts_content = "\n".join(
        [f"- 🪙 [{post.title}]({post.link})" for post in recent_posts]
    )
    
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # "## :zap: 최근 발행 포스트" 섹션 업데이트
    if "## :zap: 최근 발행 포스트" in readme:
        start_index = readme.find("## :zap: 최근 발행 포스트")
        end_index = readme.find("##", start_index + 1) if "##" in readme[start_index + 1:] else len(readme)
        updated_readme = readme[:start_index] + f"## :zap: 최근 발행 포스트\n{recent_posts_content}\n" + readme[end_index:]
    else:
        updated_readme = readme + f"\n\n## :zap: 최근 발행 포스트\n{recent_posts_content}\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated_readme)


if __name__ == "__main__":
    feeds = feedparser.parse(BLOG_URI + "rss")
    update(feeds["entries"])