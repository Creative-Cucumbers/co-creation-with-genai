"""Build the lecture slides from readme.md; run with Python 3 (standard library only)."""
from pathlib import Path
import re, html, json
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'readme.md').read_text()
clean=re.sub(r'<!--[\s\S]*?-->','',src)
def inline(s):
 s=html.escape(s)
 s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
 s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',s)
 return s.replace('&lt;br /&gt;','<br>')
def card(body,kind=''):return f'<div class="card {kind}">{body}</div>'
def diagram(code):
 if 'PCのマイク' in code:items=['PCのマイク','音声取得<br>MediaDevices API','音声解析<br>Web Audio API','画面に波形を描く']
 elif '処理：' in code:items=['入力：音の情報','処理：音が入っている間<br>大きさを増やす','出力：風船の大きさが変わる']
 else:items=['Webアプリ<br>リクエストを送る','外部API<br>データの窓口','外部サービスのデータ']
 return card('<div class="flow">'+'<span class="arrow">→</span>'.join('<div>'+x+'</div>' for x in items)+'</div>'+('<p class="caption">取得したデータは、外部APIからWebアプリへ返されます。</p>' if '外部API' in code else ''),'diagram')
def blocks(md):
 lines=md.strip().splitlines();out=[];i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('```'):
   lang=line[3:];code=[];i+=1
   while i<len(lines) and not lines[i].startswith('```'):code.append(lines[i]);i+=1
   i+=1
   if lang=='mermaid':out.append(diagram('\n'.join(code)));continue
   # Keep each prompt together when possible. Long prompts continue on another page.
   for j in range(0,len(code),10):
    title=('JSONの例' if lang=='json' else '入力・投稿の例')+('（続き）' if j else '')
    out.append(card(f'<h3>{title}</h3><pre>{html.escape(chr(10).join(code[j:j+10]))}</pre>','prompt'))
   continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    row=[x.strip() for x in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r'[:\- ]+',x) for x in row):rows.append(row)
    i+=1
   if rows and rows[0][0]=='回数':
    rows=[['回数・日程','テーマ','担当講師']]+[[rows[0][j].replace('<br />',' '),rows[1][j],rows[2][j]] for j in range(1,len(rows[0]))]
   out.append(card('<table>'+''.join('<tr>'+''.join(f'<{"th" if n==0 else "td"}>{inline(x)}</{"th" if n==0 else "td"}>' for x in r)+'</tr>' for n,r in enumerate(rows))+'</table>','table-card'));continue
  img=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
  if img:
   alt,url=img.groups();out.append(card(f'<figure><a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer"><img src="{html.escape(url)}" alt="{html.escape(alt)}"></a><figcaption>{html.escape(alt)}</figcaption></figure>','image-card'));i+=1;continue
  if re.match(r'^(- |\d+\. )',line):
   ordered=bool(re.match(r'^\d+\.',line));items=[]
   while i<len(lines) and re.match(r'^(- |\d+\. )',lines[i].strip()):
    items.append(re.sub(r'^(- |\d+\. )','',lines[i].strip()));i+=1
   tag='ol' if ordered else 'ul';out.append(card(f'<{tag}>'+''.join('<li>'+inline(x)+'</li>' for x in items)+f'</{tag}>'));continue
  paras=[line];i+=1
  while i<len(lines) and lines[i].strip() and not re.match(r'^(\||```|!\[|- |\d+\. |#)',lines[i].strip()):paras.append(lines[i].strip());i+=1
  text=' '.join(paras)
  if re.fullmatch(r'\*\*(演習|課題|クイズ|宿題)｜.*\*\*',text):continue
  out.append(card('<p>'+inline(text)+'</p>','highlight' if text.startswith('**投稿するもの**') or text.startswith('**完了の目安**') else ''))
 # Keep labels with their content and captions with their figures.
 merged=[];j=0
 while j<len(out):
  label=re.fullmatch(r'<div class="card "><p>(.*?)</p></div>',out[j])
  text=re.sub('<[^>]+>','',label[1]) if label else ''
  if label and text.startswith('図：') and merged and ('figure' in merged[-1] or 'diagram' in merged[-1]):
   merged[-1]=merged[-1][:-6]+'<p class="caption">'+label[1]+'</p></div>';j+=1;continue
  if label and len(text)<65 and (text.endswith('：') or label[1].startswith('<strong>')) and j+1<len(out):
   title=label[1].replace('<strong>','').replace('</strong>','').rstrip('：')
   nxt=out[j+1]
   if '<h3>' in nxt:nxt=re.sub(r'<h3>.*?</h3>','<h3>'+title+'</h3>',nxt,count=1)
   else:nxt=re.sub(r'(<div class="card [^"]*">)',r'\1<h3>'+title+'</h3>',nxt,count=1)
   merged.append(nxt);j+=2;continue
  merged.append(out[j]);j+=1
 return merged
