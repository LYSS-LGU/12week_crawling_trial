# C:\your_project_folder\naver_webtoon_selenium_crawler.py
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import time
import requests # 이미지 다운로드에 필요

# 1. 썸네일 이미지를 저장할 폴더 생성
image_dir = 'webtoon_thumbnails'
os.makedirs(image_dir, exist_ok=True)

# 2. Selenium으로 브라우저 실행
try:
    driver = uc.Chrome(use_subprocess=True)
    print("✅ Undetected Chrome 브라우저를 실행합니다.")
except Exception as e:
    print(f"❌ 드라이버 실행 중 에러 발생: {e}")
    exit()

# 3. 네이버 웹툰 페이지로 이동
URL = "https://comic.naver.com/index"
driver.get(URL)
print(f"✅ 페이지로 이동합니다: {URL}")

# 4. 자바스크립트가 웹툰 목록을 로드할 때까지 3초간 대기
print("⏳ 자바스크립트 로딩을 위해 3초 대기합니다...")
time.sleep(3)

# 5. 로딩이 완료된 페이지의 HTML을 가져와서 파싱
soup = BeautifulSoup(driver.page_source, "lxml")
all_webtoon_data = []

# 6. 최신 선택자로 인기 웹툰 목록 추출
webtoon_list = soup.select_one("ol.FlickingList__content_list--vG5lo")

if webtoon_list:
    print("✅ 인기 웹툰 목록을 찾았습니다. 데이터 추출을 시작합니다.")
    items = webtoon_list.select("li.FlickingListItem__item--rQ_Wz")
    
    for item in items:
        # 정보 추출
        title = item.select_one("span.ContentTitle__title--e3qXt").text.strip()
        author = "N/A" # 메인 페이지 목록에는 작가 정보가 없어 제외
        image_element = item.select_one("img.Poster__image--d9XTI")
        
        # 이미지 다운로드 (개선된 버전 - 디버깅 정보 추가)
        image_path = "N/A"
        if image_element and image_element.has_attr('src'):
            image_url = image_element['src']
            print(f"🔍 이미지 URL 발견: {image_url}")
            
            # 상대 경로를 절대 경로로 변환
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            elif image_url.startswith("/"):
                image_url = "https://comic.naver.com" + image_url
            
            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)
            file_extension = os.path.splitext(image_url)[1]
            image_filename = f"{sanitized_title}{file_extension if file_extension else '.jpg'}"
            image_path = os.path.join(image_dir, image_filename)
            
            if not os.path.exists(image_path) and (image_url.startswith("https:") or image_url.startswith("http:")):
                try:
                    # 네이버 서버 요청에 필요한 헤더 추가
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Referer': 'https://comic.naver.com/'
                    }
                    print(f"⬇️  이미지 다운로드 시도: {title}")
                    img_response = requests.get(image_url, headers=headers, timeout=10)
                    img_response.raise_for_status()
                    
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"✅ 이미지 저장 성공: {image_filename}")
                    
                except requests.exceptions.RequestException as e:
                    print(f"❌ 이미지 다운로드 실패 ({title}): {e}")
                    image_path = "N/A"
            else:
                if os.path.exists(image_path):
                    print(f"⏭️  이미지 이미 존재: {image_filename}")
                else:
                    print(f"⚠️  유효하지 않은 이미지 URL: {image_url}")

        webtoon_info = { "제목": title, "작가": author, "썸네일 파일": image_path }
        all_webtoon_data.append(webtoon_info)
        
    print(f"✅ 총 {len(all_webtoon_data)}개의 웹툰 정보를 추출했습니다.")
    
    # 7. CSV 파일로 저장
    df = pd.DataFrame(all_webtoon_data)
    df.to_csv("naver_webtoons_final.csv", index=False, encoding="utf-8-sig")
    
    print("\n--- ✨ 상위 5개 웹툰 정보 ---")
    print(df.head(5))
    print("\n\n✅ 모든 데이터를 'naver_webtoons_final.csv' 파일로 저장했습니다.")
else:
    print("❌ Selenium으로도 인기 웹툰 목록을 찾지 못했습니다. 선택자를 다시 확인해주세요.")

# 8. 브라우저 종료
driver.quit()
print("✅ 브라우저를 종료했습니다.")