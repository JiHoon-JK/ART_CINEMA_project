from flask import Flask, render_template, jsonify, request, session, escape, url_for, redirect
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)

import random
import jwt, datetime, hashlib

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.ART_Movie_Platform  # 'dbsparta'라는 이름의 db를 만듭니다.

app = Flask(__name__)

SECRET_KEY = 'apple'

# global email
global pw_hash
global pwd
global email1
global session



def genre_cnt():
    all_selected_movie = list(db.select_movie.find({}))
    print(all_selected_movie)
    all_long_movie = list(db.Long_movie_list.find({}))




    # global genre_score

    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')
        nickname = a[0].get('nickname')

    user_data = list(db.userdb.find({'nickname':nickname},{'_id':0}))
    print('장르 들어갔는지 확인')
    print(user_data)
    user_genre_score = user_data[0]['genre_score']
    print(user_genre_score)
    user_genre_score_val = list(user_genre_score.values())
    user_genre_score_vals = 0
    for i in range(len(user_genre_score_val)):
        user_genre_score_vals += user_genre_score_val[i]
        # 처음 로그인해서 진행했다면, 새로운 genre_score 셋을 줘야한다.
        if(user_genre_score_vals == 0):
            # 장르마다 점수 값 배정
            genre_score = {
                '드라마': 0,
                '판타지': 0,
                '공포': 0,
                '멜로/로맨스': 0,
                '모험': 0,
                '스릴러': 0,
                '느와르': 0,
                '다큐멘터리': 0,
                '코미디': 0,
                '가족': 0,
                '미스터리': 0,
                '전쟁': 0,
                '애니메이션': 0,
                '범죄/느와르': 0,
                '뮤지컬': 0,
                'SF': 0,
                '액션': 0
            }
            print('genre_score 셋을 생성했습니다.')
        else:
            genre_score = user_genre_score


    for i in range(len(all_selected_movie)):
        for j in range(len(all_long_movie)):
            if all_selected_movie[i].get('selected_movie') == all_long_movie[j].get('title'):
                selected_main_genre = all_long_movie[j].get('genre_1')
                selected_second_genre = all_long_movie[j].get('genre_2')
                for key in genre_score:
                    if selected_main_genre == key:
                        genre_score[key] = genre_score[key] + 5

                    if selected_second_genre == key:
                        genre_score[key] = genre_score[key] + 3

    print(genre_score)
    score_result = sorted(genre_score.items(), key=lambda x: x[1], reverse=True)
    print(score_result)
    print('선호장르 점수 결과!')
    global customer_main_genre
    global customer_second_genre
    customer_main_genre = score_result[0][0]
    customer_second_genre = score_result[1][0]

    db.userdb.update_one({'email': b}, {'$set': {'genre_score' : genre_score}})
    db.userdb.update_one({'email': b}, {'$set': {'genre_1': customer_main_genre}})
    db.userdb.update_one({'email': b}, {'$set': {'genre_2': customer_second_genre}})

    return jsonify({'result': 'success'})


  



