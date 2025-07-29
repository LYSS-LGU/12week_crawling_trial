# C:\githome\12week_crawling_trial\uc_coupang_crawler_with_images.py
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import os
import requests # 이미지 다운로드를 위해 requests를 다시 import 합니다.

# --- [추가] 이미지 저장 폴더 생성 ---
image_dir = 'product_images'
os.makedirs(image_dir, exist_ok=True)

# 1. undetected-chromedriver를 사용해 브라우저 열기
try:
    driver = uc.Chrome(use_subprocess=True)
    print("✅ Undetected Chrome 브라우저를 실행합니다.")
except Exception as e:
    print(f"❌ 드라이버 실행 중 에러 발생: {e}")
    exit()

# 2. 크롤링할 페이지로 이동
URL = "https://www.coupang.com/np/campaigns/82/components/194182?listSize=60"
driver.get(URL)
print(f"✅ 페이지로 이동합니다: {URL}")

# 3. 페이지 로딩 대기
print("⏳ 상품 정보를 불러오는 중입니다... (5초 대기)")
time.sleep(5)

# 4. 데이터 추출 준비
soup = BeautifulSoup(driver.page_source, "lxml")
product_list = soup.select_one("ul#product-list")

all_product_data = []

# 5. 상품 목록 확인 및 데이터 추출
if product_list:
    print("✅ 상품 목록을 찾았습니다. 데이터 추출을 시작합니다.")
    items = product_list.select("li.search-product, li.ProductUnit_productUnit__Qd6sv")
    
    for item in items:
        # (기존 상품명, 가격, 평점, 리뷰 수, 링크 추출 코드는 동일)
        name_element = item.select_one("div.name, div.ProductUnit_productName__gre7e")
        name = name_element.text.strip() if name_element else "N/A"
        
        price_element = item.select_one("strong.price-value")
        price = price_element.text.strip().replace(",", "") if price_element else "0"
        
        rating_element = item.select_one("em.rating")
        rating = rating_element.text.strip() if rating_element else "0"
        
        review_count_element = item.select_one("span.rating-total-count")
        review_count = "0"
        if review_count_element:
            match = re.search(r'\((\d+,?\d*)\)', review_count_element.text)
            if match: review_count = match.group(1).replace(",", "")

        link_element = item.select_one("a")
        link = "https://www.coupang.com" + link_element['href'] if link_element and link_element.has_attr('href') else "N/A"

        # --- [추가] 이미지 URL 추출 및 다운로드 ---
        image_element = item.select_one("a > figure > img")
        image_url = ""
        image_path = "N/A"
        
        if image_element and image_element.has_attr('src'):
            image_url = image_element['src']
            # URL에 'https:'가 없으면 붙여줍니다. (쿠팡은 보통 포함되어 있음)
            if not image_url.startswith("https:"):
                image_url = "https:" + image_url
            
            # 파일명으로 사용할 수 없는 문자 제거
            sanitized_name = re.sub(r'[\\/*?:"<>|]', "", name)
            image_filename = f"{sanitized_name}.jpg"
            image_path = os.path.join(image_dir, image_filename)
            
            # 이미지가 아직 다운로드되지 않았다면 저장
            if not os.path.exists(image_path):
                try:
                    img_response = requests.get(image_url)
                    img_response.raise_for_status()
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                except requests.exceptions.RequestException as e:
                    print(f"❌ 이미지 다운로드 실패: {name}, 오류: {e}")
                    image_path = "N/A" # 실패 시 경로 N/A 처리

        product_info = {
            "상품명": name, "가격": int(price), "평점": float(rating),
            "리뷰 수": int(review_count), "링크": link,
            "이미지 파일": image_path  # <-- [추가] 딕셔너리에 이미지 파일 경로 추가
        }
        all_product_data.append(product_info)
        
    if all_product_data:
        print(f"✅ 총 {len(all_product_data)}개의 상품 정보를 추출했습니다.")
        df = pd.DataFrame(all_product_data)
        df.to_csv("coupang_fruits_with_images.csv", index=False, encoding="utf-8-sig")
        
        print("\n--- ✨ 상위 5개 과일 상품 정보 ---")
        print(df.head(5))
        print("\n\n✅ 모든 데이터를 'coupang_fruits_with_images.csv' 파일로 저장했습니다.")
else:
    print("❌ 상품 목록(ul#product-list)을 찾을 수 없습니다.")

# 7. 브라우저 종료
driver.quit()
print("✅ 브라우저를 종료했습니다.")