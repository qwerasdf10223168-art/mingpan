# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import mingpan_logic as mp
import markdown
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result_html = ""
    raw_input = ""
    # 預設分析年份（若 mingpan_logic 未設定 CYEAR 則設為今年）
    year_input = getattr(mp, "CYEAR", 2025) or 2025

    if request.method == 'POST':
        raw_input = request.form.get('info', '').strip()
        year_input = int(request.form.get('year', year_input or 2025))
        mp.CYEAR = year_input  # 更新全域年份

        if raw_input:
            try:
                # 解析命盤文字
                data, col_order, year_stem = mp.parse_chart(raw_input)

                # 若存在 v7 版本則使用，否則 fallback
                if hasattr(mp, "render_markdown_table_v7"):
                    md = mp.render_markdown_table_v7(data, col_order, year_stem, raw_input)
                else:
                    md = mp.render_markdown_table(data, col_order, year_stem)

                # 將 Markdown 轉為 HTML
                result_html = markdown.markdown(md, extensions=['tables'])
            except Exception as e:
                result_html = f"<p style='color:red;'>⚠️ 發生錯誤：{e}</p>"

    return render_template('index.html',
                           result=result_html,
                           raw_input=raw_input,
                           year=year_input)

if __name__ == '__main__':
    # ✅ Render 會自動給環境變數 PORT
    port = int(os.environ.get('PORT', 5000))
    # ✅ host 必須是 0.0.0.0 才能被 Render 偵測到
    app.run(host='0.0.0.0', port=port, debug=False)