# 영화 추천 함수
def recommend_movie_db():
    db.genre1_art_movie.drop()
    db.genre2_art_movie.drop()

    all_short_movie = list(db.ART_movie_list.find({}))

    customer_genre1 = customer_main_genre
    customer_genre2 = customer_second_genre

    temp_main_genre_movie = []
    temp_second_genre_movie = []

    for k in range(len(all_short_movie)):
        # 단편영화 장르 값 입시로 저장해두기
        temp_genre1 = all_short_movie[k].get('genre_1')
        temp_genre2 = all_short_movie[k].get('genre_2')

        # 만약에 고객 메인 장르와 단편영화의 임시장르가 같으면,
        if customer_genre1 == temp_genre1 or customer_genre1 == temp_genre2:
            # 그 영화들을 하나의 리스트로 모아둔다.
            temp_main_genre_movie.append(all_short_movie[k])
        # 만약에 고객 서브 장르와 단편영화의 임시장르가 같으면,
        if customer_genre2 == temp_genre1 or customer_genre2 == temp_genre2:
            temp_second_genre_movie.append(all_short_movie[k])
        else:
            continue

    customer_genre1_movie = random.sample(temp_main_genre_movie, 3)
    customer_genre2_movie = random.sample(temp_second_genre_movie, 3)

    print("첫번째 선호하는 장르영화는", customer_genre1)
    for i in range(len(customer_genre1_movie)):
        movie_title = customer_genre1_movie[i].get('title')
        movie_poster = customer_genre1_movie[i].get('poster')
        movie_director = customer_genre1_movie[i].get('director')
        movie_summary = customer_genre1_movie[i].get('summary')
        print(movie_title, movie_poster, movie_director, movie_summary)

        # 영화 데이터
        genre1_movie = {
            'title': movie_title,
            'poster': movie_poster,
            'director': movie_director,
            'summary': movie_summary,
        }
        # 영화정보저장
        db.genre1_art_movie.insert_one(genre1_movie)

    print("두번째 선호하는 장르영화는", customer_genre2)
    for i in range(len(customer_genre2_movie)):
        movie_title = customer_genre2_movie[i].get('title')
        movie_poster = customer_genre2_movie[i].get('poster')
        movie_director = customer_genre2_movie[i].get('director')
        movie_summary = customer_genre2_movie[i].get('summary')
        print(movie_title, movie_poster, movie_director, movie_summary)

        # 영화 데이터
        genre2_movie = {
            'title': movie_title,
            'poster': movie_poster,
            'director': movie_director,
            'summary': movie_summary,
        }
        # 영화정보저장
        db.genre2_art_movie.insert_one(genre2_movie)


# HTML을 주는 부분
@app.route('/')
def home():
    if 'email' in session:
        email1 = session['email']
        print('Logged in as ' + email1)
        print(session)
        return render_template('main.html', sessionemail=email1)

    else:
        return render_template('main.html')


@app.route('/your_favorite_genre')
def page2():
    db.select_movie.drop()
    if 'email' in session:
        email1 = session['email']
        print('1Logged in as ' + email1)
        print(session)
        return render_template('page2.html', sessionemail=email1)

    else:
        return render_template('page2.html')


@app.route('/main')
@app.route('/main/rank')
def temp():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        print(a[0].get('nickname'))
        return render_template('temp.html', sessionemail2=a[0].get('nickname'))
    else:
        return render_template('temp.html')


@app.route('/recommend_movie')
def page3():
    genre_cnt()
    recommend_movie_db()
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        print('Logged in as ' + email1)
        print(session)
        return render_template('page3.html', sessionemail2=a[0].get('nickname'))

    else:
        return render_template('page3.html')


@app.route('/search_movie')
def search_page():
    para = request.args.get("search_data")
    print(para)
    print('제발....')
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        print('tempLogged in as ' + email1)
        print(session)
        return render_template('search.html', sessionemail2=a[0].get('nickname'), para_data=para)
    else:
        return render_template('search.html')


@app.route('/info_movie')
def page5():
    para = request.args.get("search_data")
    print(para)
    print('제발....')
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        print('tempLogged in as ' + email1)
        print(session)
        return render_template('page5.html', sessionemail2=a[0].get('nickname'), para_data=para)
    else:
        return render_template('page5.html')


@app.route('/mypage')
def mypage():
    if 'email' in session:
        para = request.args.get("user")
        print('zzzzzzzz')
        print(para)
        email1 = session['email']
        a = list(db.userdb.find({'nickname': para}, {'_id': 0}))
        b = list(db.userdb.find({'email': email1}, {'_id': 0}))
        print('Logged in as ' + email1)
        print(session)
        print(a)
        print(b)
        return render_template('my_page.html',sessionemail2=b[0].get('nickname'),para_data=para,para_data_2=a[0].get('genre_1'),para_data_3=a[0].get('genre_2'),user_introduce=a[0].get('introduce'))

    else:
        return render_template('my_page.html')

@app.route('/info_popup')
def info_popup():
    return render_template('info_popup.html')

# @app.route('/mypage/more_Info')
# def more_Info():
#     if 'email' in session:
#         email1 = session['email']
#         a = list(db.userdb.find({'email': email1}, {'_id': 0}))
#         print('Logged in as ' + email1)
#         print(session)
#         return render_template('(MP)more_Info.html', sessionemail2=a[0].get('nickname'))

#     else:
#         return render_template('(MP)more_Info.html')

@app.route('/user', methods=['GET'])
def listing():
    result = list(db.Long_movie_list.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'Long_movie_list': result})


