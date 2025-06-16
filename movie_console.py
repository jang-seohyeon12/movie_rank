import requests
import os
import platform
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

# --- KOFIC API 키를 붙여넣으세요 ---
KOFIC_API_KEY = "e7e2a6f478bfcf209e468cff36eb7ee0"

def clear_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def check_api_key():
    if KOFIC_API_KEY == "e7e2a6f478bfcf209e468cff36eb7ee0":
        print("\n[오류] 코드 상단에 KOFIC API 키를 먼저 입력해주세요.")
        return False
    return True

def show_daily_box_office():
    """어제 날짜의 일별 박스오피스 TOP 10을 KOFIC API로 출력합니다."""
    clear_screen()
    print("==================================================")
    print("     🏆 일별 박스오피스 TOP 10 (KOFIC 공식) 🏆")
    print("==================================================\n")
    if not check_api_key(): return

    # 어제 날짜를 YYYYMMDD 형식으로 계산
    yesterday = datetime.now() - timedelta(1)
    target_dt = yesterday.strftime('%Y%m%d')

    print(f"[{yesterday.strftime('%Y년 %m월 %d일')}] 데이터를 불러오는 중입니다...\n")
    
    api_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={KOFIC_API_KEY}&targetDt={target_dt}"
    
    try:
        res = requests.get(api_url)
        res.raise_for_status()
        data = res.json()
        movie_list = data.get('boxOfficeResult', {}).get('dailyBoxOfficeList', [])
        if not movie_list:
            print("박스오피스 정보를 가져오지 못했습니다.")
            return
        for movie in movie_list:
            print(f" {movie.get('rank'):>2}위. {movie.get('movieNm'):<25} (일일 관객수: {int(movie.get('audiCnt')):>,}명)")
    except Exception as e:
        print(f"오류: API 접속 또는 데이터 처리 중 문제가 발생했습니다. ({e})")


def show_weekly_box_office():
    """지난주의 주간 박스오피스 TOP 10을 KOFIC API로 출력합니다."""
    clear_screen()
    print("==================================================")
    print("     🗓️ 주간 박스오피스 TOP 10 (KOFIC 공식) 🗓️")
    print("==================================================\n")
    if not check_api_key(): return

    # 지난주 날짜를 YYYYMMDD 형식으로 계산 (오늘로부터 8일 전)
    last_week = datetime.now() - timedelta(8)
    target_dt = last_week.strftime('%Y%m%d')
    
    print(f"[{last_week.strftime('%Y년 %m월 %d일')} 기준 주간] 데이터를 불러오는 중입니다...\n")

    api_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchWeeklyBoxOfficeList.json?key={KOFIC_API_KEY}&targetDt={target_dt}&weekGb=0" # 0: 주간
    
    try:
        res = requests.get(api_url)
        res.raise_for_status()
        data = res.json()
        movie_list = data.get('boxOfficeResult', {}).get('weeklyBoxOfficeList', [])
        if not movie_list:
            print("주간 박스오피스 정보를 가져오지 못했습니다.")
            return
        for movie in movie_list:
            print(f" {movie.get('rank'):>2}위. {movie.get('movieNm'):<25} (주간 관객수: {int(movie.get('audiCnt')):>,}명)")
    except Exception as e:
        print(f"오류: API 접속 또는 데이터 처리 중 문제가 발생했습니다. ({e})")


def show_genre_ranking():
    """장르별 영화를 KOFIC API로 추천합니다."""
    clear_screen()
    print("==============================================")
    print("     🎬 장르별 영화 추천 (KOFIC 기반) 🎬")
    print("==============================================\n")
    if not check_api_key(): return

    genres = {'1': '드라마', '2': '판타지', '3': '서부', '4': '공포', '5': '로맨스', '6': '모험', '7': '스릴러', '8': '느와르', '9': '컬트', '10': '다큐멘터리', '11': '코미디', '12': '가족', '13': '미스터리', '14': '전쟁', '15': '애니메이션', '16': '범죄', '17': '뮤지컬', '18': 'SF', '19': '액션'}
    print("추천받고 싶은 장르의 번호를 입력하세요.")
    for key, name in genres.items():
        print(f"  {key}. {name}")
    
    choice = input("\n▶ 장르 선택: ")
    if choice not in genres:
        print("\n[오류] 잘못된 번호입니다.")
        return

    genre_name = genres[choice]
    print(f"\n'{genre_name}' 장르의 인기 영화 10편을 검색합니다...\n")

    try:
        api_url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={KOFIC_API_KEY}&itemPerPage=10&repGenreNm={quote_plus(genre_name)}"
        res = requests.get(api_url)
        res.raise_for_status()
        data = res.json()
        movie_list = data.get('movieListResult', {}).get('movieList', [])
        if not movie_list:
            print("해당 장르의 영화를 찾지 못했습니다.")
            return
        for i, movie in enumerate(movie_list):
            title = movie.get('movieNm')
            year = movie.get('prdtYear')
            directors = ", ".join([d.get('peopleNm', '') for d in movie.get('directors', [])])
            print(f" {i+1:>2}위. {title} ({year}) / 감독: {directors}")
    except Exception as e:
        print(f"오류: API 접속 또는 데이터 처리 중 문제가 발생했습니다. ({e})")

