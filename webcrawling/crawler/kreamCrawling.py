import requests 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from collections import defaultdict

TARGET_BRANDS = {
    "Stussy",
    "Supreme",
    "Human made",
    "Humanmade",
    "Neighborhood",
    "Palace",
    "Polyteru Human Index"
    "Carhartt WIP",
    "NOMANUAL"
}

TARGET_TOP = {
   
    # 한글
    "티셔츠",
    "후드",
    "맨투맨",
    "스웨트셔츠",
    "셔츠",
    "니트",
    
    # 영어
    "Shirt",
    "T-shirt",
    "Hood",
    "Sweatshirt",
    "Knit",
    "Man",
    "Sweat"
}

TARGET_BOTTOM = {
  
    # 한글
    "팬츠",
    "청바지",
    "데님",
    "치노",
    "슬랙스",

    # 영어
    "Pants",
    "Denim",
    "Chino",
    "Slacks",
    "Jeans"
}

TARGET_OUTER = {
    
    # 한글
    "자켓",
    "코트",
    "패딩",
    "점퍼",
    "재킷",
    "후드집업",

    # 영어
    "Jacket",
    "Coat",
    "Padding",
    "Bomber",
    "Hood Zip-up"
}

# chrome 웹드라이버를 설정하는 함수
def setup_driver():
    header_user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    options_ = Options()
    options_.add_argument(f"user-agent={header_user}")
    options_.add_experimental_option("detach", True) # 브라우저 자동 종료 방지
    options_.add_experimental_option("excludeSwitches", ["enable-logging"]) # 불필요한 로그 제거
    return webdriver.Chrome(options=options_)

# 크림 사이트에서 특정 키워드로 상품을 검색하고 결과를 반환하는 함수
def search_product(driver, keyword):
    driver.get("https://kream.co.kr/")
    time.sleep(5)

    driver.find_element(
        By.CSS_SELECTOR,
        ".btn_search.header-search-button.search-button-margin"
    ).click()
    time.sleep(3)

    search_input = driver.find_element(
        By.CSS_SELECTOR,
        ".input_search.show_placeholder_on_focus"
    )
    search_input.clear()
    search_input.send_keys(keyword)
    time.sleep(2)
    search_input.send_keys(Keys.ENTER)

    for _ in range(20):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    time.sleep(3)

def classify_category(product_name):
    name = product_name.lower()

    if any(k.lower() in name for k in TARGET_TOP):
        return "상의"
    if any(k.lower() in name for k in TARGET_BOTTOM):
        return "하의"
    if any(k.lower() in name for k in TARGET_OUTER):
        return "아우터"

    return "잡화"


# 제품 정보를 추출하는 함수
def extract_product_info(soup):
    products = []

    cards = soup.select("a.product_card")

    for card in cards:
        # 브랜드
        brand_tag = card.select_one("p.semibold.text-lookup.text-element")
        if not brand_tag:
            continue

        brand = brand_tag.get_text(strip=True)
        brand_normalized = brand.lower()

        if not any(b.lower() in brand_normalized for b in TARGET_BRANDS):
            continue

        # 제품명
        name_tag = card.select_one(
            "p.text-lookup.text-element:not(.semibold)"
        )
        if not name_tag:
            continue

        product_name = name_tag.get_text(strip=True)

        # 카테고리 분류
        category = classify_category(product_name)

        # 가격
        price_tag = card.select_one(
            ".price-info-container p.semibold.text-lookup.text-element"
        )
        price = price_tag.get_text(strip=True) if price_tag else "N/A"

        # 이미지 URL (수집만)
        img_tag = card.select_one("img.base-image-responsive__image")
        image_url = img_tag["src"] if img_tag else "N/A"

        products.append({
            "brand": brand,
            "category": category,
            "name": product_name,
            "price": price,
            "image_url": image_url
        })

    return products

def print_by_brand_and_category(products):
    grouped = defaultdict(lambda: defaultdict(list))

    for p in products:
        grouped[p["brand"]][p["category"]].append(p)

    for brand, categories in grouped.items():
        print(f"\n====== {brand} ======")
        for category, items in categories.items():
            print(f"\n  [{category}]")
            for item in items:
                print(f"   - {item['name']} | {item['price']}")

# 메인 함수
def main():
    # 검색어 입력 받기
    keyword = input("검색어를 입력하세요: ")

    # webdriver 설정
    driver = setup_driver()

    # 제품 검색
    search_product(driver, keyword)

    # HTML 소스 코드 가져오기 
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # 제품 정보 추출
    product_list = extract_product_info(soup)

    # 결과 출력 
    print_by_brand_and_category(product_list)

    # 드라이버 종료
    driver.quit()

if __name__ == "__main__":
    main()

