""" Functions for gathering the state of subreddits
"""
import json
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests

from reddit_delta.exc import NoPriorStateException
from reddit_delta.models import PostListPage, PostList


def get_listing_page(
    base_url: str, subreddit: str, after: Optional[str] = None
) -> PostListPage:
    """Retrieves a list of posts from the given subreddit

    :param base_url: base url of the reddit instance to query
    :param subreddit: name of the subreddit to use
    :param after: last seen post (used for pagination)
    """
    url = urljoin(base_url, f"r/{subreddit}.json")
    params = {"after": after} if after else None
    headers = {"User-Agent": "reddit delta coding-test"}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return PostListPage.parse_obj(response.json())


def get_top_posts(base_url: str, subreddit: str, num_posts: int) -> PostList:
    """Pulls the top posts from a subreddit

    :param base_url: base url of the reddit instance to query
    :param subreddit: name of the subreddit to use
    :param num_posts: number of posts to pull
    """
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


def load_state(state_dir: str, subreddit: str) -> PostList:
    """Retrieves the last saved state for a subreddit.

    :param state_dir: directory where state is stored.
    :param subreddit: subreddit to load state for
    :return: PostList instance
    """
    state_file = Path(state_dir) / f"{subreddit}.json"
    if not state_file.exists():
        raise NoPriorStateException
    with open(state_file, "rt") as fd:
        return PostList.parse_obj(json.load(fd))


def save_state(state_dir: str, subreddit: str, state: PostList):
    """Persists state into `state_dir`

    :param state_dir: directory where state is stored.
    :param subreddit: subreddit to load state for
    :param state: PostList instance to save
    """
    state_file = os.path.join(state_dir, f"{subreddit}.json")
    with open(state_file, "wt") as fd:
        json.dump(state.dict(), fd)


def validate_state(state: PostList, num_posts: int) -> PostList:
    """Validates state

    mainly ensuring state has *at most* `num_posts` children.

    :param state:
    :param num_posts:
    :return:
    """
    if num_posts < len(state.children):
        state = state.copy(update={"children": state.children[:num_posts]})

    return state