def search_movie_details():
    """영화 상세 정보를 KOFIC과 Naver를 조합하여 검색합니다."""
    clear_screen()
    print("==================================================")
    print("           🔎 영화 상세 정보 검색 🔎")
    print("==================================================\n")
    if not check_api_key(): return

    movie_title = input("▶ 검색할 영화 제목을 입력하세요: ")
    print(f"\n'{movie_title}' 정보를 검색합니다...\n")

    try:
        kofic_url = f"http://kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json?key={KOFIC_API_KEY}&movieNm={quote_plus(movie_title)}"
        res_kofic = requests.get(kofic_url)
        res_kofic.raise_for_status()
        kofic_data = res_kofic.json()
        movie_list = kofic_data.get('movieListResult', {}).get('movieList', [])
        if not movie_list:
            print("해당하는 영화 정보를 KOFIC에서 찾을 수 없습니다.")
            return
        target_movie = movie_list[0]
        title = target_movie.get('movieNm')
        year = target_movie.get('prdtYear')
        genre = target_movie.get('repGenreNm')
        directors = ", ".join([d.get('peopleNm', '') for d in target_movie.get('directors', [])])
    except Exception as e:
        print(f"오류: KOFIC에서 영화 정보를 가져오는 데 실패했습니다. ({e})")
        return

    # 줄거리, 평점 등 부가 정보는 네이버에서 크롤링 (선택적 정보)
    rating, plot = "정보 없음", "정보 없음"
    try:
        naver_url = f"https://search.naver.com/search.naver?query={quote_plus(title + ' ' + year)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res_naver = requests.get(naver_url, headers=headers)
        if res_naver.status_code == 200:
            soup = BeautifulSoup(res_naver.text, "html.parser")
            rating_tag = soup.select_one(".sc_view_rating .star_score .num")
            rating = rating_tag.get_text(strip=True) if rating_tag else "정보 없음"
            plot_tag = soup.select_one("p.desc._text")
            plot = plot_tag.get_text(strip=True) if plot_tag else "줄거리 정보 없음"
    except Exception:
        pass # 네이버 정보는 실패해도 프로그램이 멈추지 않음

    print("--------------------------------------------------")
    print(f"■ 제목: {title} ({year})")
    print(f"■ 감독: {directors}")
    print(f"■ 장르: {genre}")
    print(f"■ 네티즌 평점: {rating}")
    print("--------------------------------------------------")
    print("■ 줄거리:")
    print(f"   {plot if plot != '줄거리 정보 없음' else '   (줄거리 정보를 가져올 수 없습니다.)'}")
    print("--------------------------------------------------")


def main():
    while True:
        clear_screen()
        print("================================================")
        print("     🎬 영화 정보 프로그램 (KOFIC API 최종본) 🎬")
        print("================================================\n")
        print("  1. 일별 박스오피스 순위 (어제)")
        print("  2. 주간 박스오피스 순위 (지난주)")
        print("  3. 장르별 영화 추천")
        print("  4. 영화 상세 정보 검색")
        print("  5. 프로그램 종료\n")
        
        choice = input("▶ 메뉴를 선택해주세요: ")
        if choice == '1':
            show_daily_box_office()
        elif choice == '2':
            show_weekly_box_office()
        elif choice == '3':
            show_genre_ranking()
        elif choice == '4':
            search_movie_details()
        elif choice == '5':
            print("\n프로그램을 종료합니다. 이용해주셔서 감사합니다.")
            break
        else:
            print("\n[오류] 메뉴에 있는 번호 중에서 선택해주세요.")

        input("\n...엔터 키를 누르면 메인 메뉴로 돌아갑니다.")

if __name__ == "__main__":
    main()
