# 📈 Trading Economics 주식 지수 데이터 수집

실습일자 | 2025.07.29(화) </br>
실습주제 | 웹 데이터 수집 및 데이터베이스 구축 </br>

</br>

## 💡 실습 주제 및 데이터 선정

✔ Trading Economics 세계 주식 지수 데이터
: 활용 사이트 - Trading Economics
(https://ko.tradingeconomics.com/stocks)
</br>
</br>

## 💡 실습 파일 및 내용 안내

📃 **57_trading_economics_crawler.py** </br>
: Trading Economics 사이트에서 세계 주식 지표를 크롤링하고, 국기 이미지를 다운로드하여 데이터프레임으로 정리 후 CSV 파일과 SQLite DB로 저장하는 스크립트입니다.
</br>
</br>

📃 **stocks.db** </br>
: 수집된 주식 지수 데이터가 저장된 SQLite 데이터베이스 파일입니다.
</br>
</br>

📃 **stocks_dump.sql** </br>
: `stocks.db`의 내용을 SQL 쿼리문으로 백업한 파일입니다.
</br>
</br>

📃 **stock_indices.csv** </br>
: 수집된 데이터를 저장한 CSV 파일입니다.
</br>
</br>

📃 **flags/** </br>
: 각 국가별 국기 이미지를 담은 폴더입니다.
</br>
</br>

# 🍉 쿠팡 과일 상품 데이터 수집

</br>

## 💡 실습 주제 및 데이터 선정

✔ 쿠팡 과일 카테고리 상품 데이터
: 활용 사이트 - 쿠팡
(https://www.coupang.com/np/campaigns/82/components/194182?listSize=60)
</br>
</br>

## 💡 실습 파일 및 내용 안내

📃 **coupang_crawler_with_images.py** </br>
: 쿠팡 사이트에서 과일 상품 정보를 크롤링하고, 상품 이미지를 다운로드하여 데이터프레임으로 정리 후 CSV 파일로 저장하는 스크립트입니다.
</br>
</br>

📃 **coupang_fruits.db** </br>
: 수집된 과일 상품 데이터가 저장된 SQLite 데이터베이스 파일입니다.
</br>
</br>

📃 **coupang_fruits_dump.sql** </br>
: `coupang_fruits.db`의 내용을 SQL 쿼리문으로 백업한 파일입니다.
</br>
</br>

📃 **coupang_fruits_with_images.csv** </br>
: 수집된 데이터를 저장한 CSV 파일입니다.
</br>
</br>

📃 **product_images/** </br>
: 각 상품별 이미지를 담은 폴더입니다.
