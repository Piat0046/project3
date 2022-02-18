from flask import Flask, render_template, request
import pickle
import psycopg2



#def create_app():

app = Flask(__name__)


@app.route('/')
def index(champ1=None):
    gameId_list = []
    name = gameId_list
    return render_template('index.html',  name = name, champ1=champ1)


@app.route('/result', methods=['POST', 'GET'])
def result(champ1=None):
    import psycopg2

    conn = psycopg2.connect(
                            host="ec2-52-86-2-228.compute-1.amazonaws.com",
                            database="dd5g8l3ltkq7fu",
                            user="rxhgazotbubwqj",
                            password="8b76cbfb2cf1c6e4591ccc8eff75d95f39e7873128b563d57666c849cbff0af7"
                            )   
    #conn = sqlite3.connect('loldata.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT('ID') from Log_data")
    count = cur.fetchone()[0]

    print(count)
    
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        sel_champ = set()
        sel_nick = set()
        ## 넘겨받은 문자
        for i in range(1,11):
            sel_champ.add(request.args.get('champ'+f'{i}'))
        for i in range(1,11):
            sel_nick.add(request.args.get('champ'+f'{i}'+'_nick'))
        ## 넘겨받은 값을 원래 페이지로 리다이렉트
        sel_champ = list(sel_champ)
        sel_nick = list(sel_nick)
        num = len(sel_champ)    
        nick = request.args.get('username')
        
    
        import requests
        import json
        import time
        import pprint
        import pandas as pd
        from urllib import parse
        pp = pprint.PrettyPrinter(indent=4)
        request_header = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
                            "Accept-Language": "ko,en-US;q=0.9,en;q=0.8,es;q=0.7",
                            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                            "Origin": "https://developer.riotgames.com",
                            "X-Riot-Token": 'RGAPI-51930c7c-d051-44a4-93e8-fcbb592beb5f'
                        }

        # for문 진행률 확인 라이브러리
        from tqdm import tqdm

        def check2(url):
            r = requests.get(url, headers=request_header)
            if r.status_code == 200: # response가 정상이면 바로 맨 밑으로 이동하여 정상적으로 코드 실행
                m = 'pass'
                pass
            elif r.status_code == 403:
                m = 'pass'
            elif r.status_code == 429:
                print('api cost full : infinite loop start')
                start_time = time.time()
                
                while True: # 429error가 끝날 때까지 무한 루프
                    if r.status_code == 429:

                        print('try 10 second wait time')
                        time.sleep(10)

                        r = requests.get(url, headers=request_header)
                        print(r.status_code)

                    elif r.status_code == 200: #다시 response 200이면 loop escape
                        print('total wait time : ', time.time() - start_time)
                        print('recovery api cost')
                        m = 'pass'
                        break

                    else:
                        m = 'fail'
                        break
            
            else:
                m = 'fail'
            return m

        nick = nick.replace(" ", "")
        
        url_nick = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{parse.quote_plus(nick)}'

        m = check2(url_nick)
        if nick == "":
            m = '닉네임을 입력하세요'
            val = [count+1, nick]
            print(count, type(count))
            print(nick, type(nick))
            cur.execute(f"""INSERT INTO log_data("ID", "Input_name")
            VALUES (%s,%s);""", val)
            conn.commit()
        else:
            if m == 'fail':
                m = '소환사를 찾을 수 없습니다.'
                cur.execute(f"""INSERT INTO log_data("ID", "Input_name")
                VALUES ({count+1},'{nick}');""")
                conn.commit()
                print('소환사를 찾을 수 없습니다.')

            elif m == 'pass':
                nick_to_id = requests.get(url_nick, headers=request_header).json()
                input_id = nick_to_id['id']

                url_game = f'https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{input_id}'
                m = check2(url_game)
                
                if m == 'fail':
                    m = '소환사가 게임중이 아닙니다'
                    game = False
                    cur.execute(f"""INSERT INTO log_data("ID", "Input_name", "Ingame")
                    VALUES ({count+1},'{nick}',{game});""")
                    conn.commit()
                    print('소환사가 게임중이 아닙니다')

                elif m == 'pass':
                    #try:
                    data = requests.get(url_game, headers=request_header).json()
                    game = True
                    dic = []
                    log_data = [count+1, nick, game]

                    for i in range(0,10):
                        
                        summoner_Id = data['participants'][i]['summonerId']
                        log_data.append(summoner_Id)
                        champ_id = data['participants'][i]['championId']
                        log_data.append(champ_id)
                        champ_status_url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_Id}/by-champion/{champ_id}"
                        m = check2(champ_status_url)
                        print(m)
                        champ_status = requests.get(champ_status_url, headers=request_header).json()
                        champ_point = champ_status['championPoints']
                        dic.append(champ_id)
                        dic.append(champ_point)
                        log_data.append(champ_point)
                    print(log_data)
                    cur.execute(f"""INSERT INTO log_data("ID", "Input_name","Ingame","1pick_id","1pick","1score","2pick_id","2pick","2score",
                                                            "3pick_id","3pick","3score","4pick_id","4pick","4score","5pick_id","5pick","5score",
                                                            "6pick_id","6pick","6score","7pick_id","7pick","7score","8pick_id","8pick","8score",
                                                            "9pick_id","9pick","9score","10pick_id","10pick","10score")
                                                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", log_data)
                    conn.commit()

                    import pickle
                    import pandas as pd
                    from lightgbm import LGBMClassifier, plot_importance
                    from xgboost import XGBClassifier

                    #def create_app():

                    app = Flask(__name__)

                    model = None

                    with open('model4.pkl', 'rb') as file:
                        model = pickle.load(file)

                    columns = ['1', '1score', '2', '2score', '3', '3score', '4', '4score', '5', '5score', '6', '6score', '7', '7score', '8', '8score', '9', '9score', '10', '10score']
                    df = pd.DataFrame(columns = columns)
                    input_data = {
                                '1' : dic[0],
                                '1score' : dic[1],
                                '2' : dic[2],
                                '2score' :dic[3],
                                '3' : dic[4],
                                '3score' : dic[5],
                                '4' : dic[6],
                                '4score' : dic[7],
                                '5' : dic[8],
                                '5score' : dic[9],
                                '6' : dic[10],
                                '6score' : dic[11],
                                '7' : dic[12],
                                '7score' : dic[13],
                                '8' : dic[14],
                                '8score' : dic[15],
                                '9' : dic[16],
                                '9score' : dic[17],
                                '10' : dic[18],
                                '10score' : dic[19],
                                }
                    X_test = df.append(input_data, ignore_index=True)
                    X_test = X_test.astype(int)
                    y_pred = list(model.predict(X_test))[0]
                    c=model.predict_proba(X_test).reshape(-1,1)
                    
                    blue_team = int(list(c[0])[0]*100)
                    red_team = int(list(c[1])[0]*100)
                    
                    if y_pred == 200:
                        y_pred = '레드팀'
                    else:
                        y_pred = '블루팀'

                    m = f'예상승리팀 : {y_pred},{"     "}블루팀={int(list(c[0])[0]*100)}%, 레드팀{int(list(c[1])[0]*100)}%'
                    #except:
                        #m = '알수없는 오류입니다'
        

    cur.close
    conn.close

    return render_template('result.html', nick = sel_nick, champ=sel_champ, num = num, username = nick, m = m)


if __name__ == '__main__':
    app.run(debug=True)

#    return app