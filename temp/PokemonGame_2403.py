import time

from flask import Flask, render_template, url_for, request, redirect
# from pokemons import pokemon_list
import random
from sql_support import PSQL
from support import pokemon_xls

def vs(fight_mode, pokemon_2):
    if fight_mode == "komputer":
        random_attack_damage = 0
        random_attack = random.randint(0, 1)
        if random_attack == 0:
            random_attack_damage = random.randint(3, int(pokemon_2["obrazenia1"]))
        elif random_attack == 1:
            random_attack_damage = random.randint(3, int(pokemon_2["obrazenia2"]))
        message = pokemon_2["name"] + " atakuje za " + str(random_attack_damage) + " !!!"
        PSQL().db_fight(random_attack_damage, 0)
        return message


app: Flask = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if len(request.form['fname']) > 0 and len(request.form['lname']) > 0:
            new_fname = request.form['fname']
            new_lname = request.form['lname']
            """temp"""
            if new_fname == "Toster" and new_lname == "1234":
                return url_for('index')
            else:
                message = "Nie ma takiego użytkownika " + str(new_fname)
                return render_template('login_in.html', message=message)
        # elif len(request.form['fname']) == 0:
        #     message = "Nie podałeś imienia "
        #     return render_template('sing_up.html', message=message)
        # elif len(request.form['lname']) == 0:
        #     message = "Nie podałeś hasła "
        #     return render_template('sing_up.html', message=message)
    message = "HELLLO "
    return render_template('login_in.html', message=message)


@app.route("/main", methods=['GET', 'POST'])
def index():
    message = "Wybierz pokemona do walki!"
    PSQL().db_del_choose_pokemon()
    pokemon_list = pokemon_xls()
    print(pokemon_list)
    for pokemon_keys, pokemon_values in pokemon_list.items():
        try:
            pokemon_values['img'] is not None
        except KeyError:
            pokemon_values['img'] = "Pokeball.png"
    if request.method == 'POST':
        pokemon_chose_list = request.form.getlist('chose_pokemon')
        game_mode = request.form.get('vs')
        if len(pokemon_chose_list) == 0:
            message = "Nie wybrałeś żadnego pokemona!"
            return render_template("index.html", pokemons=pokemon_list, message=message)
        elif len(pokemon_chose_list) == 1:
            if game_mode == "yes":
                message = " Wybierzcie drugiego pokemona!"
                return render_template("index.html", pokemons=pokemon_list, message=message)
            elif game_mode is None:
                random_pokemon = random.choice(list(pokemon_list.keys()))
                PSQL().db_add_choose_pokemon(pokemon_chose_list[0], random_pokemon, "komputer")
                return redirect(url_for('fight'))
        elif len(pokemon_chose_list) > 2:
            message = "Wybrałeś więcej niż 2 pokemony!"
            return render_template("index.html", pokemons=pokemon_list, message=message)
        elif len(pokemon_chose_list) == 2:
            PSQL().db_add_choose_pokemon(pokemon_chose_list[0], pokemon_chose_list[1], "gracz")
            return redirect(url_for('fight'))
    return render_template("index.html", pokemons=pokemon_list, message=message)


@app.route("/fight", methods=['GET', 'POST'])
def fight():
    pokemon_list = pokemon_xls()
    choose_pokemons = PSQL().db_choose_pokemon_select()
    pokemon_1 = pokemon_list[choose_pokemons[0]]
    pokemon_2 = pokemon_list[choose_pokemons[1]]
    fight_mode = choose_pokemons[2]
    display = "None"
    try:
        pokemon_1_img = "static/" + pokemon_1["img"]
    except KeyError:
        pokemon_1_img = "static/Pokeball.png"
    try:
        pokemon_2_img = "static/" + pokemon_2["img"]
    except KeyError:
        pokemon_2_img = "static/Pokeball.png"
    pokemon_1_hp = pokemon_1["hp"]
    pokemon_2_hp = pokemon_2["hp"]
    if request.method == 'POST':
        message = ""
        pass
        # style = ["None", "None"]
        # if "pokemon_1_atak_1" in request.form:
        #     pokemon_1_damage_1 = random.randint(3, int(pokemon_1["obrazenia1"]))
        #     message = pokemon_1["name"] + " atakuje za " + str(pokemon_1_damage_1) + "  !!!"
        #     PSQL().db_fight(0, pokemon_1_damage_1)
        #     message = vs(fight_mode, pokemon_2)
        # elif "pokemon_1_atak_2" in request.form:
        #     pokemon_1_damage_2 = random.randint(3, int(pokemon_1["obrazenia2"]))
        #     message = pokemon_1["name"] + " atakuje za " + str(pokemon_1_damage_2) + "  !!!"
        #     PSQL().db_fight(0, pokemon_1_damage_2)
        #     message = vs(fight_mode, pokemon_2)
        # elif "pokemon_2_atak_1" in request.form:
        #     pokemon_2_damage_1 = random.randint(3, int(pokemon_2["obrazenia1"]))
        #     message = pokemon_2["name"] + " atakuje za " + str(pokemon_2_damage_1) + " !!!"
        #     PSQL().db_fight(pokemon_2_damage_1, 0)
        # elif "pokemon_2_atak_2" in request.form:
        #     pokemon_2_damage_2 = random.randint(3, int(pokemon_2["obrazenia2"]))
        #     message = pokemon_2["name"] + " atakuje za " + str(pokemon_2_damage_2) + " !!!"
        #     PSQL().db_fight(pokemon_2_damage_2, 0)
        # dam = PSQL().db_data_select()
        # if dam[0] <= 0:
        #     message = "Zwyciężył " + pokemon_2["name"]
        #     style = ["filter: grayscale(100%);", "border: 5px solid red;"]
        #     dam = None
        #     display = "block"
        # elif dam[1] <= 0:
        #     message = "Zwyciężył " + pokemon_1["name"]
        #     style = ["border: 5px solid red;", "filter: grayscale(100%);"]
        #     dam = None
        #     display = "block"
        # return render_template("Official_Battle.html", pokemon_1=pokemon_1, pokemon_2=pokemon_2,
        #                        dam=dam, style=style, display=display,
        #                        pokemon_1_img=pokemon_1_img, pokemon_2_img=pokemon_2_img, message=message)
    PSQL().db_del()
    PSQL().db_add(pokemon_1_hp, pokemon_2_hp)
    dam = PSQL().db_data_select()
    style = ""
    message = "Pojedynek !"
    return render_template("battle.html", pokemon_1=pokemon_1, pokemon_2=pokemon_2,
                           dam=dam, pokemon_1_img=pokemon_1_img, pokemon_2_img=pokemon_2_img, message=message,
                           style=style, display=display, )


if __name__ == "__main__":
    app.run(debug=True)
