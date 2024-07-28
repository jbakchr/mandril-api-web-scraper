import json

import requests
from bs4 import BeautifulSoup, Tag


def main() -> None:
    r = requests.get(
        "https://da.wikipedia.org/wiki/Figurer_fra_Casper_%26_Mandrilaftalen"
    )

    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")

    extract_characters(tables[1])


def extract_characters(table: Tag):
    characters = []

    characters_table_body = table.find("tbody")
    character_table_rows = characters_table_body.find_all("tr")

    # Loop through each character
    for character_row in character_table_rows:
        name = str(character_row.th.text).strip()

        desc_td = character_row.find_all("td")[-1:]
        for td in desc_td:
            desc = str(td.text).strip()

            character = {"name": name, "desc": desc}

            characters.append(character)

    with open("./characters.json", "w", encoding="utf-8") as f:
        characters_json = json.dumps(characters)
        f.write(characters_json)


if __name__ == "__main__":
    main()
