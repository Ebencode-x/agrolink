content = open('templates/market/listings.html', encoding='utf-8').read()

# 1. Ongeza CSS ya rating
rating_css = """
  .rating-widget{display:flex;align-items:center;gap:6px;margin-top:0.5rem;flex-wrap:wrap}
  .stars-display{display:flex;gap:2px}
  .star-filled{color:#f59e0b;font-size:0.85rem}
  .star-empty{color:var(--text-muted);font-size:0.85rem}
  .rating-count{font-size:0.72rem;color:var(--text-muted)}
  .btn-rate{display:inline-flex;align-items:center;gap:4px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);color:#fbbf24;padding:0.35rem 0.75rem;border-radius:50px;font-size:0.75rem;font-weight:600;cursor:pointer;transition:all var(--transition);white-space:nowrap}
  .btn-rate:hover{background:rgba(245,158,11,0.2);border-color:rgba(245,158,11,0.4)}
  .rate-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:1000;display:flex;align-items:center;justify-content:center;padding:1rem;backdrop-filter:blur(4px)}
  .rate-modal{background:var(--glass-bg);border:1px solid var(--glass-border);border-radius:var(--radius-md);padding:1.75rem;width:100%;max-width:360px;backdrop-filter:blur(20px)}
  .rate-modal h3{font-family:var(--font-display);font-size:1.1rem;font-weight:700;margin-bottom:0.5rem}
  .rate-modal p{font-size:0.82rem;color:var(--text-secondary);margin-bottom:1.25rem}
  .star-picker{display:flex;gap:8px;margin-bottom:1rem;justify-content:center}
  .star-picker span{font-size:2rem;cursor:pointer;transition:transform 0.15s;line-height:1}
  .star-picker span:hover,.star-picker span.active{transform:scale(1.2)}
  .rate-comment{width:100%;background:rgba(255,255,255,0.06);border:1px solid var(--glass-border);border-radius:12px;padding:0.75rem 1rem;color:var(--text-primary);font-family:var(--font-body);font-size:0.85rem;resize:none;outline:none;transition:border-color var(--transition);box-sizing:border-box}
  .rate-comment:focus{border-color:var(--emerald-bright)}
  .rate-actions{display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-top:1rem}
  .btn-cancel-rate{background:rgba(255,255,255,0.06);border:1px solid var(--glass-border);color:var(--text-secondary);padding:0.6rem;border-radius:50px;font-size:0.85rem;font-weight:600;cursor:pointer;transition:all var(--transition)}
  .btn-submit-rate{background:linear-gradient(135deg,var(--emerald-bright),#059669);border:none;color:white;padding:0.6rem;border-radius:50px;font-size:0.85rem;font-weight:600;cursor:pointer;transition:all var(--transition)}
  .btn-submit-rate:disabled{opacity:0.5;cursor:not-allowed}
"""

content = content.replace(
    '@media(max-width:640px){',
    rating_css + '  @media(max-width:640px){'
)

# 2. Ongeza rating display kwenye listing-footer (baada ya listing-seller div)
old_footer = """            <div class="listing-seller">
              <i data-lucide="user-circle" style="width:14px;height:14px"></i>
              {{ l.seller.full_name.split()[0] if l.seller else 'Mkulima' }}{% if l.seller and l.seller.is_verified %} <span style="display:inline-flex;align-items:center;gap:3px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.35);color:var(--emerald-glow);padding:1px 7px;border-radius:50px;font-size:0.7rem;font-weight:700;margin-left:4px"><i data-lucide="badge-check" style="width:11px;height:11px"></i>Verified</span>{% endif %}
              · {{ l.posted_at.strftime('%d %b') }}
            </div>"""

