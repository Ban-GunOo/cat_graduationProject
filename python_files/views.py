from django.shortcuts import render
from bson.objectid import ObjectId
from django import forms
from django.http import JsonResponse
import requests
import pprint
import json
import jwt
from python_files.tokenTest import SECRET_KEY, ALGORITHM
from python_files.user_check import userChecker
# Create your views here.

def home(request):
    res = render(request, 'home.html')
    token = request.COOKIES.get('token')
    if (token):
        access_token = jwt.decode(token, SECRET_KEY, ALGORITHM)
        return render(request, 'home.html', {'nickname':'김경태'})
    return render(request, 'home.html')

def top(request):
    #22~34번 줄이 토큰 만료 여부 확인하는 코드
    token = request.COOKIES.get('token')
    id=None
    access_token='none'
    nickname='none'
    if token != 'None' and token != None : #기존에 접속한 기록이 있을 경우, 그 기록으로 이전의 토큰을 얻는다.
        id = ObjectId(jwt.decode(token, SECRET_KEY, ALGORITHM)['id'])
        access_token = userChecker.checkToken(id)
        nickname = userChecker.checkNickname(id)
        if access_token != None and access_token != 'none':
            a = requests.get('https://kapi.kakao.com/v1/user/access_token_info', headers={"Authorization": f'Bearer ${access_token}'})
            if a.json().get('id') == None:  # 토큰이 죽어있다면 None을 반환한다.
                if a.json()['code'] == -401:
                    token='None'
        else:
            token = 'None'
    if token == 'None': #토큰이 없을 경우 발급받는다.
        code = request.GET['code']
        grant_type = 'authorization_code'
        client_id = '10ecf0439a675841802b2143335b994e'
        redirect_uri = 'http://127.0.0.1:8000/top'
        # Get access_token!
        param = {
            'grant_type': grant_type,
            'client_id': client_id,
            'redirect_uri' : redirect_uri,
            'code' : code,
        }
        url = 'https://kauth.kakao.com/oauth/token'
        r = requests.post(url, data=param)
        json_result = r.json()
        access_token = json_result['access_token']
        u = requests.get('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f'Bearer ${access_token}'})
        user_info_result = u.json()
        nickname = user_info_result['kakao_account']['profile']['nickname']
        # 회원번호 획득
        a = requests.get('https://kapi.kakao.com/v1/user/access_token_info', headers={"Authorization": f'Bearer ${access_token}'})
        userID=(a.json())['id']
        # 여기에서, 카카오 회원 번호를 써서 몽고db에 저장된 사용자의 인덱스를 얻는다. 만약 새 사용자라면 db에 추가한다.
        if userChecker.checkUserDB(userID)==False:
            userChecker.addUser(userID, nickname)
        id = userChecker.checkID(userID)
        # 발급받은 토큰을 저장한다.
        userChecker.setToken(ObjectId(id), access_token)
        data = {'id': id}
        token = jwt.encode(data, SECRET_KEY, ALGORITHM) #jwt 토큰 획득
    res = render(request, 'main/top.html', {'access_token':access_token, 'nickname':nickname})
    res.set_cookie('token', token) #만든 토큰을 쿠키에 추가
    return res


def draw_room(request):
    token = request.COOKIES.get('token')
    #입력이 들어온 경우
    if request.method == "POST":
        if request.POST.get('room_structure_number'):
            #draw_room.html의 submit_room_data함수 참고
            #undefined 들어오면 무시하고 저장하기
            room_structure_number = int(request.POST.get('room_structure_number'))
            room_element_number = int(request.POST.get('room_element_number'))

            #방 구조의 수 출력
            print('방 구조 수')
            print(room_structure_number)
            #방 요소의 수 출력
            print('방 요소 수')
            print(room_element_number)
            #방구조 정보 출력
            print('방 구조들')
            for i in range(0, room_structure_number):
                print(request.POST.get('room_structure_'+str(i)))
            #방요소 정보 출력
            print('방 요소들')
            for i in range(0, room_element_number):
                print(request.POST.get('room_element_data'+str(i)))

            #방 위치 출력
            print('방 위치')
            print(request.POST.get('room_location'))

            #방 상세 텍스트 출력
            print('방 상세 텍스트')
            print(request.POST.get('room_specific_information'))

        return render(request, 'main/draw_room.html')
    else:
        if token != 'None' and token != None:  # 기존에 접속한 기록이 있을 경우, 그 기록으로 이전의 토큰을 얻는다.
            id = ObjectId(jwt.decode(token, SECRET_KEY, ALGORITHM)['id'])
            access_token = userChecker.checkToken(id)
            nickname = userChecker.checkNickname(id)


            return render(request, 'main/draw_room.html', {'nickname':nickname})

        return render(request, 'main/draw_room.html')