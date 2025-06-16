import requests
import os
import platform

# BeautifulSoup는 이제 장르별 순위에서는 필요 없으므로, import 목록에서 제거해도 무방합니다.
# 하지만 다른 기능에서 사용하므로 일단 둡니다.
from bs4 import BeautifulSoup

def clear_screen():
    """콘솔 화면을 깨끗하게 지우는 함수"""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def get_soup(url):
    """주어진 URL의 BeautifulSoup 객체를 반환하는 함수 (박스오피스용)"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"오류: 웹사이트에 접속할 수 없습니다. ({e})")
        return None

# --- 기존 박스오피스 함수들은 그대로 사용 ---

def show_all_time_box_office():
    clear_screen()
    print("==============================================")
    print("     🏆 국내 영화 역대 박스오피스 TOP 10 🏆")
    print("==============================================\n")
    print("데이터를 불러오는 중입니다...\n")
    url = "https://search.naver.com/search.naver?query=역대+박스오피스+순위"
    soup = get_soup(url)
    if not soup: return
    container = soup.find("div", attrs={"class": "_svp_list"})
    if not container:
        print("오류: 박스오피스 정보를 찾을 수 없습니다.")
        return
    movies = container.find_all("div", attrs={"class": "list_item"})
    for i, movie in enumerate(movies[:10]):
        title = movie.find("strong", class_="title").get_text(strip=True)
        audience_span = movie.find("span", string=lambda t: t and "관객수" in t)
        if audience_span:
            audience = audience_span.find_next_sibling("span", class_="num").get_text(strip=True)
            print(f" {(i+1):>2}위. {title:<25} (관객수: {audience}명)")
        else:
            print(f" {(i+1):>2}위. {title:<25} (관객수 정보 없음)")

def show_monthly_box_office():
    clear_screen()
    print("==============================================")
    print("     📅 월별 국내 박스오피스 TOP 10 📅")
    print("==============================================\n")
    try:
        year = input("▶ 조회할 연도를 입력하세요 (예: 2024): ")
        month = input("▶ 조회할 월을 입력하세요 (예: 5): ")
        int(year); int(month)
    except ValueError:
        print("\n[오류] 연도와 월은 숫자로만 입력해주세요.")
        return
    print(f"\n{year}년 {month}월의 데이터를 불러오는 중입니다...\n")
    url = f"https://search.naver.com/search.naver?query={year}년+{month}월+영화+순위"
    soup = get_soup(url)
    if not soup: return
    container = soup.find("div", attrs={"class": "_svp_list"})
    if not container:
        print(f"오류: {year}년 {month}월 박스오피스 정보를 찾을 수 없습니다.")
        return
    movies = container.find_all("div", attrs={"class": "list_item"})
    if not movies:
        print(f"{year}년 {month}월에 대한 순위 정보가 없습니다.")
        return
    for i, movie in enumerate(movies[:10]):
        title = movie.find("strong", class_="title").get_text(strip=True)
        audience_span = movie.find("span", string=lambda t: t and "관객수" in t)
        if audience_span:
            audience = audience_span.find_next_sibling("span", class_="num").get_text(strip=True)
            print(f" {(i+1):>2}위. {title:<25} (관객수: {audience}명)")
        else:
            print(f" {(i+1):>2}위. {title:<25} (관객수 정보 없음)")

# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
#           [최종 수정] 장르별 랭킹 함수를 API 호출 방식으로 완전히 변경
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
def show_genre_ranking():
    """장르별 영화 평점 순위 TOP 10을 출력하는 함수 (API 호출 버전)"""
    clear_screen()
    print("==============================================")
    print("     🎬 장르별 영화 추천 (평점순) 🎬")
    print("==============================================\n")

    genres = {
        '1': ('코미디', '11'),
        '2': ('로맨스/멜로', '2'),
        '3': ('스릴러', '6'),
        '4': ('SF', '8')
    }

    print("선택할 장르의 번호를 입력해주세요.")
    for key, (name, _) in genres.items():
        print(f"  {key}. {name}")
    
    choice = input("\n▶ 장르 선택: ")

    if choice not in genres:
        print("\n[오류] 잘못된 번호를 선택했습니다.")
        return

    genre_name, genre_code = genres[choice]
    print(f"\n'{genre_name}' 장르의 영화 평점 순위를 불러오는 중입니다...\n")
    
    # [수정] 네이버 영화의 실제 데이터 API 주소로 직접 요청
    api_url = f"https://api.movie.naver.com/ranking/pnt/v2/current?pntCode=EXT&offset=0&limit=10&genreCode={genre_code}"
    
    try:
        # [수정] API 호출 시에는 Referer 헤더를 포함해주는 것이 좋음
        headers = {'Referer': 'https://movie.naver.com/movie/sdb/rank/rmovie.naver'}
        res = requests.get(api_url, headers=headers)
        res.raise_for_status()

        # [수정] 응답 결과를 JSON 형태로 변환
        data = res.json()
        
        # [수정] JSON 데이터 구조에 맞게 영화 목록을 가져옴
        movie_list = data.get('content', {}).get('movieList', [])

        if not movie_list:
            print("해당 장르의 순위 정보를 가져올 수 없습니다.")
            return

        for movie in movie_list:
            rank = movie.get('rank')
            title = movie.get('movieName')
            rating = movie.get('pnt')
            print(f" {rank:>2}위. {title:<25} (평점: {rating})")

    except requests.exceptions.RequestException as e:
        print(f"오류: 데이터 API에 접속할 수 없습니다. ({e})")
    except Exception as e:
        print(f"오류: 데이터를 처리하는 중 문제가 발생했습니다. ({e})")


def main():
    """메인 실행 함수"""
    while True:
        clear_screen()
        print("==============================================")
        print("      🎬 영화 순위 및 추천 프로그램 🎬      ")
        print("==============================================\n")
        print("  1. 국내 역대 박스오피스 순위")
        print("  2. 월별 국내 박스오피스 순위")
        print("  3. 장르별 영화 추천 (평점순)")
        print("  4. 프로그램 종료\n")
        
        choice = input("▶ 메뉴를 선택해주세요: ")

        if choice == '1':
            show_all_time_box_office()
        elif choice == '2':
            show_monthly_box_office()
        elif choice == '3':
            show_genre_ranking()
        elif choice == '4':
            print("\n프로그램을 종료합니다. 이용해주셔서 감사합니다.")
            break
        else:
            print("\n[오류] 1, 2, 3, 4 중에서 선택해주세요.")

        input("\n...엔터 키를 누르면 메인 메뉴로 돌아갑니다.")


if __name__ == "__main__":
    main()