@app.route('/listing2', methods=['GET'])
def listing2():
    result = list(db.ART_movie_list.find({'$where':"(this.title.length<30)"}, {'_id': 0}))
    return jsonify({'result': 'success', 'ART_movie_list': result})


# 로그인
@app.route('/test', methods=['POST'])
def login():
    email = request.form['email']
    pwd = request.form['pwd']
    pw_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()

    session['email'] = email
    session.permanent = True

    a = list(db.userdb.find({}))
    for i in range(len(a)):
        if a[i].get('email') == email:
            if a[i].get('pwd') == pw_hash:
                user_nickname = a[i].get('nickname')
                print(user_nickname)
                first_login_check = a[i].get('genre_1')
                print(first_login_check)
                return jsonify({'result': 'success', 'userdb': user_nickname, 'login_check':first_login_check})
            else:
                return jsonify({'result': 'fail', 'userdb': 'failed'})
    else:
        return jsonify({'result': 'fail', 'userdb': 'failed'})


# 로그아웃
@app.route('/customer_logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return jsonify({'result': 'success'})


# 회원가입
@app.route('/customer', methods=['POST'])
def register():
    email = request.form['email']
    pwd = request.form['pwd']
    nickname = request.form['nickname']
    introduce = request.form['introduce']

    genre_score_set = {
                '드라마': 0,
                '판타지': 0,
                '공포': 0,
                '멜로/로맨스': 0,
                '모험': 0,
                '스릴러': 0,
                '느와르': 0,
                '다큐멘터리': 0,
                '코미디': 0,
                '가족': 0,
                '미스터리': 0,
                '전쟁': 0,
                '애니메이션': 0,
                '범죄/느와르': 0,
                '뮤지컬': 0,
                'SF': 0,
                '액션': 0
            }

    pw_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()

    a = list(db.userdb.find({}))

    if len(a) == 0:
        db.userdb.insert_one({'email': email, 'pwd': pw_hash, 'nickname': nickname, 'genre_1': "", 'genre_2': "", 'profile_photo':"", "introduce":introduce, "genre_score":genre_score_set})
        return jsonify({'result': 'success'})

    else:
        for i in range(len(a)):
            if a[i].get('email') == email:
                return jsonify({'result': 'fail1'})
            elif a[i].get('nickname') == nickname:
                return jsonify({'result': 'fail2'})

        db.userdb.insert_one({'email': email, 'pwd': pw_hash, 'nickname': nickname ,'genre_1': "", 'genre_2': "", 'profile_photo':"", "introduce":introduce, "genre_score":genre_score_set})
        return jsonify({'result': 'success', 'userdb': email})



# mypage연결 api
@app.route('/info_my_like_movie', methods=['GET'])
def show_like_movie():
    nickname=request.args.get("nickname")
    print(nickname)
    print('뭐냐이거는?')
    my_like_movie = list(db.LDDB.find({'nickname':nickname, 'like':True},{'_id':0}))
    print(my_like_movie)
    print(len(my_like_movie))
    return jsonify({'result': 'success', 'my_like_movie': my_like_movie})


@app.route('/info_my_dislike_movie', methods=['GET'])
def show_dislike_movie():
    # DB_collection중 LDDB에서 정보 빼오기
    nickname=request.args.get("nickname")
    print(nickname)
    status_like = False
    my_dislike_movie = list(db.LDDB.find({'nickname':nickname,'like' : status_like}, {'_id': 0}))
    print(my_dislike_movie)
    return jsonify({'result': 'success', 'my_dislike_movie': my_dislike_movie})


@app.route('/info_my_comment_movie', methods=['GET'])
def show_comment_movie():
    # DB_collection중 serverside_usercomment 정보 빼오기
    nickname=request.args.get("nickname")
    print(nickname)
    my_comment_movie = list(db.serverside_usercomment.find({'user_nickname':nickname}, {'_id': 0}))
    print(my_comment_movie)
    return jsonify({'result': 'success', 'my_comment_movie': my_comment_movie})

@app.route('/info_my_diswatch_movie', methods=['GET'])
def show_diswatch_movie():
    for repeat in range(1):
        # 서버 내부에서 수행 할 기능 / DB에 저장돼있는 모든 정보 중 'genre1':'드라마' 가져오
        my_diswatch_movie = list(db.ART_movie_list.find({}, {'_id': 0}))
        return jsonify({'result': 'success', 'my_diswatch_movie': my_diswatch_movie})


@app.route('/dislike_movie', methods=['POST'])
def dislike_button():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')

    dislike_movie = {
        'email': b,
        'nickname': request.form['nickname'],
        'title': request.form['title'],
        'poster': request.form['poster'],
        'director' : request.form['director'],
        'like': False,
        'dislike': True
    }

    a = list(db.LDDB.find({'email': dislike_movie['email'], 'title': dislike_movie['title']}))
    # 두개 겹치는게 아얘없을때, 좋아요도 없고 실어요도 안눌린상태임
    if len(a) == 0:
        print("성공")
        print(a)
        db.LDDB.insert_one(dislike_movie)
        counting_liked_minus(dislike_movie['title'])
        all_user_disliked_movie(dislike_movie['title'], b)

        return jsonify({'result': 'success'})
    else:

        if a[0].get('dislike') == True:
            print("이미 안좋아하는 영화")
            print(a)
            return jsonify({'result': 'fail1'})

        elif a[0].get('like') == True:
            print("이미 좋아요를 누른 영화")
            print(a)
            return jsonify({'result': 'fail2'})


@app.route('/like_movie', methods=['POST'])
def like_button():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')

    like_movie = {
        'email': b,
        'nickname':request.form['nickname'],
        'title': request.form['title'],
        'poster': request.form['poster'],
        'director': request.form['director'],
        'like': True,
        'dislike': False
    }

    a = list(db.LDDB.find({'email': like_movie['email'], 'title': like_movie['title']}))
    if len(a) == 0:
        print("성공")
        print(a)
        db.LDDB.insert_one(like_movie)
        counting_liked_plus(like_movie['title'])
        all_user_liked_movie(like_movie['title'], b)


        return jsonify({'result': 'success'})
    else:
        if a[0].get('dislike') == True:
            print("이미 안좋아하는 영화")
            print(a)
            return jsonify({'result': 'fail1'})

        elif a[0].get('like') == True:
            print("이미 좋아요를 누른 영화")
            print(a)
            return jsonify({'result': 'fail2'})


@app.route('/DLupdate_movie', methods=['POST'])
def DLupdate_button():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')

    title = request.form['title']

    db.LDDB.update_one({'email': b, 'title': title}, {'$set': {'like': True, 'dislike': False}})
    counting_liked_plus(title)
    db.serverside_dislikeDB.delete_one
    ({'email': b, 'title': title})
    all_user_liked_movie(title, b)
    return jsonify({'result': 'success'})


@app.route('/LDupdate_movie', methods=['POST'])
def LDupdate_button():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')

    title = request.form['title']

    db.LDDB.update_one({'email': b, 'title': title}, {'$set': {'like': False, 'dislike': True}})
    counting_liked_minus(title)
    db.serverside_likeDB.delete_one({'email': b, 'title': title})
    all_user_disliked_movie(title, b)
    return jsonify({'result': 'success'})

@app.route('/check_LDDB' ,methods=['POST'])
def LDDB_check():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')

    director = request.form['director']
    print(director)

    test = director.strip()
    print(test)

    like_movie = {
        'email': b,
        'title': request.form['title'],
        'poster': request.form['poster'],
        'director' : request.form['director'],
        'like': True,
        'dislike': False
    }
    print(like_movie)
    a = list(db.LDDB.find({'email': like_movie['email'], 'title': like_movie['title'], 'like':True}))
    print('----test----')
    print(len(a))
    if len(a) == 0:
        print('좋아요를 누르지 않았던 영화')
        return jsonify({'result':'like_fail'})
    else:
        print('좋아요를 누른 영화')
        return jsonify({'result':'like_success'})


@app.route('/sort/comment',methods=['POST'])
def sort_comment():
    find_db = list(db.ART_movie_list.find({},{'_id':0}))
    sort_db = sorted(find_db,key=(lambda x: x['commented_cnt']),reverse=True)
    return jsonify({'result':'success', 'sort_comment':sort_db})

@app.route('/sort/like', methods=['POST'])
def sort_like():
    find_db = list(db.ART_movie_list.find({},{'_id':0}))
    sort_db = sorted(find_db,key=(lambda x: x['liked_cnt']),reverse=True)
    return jsonify({'result':'success', 'sort_like':sort_db})


@app.route('/sort/search', methods=['POST'])
def sort_search():
    find_db = list(db.ART_movie_list.find({},{'_id':0}))
    sort_db = sorted(find_db,key=(lambda x: x['searched_cnt']),reverse=True)
    return jsonify({'result':'success', 'sort_search':sort_db})

@app.route('/selected_movie', methods=['POST'])
def select_movie():
    selected_movie = request.form['m_title_give']
    data = {
        'selected_movie': selected_movie
    }
    db.select_movie.insert_one(data)
    return jsonify({'result': 'success'})


@app.route('/comment_save', methods=['POST'])
def saved_comment():
    print('들어갔냐 하...')
    user_nickname = request.form['nickname']
    print(user_nickname)
    user_comment_movie_title = request.form['user_comment_movie_title']
    user_comment_movie_poster = request.form['user_comment_movie_poster']
    user_comment_movie_director = request.form['user_comment_movie_director']
    user_comment_movie = request.form['user_comment_give']
    print(user_comment_movie)
    print(user_comment_movie_title)
    find_db = list(
        db.serverside_usercomment.find({'user_nickname': user_nickname, 'user_comment_movie_title': user_comment_movie_title},
                                       {'_id': 0}))
    print(find_db)
    find_db_len = len(find_db)
    print(find_db_len)
    if (find_db_len > 0):
        edit_check_db = find_db[0]['edit']
        print(edit_check_db)
        if (edit_check_db == False):
            print('이미 코멘트를 작성한 영화입니다.')
            comment = find_db[0]['user_comment']
            print(comment)
            return jsonify({'result': 'fail', 'comment': comment})
        if (edit_check_db == True):
            print('코멘트를 수정했습니다.')
            comment = find_db[0]['user_comment']
            print(comment)
            edit_check = find_db[0]['edit']
            print(edit_check)
            return jsonify({'result': 'success', 'comment': comment, 'edit': edit_check})
    else:
        data = {
            'user_nickname': user_nickname,
            'user_comment_movie_title': user_comment_movie_title,
            'user_comment_movie_poster': user_comment_movie_poster,
            'user_comment_movie_director' : user_comment_movie_director,
            'user_comment': user_comment_movie,
            'edit': False,
            'gonggam_cnt': 0,
            'gongmag_people': []
        }
        print(data)
        print('코멘트를 작성했습니다.')
        counting_commented_plus(user_comment_movie_title)
        db.serverside_usercomment.insert_one(data)
        return jsonify({'result': 'success'})


@app.route('/comment_edit', methods=['POST'])
def edited_comment():
    # before_edit_comment = request.form['before_edit_comment']
    # print(before_edit_comment+'1')
    nickname = request.form['nickname']
    edit_movie_title = request.form['edit_movie']
    edit_comment = request.form['edit_comment']
    print('////' + edit_comment)
    update_comment_db = list(
        db.serverside_usercomment.update({'user_nickname': nickname, 'user_comment_movie_title': edit_movie_title},
                                         {'$set': {'user_comment': edit_comment, 'edit': True}}))
    print(update_comment_db)
    return jsonify({'result': 'success'})


@app.route('/comment_remove', methods=['POST'])
def removed_comment():
    user_comment_remove = request.form['user_comment']
    print(user_comment_remove)
    find_comment_db = list(db.serverside_usercomment.find({'user_comment': user_comment_remove}, {'_id': 0}))
    print(find_comment_db)
    print('???')
    if (user_comment_remove == find_comment_db[0]['user_comment']):
        counting_commented_minus(find_comment_db[0]['user_comment_movie_title'])
        db.serverside_usercomment.remove({'user_comment': user_comment_remove})
        print('코멘트가 삭제되었습니다.')
        return jsonify({'result': 'success'})
    else:
        print('해당 코멘트가 없습니다. !오류발생!')
        return jsonify({'result': 'fail'})


@app.route('/genre1_movie', methods=['GET'])
def recommend():
    nickname_receive = request.args.get("nickname")
    print(nickname_receive)
    user_info = list(db.userdb.find({'nickname':nickname_receive}, {'_id': 0}))
    print(user_info)
    user_genre_1 = user_info[0]['genre_1']
    result = list(db.genre1_art_movie.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'movies': result, 'user_genre_1': user_genre_1})


