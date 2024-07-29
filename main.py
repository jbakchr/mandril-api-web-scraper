import json

import requests
from bs4 import BeautifulSoup, Tag


def main() -> None:
    r = requests.get(
        "https://da.wikipedia.org/wiki/Figurer_fra_Casper_%26_Mandrilaftalen"
    )

    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")

    # extract_characters(tables[1])

    extract_actors(tables[1])

    # create_seasons_table()


def extract_characters(table: Tag):
    characters = []

    characters_table_body = table.find("tbody")
    character_table_rows = characters_table_body.find_all("tr")

    # Loop through each character
    for i, character_row in enumerate(character_table_rows):
        name = str(character_row.th.text).strip()

        desc_td = character_row.find_all("td")[-1:]
        for td in desc_td:
            desc = str(td.text).strip()

            character = {
                "character_id": i - 1,
                "character_name": name,
                "character_desc": desc,
            }

            characters.append(character)

    with open("./characters.json", "w", encoding="utf-8") as f:
        characters_json = json.dumps(characters)
        f.write(characters_json)


def extract_actors(table: Tag):
    actor_set = set()

    actors_table_body = table.find("tbody")
    actor_table_rows = actors_table_body.find_all("tr")

    for actor_row in actor_table_rows:
        actor_td = actor_row.find("td")

        if actor_td:
            td_links = actor_td.find_all("a")

            for td_link in td_links:
                actor_set.add(td_link.text)

    # First 3 elements are hard-coded missing actors
    actors = [
        {"actor_id": 1, "actor_name": "Iben Sol Mauritson"},
        {"actor_id": 2, "actor_name": "Freulein"},
        {"actor_id": 3, "actor_name": "Nordine Amraoui"},
    ]

    for actor in actor_set:
        actors.append({"actor_id": len(actors) + 1, "actor_name": actor})

    with open("./actors.json", "w") as f:
        actors_json = json.dumps(actors)
        f.write(actors_json)


def create_seasons_table():
    seasons = []
    counter = 0

    for season in range(1, 3):
        for episode in range(1, 49):
            if season == 2 and episode > 19:
                break

            counter += 1
            seasons.append(
                {"episode_title_number": counter, "season": season, "episode": episode}
            )

    with open("./episodes.json", "w") as f:
        seasons_json = json.dumps(seasons)
        f.write(seasons_json)


if __name__ == "__main__":
    main()
