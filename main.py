import requests


def get_nobel():
    url = 'https://masterdataapi.nobelprize.org/2.1/laureates?offset=0&limit=100'
    laureates = []
    while True:
        new_laureates = requests.get(
            url=url,
        ).json()
        print(new_laureates['links'])
        for new_laureate in new_laureates['laureates']:
            name_key = 'fullName'
            birth_key = 'birth'
            if 'orgName' in new_laureate.keys():
                name_key = 'orgName'
                birth_key = 'founded'
            laureate = {
                'id': new_laureate['id'],
                'name': '\'' + new_laureate[name_key]['en'].replace(',', '') + '\'',
                'gender': check_exists(new_laureate, ['gender']),
                'birth_date': check_exists(new_laureate, [birth_key, 'date']),
                'birth_country': check_exists(new_laureate, [birth_key, 'place', 'country', 'en']),
                'death_date': check_exists(new_laureate, ['death', 'date']),
                'death_country': check_exists(new_laureate, ['death', 'place', 'country', 'en']),
                'prize_amount': len(new_laureate['nobelPrizes']),
                'prize_years': str([int(new_laureate['nobelPrizes'][i]['awardYear'])
                                    for i in range(len(new_laureate['nobelPrizes']))])
                .replace('[', '\'').replace(']', '\''),
                'prize_categories': '\'' + str([new_laureate['nobelPrizes'][i]['category']['en']
                                                for i in range(len(new_laureate['nobelPrizes']))])
                .lstrip('[').rstrip(']').replace('\'', '') + '\''
            }
            # print(laureate)
            laureates.append(laureate)
        if 'next' not in new_laureates['links'].keys():
            break
        url = new_laureates['links']['next']
    return laureates


def check_exists(dictionary, sub_keys):
    for key in sub_keys:
        if key in dictionary.keys():
            dictionary = dictionary[key]
        else:
            return 'NULL'
    return '\'' + dictionary + '\''


def laureate_line(laureate):
    insert = "INSERT INTO laureates(ID, Name, Gender, Birth_Date, Birth_Country, Death_Date, " \
             "Death_Country, Prize_Amount, Prize_Years, Prize_Categories) "
    a = "VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}))\n".format(laureate['id'], laureate['name'],
                                                                              laureate['gender'],
                                                                              laureate['birth_date'],
                                                                              laureate['birth_country'],
                                                                              laureate['death_date'],
                                                                              laureate['death_country'],
                                                                              laureate['prize_amount'],
                                                                              laureate['prize_years'],
                                                                              laureate['prize_categories'])
    return insert + a


if __name__ == '__main__':
    nobel_laureates = get_nobel()
    with open('data.sql', 'w') as f:
        intro = """CREATE TABLE laureates(
    ID                  INTEGER PRIMARY KEY,
    Name                TEXT,
    Gender              TEXT,
    Birth_Date          TEXT,
    Birth_Country       TEXT,
    Death_Date          TEXT,
    Death_Country       TEXT,
    Prize_Amount        INTEGER,
    Prize_Years         TEXT,
    Prize_Categories    TEXT
);
"""
        f.write(intro)
        f.writelines(laureate_line(laureate) for laureate in nobel_laureates)
