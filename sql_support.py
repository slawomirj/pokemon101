# -*- coding: utf-8 -*-
import random
from openpyxl import load_workbook
import sqlite3


def pokemon_xls():
    pok_dict = dict()
    wb = load_workbook('pok.xlsx')
    structure_ranges = wb.active
    for row in range(1000):
        if structure_ranges["A" + str(row + 2)].value is not None:
            pok_dict_temp = dict()
            pok_dict_temp["name"] = str(structure_ranges["A" + str(row + 2)].value)
            pok_dict_temp["hp"] = str(structure_ranges["B" + str(row + 2)].value)
            pok_dict_temp["attack_1"] = str(structure_ranges["C" + str(row + 2)].value)
            pok_dict_temp["damage_1"] = str(structure_ranges["D" + str(row + 2)].value)
            pok_dict_temp["attack_2"] = str(structure_ranges["E" + str(row + 2)].value)
            pok_dict_temp["damage_2"] = str(structure_ranges["F" + str(row + 2)].value)
            pok_dict_temp["ultra_beast"] = str(structure_ranges["G" + str(row + 2)].value)
            pok_dict_temp["stage"] = str(structure_ranges["H" + str(row + 2)].value)
            pok_dict_temp["img"] = str(structure_ranges["I" + str(row + 2)].value)
            pok_dict[str(structure_ranges["A" + str(row + 2)].value)] = pok_dict_temp
    return pok_dict



def random_int(r):
    ri = random.randint(0, r)
    return ri


