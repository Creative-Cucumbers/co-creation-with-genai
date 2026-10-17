const host=document.getElementById('slides');
let slides=[],current=0;
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function fit(){document.documentElement.style.setProperty('--scale',Math.min(innerWidth/1600,innerHeight/900));}
function createSlide(data,continued=false){
 const s=document.createElement('section');s.className='slide active '+data.kind;
 s.dataset.chapter=data.chapter;
 const time=data.title.match(/（[^）]*分[^）]*）$/)?.[0]||'';
 const title=data.title.replace(/（[^）]*分[^）]*）$/,'');
 s.innerHTML=`<header class="slide-header"><p class="subtitle">${esc((data.category||('第5回｜'+(data.chapter?chapterNames[data.chapter]:'2026年10月23日'))).replace(/（.*$/,''))}${time?'　'+esc(time):''}${continued?'　｜ 続き':''}</p><h1 class="slide-title">${esc(title)}</h1>${data.badge?`<span class="badge">${esc(data.badge)}</span>`:''}</header><div class="content"></div>`;
 host.append(s);slides.push(s);return s;
}
function build(){
 host.innerHTML='';slides=[];
 for(const data of sourceSlides){
  let s=createSlide(data);
  if(data.kind==='divider'){
   s.querySelector('.content').innerHTML=`<p class="divider-number">SECTION ${String(data.chapter).padStart(2,'0')}</p><p style="font-size:26px">次のページで、今日の道順を確認します。</p>`;continue;
  }
  if(data.kind==='roadmap'){s.classList.add('wide');continue;}
  const wide=data.cards.some(x=>/table-card|diagram/.test(x)||(data.kind!=='cover'&&/image-card/.test(x))||(/<pre>/.test(x)&&(x.replace(/<[^>]+>/g,'').length>240||x.split('\n').length>6)));
  if(wide)s.classList.add('wide');
  const makeColumns=()=>{const c=s.querySelector('.content');c.innerHTML='<div class="column"></div>'+(wide?'':'<div class="column"></div>');return [...c.children];};
  let cols=makeColumns(),col=0;
  // Measure all layout at native canvas scale, independent of viewport.
  for(const markup of data.cards){
   const template=document.createElement('template');template.innerHTML=markup;const node=template.content.firstElementChild;
   let target=cols[col];target.append(node);
   if(target.scrollHeight>target.clientHeight+1 && target.children.length>1){
    node.remove();col++;
    if(col>=cols.length){s.classList.remove('active');s=createSlide(data,true);if(wide)s.classList.add('wide');cols=makeColumns();col=0;}
    cols[col].append(node);
   }
  }
  s.classList.remove('active');
 }
 // Install stable URLs only after continuation pages have been created.
 slides.forEach((s,i)=>{s.id=`slide-${i+1}`;s.querySelector('h1').id=`title-${i+1}`;s.setAttribute('aria-labelledby',`title-${i+1}`);});
 const roadmapData=sourceSlides.filter(x=>x.kind==='roadmap');
 const routeTimes=['3限・前半｜0〜23分','3限・前半｜23〜50分','3限・後半｜50〜100分','4限・前半｜100〜150分','4限・後半｜150〜193分','4限・後半｜193〜200分'];
 for(const s of slides.filter(x=>x.classList.contains('roadmap'))){
  const currentChapter=Number(s.dataset.chapter);
  const source=roadmapData.find(d=>d.chapter===currentChapter);
  const nextStep=source?.cards.find(c=>c.includes('次にすること：'))||'';
  const group=(start,end,label)=>`<div class="roadmap-group"><h3>${label}</h3>`+Array.from({length:end-start+1},(_,j)=>{
   const n=start+j,index=slides.findIndex(x=>x.classList.contains('divider')&&Number(x.dataset.chapter)===n);
   return `<a class="roadmap-item ${n===currentChapter?'current':''}" href="#slide-${index+1}" ${n===currentChapter?'aria-current="step"':''}><b>${String(n).padStart(2,'0')}　${esc(chapterNames[n].replace(/（.*$/,''))}${n===currentChapter?'（いまここ）':''}</b><small>${routeTimes[n-1]}</small></a>`;
  }).join('')+'</div>';
  s.querySelector('.content').innerHTML=`<div class="roadmap-grid">${group(1,3,'3限｜100分')}${group(4,6,'4限｜100分')}</div><p class="route-note">左を上から下へ → 休憩 → 右を上から下へ。投稿時間は各演習に含みます。</p>${nextStep.replace(/class="card [^"]*"/,'class="route-note"')}`;
 }
 document.getElementById('total').textContent=slides.length;
 fromHash();fit();
}
function showSlide(n){
 current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));
 document.getElementById('page').textContent=current+1;
 document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===slides.length-1;
 const ch=slides[current].dataset.chapter;
 document.getElementById('course').textContent='2026 / 第5回'+(Number(ch)?` · ${String(ch).padStart(2,'0')} / 6　${chapterNames[ch].replace(/（.*$/,'')}`:' AIとつくるWebアプリ②');
 document.querySelector('.progress').style.width=`${(current+1)/slides.length*100}%`;
 history.replaceState(null,'',`#${slides[current].id}`);
}
function fromHash(){const m=location.hash.match(/^#slide-(\d+)$/);showSlide(m?Number(m[1])-1:0);}
document.getElementById('prev').addEventListener('click',()=>showSlide(current-1));
document.getElementById('next').addEventListener('click',()=>showSlide(current+1));
document.getElementById('toc').addEventListener('click',()=>{const ch=slides[current].dataset.chapter;const n=slides.findIndex(s=>s.classList.contains('roadmap')&&s.dataset.chapter===ch);showSlide(n<0?slides.findIndex(s=>s.classList.contains('roadmap')):n);});
document.addEventListener('click',e=>{const a=e.target.closest('.roadmap-item');if(a){e.preventDefault();showSlide(Number(a.hash.slice(7))-1);}});
document.addEventListener('keydown',e=>{if(e.defaultPrevented||e.altKey||e.ctrlKey||e.metaKey||e.shiftKey||e.target.closest('a,button,summary,input,textarea,select,[contenteditable]'))return;if(['ArrowRight','ArrowLeft',' '].includes(e.key)){e.preventDefault();showSlide(current+(e.key==='ArrowLeft'?-1:1));}});
window.addEventListener('resize',fit);window.addEventListener('hashchange',fromHash);
document.fonts.ready.then(()=>{document.documentElement.style.setProperty('--scale',1);build();window.slidesReady=true;});
