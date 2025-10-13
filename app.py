from flask import Flask, render_template, request
import mingpan_logic as mp
import markdown
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    result_html = ""
    raw_input = ""
    year_input = mp.CYEAR if hasattr(mp, "CYEAR") else 2025
    if request.method == 'POST':
        raw_input = request.form.get('info', '')
        year_input = int(request.form.get('year', year_input or 2025))
        # Set analysis year in module
        mp.CYEAR = year_input
        # Parse and analyze
        data, col_order, year_stem = mp.parse_chart(raw_input)
        md = mp.render_markdown_table_v7(data, col_order, year_stem, raw_input)
        # Convert markdown (tables) to HTML
        result_html = markdown.markdown(md, extensions=['tables'])
    return render_template('index.html', result=result_html, raw_input=raw_input, year=year_input)

if __name__ == '__main__':
    # ✅ Render 會自動給一個環境變數 PORT
    port = int(os.environ.get('PORT', 5000))
    # ✅ host 必須是 0.0.0.0 才能被 Render 偵測到
    app.run(host='0.0.0.0', port=port, debug=False)
