from unittest import mock

from reddit_delta.reddit import get_listing_page, get_top_posts


def test_get_listing_page(popular_data_001):
    with mock.patch("requests.get") as mock_get:
        mock_json = mock_get().json
        mock_json.return_value = popular_data_001

        get_listing_page(
            base_url="http://localhost",
            subreddit="popular",
        )

        mock_get.assert_called_with(
            "http://localhost/r/popular.json",
            params=None,
            headers={"User-Agent": "reddit delta coding-test"},
        )


def test_get_top_posts(popular_data_001):
    with mock.patch("requests.get") as mock_get:
        mock_json = mock_get().json
        mock_json.return_value = popular_data_001

        get_top_posts(base_url="http://localhost", subreddit="popular", num_posts=50)

        mock_get.assert_any_call(
            "http://localhost/r/popular.json",
            params=None,
            headers={"User-Agent": "reddit delta coding-test"},
        )
        mock_get.assert_any_call(
            "http://localhost/r/popular.json",
            params={"after": "t3_x95x41"},
            headers={"User-Agent": "reddit delta coding-test"},
        )
