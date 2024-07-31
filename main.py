import json
import sqlite3
import os

import requests
from bs4 import BeautifulSoup, Tag


def main() -> None:
    # Remove database if it exists
    cur_dir = os.getcwd()
    db_filename = "mandril.db"
    db_path = os.path.join(cur_dir, db_filename)

    if os.path.isfile(db_path):
        os.remove(db_filename)

    # Extract characters table from Wikipedia
    r = requests.get(
        "https://da.wikipedia.org/wiki/Figurer_fra_Casper_%26_Mandrilaftalen"
    )
    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")

    # Extract character and actor data
    extract_characters_data(tables[1])
    # extract_actors_data(tables[1])

    # # Create seasons data
    # create_episodes_data()

    # # Create and seed database
    # create_database()
    # seed_database()

    # # Extract appearances data
    # appearances = extract_appareances(tables[1])

    # # Extract cleaned appearance data
    # extract_cleaned_appearances_data(appearances["cleaned"])

    # # Seed appearances table
    # seed_appearances()


def extract_characters_data(table: Tag) -> None:
    characters = []

    # Get all "tr" elements
    characters_table_body = table.find("tbody")
    character_table_rows = characters_table_body.find_all("tr")

    for i, character_row in enumerate(character_table_rows):
        # Get character name from "th" element
        name = str(character_row.th.text).strip()

        # Extract only "td" element containing description
        desc_td = character_row.find_all("td")[-1:]
        for td in desc_td:
            desc = str(td.text).strip()

            character = {
                "character_id": i,
                "character_name": name,
                "character_desc": desc,
            }

            characters.append(character)

    with open("./data/characters.json", "w", encoding="utf-8") as f:
        characters_json = json.dumps(characters)
        f.write(characters_json)


def extract_actors_data(table: Tag) -> None:
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


def create_episodes_data() -> None:
    seasons = []

    for season in range(1, 3):
        for episode in range(1, 49):
            if season == 2 and episode > 19:
                break

            seasons.append({"season": season, "episode": episode})

    with open("./data/episodes.json", "w") as f:
        seasons_json = json.dumps(seasons)
        f.write(seasons_json)


def create_database():
    with open("./sql/create_database.sql") as f:
        sql_script = f.read()

    con = sqlite3.connect("mandril.db")

    cur = con.cursor()
    cur.executescript(sql_script)

    con.commit()
    con.close()


def seed_database():
    # seed characters
    seed_characters()

    # seed episodes
    seed_episodes()


def seed_characters():
    cur_path = os.getcwd()

    with open(os.path.join(cur_path, "data", "characters.json")) as f:
        characters = json.loads(f.read())

    con = sqlite3.connect("mandril.db")
    cur = con.cursor()

    sql = """
            INSERT INTO
                characters (character_name, character_desc)
            VALUES
                (:character_name, :character_desc)
        """

    cur.executemany(sql, characters)
    con.commit()
    con.close()


def seed_episodes():
    cur_path = os.getcwd()

    with open(os.path.join(cur_path, "data", "episodes.json")) as f:
        episodes = json.loads(f.read())

    con = sqlite3.connect("mandril.db")
    cur = con.cursor()

    sql = """
            INSERT INTO
                episodes (season, episode)
            VALUES
                (:season, :episode)
        """

    cur.executemany(sql, episodes)
    con.commit()
    con.close()


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


def extract_cleaned_appearances_data(cleaned_appearances_rows: dict):
    appearance_data = []

    # Loop through each cleaned appearance row
    for appearance_row in cleaned_appearances_rows:

        # Extract character from appearance_row
        character_name = str(appearance_row.find("th").text).strip()

        # Get character id from database
        con = sqlite3.connect("mandril.db")
        cur = con.cursor()

        res = cur.execute(
            "SELECT character_id FROM characters WHERE character_name = ?",
            [
                character_name,
            ],
        )
        character_id = res.fetchone()[0]

        # Extract appearances
        appearances = str(appearance_row.find_all("td")[2].text).strip()

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

    with open("./data/appearances.json", "w") as f:
        appearances_json = json.dumps(appearance_data)
        f.write(appearances_json)


def seed_appearances():
    cur_path = os.getcwd()

    with open(os.path.join(cur_path, "data", "appearances.json")) as f:
        appearances = json.loads(f.read())

    con = sqlite3.connect("mandril.db")
    cur = con.cursor()

    sql = """
            INSERT INTO
                appearances (character_id, episode_id)
            VALUES
                (:character_id, :episode_id)
        """

    cur.executemany(sql, appearances)
    con.commit()
    con.close()


if __name__ == "__main__":
    main()
