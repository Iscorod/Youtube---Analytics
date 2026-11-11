// Generador local de los CSV de demo. La versión Python equivalente se entrega aparte.
import fs from 'node:fs';
import path from 'node:path';
const OUT = path.join(import.meta.dirname, 'data'); fs.mkdirSync(OUT, {recursive:true});
let seed=7; function rand(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}
const START=new Date(Date.UTC(2026,7,13)), END=new Date(Date.UTC(2026,10,10));
const dates=[]; for(let d=new Date(START);d<=END;d.setUTCDate(d.getUTCDate()+1)) dates.push(new Date(d));
const channels=[['UC_TECHNORTE_DEMO','TechNorte',412000,118000,3.9,2.3,38],['UC_GADGETLAB_DEMO','GadgetLab',612000,164000,3.1,3.5,22],['UC_PIXELPRO_DEMO','PixelPro',298000,87000,4.6,1.4,55],['UC_CIRCUITOTV_DEMO','CircuitoTV',845000,201000,2.7,4.1,15]];
const titles=['Mi setup de 2026','Probé el móvil más barato del mercado','5 apps que uso a diario','Review honesta: ¿merece la pena?','Unboxing sorpresa','Tutorial: monta tu PC paso a paso','TOP 10 gadgets baratos','Qué pasó con esta marca','Respondo vuestras preguntas','Cómo editar vídeo gratis'];
const durations=[.5,.8,6,9,12,14,18,22,28,35], tagPool=['top 10','review','pc gaming','tutorial','unboxing','android','ofertas'];
function csv(name, rows){const keys=Object.keys(rows[0]); const esc=x=>{let s=String(x??'');return /[",\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};fs.writeFileSync(path.join(OUT,name), '\ufeff'+keys.join(',')+'\n'+rows.map(r=>keys.map(k=>esc(r[k])).join(',')).join('\n')+'\n','utf8');}
function dateStr(d){return d.toISOString().slice(0,10)}
function titleFlags(t){return {con_pregunta:+t.includes('?'),con_numero:+/[0-9]/.test(t),mas_30_caracteres:+(t.length>30),con_mayusculas:+/[A-Z]{4,}/.test(t)}}
const dowNames=['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];
csv('dim_fecha.csv',dates.map(d=>{let dow=d.getUTCDay(),jan=new Date(Date.UTC(d.getUTCFullYear(),0,1));return {fecha:dateStr(d),anio:d.getUTCFullYear(),mes_num:d.getUTCMonth()+1,mes:['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'][d.getUTCMonth()],dia:d.getUTCDate(),dia_semana_num:dow||7,dia_semana:dowNames[dow],semana_anio:Math.ceil((((d-jan)/86400000)+jan.getUTCDay()+1)/7),es_fin_semana:+(dow===0||dow===6)}}));
csv('dim_canal.csv',channels.map(c=>({channel_id:c[0],canal:c[1],suscriptores:c[2],vistas_medias_video:c[3],engagement_pct:c[4],videos_semana:c[5],pct_shorts:c[6]})));
const videos=[], tags=[], facts=[], channelFacts=[], heat=new Map();let vidNo=0;
for(let ci=0;ci<channels.length;ci++){
 const [cid,name,initial,mean]=channels[ci],count=ci===0?30:25;let pubs=[];
 for(let i=0;i<count;i++){let age=ci===0?3*i:Math.round(i*89/(count-1));let pub=new Date(END);pub.setUTCDate(pub.getUTCDate()-age);pubs.push(pub);}
 let subs=initial;
 for(let i=0;i<dates.length;i++){if(ci===0)subs+=Math.round(140+rand()*160+(i%17===3?500:0));else subs+=Math.round(15+rand()*50);channelFacts.push({fecha:dateStr(dates[i]),channel_id:cid,suscriptores:subs});}
 for(let ix=0;ix<pubs.length;ix++){
  const pub=pubs[ix],dur=ci===0?durations[ix%10]:[5,9,12,18,25][ix%5],short=dur<1;
  const title=ci===0?titles[ix%10]+(ix>9?` #${Math.floor(ix/10)+1}`:''):['Review de tecnología','Probamos este gadget','Guía completa de compra','¿Merece la pena?','Top productos del mes'][ix%5]+` #${Math.floor(ix/5)+1}`;
  const base=ci===0?(short?210000:(dur>=8&&dur<=20?150000:90000)):mean,total=Math.round(base*(.4+rand()*1.5)*(ci===0&&ix%7===0?2.2:1));
  const likes=Math.round(total*(.03+rand()*.04)), comments=Math.round(total*(.002+rand()*.004)), id=`SYN_${String(++vidNo).padStart(4,'0')}`;
  const hour=[8,12,16,18,20,21][Math.floor(rand()*6)],minute=[0,15,30,45][Math.floor(rand()*4)],franja=Math.floor(hour/4);
  const order=tagPool.map((x,i)=>[rand(),i]).sort((a,b)=>a[0]-b[0]).slice(0,3).map(x=>tagPool[x[1]]);
  const tramo=dur<1?'Shorts':dur<8?'1–8 min':dur<15?'8–15 min':dur<25?'15–25 min':'25+ min';
  const video={video_id:id,channel_id:cid,titulo:title,publicado:dateStr(pub),hora_publicacion:`${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')}:00`,duracion_min:dur,es_short:+short,tags:order.join(','),tramo_duracion:tramo,retencion_supuesta:dur<1?.9:dur<8?.5:dur<15?.42:dur<25?.35:.3,dia_semana:dowNames[pub.getUTCDay()],franja_horaria:`${String(franja*4).padStart(2,'0')}–${String((franja+1)*4).padStart(2,'0')}`,...titleFlags(title)};videos.push(video);order.forEach(tag=>tags.push({video_id:id,tag}));
  const ageMax=Math.round((END-pub)/86400000),weights=Array.from({length:ageMax+1},(_,age)=>Math.exp(-(short?.52:.14)*age)),norm=weights.reduce((a,b)=>a+b,0);let cum=0;
  weights.forEach((w,age)=>{let daily=Math.round(total*w/norm);if(age===ageMax)daily=total-cum;cum+=daily;facts.push({fecha:dateStr(new Date(pub.getTime()+age*86400000)),video_id:id,vistas_acum:cum,likes_acum:Math.round(likes*cum/total),comentarios_acum:Math.round(comments*cum/total)});});
  if(ci===0){const dow=(pub.getUTCDay()+6)%7,key=`${dow},${franja}`,factor=[.5,.5,1,1.4,1.9,1.5][franja],value=Math.round(40000*(1+.5*Math.sin(dow/6*Math.PI))*factor*(.8+rand()*.4));if(!heat.has(key))heat.set(key,[]);heat.get(key).push(value);}
 }
}
csv('dim_video.csv',videos);csv('dim_video_tag.csv',tags);csv('fact_video_diario.csv',facts);csv('fact_canal_diario.csv',channelFacts);
const dayNames=['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'];csv('fact_heatmap_publicacion.csv',Array.from({length:42},(_,i)=>{let d=Math.floor(i/6),b=i%6,a=heat.get(`${d},${b}`)||[];return {dia_semana_num:d+1,dia_semana:dayNames[d],franja_num:b,franja:`${String(b*4).padStart(2,'0')}–${String((b+1)*4).padStart(2,'0')}`,vistas_7d_medias:Math.round(a.reduce((x,y)=>x+y,0)/Math.max(a.length,1))}}));
csv('fact_sentimiento.csv',[...['Positivo','Neutro','Negativo'].flatMap((s,i)=>['precio','batería','cámara','garantía','comparativa'].map(tema=>({channel_id:channels[0][0],sentimiento:s,n:Math.round(5000*[.68,.22,.10][i]/5),tema})))]);
csv('rasgo_titulo.csv',['Con ?','Con número','Más de 30 car.','Con MAYÚSCULAS'].map((rasgo,i)=>({rasgo,orden:i+1})));
console.log(`CSV reproducibles escritos en ${OUT}; vídeos ${videos.length}, snapshots ${facts.length}.`);