class PSQL():
    def __init__(self):
        self.db = sqlite3.connect("data.db")
        self.cursor = self.db.cursor()

    def check_user(self, user1, e_mail, password):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user( "
                            "user_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "user_name TEXT,"
                            "e_mail TEXT,"
                            "password TEXT,"
                            "first_time TEXT,"
                            "battle_won INT DEFAULT 0 ,"
                            "battle_lost INT DEFAULT 0,"
                            "xp INT DEFAULT 0,"
                            "coin INT DEFAULT 0,"
                            "diamond INT DEFAULT 0)""")
        self.cursor.execute("SELECT user_name FROM user WHERE user_name='" + user1 + "'")
        psw_rows = self.cursor.fetchall()
        if len(psw_rows) == 0:
            # todo do ustawienia wartości 0
            first_time = "yes"
            self.cursor.execute("INSERT INTO user(user_name, e_mail, password, first_time)VALUES(?,?,?,?)",
                                (user1, e_mail, password, first_time))
            self.db.commit()
            return 1
        else:
            return 0

    def check_user_pswd(self, user, password):
        self.cursor.execute("SELECT password FROM user WHERE user_name='" + user + "'")
        psw_rows = self.cursor.fetchall()
        if len(psw_rows) == 0:
            return "Nie ma takiego gracza"
        else:
            if str(psw_rows[0][0]) == str(password):
                return "ok"
            else:
                return "Hasło jest nie poprawne"

    def show_user(self, user):
        self.cursor.execute("SELECT * FROM user WHERE user_name='" + user + "'")
        user_info = self.cursor.fetchall()
        return user_info

    def show_pokemons(self, user):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS all_pokemons( "
                            "pokemons_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "pokemon_name TEXT,"
                            "user_name TEXT,"
                            "user_id INT,"
                            "FOREIGN KEY(user_id) REFERENCES user(user_id))""")
        self.cursor.execute("SELECT * FROM all_pokemons WHERE user_name='" + user + "'")
        user_info = self.cursor.fetchall()
        return user_info

    def add_pokemon_for_user(self, user, p1):
        self.cursor.execute("SELECT user_id FROM user WHERE user_name='" + user + "'")
        psw_rows = self.cursor.fetchall()
        self.cursor.execute("INSERT INTO all_pokemons(pokemon_name, user_name, user_id)VALUES(?,?,?)",
                            (p1, user, psw_rows[0][0]))
        self.cursor.execute("UPDATE user SET first_time='no' WHERE user_id='" + str(psw_rows[0][0]) + "'")
        self.db.commit()

        # self.cursor.execute("INSERT INTO " + user + "_pokemons(pokemon_name)VALUES(?)", (p1,))
        # self.db.commit()

    """Skasowanie poprzednich wpisów i zapisanie pokemonów do walki <def fight> """

    def db_add_choose_pokemon(self, p1, p2, gamestatus):
        self.cursor.execute("DELETE FROM pokemon")
        self.cursor.execute("INSERT INTO pokemon(pokemon1, pokemon2, game_status)VALUES(?,?, ?)", (p1, p2, gamestatus))
        self.db.commit()

    """CHYBA informacje o pokemonach dla battle.html"""

    def db_choose_pokemon_select(self):
        self.cursor.execute("SELECT pokemon1, pokemon2, game_status from pokemon")
        all_rows = self.cursor.fetchall()
        for row in all_rows:
            return row

    """info o zwycięstwie"""

    def db_add_fight_result(self, result, username, axp):
        self.cursor.execute("SELECT battle_won, battle_lost, xp, diamond FROM user WHERE user_name='" + username + "'")
        battle_rows = self.cursor.fetchall()
        if result == "p1":
            self.cursor.execute(
                "UPDATE user SET battle_won='" + str(int(battle_rows[0][0]) + 1) + "' WHERE user_name='" + str(
                    username) + "'")
            self.cursor.execute(
                "UPDATE user SET xp='" + str(int(battle_rows[0][2]) + axp) + "' WHERE user_name='" + str(
                    username) + "'")
            """obsługa diamentów"""
            self.cursor.execute(
                "UPDATE user SET diamond='" + str(int(battle_rows[0][2]) // 10) + "' WHERE user_name='" + str(
                    username) + "'")
            self.db.commit()
        elif result == "p2":
            self.cursor.execute(
                "UPDATE user SET battle_lost='" + str(int(battle_rows[0][1]) + 1) + "' WHERE user_name='" + str(
                    username) + "'")
            self.db.commit()
        self.cursor.execute("SELECT * from user")
        all_rows = self.cursor.fetchall()
        for row in all_rows:
            print(row)

    def draw_cards(self, stat, username):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pok_list( "
                            "pok_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "name TEXT UNIQUE,"
                            "hp INT,"
                            "attack_1 TEXT,"
                            "damage_1 INT,"
                            "attack_2 TEXT,"
                            "damage_2 INT,"
                            "ultra_beast TEXT,"
                            "stage TEXT,"
                            "img TEXT,"
                            "type TEXT)""")
        if stat == "5diam" or stat == "new_player":
            self.cursor.execute("SELECT name FROM pok_list WHERE stage='Basic'")
            all_rows = self.cursor.fetchall()
            rr = random_int(len(all_rows))
            self.cursor.execute("SELECT img FROM pok_list WHERE name='" + all_rows[rr][0] + "'")
            pok_img = self.cursor.fetchone()
            if stat == "5diam":
                self.cursor.execute("SELECT diamond FROM user WHERE user_name='" + username + "'")
                diamonds = self.cursor.fetchone()
                if diamonds[0] < 5:
                    return "not_enough_diamonds_5"
                self.cursor.execute(
                    "UPDATE user SET diamond='" + str(int(diamonds[0]) - 5) + "' WHERE user_name='" + str(
                        username) + "'")
            self.db.commit()
            PSQL().add_pokemon_for_user(username, all_rows[rr][0])
            print(rr)
            return pok_img[0]


    def db_create_pokemon_db(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pokemon( "
                            "pokemon1 TEXT,"
                            "pokemon2 TEXT,"
                            "game_status TEXT)""")


    def create_user(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS user( "
                            "user_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "user_name TEXT,"
                            "e_mail TEXT,"
                            "password TEXT,"
                            "first_time TEXT,"
                            "battle_won INT DEFAULT 0 ,"
                            "battle_lost INT DEFAULT 0,"
                            "xp INT DEFAULT 0,"
                            "coin INT DEFAULT 0,"
                            "diamond INT DEFAULT 0)""")


    def create_pok_list(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS pok_list( "
                            "pok_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                            "name TEXT UNIQUE,"
                            "hp INT,"
                            "attack_1 TEXT,"
                            "damage_1 INT,"
                            "attack_2 TEXT,"
                            "damage_2 INT,"
                            "ultra_beast TEXT,"
                            "stage TEXT,"
                            "img TEXT,"
                            "type TEXT)""")
    def add_pok(self):
        pok_dict = pokemon_xls()
        for p in pok_dict.values():
            try:
                self.cursor.execute(
                "INSERT INTO pok_list(name, hp, attack_1, damage_1, attack_2, damage_2, ultra_beast, "
                "stage, img, type "")VALUES(?,?,?,?,?,?,?,?,?,?)",
                (p["name"], p["hp"], p["attack_1"], p["damage_1"], p["attack_2"], p["damage_2"],
                    p["ultra_beast"], p["stage"], p["img"], "0"))
                self.db.commit()
            except sqlite3.IntegrityError:
                pass

