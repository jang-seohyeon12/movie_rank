import requests
from bs4 import BeautifulSoup
import os
import platform

def clear_screen():
    """콘솔 화면을 깨끗하게 지우는 함수"""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def get_soup(url):
    """주어진 URL의 BeautifulSoup 객체를 반환하는 함수"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"오류: 웹사이트에 접속할 수 없습니다. ({e})")
        return None

def show_all_time_box_office():
    """국내 영화 역대 박스오피스 TOP 10을 출력하는 함수"""
    clear_screen()
    print("==============================================")
    print("     🏆 국내 영화 역대 박스오피스 TOP 10 🏆")
    print("==============================================\n")
    print("데이터를 불러오는 중입니다...\n")

    url = "https://search.naver.com/search.naver?query=역대+박스오피스+순위"
    soup = get_soup(url)
    if not soup:
        return

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
    """사용자에게 연도와 월을 입력받아 월별 박스오피스 TOP 10을 출력하는 함수"""
    clear_screen()
    print("==============================================")
    print("     📅 월별 국내 박스오피스 TOP 10 📅")
    print("==============================================\n")
    
    try:
        year = input("▶ 조회할 연도를 입력하세요 (예: 2024): ")
        month = input("▶ 조회할 월을 입력하세요 (예: 5): ")
        int(year) # 숫자 확인용
        int(month) # 숫자 확인용
    except ValueError:
        print("\n[오류] 연도와 월은 숫자로만 입력해주세요.")
        return

    print(f"\n{year}년 {month}월의 데이터를 불러오는 중입니다...\n")
    
    url = f"https://search.naver.com/search.naver?query={year}년+{month}월+영화+순위"
    soup = get_soup(url)
    if not soup:
        return

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


def show_genre_ranking():
    """장르별 영화 평점 순위 TOP 10을 출력하는 함수"""
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
    
    url = f"https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&tg={genre_code}"
    soup = get_soup(url)
    if not soup:
        return

    ranking_table = soup.find("table", class_="list_ranking")
    if not ranking_table:
        print("오류: 장르별 순위 정보를 찾을 수 없습니다.")
        return

    movies = ranking_table.find_all("tr")
    rank = 1
    for movie in movies:
        title_div = movie.find("div", class_="tit5")
        point_td = movie.find("td", class_="point")
        if title_div and point_td:
            title = title_div.a.get_text(strip=True)
            rating = point_td.get_text(strip=True)
            print(f" {rank:>2}위. {title:<25} (평점: {rating})")
            rank += 1
            if rank > 10:
                break


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
    