@app.route('/genre2_movie', methods=['GET'])
def recommend2():
    nickname_receive = request.args.get("nickname")
    print(nickname_receive)
    user_info = list(db.userdb.find({'nickname':nickname_receive}, {'_id': 0}))
    print(user_info)
    user_genre_2 = user_info[0]['genre_2']
    result = list(db.genre2_art_movie.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'movies': result, 'user_genre_2': user_genre_2})


@app.route('/search_movie', methods=['POST'])
def search_movie():
    search_movie = request.form['search_title_give']
    nickname = request.form['nickname']
    data = {
        'nickname' : nickname,
        'search_movie': search_movie
    }
    print('-----------xxxx----------')
    print(data)
    db.search_movie.insert(data)
    counting_searched(search_movie)
    return jsonify({'result': 'success'})

@app.route('/lastest_searching_listing', methods=['GET'])
def lastest_searching_listing():
    nickname = request.args.get("nickname")
    print(nickname)
    # 닉네임이 존재한 경우
    if(len(nickname)!=0):
        search_db = list(db.search_movie.find({'nickname':nickname},{'_id':0}))
        print('최근 검색어 리스팅이 되었습니다.')
        return jsonify({'result':'success','list':search_db})
    #닉네임이 존재하지 않은 경우 (로그인을 하지 않고 검색한 경우)
    else:
        print('유저가 없습니다.')
        return jsonify({'result':'fail'})
    
