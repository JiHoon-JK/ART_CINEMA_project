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
        '에니메이션': 0,
        '범죄': 0,
        '뮤지컬': 0,
        'SF': 0,
        '액션': 0
    }

    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email':email1},{'_id': 0}))
        b = a[0].get('email')

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

    result = sorted(genre_score.items(), key=lambda x: x[1], reverse=True)
    print(result)
    global customer_main_genre
    global customer_second_genre
    customer_main_genre = result[0][0]
    customer_second_genre = result[1][0]

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


@app.route('/page2')
def page2():
    db.select_movie.drop()
    if 'email' in session:
        email1 = session['email']
        print('1Logged in as ' + email1)
        print(session)
        return render_template('page2.html', sessionemail=email1)

    else:
        return render_template('page2.html')

@app.route('/temp')
def temp():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        print(a[0].get('nickname'))
        return render_template('temp.html', sessionemail2=a[0].get('nickname'))
    else:
        return render_template('temp.html')

@app.route('/page3')
def page3():
    genre_cnt()
    recommend_movie_db()
    return render_template('page3.html')


@app.route('/page4')
def page4():
    if 'email' in session:
        email1 = session['email']
        print('Logged in as ' + email1)
        print(session)
        return render_template('page4.html', sessionemail=email1)

    else:
        return render_template('page4.html')

@app.route('/page5')
def page5():
    if 'email' in session:
        email1 = session['email']
        print('tempLogged in as ' + email1)
        print(session)
        return render_template('page5.html', sessionemail=email1)
    else:
        return render_template('page5.html')

@app.route('/mypage')
def mypage():
    return render_template('my_page.html')


@app.route('/user', methods=['GET'])
def listing():
    result = list(db.Long_movie_list.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'Long_movie_list': result})


@app.route('/main', methods=['GET'])
def listing2():
    result = list(db.ART_movie_list.find({}, {'_id': 0}))
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
                return jsonify({'result': 'success', 'userdb': email})
            else:
                return jsonify({'result': 'fail', 'userdb': 'failed'})
    else:
        return jsonify({'result': 'fail', 'userdb': 'failed'})


# 로그아웃
@app.route('/test2', methods=['POST'])
def logout():
    session.pop('email', None)
    return jsonify({'result': 'success'})


# 회원가입
@app.route('/customer', methods=['POST'])
def register():
    email = request.form['email']
    pwd = request.form['pwd']
    nickname = request.form['nickname']

    pw_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()

    a = list(db.userdb.find({}))

    if len(a) == 0:
        db.userdb.insert_one({'email': email, 'pwd': pw_hash, 'nickname': nickname, 'genre_1': "", 'genre_2': ""})
        return jsonify({'result': 'success'})

    else:
        for i in range(len(a)):
            if a[i].get('email') == email:
                return jsonify({'result': 'fail1'})
            elif a[i].get('nickname') == nickname:
                return jsonify({'result': 'fail2'})

        db.userdb.insert_one({'email': email, 'pwd': pw_hash, 'nickname': nickname})
        return jsonify({'result': 'success', 'userdb': email})

# mypage연결 api
@app.route('/info_my_comment_movie', methods=['GET'])
def show_my_comment_movie():
    my_comment_movie = list(db.serverside_usercomment.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'my_comment_movie': my_comment_movie})


@app.route('/info_my_like_movie', methods=['GET'])
def show_like_movie():
    for count in range(1):
        # 서버 내부에서 수행 할 기능 / DB에 저장돼있는 모든 정보 중 'genre1':'드라마' 가져오
        my_like_movie = list(db.LDDB.find({}, {'_id': 0}))
        return jsonify({'result': 'success', 'my_like_movie': my_like_movie})


@app.route('/info_my_dislike_movie', methods=['GET'])
def show_dislike_movie():
    my_dislike_movie = list(db.LDDB.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'my_dislike_movie': my_dislike_movie})



@app.route('/info_my_diswatch_movie', methods=['GET'])
def show_diswatch_movie():
    for repeat in range(1):
        # 서버 내부에서 수행 할 기능 / DB에 저장돼있는 모든 정보 중 'genre1':'드라마' 가져오
        my_diswatch_movie = list(db.LDDB.find({}, {'_id': 0}))
        return jsonify({'result': 'success', 'my_diswatch_movie': my_diswatch_movie})


