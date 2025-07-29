import requests
from bs4 import BeautifulSoup
import pandas as pd
import os # 파일 및 폴더 관리를 위해 os 라이브러리를 추가합니다.
import sqlite3 # SQLite 데이터베이스를 다루기 위한 라이브러리를 추가합니다.


# --- 이미지 저장 폴더 생성 ---
# 국기 이미지를 저장할 'flags' 폴더를 만듭니다.
# exist_ok=True는 폴더가 이미 있어도 에러를 발생시키지 않는 옵션이에요.
flag_dir = 'flags'
os.makedirs(flag_dir, exist_ok=True)

# 1. 크롤링할 페이지 URL과 헤더 정보 설정
URL = "https://ko.tradingeconomics.com/stocks"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 2. 웹사이트에 데이터 요청
response = requests.get(URL, headers=headers)

# 3. 요청 성공 여부 확인 및 데이터 추출
if response.status_code == 200:
    print("✅ 웹페이지에 성공적으로 접속했습니다. 데이터 추출을 시작합니다.")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    all_stock_data = []
    tables = soup.find_all('table', class_='table-heatmap')
    
    print(f"🌍 총 {len(tables)}개의 대륙/지역별 주식 정보를 발견했습니다.")

    for table in tables:
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) < 10:
                continue
            
            # --- [변경] 국기 이미지 다운로드 로직 추가 ---
            country_code = cells[0].find('div')['class'][1].split('-')[-1]
            
            # 5-1. 국기 이미지 URL 생성 및 파일 경로 설정
            # 예: country_code가 'us'이면 https://flagcdn.com/w40/us.png 주소가 만들어집니다.
            flag_url = f"https://flagcdn.com/w40/{country_code}.png"
            flag_filename = f"{country_code.upper()}.png"
            flag_path = os.path.join(flag_dir, flag_filename)

            # 5-2. 폴더에 국기 이미지가 없으면 다운로드
            if not os.path.exists(flag_path):
                try:
                    flag_response = requests.get(flag_url)
                    if flag_response.status_code == 200:
                        with open(flag_path, 'wb') as f:
                            f.write(flag_response.content)
                        print(f"📥 국기 저장 완료: {flag_filename}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ 국기 다운로드 실패: {flag_filename}, 오류: {e}")

            # 5-3. 기존 데이터 추출 로직
            name = cells[1].text.strip()
            price = cells[2].text.strip()
            # ... (이하 동일)
            daily = cells[3].text.strip()
            percent = cells[4].text.strip()
            weekly = cells[5].text.strip()
            monthly = cells[6].text.strip()
            ytd = cells[7].text.strip()
            yoy = cells[8].text.strip()
            date = cells[9].text.strip()
            
            # --- [변경] 딕셔너리에 국기 파일 경로 추가 ---
            stock_info = {
                '국가': country_code.upper(),
                '지수명': name,
                '가격': price,
                '일별 변동': daily,
                '일별 %': percent,
                '주간 %': weekly,
                '월간 %': monthly,
                'YTD %': ytd,
                'YoY %': yoy,
                '날짜': date,
                '국기 파일 경로': flag_path # CSV에 파일 위치를 기록
            }
            all_stock_data.append(stock_info)

    # 6. 데이터프레임 생성 및 CSV 저장
    if all_stock_data:
        df = pd.DataFrame(all_stock_data)
        
        print("\n--- ✨ 상위 5개 주식 정보 ---")
        print(df.head(5))
        
        csv_path = 'stock_indices.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"\n✅ 모든 데이터를 '{csv_path}' 파일로 저장했습니다.")

        # --- 7. 데이터를 SQLite 데이터베이스에 저장하기 (새로운 부분!) ---
        print("\n--- 💾 데이터를 SQLite DB에 저장합니다. ---")
        db_path = 'stocks.db'
        table_name = 'stock_indices'
        conn = sqlite3.connect(db_path) # DB 파일에 연결 (없으면 자동 생성)
        
        # DataFrame을 SQL 테이블로 매우 쉽게 저장할 수 있습니다.
        # if_exists='replace'는 테이블이 이미 있으면 기존 것을 삭제하고 새로 만드는 옵션입니다.
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        conn.close() # 작업이 끝났으면 연결을 닫아줍니다.
        print(f"✅ 데이터베이스 '{db_path}'의 '{table_name}' 테이블에 저장 완료!")

        # --- 8. 데이터베이스 내용을 SQL 파일로 만들기 (새로운 부분!) ---
        sql_path = 'stocks_dump.sql'
        print(f"\n--- 📝 데이터베이스를 '{sql_path}' 파일로 백업합니다. ---")
        conn = sqlite3.connect(db_path) # DB 내용을 읽기 위해 다시 연결
        
        with open(sql_path, 'w', encoding='utf-8') as f:
            # iterdump()는 DB의 모든 내용을 SQL 쿼리문 형태로 만들어줍니다.
            for line in conn.iterdump():
                f.write(f'{line}\n')
                
        conn.close()
        print(f"✅ SQL 파일 '{sql_path}' 생성 완료!")
        
    else:
        print("❌ 데이터를 찾을 수 없습니다.")

else:
    print(f"❌ 페이지에 연결할 수 없습니다. 상태 코드: {response.status_code}")