# 페이지 5 내에서 검색했을 때
@app.route('/search_DB', methods=['GET'])
def search_DB():
    # search_movie = list(db.search_movie.find({}, {'_id': 0}))
    # search_title_give = search_movie[-1]['search_movie']
    # print(search_title_give)
    movie_input=request.args.get("movie_input")
    print(movie_input)
    
    counting_searched(movie_input)
    
    # 영화에 대한 코멘트가 많은데, 해당 유저의 커멘트를 찾기위해서 작성
    print(session)
    if 'email' in session:
        email1 = session['email']
        nickname = request.args.get("nickname")
        comment_db = list(db.serverside_usercomment.find(
            {'user_comment_movie_title': {'$regex': movie_input}, 'user_nickname': nickname}, {'_id': 0}))
        print(comment_db)

    print('------------------')
    print(comment_db)
    print(movie_input)
    movie_info_ART = list(db.ART_movie_list.find({'title': {'$regex': movie_input}}, {'_id': 0}))
    # movie_info_Long = list(db.Long_movie_list.find({'title':{'$regex':search_title_give}}, {'_id': 0}))
    print(movie_info_ART)
    # print(movie_info_Long)
    movie_info = movie_info_ART
    print(movie_info)
    if (movie_info == []):
        print('영화가 없을 때!!!')
        return jsonify({'result': 'fail'})
    else:
        # 코멘트가 있다면, 코멘트 작성 박스말고, 작성한 코멘트가 보이도록.
        if (comment_db != []):
            comment = comment_db[0]['user_comment']
            print('코멘트가 존재합니다.')
            print(comment)
            return jsonify(
                {'result': 'success', 'check_comment': 'success', 'Movie_info': movie_info, 'Movie_comment': comment})
        else:
            print('코멘트가 없습니다.')
            return jsonify({'result': 'success', 'check_comment': 'fail', 'Movie_info': movie_info})

