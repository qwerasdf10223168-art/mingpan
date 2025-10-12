from flask import Flask, render_template, request
import mingpan_logic as mp
import markdown
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# ---------------------- 爬蟲部分 ----------------------
def fetch_chart_selenium(year, month, day, hour, gender):
    """
    從 fate.windada.com 爬取紫微命盤文字
    （會去除開頭數字編號，但保留宮名，如「丁酉【兄弟宮】」）
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 不開視窗模式
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = 'normal'

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.set_page_load_timeout(60)
        driver.get("https://fate.windada.com/cgi-bin/fate")

        # 等待頁面性別選項出現
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Sex")))

        # 性別選擇
        if gender.lower().startswith("m"):
            driver.find_element(By.ID, "bMale").click()
        else:
            driver.find_element(By.ID, "bFemale").click()

        # 輸入年月日時
        driver.find_element(By.NAME, "Year").send_keys(str(year))
        Select(driver.find_element(By.ID, "bMonth")).select_by_value(str(month))
        Select(driver.find_element(By.ID, "bDay")).select_by_value(str(day))
        Select(driver.find_element(By.ID, "bHour")).select_by_value(str(hour))

        # 送出表單
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        # 等待命盤主表格載入
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))

        # 找出包含「命宮」字樣的主要命盤表格
        tables = driver.find_elements(By.TAG_NAME, "table")
        main_table = None
        for t in tables:
            if "命宮" in t.text:
                main_table = t
                break

        if not main_table:
            raise Exception("找不到命盤主表格。")

        # 抓取命盤內容
        cells = main_table.find_elements(By.TAG_NAME, "td")
        chart_lines = []
        for c in cells:
            txt = c.text.strip()
            if not txt:
                continue
            # 去掉開頭數字（例如 07. / 8. / 09.）
            txt = re.sub(r'^\d+\.\s*', '', txt)
            chart_lines.append(txt)

        # 將各宮位以空行分隔成完整文字
        chart_text = "\n\n".join(chart_lines)
        return chart_text

    finally:
        driver.quit()

# ---------------------- Flask 主邏輯 ----------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result_html = ""
    raw_input = ""
    user_inputs = {"year": 1990, "month": 1, "day": 1, "hour": 0, "gender": "m", "cyear": 2025}

    if request.method == "POST":
        try:
            # 取得表單輸入
            user_inputs["year"] = int(request.form.get("year", 1990))
            user_inputs["month"] = int(request.form.get("month", 1))
            user_inputs["day"] = int(request.form.get("day", 1))
            user_inputs["hour"] = int(request.form.get("hour", 0))
            user_inputs["gender"] = request.form.get("gender", "m")
            user_inputs["cyear"] = int(request.form.get("cyear", 2025))

            # 爬取命盤資料
            raw_input = fetch_chart_selenium(
                user_inputs["year"],
                user_inputs["month"],
                user_inputs["day"],
                user_inputs["hour"],
                user_inputs["gender"]
            )

            # 設定流年
            mp.CYEAR = user_inputs["cyear"]

            # 命盤解析 + Markdown 轉 HTML
            data, col_order, year_stem = mp.parse_chart(raw_input)
            md = mp.render_markdown_table_v7(data, col_order, year_stem, raw_input)
            result_html = markdown.markdown(md, extensions=["tables"])

        except Exception as e:
            result_html = f"<p style='color:red;'>發生錯誤：{e}</p>"

    return render_template("index.html", result_html=result_html, raw_input=raw_input, inputs=user_inputs)

# ---------------------- 啟動伺服器 ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
