import json
import os

import requests
from bs4 import BeautifulSoup, Tag


def main() -> None:

    # Extract characters table from Wikipedia
    url = "https://da.wikipedia.org/wiki/Figurer_fra_Casper_%26_Mandrilaftalen"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")

    # Extract character and actor data
    extract_characters_data(tables[1])
    extract_actors_data(tables[1])

    # # Create seasons data
    create_episodes_data()

    # Extract appearance data
    appearances = extract_appareances_tds(tables[1])

    simple_appearances = extract_simple_appearances(appearances["simple_tds"])
    complex_appearances = extract_complex_appearances(appearances["complex_tds"])

    combined_appearances = simple_appearances + complex_appearances

    save_appearances(combined_appearances)

    # Extract character played by
    extract_character_played_by_data(tables[1])


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
                "character_id": i - 1,
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

        # This is needed as 2 "td" elements apparently come out as "None" .. ??
        if actor_td:
            td_links = actor_td.find_all("a")

            if td_links:
                for td_link in td_links:
                    actor_set.add(td_link.text)
            else:
                actor_set.add(actor_td.text.strip())

    actors = []
    for i, actor in enumerate(actor_set):
        actors.append({"actor_id": i + 1, "actor_name": actor})

    cur_dir = os.getcwd()
    with open(os.path.join(cur_dir, "data", "actors.json"), "w") as file:
        actors_json = json.dumps(actors)
        file.write(actors_json)


def create_episodes_data() -> None:
    seasons = []
    episode_counter = 0

    for season in range(1, 3):
        for episode in range(1, 49):
            if season == 2 and episode > 19:
                break

            episode_counter += 1

            seasons.append(
                {"episode_id": episode_counter, "season": season, "episode": episode}
            )

    with open("./data/episodes.json", "w") as f:
        seasons_json = json.dumps(seasons)
        f.write(seasons_json)


def extract_appareances_tds(table: Tag) -> dict:
    appearances = {"simple_tds": [], "complex_tds": []}

    table_body = table.find("tbody")
    table_rows = table_body.find_all("tr")

    for row in table_rows[2:]:
        # Get appearance td
        appearance_td = str(row.find_all("td")[2].text).strip()

        # Check appearance td include a "-" or a "("
        if "-" in appearance_td or "(" in appearance_td:
            appearances["complex_tds"].append(row)
        else:
            appearances["simple_tds"].append(row)

    return appearances


def extract_simple_appearances(simple_td_rows: list) -> list[dict]:
    simple_appearances = []

    # Load all characters
    with open("./data/characters.json") as file:
        characters = json.loads(file.read())

    # Loop through each simple appearance td
    for appearance_row in simple_td_rows:

        # Get character id
        character_name = str(appearance_row.find("th").text).strip()

        character_id = get_character_id(characters, character_name)

        # Get appearances
        appearances = str(appearance_row.find_all("td")[2].text).strip()

        # Check for multiple appearances
        if "," in appearances:
            list_of_appearances = appearances.split(", ")
            for appearance in list_of_appearances:
                episode_id = int(appearance)

                appearance_item = {
                    "character_id": character_id,
                    "episode_id": episode_id,
                }

                simple_appearances.append(appearance_item)
        else:
            appearance_item = {
                "character_id": character_id,
                "episode_id": int(appearances),
            }

            simple_appearances.append(appearance_item)

    return simple_appearances


