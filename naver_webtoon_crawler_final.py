# C:\githome\12week_crawling_trial\naver_webtoon_crawler_final.py
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import time
import requests
from selenium.webdriver.common.by import By  # 최신 Selenium 방식 사용

image_dir = 'webtoon_thumbnails'
os.makedirs(image_dir, exist_ok=True)

# 1. 브라우저 옵션 설정 (더 사람처럼 보이게)
options = uc.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
options.add_argument('window-size=1920x1080')
# options.add_argument('--headless')  # 주석을 풀면 브라우저 창이 보이지 않게 실행됩니다.

try:
    driver = uc.Chrome(options=options, use_subprocess=True)
    print("Undetected Chrome 브라우저를 실행합니다.")
except Exception as e:
    print(f"드라이버 실행 중 에러 발생: {e}")
    exit()

URL = "https://comic.naver.com/index"
driver.get(URL)
print(f" 페이지로 이동합니다: {URL}")

print(" 자바스크립트 로딩을 위해 7초간 대기합니다...")
time.sleep(7)

soup = BeautifulSoup(driver.page_source, "lxml")
all_webtoon_data = []

try:
    # 메뉴에서 웹툰 섹션으로 이동 (#menu > li:nth-child(1) > a)
    webtoon_menu = driver.find_element(By.CSS_SELECTOR, "#menu > li:nth-child(1) > a")
    webtoon_menu.click()
    print(" 웹툰 메뉴를 클릭했습니다.")
    time.sleep(3)
    
    # 장르별 버튼 클릭 (#content > div:nth-child(1) > div.ComponentHead__component_head--O2tPr.ComponentHead__type_genre--ioHSd > div > div > button:nth-child(1))
    genre_button = driver.find_element(By.CSS_SELECTOR, "#content > div:nth-child(1) > div.ComponentHead__component_head--O2tPr.ComponentHead__type_genre--ioHSd > div > div > button:nth-child(1)")
    genre_button.click()
    print(" 장르별 버튼을 클릭했습니다.")
    time.sleep(3)
    
    # 새로운 페이지 소스 가져오기
    soup = BeautifulSoup(driver.page_source, "lxml")
    
    # 웹툰 이미지들 선택 (#content > div:nth-child(1) > div.FlickingList__flicking_wrap--vnPay > div.flicking-viewport > div > ol > li:nth-child(1) > a > div > img)
    webtoon_images = soup.select("#content > div:nth-child(1) > div.FlickingList__flicking_wrap--vnPay > div.flicking-viewport > div > ol > li > a > div > img")
    print(f" 웹툰 이미지 목록을 찾았습니다. 총 {len(webtoon_images)}개의 웹툰을 발견했습니다.")
    
    # 웹툰 링크들도 함께 가져오기
    webtoon_links = soup.select("#content > div:nth-child(1) > div.FlickingList__flicking_wrap--vnPay > div.flicking-viewport > div > ol > li > a")
    
    for i, (image_element, link_element) in enumerate(zip(webtoon_images, webtoon_links)):
        # 제목은 alt 속성이나 aria-label에서 가져오기
        title = image_element.get('alt', f'웹툰_{i+1}')
        if not title or title == '':
            title = link_element.get('aria-label', f'웹툰_{i+1}')
        
        author = "N/A"  # 현재 셀렉터로는 작가 정보를 가져올 수 없음
        rating = "0"    # 현재 셀렉터로는 별점 정보를 가져올 수 없음
        image_path = "N/A"
        
        # 이미지 다운로드 처리
        if image_element and image_element.has_attr('src'):
            image_url = image_element['src']
            
            if image_url.startswith("//"): image_url = "https:" + image_url

            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
            file_extension = os.path.splitext(image_url)[1]
            image_filename = f"{sanitized_title}{file_extension if file_extension else '.jpg'}"
            image_path = os.path.join(image_dir, image_filename)
            
            if not os.path.exists(image_path) and image_url.startswith("https:"):
                try:
                    # 이미지 다운로드 시 'Referer' 헤더 추가
                    img_headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                        'Referer': 'https://comic.naver.com/'
                    }
                    img_response = requests.get(image_url, headers=img_headers)
                    img_response.raise_for_status()
                    with open(image_path, 'wb') as f: f.write(img_response.content)
                    print(f" 이미지 다운로드 완료: {image_filename}")
                except requests.exceptions.RequestException as e:
                    print(f" 이미지 다운로드 실패: {e}")
                    image_path = "N/A"

        webtoon_info = { "제목": title, "작가": author, "별점": float(rating), "썸네일 파일": image_path }
        all_webtoon_data.append(webtoon_info)
        
    print(f"총 {len(all_webtoon_data)}개의 웹툰 정보를 추출했습니다.")
    
    if all_webtoon_data:
        df = pd.DataFrame(all_webtoon_data)
        df.to_csv("naver_webtoons_final.csv", index=False, encoding="utf-8-sig")
        
        print("\n---  상위 5개 웹툰 정보 ---")
        print(df.head(5))
        print("\n\n 모든 데이터를 'naver_webtoons_final.csv' 파일로 저장했습니다.")
    else:
        print(" 웹툰 데이터를 찾을 수 없습니다.")
        
except Exception as e:
    print(f" 크롤링 중 에러 발생: {e}")
    print("대체 방법으로 메인 페이지에서 직접 크롤링을 시도합니다...")
    
    # 기존 방식으로 시도
    soup = BeautifulSoup(driver.page_source, "lxml")
    webtoon_section = soup.find("div", attrs={"data-testid": "오늘의 인기 웹툰"})
    
    if webtoon_section:
        items = webtoon_section.select("li.FlickingListItem__item--rQ_Wz")
        print(f" 인기 웹툰 목록을 찾았습니다. 총 {len(items)}개의 웹툰을 발견했습니다.")
        
        for item in items:
            title = item.select_one("span.ContentTitle__title--e3qXt").text.strip()
            author = "N/A"
            rating = "0"
            image_element = item.select_one("a > div > img.Poster__image--d9XTI")
            image_path = "N/A"
            
            if image_element and image_element.has_attr('src'):
                image_url = image_element['src']
                
                if image_url.startswith("//"): image_url = "https:" + image_url

                sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
                file_extension = os.path.splitext(image_url)[1]
                image_filename = f"{sanitized_title}{file_extension if file_extension else '.jpg'}"
                image_path = os.path.join(image_dir, image_filename)
                
                if not os.path.exists(image_path) and image_url.startswith("https:"):
                    try:
                        img_headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                            'Referer': 'https://comic.naver.com/'
                        }
                        img_response = requests.get(image_url, headers=img_headers)
                        img_response.raise_for_status()
                        with open(image_path, 'wb') as f: f.write(img_response.content)
                    except requests.exceptions.RequestException:
                        image_path = "N/A"

            webtoon_info = { "제목": title, "작가": author, "별점": float(rating), "썸네일 파일": image_path }
            all_webtoon_data.append(webtoon_info)
            
        if all_webtoon_data:
            df = pd.DataFrame(all_webtoon_data)
            df.to_csv("naver_webtoons_final.csv", index=False, encoding="utf-8-sig")
            print(f"총 {len(all_webtoon_data)}개의 웹툰 정보를 추출했습니다.")
        else:
            print(" 웹툰 데이터를 찾을 수 없습니다.")
    else:
        print(" 인기 웹툰 목록 영역을 찾을 수 없습니다.")

driver.quit()
print(" 브라우저를 종료했습니다.")