@app.route('/search_title', methods=['GET'])
def search_title():
    search_data = request.args.get("search_data")
    print(search_data)
    search_title_info = list(db.ART_movie_list.find({'title':{'$regex':search_data}},{'_id':0}))
    print(search_title_info)
    if(search_title_info == []):
        print('해당 영화제목은 없습니다.')
        return jsonify({'result':'fail'})
    else:
        print('해당 영화제목은 존재합니다.')
        return jsonify({'result':'success','title_info':search_title_info})

@app.route('/search_director', methods=['GET'])
def search_director():
    search_data = request.args.get("search_data")
    print(search_data)
    search_director_info = list(db.ART_movie_list.find({'director':{'$regex':search_data}},{'_id':0}))
    print(search_director_info)
    if(search_director_info == []):
        print('해당 감독은 없습니다.')
        return jsonify({'result':'fail'})
    else:
        print('해당 감독은 존재합니다.')
        return jsonify({'result':'success','director_info':search_director_info})


@app.route('/search_user', methods=['GET'])
def search_user():
    search_data = request.args.get("search_data")
    print(search_data)
    search_user_info = list(db.userdb.find({'nickname':{'$regex':search_data}},{'_id':0}))
    print(search_user_info)
    user_comment = list(db.serverside_usercomment.find({'user_nickname':{'$regex':search_data}},{'_id':0}))
    print(user_comment)
    user_comment_count = len(user_comment)
    print(user_comment_count)
    if(search_user_info == []):
        print('해당 유저는 없습니다.')
        return jsonify({'result':'fail'})
    else:
        print('해당 유저는 존재합니다.')
        return jsonify({'result':'success','user_info':search_user_info,'user_comment_count':user_comment_count})

    