def extract_complex_appearances(complex_td_rows: list) -> list[dict]:
    complex_appearances = []

    # Load all characters
    with open("./data/characters.json") as file:
        characters = json.loads(file.read())

    # Loop through each complex td rows
    for appearance_row in complex_td_rows:

        # Get character id
        character_name = str(appearance_row.find("th").text).strip()

        character_id = get_character_id(characters, character_name)

        # Get appearances
        appearances = str(appearance_row.find_all("td")[2].text).strip()

        if "(" in appearances:
            list_of_appearances = extract_appearances_without_parentheses(appearances)

            for appearance in list_of_appearances:
                appearance_item = {
                    "character_id": character_id,
                    "episode_id": appearance,
                }

                complex_appearances.append(appearance_item)

        else:
            list_of_appearances = extract_appearance_sequences(appearances)

            # Loop through each appearance and add to "complex_appearances"
            for appearance in list_of_appearances:
                appearance_item = {
                    "character_id": character_id,
                    "episode_id": appearance,
                }

                complex_appearances.append(appearance_item)

    # print(complex_appearances)

    return complex_appearances


def extract_appearances_without_parentheses(appearances: str) -> list[int]:
    result = []

    # Split string of appearances by ", "
    splitted_appearance = appearances.split(", ")

    # Loop through each splitted appearance
    for appearance in splitted_appearance:

        if "(" in appearance:
            # Split appearance by " ("
            cleaned_appearance = appearance.split(" (")[0]

            # Check if "cleaned_appearance" has a "-" in it
            if "-" in cleaned_appearance:

                splitted_cleaned_appearance = cleaned_appearance.split("-")

                start = int(splitted_cleaned_appearance[0])
                end = int(splitted_cleaned_appearance[1])

                for i in range(start, end + 1):
                    result.append(i)

            else:
                result.append(int(cleaned_appearance))
        else:
            result.append(int(appearance))

    return result


def extract_appearance_sequences(string_of_apperances: str) -> list[int]:
    apperances = []

    # Split appearances
    splitted_appearances = string_of_apperances.split(", ")

    # Loop through appearances
    for apperance in splitted_appearances:

        # Checks multiple appearances
        if "-" in apperance:
            # Split appearance to extract each appearance
            splitted_appearance = apperance.split("-")

            # Extract start and stop appearance
            start = splitted_appearance[0]
            end = splitted_appearance[1]

            for i in range(int(start), int(end) + 1):
                apperances.append(i)
        else:
            apperances.append(int(apperance))

    return apperances


def save_appearances(appearances: list[dict]) -> None:
    with open("./data/appearances.json", "w") as f:
        c_json = json.dumps(appearances)
        f.write(c_json)


def extract_character_played_by_data(table: Tag):
    # Get all "played by" trs
    tbody = table.find("tbody")
    played_by_trs = tbody.find_all("tr")

    # Load characters
    with open("./data/characters.json") as file:
        characters = json.loads(file.read())

    # Get character id and actor ids
    for tr in played_by_trs:

        # Get character id
        character_name = str(tr.find("th").text).strip()
        character_id = get_character_id(characters, character_name)

        # Get list of actor ids
        actor_td = tr.find("td")

        actor_names = get_list_of_actor_names(actor_td)
        print(actor_names)


def get_character_id(characters: list[str], name: str) -> int:

    # # Loop through all characters and find the character id
    for character in characters:
        character_name = character["character_name"]

        if character_name == name:
            return character["character_id"]


def get_list_of_actor_names(actor_td):
    list_of_actor_names = []

    # TODO: Her er du nået til!!

    if actor_td:

        # Check for multiple actors
        if "og" in actor_td.text:

            if ", " in actor_td.text:
                splitted_by_ampersand = str(actor_td.text).strip().split(" og ")

                split_by_comma = splitted_by_ampersand[0].split(", ")

                for name in split_by_comma:
                    list_of_actor_names.append(name)

                end_name = splitted_by_ampersand[1]
                list_of_actor_names.append(end_name)

            else:
                splitted_actor_names = str(actor_td.text).strip().split(" og ")

                for name in splitted_actor_names:
                    list_of_actor_names.append(name)

        else:
            has_link = actor_td.find("a")

            if has_link:
                actor = has_link.text
                list_of_actor_names.append(actor)
            else:
                actor = str(actor_td.text).strip()
                list_of_actor_names.append(actor)

    return list_of_actor_names


if __name__ == "__main__":
    main()
