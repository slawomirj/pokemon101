import sqlite3
import time

from flask import Flask, render_template, url_for, request, redirect
import random
from sql_support import PSQL, pokemon_xls


app: Flask = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if len(request.form['username']) > 0 and len(request.form['pswd']) > 0:
            username = request.form['username']
            password = request.form['pswd']
            try:
                log_status = PSQL().check_user_pswd(username, password)
                if log_status == "ok":
                    check_is_new = PSQL().show_user(username)
                    if check_is_new[0][4] == "yes":
                        return redirect(url_for('draw', username=username, status="new_player"))
                    return redirect(url_for('index', username=username))
                else:
                    message = log_status
                    return render_template('login_in.html', message=message)
            except sqlite3.OperationalError:  # brak tablicy user
                pass
    message = "Wypełnij dwa pola by się zalogować:"
    return render_template('login_in.html', message=message)


@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    message = "Pola z gwiazdkami są wymagane"
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        if password == repeat_password:
            new_user_status = PSQL().check_user(username, email, password)
            if new_user_status == 0:
                message = "Taki użytkownik już istnieje"
            elif new_user_status == 1:
                return render_template('login_in.html')
        else:
            message = "Hasła nie są identyczne"
        # TODO: powrót do strony logowania
    return render_template("sign_up.html", message=message)


@app.route("/<username>", methods=['GET', 'POST'])
def index(username):
    # todo: przeniesienie pokemonów z sql
    pokemon_list = pokemon_xls()
    user_pokemons_temp = dict()
    user_data = PSQL().show_user(username)
    message = "Witaj " + str(user_data[0][1])
    if request.method == 'POST':
        pokemon_chose_list = request.form.getlist('chose_pokemon')
        pokemon_chose_my_list = request.form.getlist('chose_my_pokemon')
        if len(pokemon_chose_my_list) == 0:
            message = "Wybierz swojego pokemona"
        elif len(pokemon_chose_my_list) > 1:
            message = "Wybrałeś za dużo swoich pokemonów do walki"
        elif len(pokemon_chose_list) == 0:
            message = "Wybierz przeciwnika"
        elif len(pokemon_chose_list) > 1:
            message = "Wybrałeś za dużo przeciwników"
        elif len(pokemon_chose_my_list) == 1 and len(pokemon_chose_list) == 1:
            PSQL().db_add_choose_pokemon(pokemon_chose_my_list[0], pokemon_chose_list[0], "comp")
            # return redirect(url_for('fight'))
            return redirect(url_for('fight', username=username))
    # TODO: TUTAJ JEST BLAD
    user_pokemons = PSQL().show_pokemons(username)
    for my_pokemons in user_pokemons:
        user_pokemons_temp[my_pokemons[1]] = pokemon_list[my_pokemons[1]]
    return render_template("index.html", username=username, user_data=user_data, message=message,
                           user_pokemons_temp=user_pokemons_temp,
                           pokemon_list=pokemon_list)


@app.route("/<username>/fight", methods=['GET', 'POST'])
def fight(username):
    xp = dict(Basic=10, Stage0=20, Stage1=50, Stage2=75, VMAX=100, VSTAR=125)

    pokemon_list = pokemon_xls()
    choose_pokemons = PSQL().db_choose_pokemon_select()
    pokemon_1 = pokemon_list[choose_pokemons[0]]
    pokemon_2 = pokemon_list[choose_pokemons[1]]
    fight_mode = choose_pokemons[2]
    """-------------"""
    # print(type(pokemon_1['img']))
    # todo: brak zdjęcia pokemona
    """zwraca 2 wartości win_pokemon = p1/p2 oraz win_side ="win"/"lose"""
    if request.method == 'POST':
        xp_pokemon_stage = pokemon_1["stage"]
        add_xp = xp[xp_pokemon_stage]
        PSQL().db_add_fight_result(request.form['win_pokemon'], username, add_xp)
        return redirect(url_for('index', username=username))
    message = "Pojedynek !"
    return render_template("battle.html", pokemon_1=pokemon_1, pokemon_2=pokemon_2, message=message,
                           fight_mode=fight_mode, username=username)


@app.route("/<username>/marketplace", methods=['GET', 'POST'])
def marketplace(username):
    user_data = PSQL().show_user(username)
    message = "Diamenty: " + str(user_data[0][9]) + ", Monety: " + str(user_data[0][8])
    status1 = "5diam"
    status2 = "50diam"
    status3 = "700xp"
    return render_template("marketplace.html", user_data=user_data, username=username, status1=status1, status2=status2,
                           status3=status3, message=message)


@app.route("/<username>/draw/<status>", methods=['GET', 'POST'])
def draw(username, status):
    message = "Wylosuj kartę"
    user_data = PSQL().show_user(username)
    src = "/assets/pokquestion.jpg"
    display_back_button = "none"
    draw_button = "block"
    draw = ""
    # todo: odejmowanie diamentów, przycisk po wylosowaniu, ponowne losowanie jak jest już pokemon na twoim koncie
    if request.method == 'POST':
        if status == "new_player":
            draw = PSQL().draw_cards("new_player", username)
            message = "Twój nowy Pokemon"
        elif status == "5diam":
            draw = PSQL().draw_cards("5diam", username)
        if draw == "not_enough_diamonds_5":
            message= "Masz za mało diamentów"
        else:
            src = "/"+draw
        draw_button = "none"
        display_back_button = "block"
    return render_template("draw.html", username=username, status=status, src=src, user_data=user_data,
                           draw_button=draw_button, display_back_button=display_back_button, message=message)


@app.route("/add_pokemon/", methods=['GET', 'POST'])
def add_pokemon():
    if request.method == 'POST':
        aa = request.form.to_dict()
        return render_template("add_pokemon.html")
    return render_template("add_pokemon.html")


if __name__ == "__main__":
    app.run(debug=True)
