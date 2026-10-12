const fs=require('fs');
const {ExternalHyperlink,Document,Packer,Paragraph,TextRun,ImageRun,Table,TableRow,TableCell,WidthType,ShadingType,BorderStyle,AlignmentType,HeadingLevel,LevelFormat,Footer,PageNumber}=require('docx');
const MD=process.argv[2]||'/home/claude/worlds/artifact/proj/bit-tbd-worlds-t1-article.md'; const OUTF=process.argv[3]||'/mnt/user-data/outputs/bit-tbd-worlds-t1-draft.docx';
const FIG={1:'fig-tbd-big-worlds-elo-2026.png',2:'fig-tbd-if-worlds-t1.png',3:'fig-tbd-true-formats.png',odds:'fig-tbd-odds-2026.png'};
const FIGDIR='/home/claude/worlds/artifact/';
const ACC='C1440E', FONT='Georgia', SANS='Arial';
const BOX={verdict:{fill:'FBEFE9',rule:ACC},numbers:{fill:'FBEFE9',rule:ACC},callout:{fill:'EEF3F6',rule:'5B8FA8'},lit:{fill:'EDF2EE',rule:'2E6B57'},receipts:{fill:'F0F3F5',rule:'2F4F5F'},predictions:{fill:'EEF3F6',rule:'5B8FA8'}};
const W=9026; // A4 text width, 1in margins

