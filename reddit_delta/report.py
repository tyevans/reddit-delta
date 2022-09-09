""" Functions for displaying subreddit deltas
"""
from rich.console import Console
from rich.table import Table

from reddit_delta.models import PostList


def format_delta_value(old_value: int, new_value: int) -> str:
    """ Compares to ints and returns a formatted string describing the difference."""
    if old_value > new_value:
        return f"{new_value} ([red]-{old_value - new_value}[/red])"
    elif old_value < new_value:
        return f"{new_value} ([green]+{new_value - old_value}[/green])"
    else:
        return f"{new_value} (--)"


def generate_delta_report(subreddit: str, old_posts: PostList, new_posts: PostList):
    """ Prints a subreddit delta report to the console
    """
    old_order = [post.data.name for post in old_posts.children]
    new_order = [post.data.name for post in new_posts.children]
    old_by_name = {post.data.name: post for post in old_posts.children}

    table = Table(title=f"r/{subreddit} Delta Report")
    table.add_column("Rank")
    table.add_column("Score")
    table.add_column("Title")

    for rank, post in enumerate(new_posts.children, 1):
        name = post.data.name
        score = post.data.score
        title = post.data.title

        try:
            prior_state = old_by_name[name]
        except KeyError:
            table.add_row(
                f"{rank} ([bold blue]New![/bold blue])", f"{score} (--)", title
            )
        else:
            prior_rank = old_order.index(post.data.name) + 1
            table.add_row(
                format_delta_value(prior_rank, rank),
                format_delta_value(prior_state.data.score, score),
                title,
            )

    console = Console()
    console.print(table)

    fallen_names = set(old_order).difference(new_order)
    if fallen_names:
        fallout_table = Table(
            title=f"r/{subreddit} - no longer appearing in top since last run"
        )
        fallout_table.add_column("Last Seen Rank")
        fallout_table.add_column("Last Seen Score")
        fallout_table.add_column("Title")

        for post_name in fallen_names:
            post = old_by_name[post_name]
            prior_rank = old_order.index(post_name) + 1

            fallout_table.add_row(
                str(prior_rank), str(post.data.score), post.data.title
            )

        console.print(fallout_table)
