import json
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from rich import print as rich_print

from reddit_delta.exc import NoPriorStateException
from reddit_delta.models import PostListPage, PostList


def get_listing_page(base_url, subreddit: str, after: Optional[str] = None):
    url = urljoin(base_url, f"r/{subreddit}.json")
    params = {"after": after} if after else None
    headers = {"User-Agent": "reddit delta coding-test"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return PostListPage.parse_obj(response.json())


def get_top_posts(base_url, subreddit, num_posts):
    posts = []
    after = None

    while len(posts) < num_posts:
        page = get_listing_page(base_url, subreddit, after)
        if not page.data.children:
            break
        after = page.data.after
        posts.extend(page.data.children)

    posts = posts[:num_posts]

    return PostList(after=posts[-1].data.name, children=posts)


def load_state(state_dir, subreddit):
    state_file = Path(state_dir) / f"{subreddit}.json"
    if not state_file.exists():
        raise NoPriorStateException
    with open(state_file, "rt") as fd:
        return PostList.parse_obj(json.load(fd))


def save_state(state_dir, subreddit, state: PostList):
    state_file = os.path.join(state_dir, f"{subreddit}.json")
    with open(state_file, "wt") as fd:
        json.dump(state.dict(), fd)


def validate_state(state, num_posts):
    if num_posts > len(state.children):
        rich_print(
            f"[bold red]Post count mismatch (old: {len(state.children)}, current: {num_posts}).[/bold red]"
        )
        rich_print(f"[bold red]Discarding prior state.[/bold red]")
        state = PostList(children=[])

    elif num_posts < len(state.children):
        rich_print(
            f"[bold red]Post count mismatch (old: {len(state.children)}, current: {num_posts}).[/bold red]"
        )
        rich_print(f"[bold red]Truncating prior state.[/bold red]")
        state = state.copy(update={"children": state.children[:num_posts]})

    return state