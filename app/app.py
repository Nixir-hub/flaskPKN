
from datetime import datetime, date
from flask import Flask, render_template, session, request, flash, url_for
from flask.views import View
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect


app = Flask(__name__)
app.secret_key = 'SUPER_SUPER_SECRET_KEY'
db_name = 'flask_KPN.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)


# player model
class Player(db.Model):
    name = db.Column(db.String(50))
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)

    def __init__(self, a):
        self.name = session["name"]

    def __repr__(self):
        return f'<Player {self.name!r}>'

    def new():
        #create new player
        if request.method == 'POST':
            player = Player(session["name"])
            db.session.add(player)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_game'))


#model of game
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(120))
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    player_points = db.Column(db.Integer, default=0)
    game_date = db.Column(db.Date, nullable=False, default=date.today())
    game_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def new():
        if request.method == 'POST':
            game = Game(result=kmn_fun(int(request.form.get("sign"))), player_id=Player.query.filter_by(name=session["name"])[-1].id,
                        game_date=date.today(), game_datetime=datetime.utcnow())
            db.session.add(game)
            db.session.commit()
            return redirect(url_for('show_game'))

    def __repr__(self):
        return '<Game no. %r>' % self.id



def kmn_fun(a):
    #Method for game paper, scisors, stone
    import random
    strzal = random.randint(1, 3)
    PAPIER, KAMIEN, NOZYCE = 1, 2, 3
    if strzal == a:
        return f'Remis'
    elif a == KAMIEN and strzal == PAPIER or a == PAPIER and strzal == NOZYCE:
        return f'Przegrana'
    else:
        return f"Wygrana"


@app.route('/delete_nick', methods=['GET', 'POST'])
def delete_nick():
    # Clear the nick stored in the session object
    if request.method == "GET":
        return render_template("del_form.html")
    if request.method == "POST":
        session.pop('name', default=None)
        return redirect(url_for('main_view'))


@app.route('/set_name', methods=['GET', 'POST'])
def set_name():
    # Create player modelview
    if request.method == 'POST':
        session['name'] = request.form['name']
        Player.new()
        Game(result=kmn_fun(3), player_id=Player.query.filter_by(name=session["name"])[-1].id,
             player_points=0, game_date=date.today(), game_datetime=datetime.utcnow())
        db.session.commit()
        db.create_all()
        return redirect(url_for('main_view'))
    return render_template("form.html")


class Main(View):
    # Main page view
    def dispatch_request(self):
        if request.method == "GET":
            return render_template('base.html')
        elif request.method == "POST":
            return render_template('base.html')


class ChargePoints(View):
    methods = ['GET', 'POST']

    #View to charge points
    def dispatch_request(self):
        if request.method == "GET":
            return render_template('del_form.html')
        elif request.method == "POST":
            player = Player.query.filter_by(name=session["name"])[-1]
            if player.points != 0:
                return redirect(url_for('show_game'))
            else:
                player.points += 10
                db.session.commit()
                db.create_all()
                return redirect(url_for('show_game'))


class ShowGame(View):
    methods = ['GET', 'POST']
    # game view

    def dispatch_request(self):
        if request.method == "GET":
            players = Player.query.all()
            last_p = players[len(players) - 1]
            return render_template('game.html', player=last_p)
        elif request.method == "POST":
            players = Player.query.all()
            player = players[len(players) - 1]
            if player.points >= 3:
                game = Game(result=kmn_fun(int(request.form.get("sign"))), player_id=Player.query.filter_by(name=session["name"])[-1].id,
                            player_points=player.points, game_date=date.today(), game_datetime=datetime.utcnow())
                player.points -= 3
                db.session.add(game)
                db.session.commit()
                db.create_all()
                games = Game.query.all()
                game1 = games[len(games) - 1]
                if game.result == "Wygrana":
                    player.points += 4
                    db.session.commit()
                    db.create_all()
                    return render_template("resume.html", game=game1, player=player)
                elif game.result == "Przegrana":
                    db.session.commit()
                    db.create_all()
                    return render_template("resume.html", game=game1, player=player)
                elif game.result == 'Remis':
                    return render_template("resume.html", game=game1, player=player)
            else:
                return render_template("game_over.html")


class GameHistory(View):
    methods = ['GET', 'POST']
    # list of games played today

    def dispatch_request(self):
        today = date.today()
        today_games = Game.query.filter_by(game_date=today).all()
        if today_games == None:
            return redirect("show_game")
        else:
            return render_template("game_history.html", object_list=today_games)


app.add_url_rule('/', view_func=Main.as_view('main_view'))
app.add_url_rule('/game/', view_func=ShowGame.as_view('show_game'))
app.add_url_rule('/history/', view_func=GameHistory.as_view('history_view'))
app.add_url_rule('/charge/', view_func=ChargePoints.as_view('charge_view'))

if __name__ == '__main__':
    db.create_all()
    app.run()