function runs(text,base={}){
  const out=[]; const re=/(\[[^\]]+\]\([^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[AUTHOR[^\]]*\])/g; let i=0,m;
  while((m=re.exec(text))){ if(m.index>i) out.push(new TextRun({text:text.slice(i,m.index),...base}));
    const t=m[0];
    if(/^\[[^\]]+\]\(/.test(t)){ const mm=t.match(/^\[([^\]]+)\]\(([^)]+)\)$/); out.push(new ExternalHyperlink({link:mm[2],children:[new TextRun({text:mm[1],style:'Hyperlink',color:'C1440E',underline:{},...base})]})); }
    else if(t.startsWith('**')) out.push(new TextRun({text:t.slice(2,-2),bold:true,...base}));
    else if(t.startsWith('`')) out.push(new TextRun({text:t.slice(1,-1),font:'Courier New',...base}));
    else if(t.startsWith('[AUTHOR')) out.push(new TextRun({text:t,highlight:'yellow',...base}));
    else out.push(new TextRun({text:t.slice(1,-1),italics:true,...base}));
    i=m.index+t.length; }
  if(i<text.length) out.push(new TextRun({text:text.slice(i),...base}));
  return out;
}
const P=(text,opt={})=>new Paragraph({children:runs(text,opt.run||{}),spacing:{after:140,line:300},...(opt.p||{})});
function bulletPara(line,bodyText=false){
  const m=line.match(/^(\s*)- (.*)$/); const lvl=Math.floor(m[1].length/2);
  return new Paragraph({children:runs(m[2],bodyText?{}:{size:20,font:SANS}),numbering:{reference:'b',level:Math.min(lvl,2)},spacing:bodyText?{after:100,line:300}:{after:60}});
}
function box(kind,lines){
  const st=BOX[kind]; const kids=[];
  for(const l of lines){
    if(!l.trim()) continue;
    const im=l.trim().match(/^\{\{FIG:(\w+)\}\}$/); if(im){ kids.push(imgPara(im[1],5.9)); continue; }
    if(/^\s*- /.test(l)) kids.push(bulletPara(l));
    else if(/^\*\*[A-Z0-9 &#.:—-]+\*\*$/.test(l.trim())||/^\*\*BIT/.test(l.trim())) kids.push(new Paragraph({children:[new TextRun({text:l.trim().replace(/\*\*/g,''),bold:true,size:18,font:SANS,color:st.rule,characterSpacing:30})],spacing:{after:100}}));
    else kids.push(new Paragraph({children:runs(l.trim(),{size:20,font:SANS}),spacing:{after:80}}));
  }
  const nb={style:BorderStyle.NONE,size:0,color:'FFFFFF'};
  return new Table({width:{size:W,type:WidthType.DXA},columnWidths:[W],rows:[new TableRow({children:[new TableCell({width:{size:W,type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:st.fill,color:'auto'},margins:{top:160,bottom:120,left:240,right:240},borders:{top:nb,bottom:nb,right:nb,left:{style:BorderStyle.SINGLE,size:24,color:st.rule}},children:kids})]})]});
}
function imgPara(key,inch){
  const IT=/-it\.md$|articolo-it/.test(process.argv[2]||''); const f=IT?('/mnt/user-data/outputs/'+FIG[key].replace('.png','-it.png')):FIGDIR+FIG[key]; const buf=fs.readFileSync(f);
  const w=buf.readUInt32BE(16),h=buf.readUInt32BE(20); const pw=inch*96;
  return new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:80,after:120},children:[new ImageRun({type:'png',data:buf,transformation:{width:pw,height:pw*h/w},altText:{title:key,description:key,name:FIG[key]}})]});
}
function figure(n,caption){
  const IT=/-it\.md$|articolo-it/.test(process.argv[2]||''); const f=IT?('/mnt/user-data/outputs/'+FIG[n].replace('.png','-it.png')):FIGDIR+FIG[n]; const buf=fs.readFileSync(f);
  const w=buf.readUInt32BE(16),h=buf.readUInt32BE(20); const pw=4.4*96;
  return [new Paragraph({alignment:AlignmentType.CENTER,keepNext:true,spacing:{before:200,after:100},children:[new ImageRun({type:'png',data:buf,transformation:{width:pw,height:pw*h/w},altText:{title:`Figure ${n}`,description:caption.slice(0,200),name:FIG[n]}})]}),
    new Paragraph({children:runs(caption,{size:18,font:SANS,color:'444444'}),spacing:{after:240}})];
}
const md=fs.readFileSync(MD,'utf8').replace(/<!--[\s\S]*?-->/g,'').split('\n');
const body=[]; let i=0;
while(i<md.length){
  let l=md[i];
  if(!l.trim()){i++;continue;}
  if(l.startsWith('>')){ const blk=[]; while(i<md.length&&md[i].startsWith('>')){blk.push(md[i].replace(/^> ?/,''));i++;}
    const h=blk[0];
    const fm=h.match(/^\*\*(Figure|Figura) (\d)\.\*\* (.*)/);
    if(fm){ body.push(...figure(+fm[2],'**'+fm[1]+' '+fm[2]+'.** '+fm[3])); continue; }
    const kind=/VERDICT|VERDETTO/.test(h)?'verdict':/NUMBERS|I NUMERI/.test(h)?'numbers':/LITERATURE|LETTERATURA/.test(h)?'lit':/PIPELINE|CARDS ON THE TABLE|CARTE IN TAVOLA/.test(h)?'receipts':/PREDICTIONS|PREVISIONI/.test(h)?'predictions':'callout';
    // THE NUMBERS lines: "**5** — text"
    body.push(box(kind,blk)); body.push(new Paragraph({spacing:{after:120},children:[]})); continue; }
  if(l.startsWith('|')){ const tl=[]; while(i<md.length&&md[i].startsWith('|')){tl.push(md[i]);i++;}
    const cells=tl.filter(x=>!/^\|[-| ]+\|$/.test(x)).map(x=>x.slice(1,-1).split('|').map(c=>c.trim()));
    const nc=cells[0].length; const cw=[2050,1550,560]; const rest=Math.floor((W-cw.reduce((a,b)=>a+b,0))/(nc-3)); for(let k=3;k<nc;k++) cw.push(rest);
    cw[nc-1]+=W-cw.reduce((a,b)=>a+b,0);
    const bd={style:BorderStyle.SINGLE,size:4,color:'DDDDDD'};
    body.push(new Table({width:{size:W,type:WidthType.DXA},columnWidths:cw,rows:cells.map((r,ri)=>new TableRow({tableHeader:ri===0,children:r.map((c,ci)=>new TableCell({width:{size:cw[ci],type:WidthType.DXA},margins:{top:40,bottom:40,left:80,right:80},borders:{top:bd,bottom:bd,left:{style:BorderStyle.NONE,size:0,color:'FFFFFF'},right:{style:BorderStyle.NONE,size:0,color:'FFFFFF'}},shading:ri===0?{type:ShadingType.CLEAR,fill:'F3F1EE',color:'auto'}:(r[0]==='T1'?{type:ShadingType.CLEAR,fill:'FBEFE9',color:'auto'}:undefined),
      children:[new Paragraph({alignment:ci>=2?AlignmentType.RIGHT:AlignmentType.LEFT,children:[new TextRun({text:c,font:SANS,size:16,bold:ri===0||r[0]==='T1',color:r[0]==='T1'&&ri>0?ACC:'222222'})]})]}))}))}));
    body.push(new Paragraph({spacing:{after:200},children:[]})); continue; }
  if(l==='BIG IF TRUE'){ body.push(new Paragraph({children:[new TextRun({text:'BIG IF TRUE',bold:true,font:SANS,size:18,color:ACC,characterSpacing:60})],spacing:{after:80}})); i++; continue; }
  if(l.startsWith('# ')){ body.push(new Paragraph({heading:HeadingLevel.TITLE,children:[new TextRun({text:l.slice(2)})],spacing:{after:240}})); i++; continue; }
  if(l.startsWith('## ')){ body.push(new Paragraph({heading:HeadingLevel.HEADING_1,children:runs(l.slice(3)),spacing:{before:320,after:160}})); i++; continue; }
  if(/^\s*- /.test(l)){ while(i<md.length&&/^\s*- /.test(md[i])){ body.push(bulletPara(md[i],true)); i++; } continue; }
  if(/^\*[^*].*\*$/.test(l.trim())){ body.push(P(l.trim().slice(1,-1),{run:{italics:true,color:'555555'}})); i++; continue; }
  body.push(P(l)); i++;
}
const doc=new Document({
  creator:'Riccardo Gallotti',title:'T1: the Korean esports team that only gets better in October',
  styles:{default:{document:{run:{font:FONT,size:22}}},paragraphStyles:[
    {id:'Title',name:'Title',basedOn:'Normal',run:{font:FONT,size:44,bold:true}},
    {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,run:{font:FONT,size:30,bold:true,color:'1D1B19'},paragraph:{outlineLevel:0}}]},
  numbering:{config:[{reference:'b',levels:[0,1,2].map(k=>({level:k,format:LevelFormat.BULLET,text:['•','–','·'][k],alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:360*(k+1),hanging:240}}}}))}]},
  sections:[{properties:{page:{margin:{top:1440,bottom:1440,left:1440,right:1440}}},
    footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:'BIG IF TRUE · draft · ',size:16,font:SANS,color:'888888'}),new TextRun({children:[PageNumber.CURRENT],size:16,font:SANS,color:'888888'})]})]})},
    children:body}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync(OUTF,b);console.log('ok',b.length)});
