from typing import Literal, TypedDict

import grequests
from thefuzz import fuzz

BASE_URL = "https://hacker-news.firebaseio.com/v0"


class Post(TypedDict):
    title: str
    url: str
    comments_url: str
    by: str
    score: int
    timestamp: int


def get_stories(num: int = 10, key=Literal["topstories", "newstories"]) -> list[Post]:
    """
    Retrieve a list of stories from HackerNews
    Either top stories (key="topstories") or newest stories (key="newstories")

    Args:
    - num (int): Number of stories to retrieve
    - key (str): Either "topstories" or "newstories"

    Returns:
        A list of stories, where each story is a dictionary with the following keys:
        - title (str): The title of the story
        - url (str): The URL of the posted story
        - comments_url (str): The URL linking to the HackerNews comments thread
        - by (str): The username of the original poster
        - score (int): The current score of the story
        - timestamp (int): Creation timestamp of the story in Unix Time
    """
    response = grequests.map((grequests.get(BASE_URL + f"/{key}.json"),))
    data = response[0].json()
    post_responses = grequests.map(
        grequests.get(f"{BASE_URL}/item/{post_id}.json") for post_id in data[:num]
    )
    posts = [r.json() for r in post_responses]
    return [
        Post(
            title=p.get("title"),
            url=p.get("url"),
            comments_url=f"https://news.ycombinator.com/item?id={p.get('id')}",
            by=p.get("by"),
            score=p.get("score"),
            timestamp=p.get("timestamp"),
        )
        for p in posts
    ]


def get_top_stories(num: int = 10) -> list[Post]:
    """
    Retrieve the top stories from HackerNews

    Args:
    - num (int): Number of stories to retrieve

    Returns:
        A list of stories, where each story is a dictionary with the following keys:
        - title (str): The title of the story
        - url (str): The URL of the posted story
        - comments_url (str): The URL linking to the HackerNews comments thread
        - by (str): The username of the original poster
        - score (int): The current score of the story
        - timestamp (int): Creation timestamp of the story in Unix Time
    """
    return get_stories(num, "topstories")


def get_new_stories(num: int = 10) -> list[Post]:
    """
    Retrieve the newest stories from HackerNews

    Args:
    - num (int): Number of stories to retrieve

    Returns:
        A list of stories, where each story is a dictionary with the following keys:
        - title (str): The title of the story
        - url (str): The URL of the posted story
        - comments_url (str): The URL linking to the HackerNews comments thread
        - by (str): The username of the original poster
        - score (int): The current score of the story
        - timestamp (int): Creation timestamp of the story in Unix Time
    """
    return get_stories(num, "newstories")


def search_new_stories_by_title(query: str, num: int = 10) -> list[Post]:
    """
    Search the newest stories by their titles
    Uses fuzzy string matching to match the query to story titles

    Args:
    - query (str): Search query
    - num (int): Number of stories to retrieve

    Returns:
        A list of stories, where each story is a dictionary with the following keys:
        - title (str): The title of the story
        - url (str): The URL of the posted story
        - comments_url (str): The URL linking to the HackerNews comments thread
        - by (str): The username of the original poster
        - score (int): The current score of the story
        - timestamp (int): Creation timestamp of the story in Unix Time
    """
    posts = get_new_stories(num=100)
    posts.sort(key=lambda x: -fuzz.token_set_ratio(query, x["title"]))
    return posts[:num]