chapters={int(n):title for n,title in re.findall(r'^## (\d+)\. (.+)$',clean,re.M)}
sections=[]
current=0;category=''
for match in re.finditer(r'^(## |### |#### )(.+)$',clean,re.M):
 level,title=match.groups()
 if level=='## ':
  m=re.match(r'(\d+)\. ',title)
  if m:category='';current=int(m[1]);sections.append(dict(title=title,chapter=current,kind='divider',cards=[]))
 elif level=='### ':category=title
 elif level=='#### ':
  end=re.search(r'^#{2,4} ',clean[match.end():],re.M)
  content=clean[match.end():match.end()+end.start() if end else len(clean)]
  badge=re.search(r'^\*\*((?:演習|課題|クイズ|宿題)｜.*?)\*\*',content,re.M)
  sections.append(dict(title=title,chapter=current,category=category,kind='roadmap' if title.startswith('今日の道順') else 'normal',badge=badge[1] if badge else '',cards=blocks(content)))
# The opening course schedule and illustration are also part of the README.
intro=clean[:clean.index('## 3限')]
schedule=re.search(r'(\| 回数[\s\S]+?)\n\n### 目次',intro)[1]
sections=[dict(title='作れるWebアプリの幅を広げよう！',chapter=0,kind='cover',cards=[card('<h3>入力・表現・データ</h3><p>何を受け取る？<br>どう反応する？ どう見せる？<br>どんな情報を使う？</p><p>2026年10月23日｜第5回<br>プログラミング演習</p>'),card('<figure><img src="images/a.png" alt="Webアプリの画面やクラウド、操作をイメージしたイラスト"><figcaption>既存の授業資料に収録された生成AIによるイラスト</figcaption></figure>','image-card')]),dict(title='全7回の授業スケジュール',chapter=0,kind='normal',cards=blocks(schedule))]+sections
# Keep teacher notes and answers in HTML comments, never in slide contents.
notes='\n'.join(re.findall(r'<!--[\s\S]*?-->',src))
style='''
:root{--ink:#242424;--muted:#666;--blue:#004898;--panel:#f2f3f4;--highlight:#edf3f9;--line:#d9dde2;--paper:#fff}
*{box-sizing:border-box;margin:0}body{font-family:"Helvetica Neue",Arial,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;background:#e6e8eb;color:var(--ink);overflow:hidden;height:100dvh}.canvas{position:absolute;left:50%;top:50%;width:1600px;height:900px;transform:translate(-50%,-50%) scale(var(--scale,1));background:white;box-shadow:0 12px 55px #0001}.slide{position:absolute;inset:0;display:none;padding:70px 80px 100px}.slide.active{display:flex;flex-direction:column}.slide-header{border-bottom:2px solid var(--ink);padding-bottom:24px;margin-bottom:28px;flex:none}.subtitle{font-size:20px;color:var(--muted);line-height:1.4;margin-bottom:8px}.slide-title{font-size:44px;line-height:1.4;letter-spacing:-.035em}.content{flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:stretch;font-size:23px;line-height:1.7}.column{display:flex;flex-direction:column;gap:18px;min-width:0;min-height:0}.wide .content{grid-template-columns:1fr}.card{background:var(--panel);border-top:3px solid var(--line);padding:22px 28px;flex:none;min-width:0}.highlight,.prompt{background:var(--highlight);border-color:var(--blue)}h3{font-size:26px;line-height:1.4;margin-bottom:12px}p+p{margin-top:12px}pre{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65}code{overflow-wrap:anywhere}ul,ol{padding-left:1.4em}li+li{margin-top:8px}a{color:var(--blue);text-decoration:underline;text-underline-offset:4px;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:21px;line-height:1.6}td,th{padding:10px 16px;border:1px solid var(--line);text-align:left}th{background:var(--blue);color:white}th:first-child{white-space:nowrap}.table-card{padding:0;border:0}.image-card{background:white;border:0;padding:0}figure img{display:block;width:100%;height:350px;object-fit:contain}.wide figure img{height:430px}.caption,figcaption{font-size:17px;color:var(--muted);line-height:1.6;margin-top:10px}.flow{display:flex;align-items:center;gap:12px}.flow>div{flex:1;text-align:center;padding:20px 12px;background:var(--highlight);border-top:3px solid var(--blue)}.flow .arrow{color:var(--blue);font-size:28px}.diagram{background:white;border:0;padding:0}.badge{display:inline-block;border:1px solid var(--blue);background:var(--highlight);color:var(--blue);font-size:18px;line-height:1.5;padding:4px 10px;margin-top:10px}.course{position:absolute;top:28px;left:80px;font-size:15px;color:var(--blue);font-weight:bold}.counter{position:absolute;top:28px;right:80px;font-size:16px;color:var(--muted)}footer{position:absolute;bottom:34px;left:80px;font-size:15px;color:var(--muted)}nav{position:absolute;bottom:22px;right:80px;display:flex;gap:12px}button{font:inherit;font-size:18px;background:white;border:1px solid var(--line);padding:12px 22px;cursor:pointer}button:disabled{color:#aaa;cursor:default}button:hover:not(:disabled){background:var(--highlight)}:focus-visible{outline:3px solid var(--blue);outline-offset:5px}.progress{position:absolute;bottom:0;left:0;height:4px;background:var(--blue)}.divider .slide-title{font-size:64px;max-width:1300px}.divider .slide-header{border:0;margin-top:120px}.divider .content{display:block}.divider-number{font-size:24px;font-weight:bold;color:var(--blue);margin-bottom:30px}.cover .slide-title{font-size:64px}.cover figure img{height:380px}.roadmap-grid{display:grid;grid-template-columns:1fr 1fr;gap:36px;width:100%;font-size:22px;line-height:1.55}.roadmap-group h3{color:var(--blue);margin-bottom:14px}.roadmap-item{display:block;background:var(--panel);border:1px solid var(--line);padding:15px 20px;margin-bottom:12px;text-decoration:none;color:var(--ink)}.roadmap-item.current{background:var(--highlight);border-left:5px solid var(--blue)}.roadmap-item b{color:var(--blue)}.roadmap-item small{display:block;color:var(--muted);font-size:18px;margin-top:4px}.roadmap .content{display:block}.route-note{margin-top:8px;font-size:20px;color:var(--muted)}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}@media print{body{overflow:visible}.canvas{position:static;transform:none;height:auto;box-shadow:none}.slide,.slide.active{position:relative;display:flex;height:900px;break-after:page}nav,footer,.course,.counter,.progress{display:none}@page{size:1600px 900px;margin:0}}
'''
script=Path(__file__).with_name('slides-runtime.js').read_text()
page='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第5回｜AIを活用したアプリ生成②</title><style>'+style+'</style></head><body><main class="canvas" aria-label="第5回 講義スライド"><div class="course" id="course"></div><div class="counter" role="status" aria-live="polite"><span id="page">1</span> / <span id="total">'+str(len(sections))+'</span></div><div id="slides"></div><footer>プログラミング演習｜第5回 · <a href="readme.md">詳しい授業資料</a></footer><nav aria-label="スライド操作"><button id="toc">目次</button><button id="prev">◀ 前へ</button><button id="next">次へ ▶</button></nav><div class="progress"></div></main><script>const sourceSlides='+json.dumps(sections,ensure_ascii=False)+';const chapterNames='+json.dumps(chapters,ensure_ascii=False)+';\n'+script+'</script>\n'+notes+'\n</body></html>'
(ROOT/'index.html').write_text(page)
print(f'Built {len(sections)} source slides; pagination adapts to measured content at 1600 × 900.')
