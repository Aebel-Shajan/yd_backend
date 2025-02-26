import pandas as pd
import sqlite3
from yd_pipeline.utils import validate_columns, load_graphql_query
from typing import TypedDict, List
import requests


class ContributionInfo(TypedDict):
    commitCount: int
    occurredAt: str
    repository_name: str


def unpack_contributions_dict(contributions_for_repo: dict) -> List[ContributionInfo]:
    """Unpacks contribution dicts obtained from the using a graphql query on github
    contribution activity.

    Parameters
    ----------
    contributions_for_repo : dict
        Has structure like:
        ```
        {
            "contributions": {
                "nodes": [
                    {
                        "commitCount": int,
                        "occurredAt": str,
                        "repository": {
                            "name": str,
                            "url": str,
                            "openGraphImageUrl": str
                        }
                    }
                ]
            }
        }
        ```

    Returns
    -------
    list[ContributionInfo]
        Has structure like:
        ```
        [
            {
                commitCount: int
                occurredAt: str
                repository_name: str,
                repository_url: str,
                repositroy_image: str
            }
        ]
        ```
    """
    node_list = contributions_for_repo["contributions"]["nodes"]
    node_list = [
        {
            "commitCount": node["commitCount"],
            "occurredAt": node["occurredAt"],
            "repository_name": node["repository"][
                "name"
            ],  # these should all be the same :p
            "repository_url": node["repository"]["url"],
            "repository_image": node["repository"]["openGraphImageUrl"],
        }
        for node in node_list
    ]
    return node_list


def process_github_data(github_username: str, github_token: str):
    """Using github username and github token, generate a table containing all repos and all commits.

    I used a graphql query to get only the commitCount for each repo in a given year.
    I used the explorer from here: "https://docs.github.com/en/graphql/overview/explorer"

    The structure of the response json has the format:
    ```
    {
       "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": RepoContribution[]
                }
            }
        }
    }
    ```
    where RepoContribution has structure like:
    ```
    {
        "contributions": {
            "nodes": [
                {
                    "commitCount": int,
                    "occurredAt": str,
                    "repository": {
                        "name": str,
                        "url": str,
                        "openGraphImageUrl": str
                    }
                }
            ]
        }
    }
    ```

    Parameters
    ----------
    github_username : str
        Username for github.com
    github_token : str
        Github token for corresponding user.
    """
    query = load_graphql_query("yd_pipeline/graphql/github_user_contributions.graphql")
    variables = {
        "username": github_username,
        "from": "2024-01-01T00:00:00Z",
        "to": "2024-12-31T23:59:59Z",
    }
    headers = {"Authorization": f"Bearer {github_token}"}
    repos_url = f"https://api.github.com/graphql"
    response = requests.post(
        repos_url,
        json={"query": query, "variables": variables},
        headers=headers,
    )
    if not response.ok:
        response.raise_for_status()

    response_json = response.json()
    contributions_by_repos = response_json["data"]["user"]["contributionsCollection"][
        "commitContributionsByRepository"
    ]

    full_contribution_list = []
    for repo_contributions in contributions_by_repos:
        full_contribution_list.extend(unpack_contributions_dict(repo_contributions))

    github_activity_df = pd.DataFrame(full_contribution_list)
    validate_columns(
        github_activity_df,
        [
            "commitCount",
            "occurredAt",
            "repository_name",
            "repository_url",
            "repository_image",
        ],
    )
    github_activity_df = github_activity_df.rename(
        columns={"commitCount": "total_commits", "occurredAt": "date"}
    )
    github_activity_df["date"] = pd.to_datetime(
        github_activity_df["date"], format="ISO8601"
    ).dt.date
    connection = sqlite3.connect("data/output/year_in_data.db")
    github_activity_df.to_sql("github_data_daily", connection, if_exists="replace")


def get_distinct_repos():
    connection = sqlite3.connect("data/output/year_in_data.db")
    cursor = connection.cursor()
    query = """
    SELECT 
        repository_name, 
        repository_url, 
        repository_image, 
        MAX(date) as latest_date 
    FROM 
        github_data_daily 
    GROUP BY 
        repository_name, 
        repository_url, 
        repository_image
    ORDER BY 
        latest_date
    """
    distinct_repos = cursor.execute(query).fetchall()
    distinct_repos_df = pd.DataFrame(
        distinct_repos,
        columns=[
            "repository_name",
            "repository_url",
            "repository_image",
            "latest_date",
        ],
    )
    distinct_repos_df.to_sql("github_distinct_repos", connection, if_exists="replace")
