from flask import Flask, render_template, request
import sqlite3


def create_app():

    app = Flask(__name__)

    conn = sqlite3.connect('loldata.db')
    cur = conn.cursor()
    gameId_list = [] 
    for row in cur.execute("SELECT ci.Name FROM ChampID ci ORDER BY Name ASC"):
        gameId_list.append(str(row).split('\'')[1])

    conn.commit()
    cur.close
    conn.close

    @app.route('/')
    def index(champ1=None):
        name = gameId_list
        return render_template('index.html',  name = name, champ1=champ1)


    @app.route('/calculate', methods=['POST', 'GET'])
    def calculate(champ1=None):
        ## 어떤 http method를 이용해서 전달받았는지를 아는 것이 필요함
        ## 아래에서 보는 바와 같이 어떤 방식으로 넘어왔느냐에 따라서 읽어들이는 방식이 달라짐
        if request.method == 'POST':
            #temp = request.form['num']
            pass
        elif request.method == 'GET':
            sel_champ = []
            ## 넘겨받은 문자
            for i in range(1,11):
                sel_champ.append(request.args.get('champ'+f'{i}'))
            ## 넘겨받은 값을 원래 페이지로 리다이렉트
            return render_template('index.html', champ=sel_champ)


    if __name__ == '__main__':
        app.run(debug=True)

    return app