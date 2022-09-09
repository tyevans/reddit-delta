from typing import Optional, List

from pydantic import BaseModel


class Post(BaseModel):
    subreddit: str
    name: str
    title: str
    score: int
    ups: int
    downs: int
    upvote_ratio: float


class PostContainer(BaseModel):
    data: Post


class PostList(BaseModel):
    after: Optional[str]
    children: List[PostContainer]


class PostListPage(BaseModel):
    data: PostList
