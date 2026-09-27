const pages={executive,realtime,sources,cdp,journey,lost,campaigns,attribution,cost,maps,qr,influencers,brokers,callcenter,whatsapp,integrations,settings};
function render(){const label=NAV.flatMap(x=>x[1]).find(x=>x[0]===current)?.[2]||'';$('#crumb').textContent=label;content.innerHTML=pages[current]();window.scrollTo({top:0,behavior:'smooth'})}
navRender();render();
$('#menuBtn').onclick=()=>$('#sidebar').classList.toggle('open');
const modal=$('#leadModal');$('#newLeadBtn').onclick=()=>modal.classList.add('show');$('#closeModal').onclick=$('#cancelModal').onclick=()=>modal.classList.remove('show');$('#saveLead').onclick=()=>{modal.classList.remove('show');const t=$('#toast');t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2500)};
modal.onclick=e=>{if(e.target===modal)modal.classList.remove('show')};