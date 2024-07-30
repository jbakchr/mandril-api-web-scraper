import json
import sqlite3

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

    # appearances = extract_appareances(tables[1])

    # save_cleaned_appearances(appearances["cleaned"])

    # create_database()


def extract_characters(table: Tag) -> None:
    characters = []

    characters_table_body = table.find("tbody")
    character_table_rows = characters_table_body.find_all("tr")

    # Loop through each character
    for character_row in character_table_rows:
        name = str(character_row.th.text).strip()

        desc_td = character_row.find_all("td")[-1:]
        for td in desc_td:
            desc = str(td.text).strip()

            character = {
                "character_name": name,
                "character_desc": desc,
            }

            characters.append(character)

    with open("./data/characters.json", "w", encoding="utf-8") as f:
        characters_json = json.dumps(characters)
        f.write(characters_json)


def extract_actors(table: Tag) -> None:
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
        {"actor_name": "Iben Sol Mauritson"},
        {"actor_name": "Freulein"},
        {"actor_name": "Nordine Amraoui"},
    ]

    for actor in actor_set:
        actors.append({"actor_name": actor})

    with open("./data/actors.json", "w") as f:
        actors_json = json.dumps(actors)
        f.write(actors_json)


def create_seasons_table() -> None:
    seasons = []
    counter = 0

    for season in range(1, 3):
        for episode in range(1, 49):
            if season == 2 and episode > 19:
                break

            counter += 1
            seasons.append(
                {"episode_id": counter, "season": season, "episode": episode}
            )

    with open("./episodes.json", "w") as f:
        seasons_json = json.dumps(seasons)
        f.write(seasons_json)


def extract_appareances(table: Tag) -> dict:
    appearances = {"cleaned": [], "missing": []}

    appearances_table_body = table.find("tbody")
    appearances_table_rows = appearances_table_body.find_all("tr")

    # Extract cleaned table rows
    for appearance_row in appearances_table_rows[2:]:

        # Get appearance td
        appearance_td = appearance_row.find_all("td")[2].text.strip()

        # Check appearance td include a "-" or a "("
        if "-" in appearance_td or "(" in appearance_td:
            appearances["missing"].append(appearance_row)
        else:
            appearances["cleaned"].append(appearance_row)

    return appearances


def save_cleaned_appearances(cleaned_appearances_rows: dict):
    appearance_data = []

    # Load characters
    with open("./characters.json") as f:
        characters = json.loads(f.read())

    # Loop through each cleaned appearences row
    for i, appearance_row in enumerate(cleaned_appearances_rows):

        # Get "character_id" from "characters"
        character_id = characters[i]["character_id"]

        # Get appearances
        appearances = appearance_row.find_all("td")[2].text.strip()

        if "," in appearances:
            list_of_appearances = appearances.split(", ")
            for appearance in list_of_appearances:
                episode_id = int(appearance)

                appearance_item = {
                    "character_id": character_id,
                    "episode_id": episode_id,
                }

                appearance_data.append(appearance_item)
        else:
            appearance_item = {
                "character_id": character_id,
                "episode_id": int(appearances),
            }

            appearance_data.append(appearance_item)

    with open("./appearances.json", "w") as f:
        appearance_json = json.dumps(appearance_data)
        f.write(appearance_json)


def create_database():
    with open("./sql/create_database.sql") as f:
        sql_script = f.read()

    con = sqlite3.connect("mandril.db")

    cur = con.cursor()
    cur.executescript(sql_script)

    con.commit()
    con.close()


if __name__ == "__main__":
    main()
