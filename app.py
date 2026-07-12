import os, json, math, re, io
from flask import Flask, request, jsonify, send_file, render_template_string
from anthropic import Anthropic

app = Flask(__name__)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Eleva</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;background:#F0F4F8;min-height:100vh}
header{background:#1A4A8B;color:#fff;padding:18px 24px;display:flex;align-items:center;justify-content:space-between}
.logo{font-size:22px;font-weight:800;letter-spacing:2px}
.logo-sub{font-size:11px;opacity:.85;margin-top:2px}
.container{max-width:640px;margin:32px auto;padding:0 16px 60px}
.card{background:#fff;border-radius:14px;padding:28px 24px;box-shadow:0 2px 16px rgba(0,0,0,.08)}
.titulo{font-size:15px;font-weight:700;color:#1A4A8B;border-left:4px solid #1A4A8B;padding-left:12px;margin-bottom:22px}
.campo{margin-bottom:16px}
.campo label{display:block;font-size:12px;font-weight:600;color:#555;margin-bottom:5px}
.campo input{width:100%;padding:11px 14px;border:1.5px solid #D0D5DD;border-radius:8px;font-size:15px;color:#222;background:#FAFAFA;outline:none}
.campo input:focus{border-color:#1A4A8B}
.upload{border:2px dashed #C0CCDA;border-radius:10px;padding:24px;text-align:center;cursor:pointer;background:#F8FAFC}
.upload.ok{border-color:#1A4A8B;border-style:solid;background:#EEF3FB}
.btn{width:100%;background:#1A4A8B;color:#fff;border:none;padding:14px;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer;margin-top:8px}
.btn:disabled{background:#8BA7CC;cursor:not-allowed}
.btn2{width:100%;background:#fff;color:#1A4A8B;border:2px solid #1A4A8B;padding:12px;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;margin-top:12px;display:none}
.log{margin-top:20px;display:none;background:#F8FAFC;border:1px solid #D0DCF0;border-radius:10px;padding:14px}
.log-item{font-size:13px;color:#555;padding:5px 0;border-bottom:1px solid #F0F0F0}
.resultado{margin-top:20px;display:none}
.res-header{background:#1A4A8B;color:#fff;border-radius:10px 10px 0 0;padding:14px 16px}
.res-nome{font-size:14px;font-weight:700}
.res-sub{font-size:11px;opacity:.85;margin-top:3px}
table{width:100%;border-collapse:collapse}
th{background:#EEF3FB;font-size:11px;font-weight:600;color:#1A4A8B;padding:8px 12px;text-align:left;border-bottom:1px solid #D0DCF0}
td{padding:9px 12px;font-size:13px;border-bottom:1px solid #F0F0F0}
.linha-alt td{background:#FFF3E0;color:#B45309;font-weight:600}
.linha-def td{background:#FEF2F2;color:#B91C1C;font-weight:600}
.linha-rec td{background:#1A4A8B;color:#fff;font-weight:700;font-size:14px}
.tabela-wrap{border:1px solid #D0DCF0;border-top:none;border-radius:0 0 10px 10px;overflow:hidden}
.mem{margin-top:14px;background:#F8FAFC;border:1px solid #D0DCF0;border-radius:10px;padding:14px}
.mem-titulo{font-size:11px;font-weight:600;color:#1A4A8B;text-transform:uppercase;margin-bottom:8px}
.mem-linha{display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px dashed #E0E7EF;color:#555}
.mem-linha:last-child{border-bottom:none;font-weight:700;color:#1A4A8B;font-size:13px}
.erro{background:#FEE2E2;border:1px solid #FECACA;border-radius:8px;padding:12px;color:#B91C1C;font-size:13px;margin-top:14px;display:none}
</style>
</head>
<body>
<header>
<div><div class="logo">ELEVA</div><div class="logo-sub">Corretoria &amp; Consultoria de Seguros</div></div>
<div style="font-size:11px;opacity:.85;text-align:right">SUSEP: 252168625<br>Análise de Cobertura</div>
</header>
<div class="container">
<div class="card">
<div class="titulo">Nova análise de cobertura</div>
<div class="campo">
<label>CNPJ do condomínio</label>
<input type="text" id="cnpj" placeholder="00.000.000/0001-00" maxlength="18" oninput="mascCNPJ(this)">
</div>
<div class="campo">
<label>Apólice de seguro (PDF)</label>
<div class="upload" id="zona" onclick="document.getElementById('arq').click()">
<div style="font-size:32px">📄</div>
<div style="font-size:13px;color:#666;margin-top:6px">Toque para selecionar o PDF da apólice</div>
<div id="nome-arq" style="font-size:13px;font-weight:600;color:#1A4A8B;margin-top:4px;display:none"></div>
</div>
<input type="file" id="arq" accept=".pdf" style="display:none" onchange="selecionarArq(this)">
</div>
<div class="campo">
<label>Valor segurado atual — Incêndio/Raio/Explosão (R$)</label>
<input type="text" id="cobertura" placeholder="7.000.000,00" oninput="mascValor(this)">
<div style="font-size:11px;color:#999;margin-top:4px">Extraído automaticamente da apólice ou preencha manualmente.</div>
</div>
<button class="btn" id="btn" onclick="analisar()">🔍 Analisar cobertura</button>
<div class="erro" id="erro"></div>
<div class="log" id="log"><div id="log-itens"></div></div>
<div class="resultado" id="resultado">
<div class="res-header"><div class="res-nome" id="r-nome"></div><div class="res-sub" id="r-sub"></div></div>
<div class="tabela-wrap">
<table><thead><tr><th style="width:52%">Cobertura</th><th style="width:26%">Valor</th><th style="width:22%">Status</th></tr></thead>
<tbody id="r-corpo"></tbody></table>
</div>
<div class="mem"><div class="mem-titulo">Memória de cálculo</div><div id="r-mem"></div></div>
</div>
<button class="btn2" id="btn2" onclick="gerarPDF()">📥 Baixar relatório PDF</button>
</div>
</div>
<script>
let b64=null,dados=null;
function mascCNPJ(i){let v=i.value.replace(/\D/g,'').slice(0,14);v=v.replace(/^(\d{2})(\d)/,'$1.$2').replace(/^(\d{2})\.(\d{3})(\d)/,'$1.$2.$3').replace(/\.(\d{3})(\d)/,'.$1/$2').replace(/(\d{4})(\d)/,'$1-$2');i.value=v;}
function mascValor(i){let v=i.value.replace(/\D/g,'');if(!v){i.value='';return;}v=(parseInt(v)/100).toFixed(2);i.value=parseFloat(v).toLocaleString('pt-BR',{minimumFractionDigits:2});}
function selecionarArq(i){const f=i.files[0];if(!f)return;const r=new FileReader();r.onload=e=>{b64=e.target.result.split(',')[1];const z=document.getElementById('zona');z.classList.add('ok');z.querySelector('div').textContent='✅';const n=document.getElementById('nome-arq');n.textContent=f.name;n.style.display='block';};r.readAsDataURL(f);}
function addLog(t){const c=document.getElementById('log-itens');const d=document.createElement('div');d.className='log-item';d.textContent=t;c.appendChild(d);}
function fmt(v){return'R$ '+Math.abs(Math.round(v)).toLocaleString('pt-BR');}
async function analisar(){
const cnpj=document.getElementById('cnpj').value.replace(/\D/g,'');
const cobStr=document.getElementById('cobertura').value.replace(/\./g,'').replace(',','.');
const cob=parseFloat(cobStr)||0;
if(cnpj.length!==14){mostrarErro('Digite o CNPJ completo.');return;}
if(!b64){mostrarErro('Selecione o PDF da apólice.');return;}
document.getElementById('btn').disabled=true;
document.getElementById('erro').style.display='none';
document.getElementById('resultado').style.display='none';
document.getElementById('btn2').style.display='none';
document.getElementById('log-itens').innerHTML='';
document.getElementById('log').style.display='block';
addLog('⏳ Lendo apólice PDF...');
try{
const r=await fetch('/analisar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cnpj,pdf_base64:b64,cobertura:cob})});
addLog('⏳ Pesquisando dados do imóvel...');
const d=await r.json();
if(!r.ok)throw new Error(d.erro||'Erro na análise');
addLog('✅ Endereço: '+d.bairro+', '+d.cidade);
addLog('✅ Área estimada: '+d.area_m2+' m² — Padrão: '+d.padrao);
addLog('✅ Valor de risco calculado!');
dados=d;
renderResultado(d);
}catch(e){mostrarErro('Erro: '+e.message);}
finally{document.getElementById('btn').disabled=false;}
}
function renderResultado(d){
document.getElementById('r-nome').textContent=d.nome;
document.getElementById('r-sub').textContent='CNPJ: '+d.cnpj_fmt+' | '+d.seguradora+' nº '+d.apolice+' | Vigência: '+d.vigencia;
const exc=d.cobertura_atual>d.valor_risco;
const perc=(d.cobertura_atual/d.valor_risco*100).toFixed(1);
const dif=Math.abs(d.cobertura_atual-d.valor_risco);
document.getElementById('r-corpo').innerHTML=
'<tr><td>Limite atual — Incêndio, Raio, Explosão<br><small style="color:#888">'+d.seguradora+' — '+d.apolice+'</small></td><td><strong>'+fmt(d.cobertura_atual)+'</strong></td><td>'+perc.replace('.',',')+' % '+(exc?'do VR':'coberto')+'</td></tr>'+
'<tr><td>Valor de risco estimado</td><td>'+fmt(d.valor_risco)+'</td><td>Referência</td></tr>'+
'<tr class="'+(exc?'linha-alt':'linha-def')+'"><td>'+(exc?'Excedente de cobertura':'Diferença não coberta')+'</td><td>'+fmt(dif)+'</td><td>'+(exc?'Possível redução':'Ajuste necessário')+'</td></tr>'+
'<tr class="linha-rec"><td>Capital '+(exc?'adequado sugerido':'recomendado')+' pela Eleva</td><td>'+fmt(d.recomendado)+'</td><td>✔ '+(exc?'Otimizado':'Adequado')+'</td></tr>';
const caj=d.cub_base*d.fp*d.fl;const custo=d.area_m2*caj;const bdi=custo*d.bdi/100;
document.getElementById('r-mem').innerHTML=
'<div class="mem-linha"><span>CUB/RS R-8N ('+d.mes_cub+')</span><span>'+fmt(d.cub_base)+'/m²</span></div>'+
'<div class="mem-linha"><span>× Fator padrão ('+d.padrao+')</span><span>'+d.fp.toFixed(2).replace('.',',')+'</span></div>'+
'<div class="mem-linha"><span>× Fator localização ('+d.bairro+')</span><span>'+d.fl.toFixed(2).replace('.',',')+'</span></div>'+
'<div class="mem-linha"><span>Área estimada</span><span>'+d.area_m2+' m²</span></div>'+
'<div class="mem-linha"><span>Custo de construção</span><span>'+fmt(custo)+'</span></div>'+
'<div class="mem-linha"><span>BDI ('+d.bdi+'%)</span><span>'+fmt(bdi)+'</span></div>'+
'<div class="mem-linha"><span>Valor de risco total</span><span>'+fmt(d.valor_risco)+'</span></div>';
document.getElementById('resultado').style.display='block';
document.getElementById('btn2').style.display='block';
}
async function gerarPDF(){
document.getElementById('btn2').textContent='⏳ Gerando...';
try{
const r=await fetch('/gerar-pdf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(dados)});
if(!r.ok)throw new Error('Falha');
const blob=await r.blob();
const url=URL.createObjectURL(blob);
const a=document.createElement('a');a.href=url;a.download='Eleva_'+dados.nome.replace(/[^a-zA-Z0-9]/g,'_')+'.pdf';a.click();
}catch(e){mostrarErro(e.message);}
finally{document.getElementById('btn2').innerHTML='📥 Baixar relatório PDF';}
}
function mostrarErro(m){const e=document.getElementById('erro');e.textContent=m;e.style.display='block';}
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/analisar", methods=["POST"])
def analisar():
    try:
        body = request.json
        cnpj = body.get("cnpj","")
        pdf_b64 = body.get("pdf_base64","")
        cob_manual = body.get("cobertura", 0)
        prompt = f"""Analise o PDF da apólice e o CNPJ {cnpj}. Retorne SOMENTE JSON válido sem texto antes ou depois:
{{
  "nome": "Nome do condomínio",
  "cnpj_fmt": "XX.XXX.XXX/XXXX-XX",
  "endereco": "Endereço completo",
  "bairro": "Bairro",
  "cidade": "Cidade",
  "seguradora": "Nome da seguradora",
  "apolice": "Número da apólice",
  "vigencia": "DD/MM/AAAA a DD/MM/AAAA",
  "cobertura_atual": 7000000,
  "andares": 4,
  "area_m2": 1160,
  "padrao": "médio",
  "fp": 1.00,
  "fl": 1.00,
  "cub_base": 3150,
  "mes_cub": "jun/2026",
  "bdi": 18,
  "valor_risco": 4311720,
  "recomendado": 5000000,
  "obs": "observação"
}}
Extraia da apólice: nome, seguradora, apólice, vigência, valor de Incêndio/Raio/Explosão.
Se cobertura_atual vier zerada, use o valor extraído da apólice.
Estime área pelo número de andares e padrão construtivo.
CUB/RS R-8N jun/2026 = R$3.150/m². BDI=18%. Recomendado=arredondar ao milhão acima."""
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role":"user","content":[
                {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":pdf_b64}},
                {"type":"text","text":prompt}
            ]}]
        )
        texto = response.content[0].text.strip()
        texto = re.sub(r"```json|```","",texto).strip()
        d = json.loads(texto)
        if cob_manual > 0:
            d["cobertura_atual"] = cob_manual
        cub_aj = d["cub_base"] * d["fp"] * d["fl"]
        d["valor_risco"] = round(d["area_m2"] * cub_aj * 1.18)
        d["recomendado"] = math.ceil(d["valor_risco"] / 1_000_000) * 1_000_000
        return jsonify(d)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/gerar-pdf", methods=["POST"])
def gerar_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.colors import HexColor, white
        from reportlab.pdfgen import canvas as rl
        from reportlab.platypus import Table, TableStyle
        from datetime import date
        d = request.json
        W,H = A4
        buf = io.BytesIO()
        AZUL=HexColor("#1A4A8B");AZUL_C=HexColor("#EEF3FB");CE=HexColor("#2C2C2C");CM=HexColor("#555555");CL=HexColor("#AAAAAA");VM=HexColor("#C0392B");LJ=HexColor("#E67E22");CLn=HexColor("#F7F7F7");CB=HexColor("#CCCCCC")
        c=rl.Canvas(buf,pagesize=A4);mg=18*mm;larg=W-2*mg
        def fmt(v):return "R$ {:,.2f}".format(abs(v)).replace(",","X").replace(".",",").replace("X",".")
        caj=d["cub_base"]*d["fp"]*d["fl"];custo=d["area_m2"]*caj;bdi_v=custo*d["bdi"]/100;vr=d["valor_risco"];dif=d["cobertura_atual"]-vr;exc=dif>0;perc=(d["cobertura_atual"]/vr)*100
        hoje=date.today().strftime("%d de %B de %Y")
        for en,pt in {"January":"janeiro","February":"fevereiro","March":"março","April":"abril","May":"maio","June":"junho","July":"julho","August":"agosto","September":"setembro","October":"outubro","November":"novembro","December":"dezembro"}.items():hoje=hoje.replace(en,pt)
        c.setFillColor(AZUL);c.rect(0,H-22*mm,W,22*mm,fill=1,stroke=0)
        c.setFillColor(white);c.setFont("Helvetica-Bold",16);c.drawString(mg,H-10*mm,"ELEVA")
        c.setFont("Helvetica",8);c.drawString(mg,H-14.5*mm,"Corretoria & Consultoria de Seguros")
        c.setFont("Helvetica",7.5);c.drawRightString(W-mg,H-9*mm,"SUSEP: 252168625");c.drawRightString(W-mg,H-13*mm,"Porto Alegre, "+hoje)
        c.setFillColor(CL);c.setFont("Helvetica-Oblique",6.5);c.drawCentredString(W/2,H-24.5*mm,f"Análise de cobertura básica — CUB/RS R-8N SINDUSCON-RS {d['mes_cub']} | Apólice {d['seguradora']} nº {d['apolice']}")
        y=H-29*mm
        c.setFillColor(CE);c.setFont("Helvetica-Bold",11.5);c.drawCentredString(W/2,y,"RELATÓRIO DE ADEQUAÇÃO — COBERTURA BÁSICA DE SEGURO")
        y-=4.5*mm;c.setStrokeColor(AZUL);c.setLineWidth(1.2);c.line(mg,y,W-mg,y);y-=4*mm
        c.setFillColor(CE);c.setFont("Helvetica-Bold",9);c.drawString(mg,y,d["nome"])
        y-=4*mm;c.setFont("Helvetica",7.5);c.setFillColor(CM);c.drawString(mg,y,f"CNPJ: {d['cnpj_fmt']}   |   {d['seguradora']} nº {d['apolice']}   |   Vigência: {d['vigencia']}")
        y-=5*mm;c.setFillColor(AZUL_C);c.roundRect(mg,y-6.5*mm,larg,8*mm,2*mm,fill=1,stroke=0);c.setFillColor(AZUL);c.setFont("Helvetica-Bold",7.5);c.drawString(mg+3*mm,y-3.5*mm,"✔  IMÓVEL IDENTIFICADO — "+d["endereco"])
        y-=10*mm
        c.setFillColor(AZUL);c.setFont("Helvetica-Bold",9);c.drawString(mg,y,"1. DADOS DO IMÓVEL")
        y-=2*mm;c.setLineWidth(0.4);c.setStrokeColor(AZUL);c.line(mg,y,W-mg,y);y-=4*mm
        t1=Table([["PARÂMETRO","VALOR","FONTE"],["Pavimentos",str(d["andares"])+" andares","Extraído da apólice"],["Padrão construtivo",d["padrao"],f"Fator: {d['fp']:.2f}".replace(".",",")],["Fator localização",d["bairro"],f"Fator: {d['fl']:.2f}".replace(".",",")],["ÁREA TOTAL ESTIMADA",str(d["area_m2"])+" m²","Estimativa por tipologia"]],colWidths=[larg*0.25,larg*0.30,larg*0.45])
        t1.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),AZUL),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7.5),("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),7),("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),("BACKGROUND",(0,-1),(-1,-1),AZUL_C),("ROWBACKGROUNDS",(0,1),(-1,-2),[white,CLn]),("GRID",(0,0),(-1,-1),0.3,CB),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),5)]))
        _,th1=t1.wrapOn(c,larg,300);t1.drawOn(c,mg,y-th1);y-=th1+5*mm
        c.setFillColor(AZUL);c.setFont("Helvetica-Bold",9);c.drawString(mg,y,"2. CÁLCULO DO VALOR DE RISCO — CUB/RS SINDUSCON-RS")
        y-=2*mm;c.line(mg,y,W-mg,y);y-=4*mm
        t2=Table([["COMPONENTE","VALOR"],[f"CUB/RS R-8N ({d['mes_cub']})",fmt(d["cub_base"])+"/m²"],[f"Fator padrão ({d['padrao']})",f"× {d['fp']:.2f}".replace(".",",")],[f"Fator localização ({d['bairro']})",f"× {d['fl']:.2f}".replace(".",",")],["CUB ajustado",fmt(caj)+"/m²"],[f"Custo ({d['area_m2']} m²)",fmt(custo)],[f"BDI ({d['bdi']}%)",fmt(bdi_v)],["VALOR DE RISCO",fmt(vr)]],colWidths=[larg*0.70,larg*0.30])
        t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),AZUL),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7.5),("FONTNAME",(0,1),(-1,-2),"Helvetica"),("FONTSIZE",(0,1),(-1,-2),7),("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,-1),(-1,-1),8),("BACKGROUND",(0,-1),(-1,-1),AZUL),("TEXTCOLOR",(0,-1),(-1,-1),white),("ROWBACKGROUNDS",(0,1),(-1,-2),[white,CLn]),("ALIGN",(1,0),(1,-1),"RIGHT"),("GRID",(0,0),(-1,-1),0.3,CB),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(1,0),(1,-1),5)]))
        _,th2=t2.wrapOn(c,larg,300);t2.drawOn(c,mg,y-th2);y-=th2+5*mm
        c.setFillColor(AZUL);c.setFont("Helvetica-Bold",9);c.drawString(mg,y,"3. SITUAÇÃO DA COBERTURA BÁSICA")
        y-=2*mm;c.line(mg,y,W-mg,y);y-=4*mm
        ld=("EXCEDENTE DE COBERTURA" if exc else "DIFERENÇA NÃO COBERTA");md=("Possível redução" if exc else "Ajuste necessário");lr=("CAPITAL ADEQUADO SUGERIDO" if exc else "CAPITAL RECOMENDADO PELA ELEVA");cd=HexColor("#FFF3E0") if exc else HexColor("#FDECEC");ct=LJ if exc else VM;st=f"{perc:.1f}% do VR".replace(".",",") if exc else f"{perc:.1f}% coberto".replace(".",",")
        t3=Table([["COBERTURA","VALOR","STATUS"],[f"Limite atual\n{d['seguradora']} — {d['apolice']}",fmt(d["cobertura_atual"]),st],["Valor de risco (Valor de Novo)",fmt(vr),"—"],[ld,fmt(abs(dif)),md],[lr,fmt(d["recomendado"]),"✔ "+("Otimizado" if exc else "Adequado")]],colWidths=[larg*0.52,larg*0.26,larg*0.22])
        t3.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),AZUL),("TEXTCOLOR",(0,0),(-1,0),white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7.5),("FONTNAME",(0,1),(-1,-3),"Helvetica"),("FONTSIZE",(0,1),(-1,-3),7),("BACKGROUND",(0,-2),(-1,-2),cd),("TEXTCOLOR",(0,-2),(-1,-2),ct),("FONTNAME",(0,-2),(-1,-2),"Helvetica-Bold"),("BACKGROUND",(0,-1),(-1,-1),AZUL),("TEXTCOLOR",(0,-1),(-1,-1),white),("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,-1),(-1,-1),8),("ROWBACKGROUNDS",(0,1),(-1,-3),[white,CLn]),("GRID",(0,0),(-1,-1),0.3,CB),("ALIGN",(1,0),(2,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),("LEFTPADDING",(0,0),(-1,-1),5)]))
        _,th3=t3.wrapOn(c,larg,300);t3.drawOn(c,mg,y-th3);y-=th3+4*mm
        nota=f"Metodologia: CUB/RS R-8N SINDUSCON-RS {d['mes_cub']} × fator padrão {d['fp']:.2f} × fator localização {d['fl']:.2f}. BDI {d['bdi']}%. Capital arredondado ao milhão superior. Estimativa técnica — valor exato requer consulta à matrícula (CRI) ou IPTU/PMPA."
        c.setFillColor(HexColor("#F9F9F9"));c.setStrokeColor(CB);c.setLineWidth(0.4);nh=12*mm;c.rect(mg,y-nh,larg,nh,fill=1,stroke=1);c.setFillColor(CM);c.setFont("Helvetica",5.8)
        palavras=nota.split(" ");linhas=[];linha=""
        for p in palavras:
            if len(linha)+len(p)+1<=200:linha+=(" " if linha else "")+p
            else:linhas.append(linha);linha=p
        if linha:linhas.append(linha)
        ly=y-3.5*mm
        for ln in linhas[:3]:c.drawString(mg+2*mm,ly,ln);ly-=3.2*mm
        c.setFillColor(AZUL);c.rect(0,0,W,16*mm,fill=1,stroke=0);c.setFillColor(white)
        c.setFont("Helvetica-Bold",8);c.drawString(mg,11*mm,"Eleva Corretoria e Consultoria de Seguros")
        c.setFont("Helvetica",7);c.drawString(mg,7.5*mm,"SUSEP: 252168625  |  roberto@elevags.com.br");c.drawString(mg,4.5*mm,"(51) 98256-2976  |  Porto Alegre/RS");c.drawRightString(W-mg,9*mm,"Emitido em: "+hoje)
        c.save();buf.seek(0)
        return send_file(buf,mimetype="application/pdf",as_attachment=True,download_name="Eleva_Relatorio.pdf")
    except Exception as e:
        return jsonify({"erro":str(e)}),500

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)





