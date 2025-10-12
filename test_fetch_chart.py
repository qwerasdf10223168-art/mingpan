from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

def fetch_chart_selenium(year, month, day, hour, gender):
    options = Options()
    # options.add_argument("--headless")  # 如需背景執行可啟用
    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.set_page_load_timeout(60)
        driver.get("https://fate.windada.com/cgi-bin/fate")

        # 等頁面載入
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Sex")))

        # 性別選擇
        if gender.lower().startswith("m"):
            driver.find_element(By.ID, "bMale").click()
        else:
            driver.find_element(By.ID, "bFemale").click()

        # 年月日時
        driver.find_element(By.NAME, "Year").send_keys(str(year))
        Select(driver.find_element(By.ID, "bMonth")).select_by_value(str(month))
        Select(driver.find_element(By.ID, "bDay")).select_by_value(str(day))
        Select(driver.find_element(By.ID, "bHour")).select_by_value(str(hour))

        # 送出查詢
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        # 等命盤主表格出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
        )

        # 找到主要命盤表格（包含「命宮」字樣）
        tables = driver.find_elements(By.TAG_NAME, "table")
        main_table = None
        for t in tables:
            if "命宮" in t.text:
                main_table = t
                break

        if not main_table:
            raise Exception("找不到命盤主表格。")

        # 擷取每個宮位文字
        cells = main_table.find_elements(By.TAG_NAME, "td")
        chart_data = []
        for c in cells:
            txt = c.text.strip()
            if not txt:
                continue

            # 去掉開頭的 07. / 8. / 09. 類型
            txt = re.sub(r'^\d+\.\s*', '', txt)
            chart_data.append(txt)

        # 直接印出乾淨命盤
        print("✅ 命盤內容：\n")
        for cell in chart_data:
            print(cell)
            print()  # 每宮之間空一行

        return chart_data

    finally:
        driver.quit()


if __name__ == "__main__":
    # 範例輸入
    year = 1991
    month = 7
    day = 24
    hour = 17
    gender = "m"

    try:
        fetch_chart_selenium(year, month, day, hour, gender)
    except Exception as e:
        print(f"⚠️ 發生錯誤：{e}")