def counting_liked_plus(title):
    db.ART_movie_list.update_one({'title': title}, {'$inc': {'liked_cnt': 1}})


def counting_liked_minus(title):
    db.ART_movie_list.update_one({'title': title}, {'$inc': {'liked_cnt': -1}})


def all_user_liked_movie(title, b):
    db.serverside_likeDB.insert_one({'email': b, 'title': title})


def all_user_disliked_movie(title, b):
    db.serverside_dislikeDB.insert_one({'email': b, 'title': title})


def counting_searched(data):
    print(data)
    print('cnt_search test')
    db.ART_movie_list.update_one({'title': {'$regex':data}}, {'$inc': {'searched_cnt': 1}})
    db.ART_movie_list.update_one({'director': {'$regex':data}}, {'$inc': {'searched_cnt': 1}})


def counting_commented_plus(title):
    print(title)
    db.ART_movie_list.update_one({'title': title}, {'$inc': {'commented_cnt': 1}})


def counting_commented_minus(title):
    print(title)
    db.ART_movie_list.update_one({'title': title}, {'$inc': {'commented_cnt': -1}})

@app.route('/get_movie_genre', methods=['POST'])
def get_genre():

    test = request.form['movie_title']
    nickname = request.form['nickname']
    check = request.form['check']

    # test 변수가 띄어쓰기가 굉장히 많은 변수였다...
    movie_title = test.strip()

    print(movie_title)
    print(nickname)
    print(check)

    print('장르 계산!')

    movie_title_info = list(db.ART_movie_list.find({ 'title' : movie_title},{'_id':0}));
    print(movie_title_info)

    if(movie_title_info != []):
        movie_title_genre_1 = movie_title_info[0]['genre_1']
        movie_title_genre_2 = movie_title_info[0]['genre_2']
    else:
        return jsonify({'result':'fail'})

    if(check == 'plus'):
        genre_score_plus(nickname,movie_title_genre_1,movie_title_genre_2)
    elif (check == 'minus'):
        genre_score_minus(nickname,movie_title_genre_1,movie_title_genre_2)

    
    return jsonify({'result':'success'})

# 영화 장르 점수에 점수 더해지는 함수
def genre_score_plus(nickname,genre_1,genre_2):

    print('장르 계산기 시작!')
    user_nickname = nickname
    genre_1_receive = genre_1
    print(genre_1_receive)
    genre_2_receive = genre_2
    print(genre_2_receive)

    user_info= list(db.userdb.find({'nickname':nickname},{'_id':0}));
    print(user_info)

    if(genre_1_receive != '기타'):
        user_genre_1_data = user_info[0]['genre_score'][genre_1_receive]
        print(user_genre_1_data)
        user_genre_1_data_plus = user_genre_1_data + 2
        db.userdb.update_one({'nickname': nickname},
                             {'$set': {'genre_score.' + genre_1_receive + '': user_genre_1_data_plus}})

    else:
        print('장르1는 기타 입니다.')

    if (genre_2_receive != 'NONE'):
        user_genre_2_data = user_info[0]['genre_score'][genre_2_receive]
        print(user_genre_2_data)
        user_genre_2_data_plus = user_genre_2_data + 1
        db.userdb.update_one({'nickname': nickname},
                             {'$set': {'genre_score.' + genre_2_receive + '': user_genre_2_data_plus}})

    else:
        print('장르2는 존재하지않습니다.')


