content = open('templates/market/listings.html', encoding='utf-8').read()

old = """  try{
    const res = await fetch('/listings/'+currentListingId+'/rate', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({stars:selectedStars, comment:comment})
    });
    const data = await res.json();
    if(res.ok){
      updateStars(currentListingId, data.avg, data.count);
      document.getElementById('rate-modal-overlay').style.display='none';
    } else {
      alert(data.error||'Hitilafu. Jaribu tena.');
    }
  } catch(err){
    alert('Tatizo la mtandao: ' + err.message);
  }"""

new = """  try{
    const res = await fetch('/listings/'+currentListingId+'/rate', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({stars:selectedStars, comment:comment})
    });
    const text = await res.text();
    let data;
    try{ data = JSON.parse(text); }
    catch(e){
      if(res.status===401||text.includes('login')||text.includes('ingia')){
        alert('Tafadhali ingia kwanza ili uweze ku-rate.');
      } else {
        alert('Hitilafu. Jaribu tena.');
      }
      btn.disabled=false; btn.textContent='Tuma'; return;
    }
    if(res.ok){
      updateStars(currentListingId, data.avg, data.count);
      document.getElementById('rate-modal-overlay').style.display='none';
    } else {
      alert(data.error||'Hitilafu. Jaribu tena.');
    }
  } catch(err){
    alert('Tatizo la mtandao: ' + err.message);
  }"""

content = content.replace(old, new)
open('templates/market/listings.html', 'w', encoding='utf-8').write(content)
print('DONE!')