new_footer = """            <div style="display:flex;flex-direction:column;gap:4px">
              <div class="listing-seller">
                <i data-lucide="user-circle" style="width:14px;height:14px"></i>
                {{ l.seller.full_name.split()[0] if l.seller else 'Mkulima' }}{% if l.seller and l.seller.is_verified %} <span style="display:inline-flex;align-items:center;gap:3px;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.35);color:var(--emerald-glow);padding:1px 7px;border-radius:50px;font-size:0.7rem;font-weight:700;margin-left:4px"><i data-lucide="badge-check" style="width:11px;height:11px"></i>Verified</span>{% endif %}
                · {{ l.posted_at.strftime('%d %b') }}
              </div>
              <div class="rating-widget" id="rating-{{ l.id }}">
                <div class="stars-display" id="stars-{{ l.id }}">
                  <span class="star-empty">☆</span><span class="star-empty">☆</span><span class="star-empty">☆</span><span class="star-empty">☆</span><span class="star-empty">☆</span>
                </div>
                <span class="rating-count" id="rcount-{{ l.id }}">Bado hakuna rating</span>
                {% if current_user.is_authenticated and current_user.id != l.seller_id %}
                <button class="btn-rate" onclick="openRateModal({{ l.id }}, '{{ l.seller.full_name.split()[0] if l.seller else 'Mkulima' }}')">
                  <i data-lucide="star" style="width:11px;height:11px"></i>Rate
                </button>
                {% endif %}
              </div>
            </div>"""

content = content.replace(old_footer, new_footer)

# 3. Ongeza modal na JS
old_script = "<script>\nasync function reportListing"
new_script = """<div id="rate-modal-overlay" class="rate-modal-overlay" style="display:none" onclick="closeRateModal(event)">
  <div class="rate-modal">
    <h3>Tathmini Muuzaji</h3>
    <p id="rate-modal-name">Mpe muuzaji nyota</p>
    <div class="star-picker" id="star-picker">
      <span onclick="selectStar(1)" title="1">☆</span>
      <span onclick="selectStar(2)" title="2">☆</span>
      <span onclick="selectStar(3)" title="3">☆</span>
      <span onclick="selectStar(4)" title="4">☆</span>
      <span onclick="selectStar(5)" title="5">☆</span>
    </div>
    <textarea class="rate-comment" id="rate-comment" rows="3" placeholder="Maoni yako (si lazima)..."></textarea>
    <div class="rate-actions">
      <button class="btn-cancel-rate" onclick="closeRateModal()">Ghairi</button>
      <button class="btn-submit-rate" id="btn-submit-rate" onclick="submitRating()">Tuma</button>
    </div>
  </div>
</div>

<script>
// Load ratings for all listings
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.listing-card').forEach(card => {
    const id = card.id.replace('listing-card-','');
    loadRating(id);
  });
});

async function loadRating(listingId){
  try{
    const res = await fetch('/api/listing/'+listingId+'/rating');
    if(!res.ok) return;
    const data = await res.json();
    updateStars(listingId, data.avg, data.count);
  }catch(e){}
}

function updateStars(listingId, avg, count){
  const starsEl = document.getElementById('stars-'+listingId);
  const countEl = document.getElementById('rcount-'+listingId);
  if(!starsEl) return;
  let html = '';
  for(let i=1;i<=5;i++){
    html += i<=Math.round(avg)
      ? '<span class="star-filled">★</span>'
      : '<span class="star-empty">☆</span>';
  }
  starsEl.innerHTML = html;
  if(count > 0){
    countEl.textContent = avg.toFixed(1) + ' (' + count + ')';
  } else {
    countEl.textContent = 'Bado hakuna rating';
  }
}

let currentListingId = null;
let selectedStars = 0;

function openRateModal(listingId, sellerName){
  currentListingId = listingId;
  selectedStars = 0;
  document.getElementById('rate-modal-name').textContent = 'Mpe ' + sellerName + ' nyota';
  document.getElementById('rate-comment').value = '';
  document.getElementById('star-picker').querySelectorAll('span').forEach(s => s.textContent='☆');
  document.getElementById('rate-modal-overlay').style.display='flex';
}

function closeRateModal(e){
  if(!e || e.target===document.getElementById('rate-modal-overlay')){
    document.getElementById('rate-modal-overlay').style.display='none';
  }
}

function selectStar(n){
  selectedStars = n;
  document.getElementById('star-picker').querySelectorAll('span').forEach((s,i) => {
    s.textContent = i<n ? '★' : '☆';
    s.classList.toggle('active', i<n);
  });
}

async function submitRating(){
  if(!selectedStars){ alert('Chagua nyota kwanza!'); return; }
  const btn = document.getElementById('btn-submit-rate');
  btn.disabled = true;
  btn.textContent = 'Inatuma...';
  const comment = document.getElementById('rate-comment').value.trim();
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
  btn.disabled=false;
  btn.textContent='Tuma';
}

async function reportListing"""

content = content.replace(old_script, new_script)

open('templates/market/listings.html', 'w', encoding='utf-8').write(content)
print('DONE!')
