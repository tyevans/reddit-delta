import requests
import typer
from rich import print as rich_print

from reddit_delta.exc import NoPriorStateException
from reddit_delta.models import PostList
from reddit_delta.reddit import load_state, get_top_posts, save_state, validate_state
from reddit_delta.report import generate_delta_report

app = typer.Typer()


@app.command()
def redditdelta(
    subreddit: str = typer.Option(
        "popular", help="Name of the subreddit to pull posts from."
    ),
    base_url: str = typer.Option(
        "https://www.reddit.com", help="Base url of the reddit instance."
    ),
    state_dir: str = typer.Option(
        ".", help="Local directory to save state in between runs."
    ),
    num_posts: int = typer.Option(75, help="Number of posts to pull."),
):
    """
    Pulls the top posts from a subreddit and displays changes since last run.
    """
    try:
        old_posts = load_state(state_dir, subreddit)
    except NoPriorStateException:
        rich_print("[bold red]No prior state found![/bold red]")
        old_posts = PostList(children=[])
    else:
        old_posts = validate_state(old_posts, num_posts)

    try:
        new_posts = get_top_posts(base_url, subreddit, num_posts)
    except requests.exceptions.HTTPError:
        rich_print("[bold red]Error retrieving reddit data![/bold red]")
        raise typer.Exit(code=1)

    generate_delta_report(subreddit, old_posts, new_posts)
    save_state(state_dir, subreddit, new_posts)


if __name__ == "__main__":
    app()