@app.route('/dislike_movie', methods=['POST'])
def dislike_button():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')

    dislike_movie = {
        'email': b,
        'title': request.form['title'],
        'poster': request.form['poster'],
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
        'title': request.form['title'],
        'poster': request.form['poster'],
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

    title= request.form['title']

    db.LDDB.update_one({'email': b, 'title':title}, {'$set': {'like':True,'dislike':False}})
    counting_liked_plus(title)
    db.serverside_dislikeDB.remove({'email':b, 'title':title})
    all_user_liked_movie(title, b)
    return jsonify({'result': 'success'})

@app.route('/LDupdate_movie', methods=['POST'])
def LDupdate_button():
    if 'email' in session:
        email1 = session['email']
        a = list(db.userdb.find({'email': email1}, {'_id': 0}))
        b = a[0].get('email')

    title= request.form['title']

    db.LDDB.update_one({'email': b, 'title':title}, {'$set': {'like':False,'dislike':True}})
    counting_liked_minus(title)
    db.serverside_likeDB.remove({'email':b, 'title':title})
    all_user_disliked_movie(title, b)
    return jsonify({'result': 'success'})



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
    user_email = request.form['email']
    user_comment_movie_title = request.form['user_comment_movie_title']
    user_comment_movie_poster = request.form['user_comment_movie_poster']
    user_comment_movie = request.form['user_comment_give']
    print(user_comment_movie_title)
    print(user_comment_movie)
    find_db = list(db.serverside_usercomment.find({'user_email':user_email,'user_comment_movie_title':user_comment_movie_title}, {'_id' : 0}))
    print(find_db)
    find_db_len =len(find_db)
    print(find_db_len)
    if(find_db_len > 0):
        edit_check_db = find_db[0]['edit']
        print(edit_check_db)
        if(edit_check_db == False):
            print('이미 코멘트를 작성한 영화입니다.')
            comment = find_db[0]['user_comment']
            print(comment)
            return jsonify({'result': 'fail', 'comment': comment})
        if(edit_check_db == True):
            print('코멘트를 수정했습니다.')
            comment = find_db[0]['user_comment']
            print(comment)
            edit_check = find_db[0]['edit']
            print(edit_check)
            return jsonify({'result': 'success', 'comment': comment, 'edit' : edit_check})
    else:
        data = {
            'user_email': user_email,
            'user_comment_movie_title': user_comment_movie_title,
            'user_comment_movie_poster': user_comment_movie_poster,
            'user_comment': user_comment_movie,
            'edit':False,
        }
        print(data)
        print('코멘트를 작성했습니다.')
        db.serverside_usercomment.insert_one(data)
        return jsonify({'result': 'success'})

@app.route('/comment_edit', methods=['POST'])
def edited_comment():
    # before_edit_comment = request.form['before_edit_comment']
    # print(before_edit_comment+'1')
    email = request.form['email']
    edit_movie_title = request.form['edit_movie']
    edit_comment = request.form['edit_comment']
    print('////'+edit_comment)
    update_comment_db = list(db.serverside_usercomment.update({'user_email':email,'user_comment_movie_title':edit_movie_title},{'$set':{'user_comment':edit_comment,'edit':True}}))
    print(update_comment_db)
    return jsonify({'result':'success'})


@app.route('/comment_remove', methods=['POST'])
def removed_comment():
    user_comment_remove = request.form['user_comment']
    print(user_comment_remove)
    find_comment_db = list(db.serverside_usercomment.find({'user_comment':user_comment_remove},{'_id':0}))
    print(find_comment_db)
    if(user_comment_remove == find_comment_db[0]['user_comment']):
        db.serverside_usercomment.remove({'user_comment':user_comment_remove})
        print('코멘트가 삭제되었습니다.')
        return jsonify({'result':'success'})
    else:
        print('해당 코멘트가 없습니다. !오류발생!')
        return jsonify({'result':'fail'})



@app.route('/genre1_movie', methods=['GET'])
def recommend():
    user_info = list(db.userdb.find({}, {'_id': 0}))

    print(user_info)
    user_genre_1 = (user_info[0]['genre_1'])
    result = list(db.genre1_art_movie.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'movies': result, 'user_genre_1': user_genre_1})


@app.route('/genre2_movie', methods=['GET'])
def recommend2():
    user_info = list(db.userdb.find({}, {'_id': 0}))
    print(user_info)
    user_genre_2 = (user_info[0]['genre_2'])
    result = list(db.genre2_art_movie.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'movies': result, 'user_genre_2': user_genre_2})

@app.route('/search_movie', methods=['POST'])
def search_movie():
    search_movie = request.form['search_title_give']
    data = {
        'search_movie': search_movie
    }
    db.search_movie.insert_one(data)
    return jsonify({'result': 'success'})

@app.route('/search_DB', methods=['GET'])
def search_DB():
    search_movie = list(db.search_movie.find({}, {'_id': 0}))
    print(search_movie)
    search_title_give = search_movie[-1]['search_movie']
    print(search_title_give)
    movie_info_ART = list(db.ART_movie_list.find({'title':{'$regex':search_title_give}}, {'_id': 0}))
    movie_info_Long = list(db.Long_movie_list.find({'title':{'$regex':search_title_give}}, {'_id': 0}))
    print(movie_info_ART)
    print(movie_info_Long)
    movie_info = movie_info_ART + movie_info_Long
    print(movie_info)
    if (movie_info == []):
        print('영화가 없을 때!!!')
        return jsonify({'result': 'fail'})
    else:
        print('영화가 있을 때!!!')
        return jsonify({'result': 'success', 'Movie_info':movie_info})

def counting_liked_plus(title):
    db.ART_movie_list.update_one({'title': title}, {'$inc': {'liked_cnt':1}})
def counting_liked_minus(title):
    db.ART_movie_list.update_one({'title': title}, {'$inc': {'liked_cnt':-1}})

def all_user_liked_movie(title,b):
    db.serverside_likeDB.insert_one({'email':b, 'title':title})
def all_user_disliked_movie(title,b):
    db.serverside_dislikeDB.insert_one({'email':b, 'title':title})

def counting_searched(title):
    print(title)
    db.Long_movie_list.update_one({'title':title}, {'$inc': {'searched_cnt':1}})
    

if __name__ == '__main__':
    app.secret_key = 'heejin'
    app.run('localhost', port=5000, debug=True)