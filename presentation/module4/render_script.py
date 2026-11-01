import os
import subprocess
import pymupdf

# Create separate HTML files for each slide so we can take clean screenshots
with open('presentation/module4/render_slides.html', 'r', encoding='utf-8') as f:
    full_html = f.read()

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
pdf_doc = pymupdf.open()

for slide_num in [1, 2, 3]:
    start_tag = f"<div class='slide-container' id='slide{slide_num}'>"
    start_idx = full_html.find(start_tag)
    end_tag = "<!-- Slide" if slide_num < 3 else "</body>"
    end_idx = full_html.find(end_tag, start_idx + len(start_tag))
    slide_body = full_html[start_idx:end_idx].strip()
    if not slide_body.endswith('</div>'):
        slide_body = slide_body[:slide_body.rfind('</div>') + 6]
    
    slide_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 960px;
    height: 540px;
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #fff;
    font-family: 'Crimson Pro', 'Latin Modern Roman', 'Times New Roman', serif;
    color: #1F2933;
    -webkit-font-smoothing: antialiased;
  }}
  .slide-container {{
    width: 960px;
    height: 540px;
    background: #fff;
    padding: 22px 32px 18px 32px;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }}
  .header {{
    border-bottom: 1.5px solid #7B2D8E;
    padding-bottom: 4px;
    margin-bottom: 8px;
  }}
  .title {{
    font-size: 21px;
    font-weight: 700;
    color: #1F2933;
    line-height: 1.2;
  }}
  .subtitle {{
    font-size: 11px;
    color: #5F6B7A;
    margin-top: 2px;
  }}
  .content {{
    flex: 1;
    display: flex;
    gap: 22px;
    font-size: 12px;
    line-height: 1.35;
  }}
  .col {{ flex: 1; }}
  .col-50 {{ flex: 0 0 50%; }}
  .col-48 {{ flex: 0 0 48%; }}
  .col-52 {{ flex: 0 0 52%; }}
  .col-46 {{ flex: 0 0 46%; }}
  h4 {{
    color: #7B2D8E;
    font-size: 13px;
    font-weight: 700;
    margin-top: 4px;
    margin-bottom: 2px;
  }}
  ul, ol {{
    padding-left: 16px;
    margin-bottom: 4px;
  }}
  li {{ margin-bottom: 2px; }}
  .takeaway {{
    background: #F3EDF6;
    border: 1px solid #C9B6D3;
    border-radius: 3px;
    padding: 6px 10px;
    font-size: 10.5px;
    line-height: 1.35;
    color: #1F2933;
    margin-top: 4px;
  }}
  .footer {{
    display: flex;
    justify-content: flex-end;
    font-size: 10px;
    color: #8898AA;
    padding-top: 2px;
  }}
  .formula-box {{
    background: #FAF8FB;
    border-left: 2px solid #7B2D8E;
    padding: 3px 6px;
    margin: 3px 0;
    font-size: 11px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 10.5px;
    margin: 4px 0;
  }}
  th, td {{
    padding: 2.5px 4px;
    text-align: left;
  }}
  th {{
    border-top: 1.2px solid #1F2933;
    border-bottom: 1px solid #1F2933;
    font-weight: 600;
  }}
  tr.bottom-border td {{
    border-bottom: 1.2px solid #1F2933;
  }}
  img {{
    max-width: 100%;
    display: block;
    margin: 0 auto;
    object-fit: contain;
  }}
</style>
</head>
<body>
{slide_body}
</body>
</html>'''
    temp_html = f'presentation/module4/temp_slide_{slide_num}.html'
    out_png = f'presentation/module4/preview_page_{slide_num}.png'
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(slide_html)
    
    file_url = 'file:///' + os.path.abspath(temp_html).replace('\\', '/')
    cmd = [
        chrome_path,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--hide-scrollbars',
        '--window-size=960,540',
        f'--screenshot={os.path.abspath(out_png)}',
        file_url
    ]
    subprocess.run(cmd, capture_output=True, timeout=15)
    print(f'Rendered {out_png}, size:', os.path.getsize(out_png))

    # Add to preview PDF
    rect = pymupdf.Rect(0, 0, 453.54, 255.12)
    pdf_page = pdf_doc.new_page(width=453.54, height=255.12)
    pdf_page.insert_image(rect, filename=out_png)

pdf_doc.save('presentation/module4/module4_slides_preview.pdf')
print('Created presentation/module4/module4_slides_preview.pdf with', len(pdf_doc), 'pages')