# 영화 장르 점수에 점수 더해지는 함수
def genre_score_minus(nickname,genre_1,genre_2):

    print('장르 계산기 시작!')
    user_nickname = nickname
    genre_1_receive = genre_1
    print(genre_1_receive)
    genre_2_receive = genre_2
    print(genre_2_receive)

    user_info= list(db.userdb.find({'nickname':nickname},{'_id':0}));
    print(user_info)

    if(genre_1_receive != '기타'):
        user_genre_1_data = user_info[0]['genre_score'][genre_1_receive]
        print(user_genre_1_data)
        user_genre_1_data_minus = user_genre_1_data - 2
        db.userdb.update_one({'nickname': nickname},
                             {'$set': {'genre_score.' + genre_1_receive + '': user_genre_1_data_minus}})

    else:
        print('장르1는 기타 입니다.')

    if (genre_2_receive != 'NONE'):
        user_genre_2_data = user_info[0]['genre_score'][genre_2_receive]
        print(user_genre_2_data)
        user_genre_2_data_minus = user_genre_2_data - 1
        db.userdb.update_one({'nickname': nickname},
                             {'$set': {'genre_score.' + genre_2_receive + '': user_genre_2_data_minus}})

    else:
        print('장르2는 존재하지않습니다.')



@app.route('/get_comments', methods=['POST'])
def get_comments():
    if 'email' in session:
        email1 = session['email']

    title = request.form['title']
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    others_comments = list(db.serverside_usercomment.find({'user_comment_movie_title':title},{'_id':0}))
    others_comments = sorted(others_comments, key=(lambda x: x['gonggam_cnt']), reverse=True)
    print(others_comments)

    return jsonify({'result': 'success', 'others_comments': others_comments})

    #db.serverside_usercomment.drop()

    # others_comments 부분을 통해서, db에 정렬을 해야지, 오류가 발생하지 않음. 해당부분을 디버깅해야할듯.
    #if(others_comments == []):
        #pass
    #else:
        #print(others_comments)
        #db.serverside_usercomment.insert_many(others_comments)

    # print(others_comments)
    # print(others_comments[0].get('user_email'))
    # for i in range(len(others_comments)):
    #     if others_comments[i].get('user_email') == email1:


@app.route('/comment_like_counting', methods=['POST'])
def comment_like_counting():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('nickname')

    title = request.form['title']
    nickname = request.form['nickname']

    db.serverside_usercomment.update_one({'user_comment_movie_title': title, 'user_nickname': nickname},
                                         {'$inc': {'gonggam_cnt': 1}})
    db.serverside_usercomment.update({'user_nickname': nickname, 'user_comment_movie_title': title},
                                     {'$push': {'gongmag_people': b}})

    return jsonify({'result': 'success'})


@app.route('/comment_dislike_counting', methods=['POST'])
def comment_dislike_counting():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('nickname')

    title = request.form['title']
    nickname = request.form['nickname']

    db.serverside_usercomment.update_one({'user_comment_movie_title': title, 'user_nickname': nickname},
                                         {'$inc': {'gonggam_cnt': -1}})
    db.serverside_usercomment.update_one({'user_nickname': nickname, 'user_comment_movie_title': title},
                                         {'$pull': {'gongmag_people': b}})

    return jsonify({'result': 'success'})


@app.route('/check_comment', methods=['POST'])
def comment_check():
    gg = []
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('nickname')
        print(b)

    title = request.form['title']
    num = int(request.form['num'])

    p = db.serverside_usercomment.find({'user_comment_movie_title': title})
    pp = list(p)
    pp = sorted(pp, key=(lambda x: x['gonggam_cnt']), reverse=True)
    
    if len(pp) > 0:
        jj = pp[num].get('gongmag_people')
        if b in jj:
            print('좋아요를 누른 댓글')
            return jsonify({'result': 'like_success'})
        else:
            print('좋아요를 누르지 않았던 댓글')
            return jsonify({'result': 'like_fail'})

    else:
        print("길이 0")
        print('좋아요를 누르지 않았던 댓글')
        return jsonify({'result': 'nolike'})


if __name__ == '__main__':
    app.secret_key = 'heejin'
    app.run('localhost', port=5000, debug=False)
