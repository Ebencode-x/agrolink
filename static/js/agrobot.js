/* AgroBot v3.0 — AgroLink Tanzania © Ebenezer Richard */
(function(){
"use strict";
const STORAGE_KEY="agrobot_v3";
const MAX_H=50;

// ── KNOWLEDGE BASE (KB) ────────────────────────────────────────────────────
const KB=[
// ── UTAMBULISHO ─────────────────────────────────────────────────────────────
{k:["wewe ni nani","jina lako","unaitwa nani","identity","nani wewe","ni nani","mimi ni nani","unajitambulisha"],
r:"Habari! Mimi ni <strong>AgroBot</strong> — msaidizi wako wa kidijitali wa kilimo hapa AgroLink Tanzania! 🌱<br>Niko hapa kukusaidia na magonjwa ya mazao, bei za soko, hifadhi ya mazao, mbolea, umwagiliaji na mengi zaidi. Niambie unachohitaji!"},
{k:["unafanya nini","kazi yako","majukumu","unaweza kusaidia","faida yako","ninakusaidia","uwezo wako"],
r:"Ninaweza kukusaidia na:<br>✅ Magonjwa ya mimea na dawa zake<br>✅ Bei za mazao sokoni Tanzania<br>✅ Hifadhi ya mazao baada ya kuvuna<br>✅ Mbolea na virutubisho<br>✅ Kilimo cha mazao mbalimbali<br>✅ Masoko na wanunuzi<br>✅ Umwagiliaji na hali ya hewa<br>✅ Mikopo ya kilimo<br><br>Niulize chochote — niko hapa!"},
{k:["nani aliyekutengeneza","developer","creator","muundo","nani amekuunda","bosi wako","timu yako","nani mkuunda"],
r:"Nimeundwa na <strong>AgroLink Team</strong> ikiongozwa na <strong>Ebenezer Richard</strong> — mhandisi wa programu kutoka Mbeya, Tanzania. Lengo lao ni kuleta teknolojia ya kisasa kwenye kilimo cha Kitanzania! 🇹🇿"},
{k:["api key","database","users wangapi","data ya watu","secret","nywila","password","token","server","code yako"],
r:"Samahani, taarifa za ndani za mfumo ni siri — siwezi kuzishiriki. 🔒 Kama una tatizo la kiufundi, wasiliana na timu yetu kupitia ukurasa wa Mawasiliano."},

// ── SALAMU ──────────────────────────────────────────────────────────────────
{k:["habari","mambo","hello","hi","niaje","mambo vipi","shikamoo","karibu","salam","hujambo","hamjambo","hey","halo","oya","sasa","vipi"],
r:"Habari sana mdau wa kilimo! Karibu sana AgroLink Tanzania. 🌿 Niko tayari kukusaidia na maswali yoyote ya kilimo, masoko, au mazao yako. Niambie!"},
{k:["asante","shukrani","nashukuru","umesaidia","poa sana","safi kabisa","hongera","vizuri sana","nimeridhika"],
r:"Pamoja sana! Kilimo ni uti wa mgongo wa Tanzania, na AgroLink ipo hapa kulinda uti huo. 🌾 Rudi tena ukihitaji msaada!"},
{k:["bye","kwaheri","tutaonana","baadaye","lala salama","nenda salama","ciao","ondo"],
r:"Kwaheri mdau! Kazi njema shambani. Usisahau kurudi AgroLink — soko linabadilika kila siku! 🚜"},

// ── MAHINDI ─────────────────────────────────────────────────────────────────
{k:["mahindi yanaliwa","wadudu mahindi","funza mahindi","viwavijeshi","fall armyworm","armyworm",
    "mahindi kuharibika","matundu mahindi","kinyesi mahindi","mabua ya mahindi","stalk borer"],
r:"<strong>Wadudu wa Mahindi:</strong><br><br>🐛 <strong>Viwavijeshi (Fall Armyworm)</strong><br>Dalili: Majani yenye matundu, kinyesi cha kahawia moyoni, mmea kudumaa.<br>Dawa: Karate (1ml/L), Ampligo, Coragen. Nyunyiza <em>asubuhi mapema</em>!<br><br>🐛 <strong>Funza wa Mabua (Stalk Borer)</strong><br>Dalili: Matundu kwenye shina, ungaunga wa msumeno kwenye majani.<br>Dawa: Furadan (punje 3-5 moyoni) au Karate.<br><br>⚠️ Nyunyiza wiki mbili mara baada ya kuona wadudu wa kwanza — usichelewe!"},
{k:["mahindi njano","mahindi rangi ya njano","majani ya njano mahindi","mahindi kugeuka njano",
    "njano mahindi","mahindi kukauka","majani kukauka mahindi","mahindi kudumaa"],
r:"<strong>Mahindi Kugeuka Njano — Sababu na Suluhisho:</strong><br><br>🌽 <strong>Upungufu wa Nitrojeni</strong> — Majani ya chini yanageuka njano kwanza. Suluhisho: UREA au CAN (50kg/ekari).<br><br>🌽 <strong>Maji Mengi (Waterlogging)</strong> — Majani yote njano. Tengeneza mifereji.<br><br>🌽 <strong>Streak Virus</strong> — Mstari wa njano kwenye majani. Dawa: Actara kuzuia wadudu wabebao virusi.<br><br>🌽 <strong>Ukosefu wa Sulfuri</strong> — Majani mapya njano, ya zamani ya kijani. Weka Ammonium Sulphate."},
{k:["kilimo cha mahindi","kupanda mahindi","mbolea ya mahindi","mbegu za mahindi","nafasi ya mahindi","mahindi msimu"],
r:"<strong>Kilimo Bora cha Mahindi Tanzania:</strong><br><br>🌽 <strong>Mbegu Bora:</strong> DK8031, H614D, Seedco SC403, SEEDCO SC627<br><br>🌽 <strong>Kupanda:</strong> Nafasi cm 75 kati ya mistari, cm 25-30 kati ya mimea. Mbegu 2 kwa shimo.<br><br>🌽 <strong>Mbolea:</strong> DAP wakati wa kupanda (50kg/ekari). UREA/CAN wiki 4-6 baadaye (50kg/ekari).<br><br>🌽 <strong>Msimu:</strong> Masika (Machi-Mei) na Vuli (Oktoba-Desemba).<br><br>🌽 <strong>Mavuno:</strong> Tani 3-8 kwa hekta ukitumia mbegu bora na mbolea sahihi."},

// ── NYANYA ──────────────────────────────────────────────────────────────────
{k:["ugonjwa wa nyanya","magonjwa ya nyanya","nyanya zinaoza","nyanya zinakauka",
    "madoa kwenye nyanya","blight ya nyanya","nyanya zina madoa","nyanya kuharibika","nyanya zinaungua"],
r:"<strong>Magonjwa Makuu ya Nyanya:</strong><br><br>🔴 <strong>Ukungu Mapema (Early Blight)</strong><br>Dalili: Madoa ya kahawia yenye mviringo, majani kufa mapema.<br>Dawa: Mancozeb, Ridomil Gold, Dithane M-45.<br><br>🔴 <strong>Ukungu Chelewa (Late Blight)</strong><br>Dalili: Madoa makubwa ya kijivu-kahawia, uvundo.<br>Dawa: Ridomil Gold MZ, Acrobat MZ. Nyunyiza HARAKA!<br><br>🔴 <strong>Mnyauko (Fusarium Wilt)</strong><br>Dalili: Mmea unanyauka ghafla hata ukimwagilia.<br>Kinga: Mbegu bora, epuka maji kusimama.<br><br>🔴 <strong>Uoza wa Kitako</strong><br>Dalili: Sehemu ya chini ya tunda inageuka nyeusi.<br>Dawa: Mbolea ya CAN (chokaa)."},
{k:["tuta absoluta","nondo wa nyanya","funza wa nyanya","matundu nyanya","wadudu wa nyanya","nyanya mashimo"],
r:"<strong>Tuta Absoluta — Adui Mkubwa wa Nyanya:</strong><br><br>Dalili: Matundu madogo kwenye majani, majani yanaojikunja, matunda yenye mashimo ya ndani.<br><br>✅ Udhibiti:<br>• Mitego ya pheromone (AGROVET)<br>• Coragen, Ampligo au Karate<br>• Ng'oa na choma mimea iliyoathirika sana<br>• Safisha shamba kabisa baada ya mavuno"},
{k:["kilimo cha nyanya","kupanda nyanya","nyanya mbegu","nafasi ya nyanya","nyanya msimu"],
r:"<strong>Kilimo Bora cha Nyanya Tanzania:</strong><br><br>🍅 <strong>Mbegu Bora:</strong> Anna F1, Tengeru 97, Marglobe, Hytec 36, Julius F1<br><br>🍅 <strong>Kupanda:</strong> Vitalu kwanza, pandikiza baada ya wiki 3-4. Nafasi: cm 60×60.<br><br>🍅 <strong>Mbolea:</strong> DAP kupandia. CAN kukuzia. Foliar spray kwa calcium.<br><br>🍅 <strong>Umwagiliaji:</strong> Mara kwa mara lakini si maji mengi. Drip irrigation ni bora.<br><br>🍅 <strong>Msimu Bora:</strong> Juni-Septemba (baridi — ubora wa juu, bei nzuri)."},

// ── VIAZI ────────────────────────────────────────────────────────────────────
{k:["ugonjwa wa viazi","magonjwa ya viazi","viazi kuoza","viazi vidogo","blight ya viazi",
    "viazi kuharibika","madoa viazi","viazi vitamu magonjwa"],
r:"<strong>Magonjwa ya Viazi:</strong><br><br>🥔 <strong>Blight ya Viazi (Late Blight)</strong><br>Dalili: Madoa ya kahawia-nyeusi kwenye majani, uvundo mbaya.<br>Dawa: Ridomil Gold, Curzate M8. Anza mapema kabla ya ugonjwa!<br><br>🥔 <strong>Scab Disease</strong><br>Dalili: Makucha makali kwenye ngozi ya kiazi.<br>Sababu: pH ya juu. Punguza kwa kuongeza asidi.<br><br>🥔 <strong>Vidonda vya Mizizi</strong><br>Dalili: Mizizi inageuka kahawia, mmea unanyauka.<br>Kinga: Panda kwenye matuta — maji yatiririke vizuri."},
{k:["kilimo cha viazi","kupanda viazi","viazi mbegu","viazi msimu","viazi mviringo","viazi vitamu"],
r:"<strong>Kilimo cha Viazi Tanzania:</strong><br><br>🥔 <strong>Aina Bora:</strong> Viazi Mviringo: Tigoni, Asante, Desiree. Viazi Vitamu: Kabode, Ejumula.<br><br>🥔 <strong>Kupanda:</strong> Tumia mbegu bora (seed potatoes). Nafasi cm 75×30. Panda kwenye matuta.<br><br>🥔 <strong>Mbolea:</strong> DAP kupandia. NPK kukuzia. Samadi ni ya muhimu.<br><br>🥔 <strong>Msimu:</strong> Mikoa ya baridi (Mbeya, Iringa, Njombe) — Julai-Septemba ni bora.<br><br>🥔 <strong>Mavuno:</strong> Tani 10-25 kwa hekta kwa mbegu bora."},

// ── MPUNGA ───────────────────────────────────────────────────────────────────
{k:["ugonjwa wa mpunga","magonjwa ya mpunga","mpunga kukauka","blast ya mpunga",
    "njano ya mpunga","mpunga kuharibika","mchele ugonjwa","mpunga madoa"],
r:"<strong>Magonjwa ya Mpunga:</strong><br><br>🌾 <strong>Blast ya Mpunga (Rice Blast)</strong><br>Dalili: Madoa meupe-kijivu kwenye majani, shingo ya swimbi inakufa.<br>Dawa: Tricyclazole (Beam), Propiconazole.<br><br>🌾 <strong>Njano ya Majani (Bacterial Leaf Blight)</strong><br>Dalili: Kingo za majani zinageuka njano-kahawia.<br>Kinga: Mbegu safi, punguza mbolea ya nitrojeni.<br><br>🌾 <strong>Kutu ya Kahawia (Brown Spot)</strong><br>Dalili: Madoa ya mviringo ya kahawia kwenye majani.<br>Sababu: Upungufu wa mbolea. Weka UREA/CAN kwa wakati."},
{k:["kilimo cha mpunga","kupanda mpunga","mpunga mbegu","paddy","kilimo cha mchele","mpunga msimu"],
r:"<strong>Kilimo cha Mpunga Tanzania:</strong><br><br>🌾 <strong>Mbegu Bora:</strong> SARO 5, TXD 306, IR64, Komboka<br><br>🌾 <strong>Kupanda:</strong> Vitalu au moja kwa moja (direct seeding). Nafasi: cm 20×20.<br><br>🌾 <strong>Maji:</strong> Inchi 5-10 za maji mara kwa mara. Kausha wiki 2 kabla ya kuvuna.<br><br>🌾 <strong>Mbolea:</strong> DAP kupandia. UREA wakati wa tillering (wiki 4-5).<br><br>🌾 <strong>Misimu:</strong> Masika (Machi-Juni) na Vuli (Oktoba-Januari) — mikoa ya Morogoro, Mwanza, Shinyanga."},

// ── MAHARAGE ─────────────────────────────────────────────────────────────────
{k:["ugonjwa wa maharage","magonjwa ya maharage","maharage kukauka","kutu ya maharage",
    "maharage kuharibika","madoa maharage","ndui ya maharage","anthracnose maharage"],
r:"<strong>Magonjwa ya Maharage:</strong><br><br>🫘 <strong>Kutu ya Maharage (Bean Rust)</strong><br>Dalili: Mabaka ya rangi ya kutu chini ya majani.<br>Dawa: Mancozeb, Thiovit (sulfur). Nyunyiza kila wiki 10-14.<br><br>🫘 <strong>Ndui ya Maharage (Anthracnose)</strong><br>Dalili: Madoa ya kahawia-nyekundu kwenye maganda. Mbegu zina madoa meusi.<br>Dawa: Mancozeb au Copper fungicide.<br><br>🫘 <strong>Mnyauko wa Bakteria</strong><br>Dalili: Mmea unanyauka, usaha mzito ukikata shina.<br>Kinga: Mbegu bora, palilia magugu, zungushia mazao."},
{k:["kilimo cha maharage","kupanda maharage","maharage msimu","maharage mbegu","nafasi ya maharage"],
r:"<strong>Kilimo cha Maharage Tanzania:</strong><br><br>🫘 <strong>Aina Bora:</strong> Lyamungu 85, Jesca, Selian 97, BARI 1<br><br>🫘 <strong>Kupanda:</strong> Nafasi cm 50×10-15. Mbegu 1-2 kwa shimo. Kina cm 3-5.<br><br>🫘 <strong>Mbolea:</strong> DAP kupandia (kidogo — maharage yana nitrojeni yao). Samadi ni bora.<br><br>🫘 <strong>Msimu:</strong> Mei-Agosti (baridi kwa Mbeya, Iringa). Oktoba-Januari kwa maeneo ya chini.<br><br>🫘 <strong>Faida:</strong> Inaboresha udongo kwa nitrojeni — nzuri kabla ya mahindi!"},

// ── MUHOGO ───────────────────────────────────────────────────────────────────
{k:["muhogo","kilimo cha muhogo","magonjwa ya muhogo","muhogo kukauka","muhogo madoa",
    "cassava","muhogo kuharibika","wadudu wa muhogo"],
r:"<strong>Kilimo na Magonjwa ya Muhogo Tanzania:</strong><br><br>🌿 <strong>Magonjwa Makuu:</strong><br>• <strong>Mosaic Virus (CMD)</strong> — Majani yenye madoa ya njano na kijani. Husambazwa na nzi weupe. Tumia mbegu bora zinazostahimili.<br>• <strong>Brown Streak Disease (CBSD)</strong> — Ugonjwa mbaya sana Tanzania. Muhogo wa ndani unaoza. Hakuna dawa — tumia mbegu safi tu.<br>• <strong>Batobato (Anthracnose)</strong> — Madoa meusi kwenye majani na matawi. Dawa: Mancozeb.<br><br>🌿 <strong>Kilimo:</strong><br>• Tumia vipande vya shina (vipande 25-30cm) kutoka mimea yenye afya<br>• Nafasi: mita 1×1 au 0.9×0.9<br>• Inastahimili ukame — nzuri kwa maeneo makame"},

// ── ALIZETI ──────────────────────────────────────────────────────────────────
{k:["alizeti","kilimo cha alizeti","magonjwa ya alizeti","alizeti kukauka","sunflower",
    "mbegu za alizeti","mafuta ya alizeti","alizeti msimu"],
r:"<strong>Kilimo cha Alizeti Tanzania:</strong><br><br>🌻 <strong>Mbegu Bora:</strong> AGUARA 4, HYSUN 33, NSFH 36, NSFH 145<br><br>🌻 <strong>Magonjwa:</strong><br>• Yellow Blotch — Rangi ya njano, maua kuharibika. Dawa: Agrozinon 60EC<br>• Sclerotinia (White Mold) — Uoza wa shina na kichwa. Fanya crop rotation kila miaka 5.<br>• Viwavi (African Bollworm) — Hula mbegu. Dawa: Konto au Antario.<br><br>🌻 <strong>Kupanda:</strong> Nafasi cm 75×30. Kina cm 3-5. Mbolea: DAP kupandia.<br><br>🌻 <strong>Kuvuna:</strong> Vichwa vinapogeuka njano-kahawia (miezi 4-6). Kausha vizuri kabla ya kusindika."},

// ── KOROSHO ──────────────────────────────────────────────────────────────────
{k:["korosho","kilimo cha korosho","magonjwa ya korosho","cashew","korosho msimu",
    "korosho bei","korosho Tanzania","wadudu wa korosho"],
r:"<strong>Kilimo cha Korosho Tanzania:</strong><br><br>🥜 <strong>Maeneo Bora:</strong> Mtwara, Lindi, Ruvuma, Pwani, Tanga.<br><br>🥜 <strong>Kupanda:</strong> Nafasi mita 9×9. Shimo cm 30-40 kina. Jaza samadi kabla ya kupanda.<br><br>🥜 <strong>Magonjwa:</strong><br>• Kutu ya Korosho (Powdery Mildew) — Unga mweupe kwenye majani. Dawa: Sulfur fungicide.<br>• Mnyauko wa Majani — Majani yanakauka na kuanguka. Kata matawi yaliyoathirika.<br><br>🥜 <strong>Wadudu:</strong> Tea Mosquito Bug — inasababisha vidonda kwenye matunda. Dawa: Dimethoate.<br><br>🥜 <strong>Bei:</strong> TZS 2,000-3,500/kg (korosho ghafi). Export kwenda India na Vietnam."},

// ── KARANGA ──────────────────────────────────────────────────────────────────
{k:["karanga","kilimo cha karanga","magonjwa ya karanga","groundnut","karanga msimu",
    "karanga bei","karanga kuoza","aflatoxin"],
r:"<strong>Kilimo cha Karanga Tanzania:</strong><br><br>🥜 <strong>Mbegu Bora:</strong> Mnanje, Pendo, Naliendele 96E<br><br>🥜 <strong>Kupanda:</strong> Nafasi cm 45×15. Kina cm 4-5. Udongo tifutifu wenye mifereji.<br><br>🥜 <strong>Magonjwa:</strong><br>• Cercospora Leaf Spot (madoa ya kahawia) — Dawa: Mancozeb<br>• Kutu (Rust) — Madoa ya chungwa chini ya majani. Dawa: Bayleton<br>• Aflatoxin — Sumu hatari inayotokea kwa uhifadhi mbaya. Kausha vizuri hadi 10% unyevu!<br><br>🥜 <strong>Kuvuna:</strong> Miezi 3-4. Ng'oa, kausha juani siku 5-7. Hifadhi vizuri!"},

// ── NDIZI ────────────────────────────────────────────────────────────────────
{k:["ndizi","kilimo cha ndizi","magonjwa ya ndizi","banana","ndizi kuoza","sigatoka",
    "panama disease","ndizi msimu","ndizi bei","machungwa","ndizi kukauka"],
r:"<strong>Kilimo na Magonjwa ya Ndizi Tanzania:</strong><br><br>🍌 <strong>Magonjwa Makuu:</strong><br>• <strong>Sigatoka Nyeusi</strong> — Madoa meusi kwenye majani, matunda yaniva mapema. Dawa: Mancozeb, Topsin M.<br>• <strong>Panama Disease (Fusarium Wilt)</strong> — Mmea unanyauka kabisa — HAINA DAWA. Tumia mbegu bora safi.<br>• <strong>Bunchy Top Virus</strong> — Majani madogo yanakunjamana. Ng'oa na choma mara moja!<br><br>🍌 <strong>Kilimo:</strong> Tumia suckers zenye afya. Nafasi mita 3×3. Mbolea ya samadi mingi. Maji ya kutosha.<br><br>🍌 <strong>Bei:</strong> TZS 300-800/kg. Masoko bora: DSM, Zanzibar, Mombasa."},

// ── PARACHICHI ───────────────────────────────────────────────────────────────
{k:["parachichi","avocado","kilimo cha parachichi","miche ya parachichi","hass avocado",
    "parachichi mbeya","parachichi export","parachichi magonjwa","parachichi bei"],
r:"<strong>Parachichi — Dhahabu ya Kijani ya Nyanda za Juu!</strong><br><br>🥑 <strong>Aina Bora:</strong> Hass (export), Fuerte, Pinkerton<br><br>🥑 <strong>Kupanda:</strong> Miche iliyopandikizwa (grafted) — inatoa matunda miaka 3-4. Nafasi mita 5×5 au 6×6. pH 5.5-7.0.<br><br>🥑 <strong>Magonjwa:</strong><br>• Phytophthora Root Rot — Epuka maji kusimama. Tumia Aliette.<br>• Anthracnose — Madoa meusi kwenye matunda. Dawa: Copper oxychloride.<br><br>🥑 <strong>Soko:</strong> Export kwenda Ulaya, UAE kupitia TAHA au FRUTCO (Arusha).<br><br>🥑 <strong>Bei:</strong> TZS 500-1,500/kg ndani. USD 0.80-2.00/kg export!"},

// ── VITUNGUU ─────────────────────────────────────────────────────────────────
{k:["vitunguu","kilimo cha vitunguu","vitunguu maji","magonjwa ya vitunguu","onion",
    "vitunguu saumu","garlic","vitunguu bei","vitunguu msimu"],
r:"<strong>Kilimo cha Vitunguu Tanzania:</strong><br><br>🧅 <strong>Maeneo Bora:</strong> Morogoro (Kilosa), Singida, Manyara (Babati).<br><br>🧅 <strong>Mbegu Bora:</strong> Red Pinoy, Bombay Red, Tengeru White<br><br>🧅 <strong>Kupanda:</strong> Vitalu kwanza (wiki 6-8), pandikiza. Nafasi cm 10×20.<br><br>🧅 <strong>Magonjwa:</strong><br>• Purple Blotch — Madoa ya zambarau. Dawa: Mancozeb<br>• Downy Mildew — Unga mweupe. Dawa: Ridomil<br>• Thrips — Dawa: Karate<br><br>🧅 <strong>Kuvuna:</strong> 80% ya majani yamepinda. Punguza maji wiki 2 kabla ya kuvuna."},

// ── PILIPILI ──────────────────────────────────────────────────────────────────
{k:["pilipili","kilimo cha pilipili","pilipili hoho","pilipili kali","pepper",
    "pilipili kuoza","magonjwa ya pilipili","pilipili bei","pilipili msimu"],
r:"<strong>Kilimo cha Pilipili Tanzania:</strong><br><br>🌶️ <strong>Aina Bora:</strong> California Wonder (hoho), Capsicum annuum (kali)<br><br>🌶️ <strong>Kupanda:</strong> Vitalu kwanza. Nafasi cm 60×45. Joto 18-30°C.<br><br>🌶️ <strong>Magonjwa:</strong><br>• Phytophthora Blight — Mmea unanyauka ghafla. Epuka maji kusimama.<br>• Anthracnose — Madoa meusi. Dawa: Copper fungicide<br>• Aphids — Dawa: Actara au Karate<br><br>🌶️ <strong>Bei:</strong> TZS 1,500-4,000/kg. Msimu bora: panda Juni-Julai, vuna Oktoba-Desemba."},

// ── MCHICHA / MBOGA ──────────────────────────────────────────────────────────
{k:["mchicha","mboga","spinach","sukuma wiki","bamia","kabichi","cauliflower","broccoli",
    "mboga za majani","vegetables","mboga msimu","mboga magonjwa","mboga bei"],
r:"<strong>Kilimo cha Mboga Tanzania:</strong><br><br>🥬 <strong>Sukuma Wiki (Kale):</strong> Rahisi kulima, soko zuri kila wakati. Msimu wote. Dawa: Karate kwa wadudu.<br><br>🥬 <strong>Mchicha:</strong> Hukomaa haraka (wiki 4-6). Maji mengi. Soko zuri DSM.<br><br>🥬 <strong>Kabichi:</strong> Mbegu bora: Gloria F1, Oxylus. Nafasi cm 45×45. Msimu wa baridi ni bora.<br><br>🥬 <strong>Bamia:</strong> Inastahimili ukame. Mavuno mengi. Bei TZS 600-1,500/kg.<br><br>🥬 <strong>Wadudu wa Mboga:</strong> Aphids, Diamondback Moth, Cutworm. Dawa: Karate, Dipel (bio)."},

// ── MATUNDA ──────────────────────────────────────────────────────────────────
{k:["mwembe","embe","mango","kilimo cha embe","embe magonjwa","embe bei",
    "machungwa","chungwa","orange","limau","lemon","lime","matunda","fruit"],
r:"<strong>Matunda ya Biashara Tanzania:</strong><br><br>🥭 <strong>Embe (Mango):</strong> Aina bora: Tommy Atkins, Apple Mango, Ngowe. Magonjwa: Anthracnose (Copper fungicide). Bei: TZS 400-1,200/kg.<br><br>🍊 <strong>Machungwa (Orange):</strong> Aina: Valencia, Navel. Magonjwa: Citrus Greening (hakuna dawa — zuia wadudu). Bei: TZS 300-800/kg.<br><br>🍍 <strong>Nanasi (Pineapple):</strong> Maeneo bora: Pwani, Tanga, Morogoro. Bei: TZS 500-1,500/kipande.<br><br>🍉 <strong>Tikiti Maji (Watermelon):</strong> Msimu wa kiangazi — faida kubwa. Bei: TZS 400-1,000/kg."},

// ── WADUDU WA JUMLA ──────────────────────────────────────────────────────────
{k:["wadudu","aphid","vidung'ata","thrips","whitefly","inzi weupe","nzi","mbu wa mimea",
    "sarafu","mite","spider mite","wadudu wanaouma","kunyonya mimea","wadudu shambani"],
r:"<strong>Wadudu Waharibifu wa Kawaida Tanzania:</strong><br><br>🦗 <strong>Aphids (Vidung'ata)</strong><br>Dalili: Majani yanakunjamana, utomvu mzito.<br>Dawa: Karate, Actara, au maji ya sabuni ya kufulia.<br><br>🦗 <strong>Thrips</strong><br>Dalili: Majani yanageuka fedha, matunda yana makucha.<br>Dawa: Abamectin, Karate.<br><br>🦗 <strong>Whitefly (Inzi Weupe)</strong><br>Dalili: Wadudu wadogo weupe wanaoruka, majani njano.<br>Dawa: Actara, Confidor. Mtego wa njano wenye gundi!<br><br>🦗 <strong>Spider Mites (Sarafu)</strong><br>Dalili: Utando mzito chini ya majani, majani kahawia.<br>Dawa: Abamectin, Oberon."},

// ── MBOLEA ───────────────────────────────────────────────────────────────────
{k:["mbolea","nitrojeni","phosphorus","potassium","DAP","UREA","CAN","NPK","mbolea gani",
    "virutubisho","kuweka mbolea","mbolea ya kupandia","mbolea ya kukuzia","samadi","compost","mboji"],
r:"<strong>Mwongozo wa Mbolea Tanzania:</strong><br><br>🌱 <strong>DAP</strong> — Kupandia. Inasaidia mizizi kukua. 50kg/ekari wakati wa kupanda.<br><br>🌱 <strong>UREA (46% N)</strong> — Kukuzia. Fanya majani ya kijani. Wiki 4-6 baada ya kuota.<br><br>🌱 <strong>CAN</strong> — Bora kwa nyanya. Ina nitrojeni + chokaa. Inazuia uoza wa kitako.<br><br>🌱 <strong>NPK 17:17:17</strong> — Mbolea kamili kwa mazao yote.<br><br>🌱 <strong>Samadi/Compost</strong> — Toni 5-10/ekari. Inatoa virutubisho kwa miaka mingi. BORA KABISA!<br><br>⚠️ Usiweke mbolea nyingi — inaweza kuchoma mimea na kuharibu udongo!"},

// ── HIFADHI YA MAZAO ─────────────────────────────────────────────────────────
{k:["kuhifadhi mazao","hifadhi","ghala","post harvest","baada ya kuvuna",
    "mazao kuoza","storage","kuhifadhi mahindi","kuhifadhi nyanya","PICS bag","postharvest"],
r:"<strong>Jinsi ya Kuhifadhi Mazao Tanzania:</strong><br><br>🏪 <strong>Mahindi:</strong> Kausha hadi 13% unyevu. ACTELLIC DUST au SKANA P. PICS Bag au gunia safi.<br><br>🏪 <strong>Maharage:</strong> Changanya na majivu ya kuni (1:10) — inazuia wadudu bila dawa!<br><br>🏪 <strong>Nyanya/Mboga:</strong> Ziuze ndani ya siku 3-7. Usizifunge kwenye plastiki iliyofungwa.<br><br>🏪 <strong>Viazi:</strong> Giza, ubaridi, hewa nzuri. Epuka mwanga wa jua — sumu (solanine)!<br><br>🏪 <strong>Mpunga:</strong> Kausha hadi 12-14%. Gunia safi. Angalia panya na wadudu.<br><br>🏪 <strong>Karanga:</strong> Kausha vizuri hadi 10% — kuzuia Aflatoxin!"},

// ── UMWAGILIAJI ──────────────────────────────────────────────────────────────
{k:["umwagiliaji","maji","kumwagilia","drip irrigation","mfumo wa maji","ukame",
    "kiangazi","maji shambani","kukosa maji","mimea inakauka","irrigation","mifereji"],
r:"<strong>Mwongozo wa Umwagiliaji:</strong><br><br>💧 <strong>Wakati Bora:</strong> Asubuhi saa 12-2 (6-8 AM). Epuka mchana — maji yanabubujika.<br><br>💧 <strong>Drip Irrigation:</strong> Inaokoa maji 40-60%. Bora kwa nyanya, pilipili, mboga.<br><br>💧 <strong>Ishara za Kukosa Maji:</strong> Majani yanakunjamana asubuhi, rangi kuwa nyepesi, mmea kudumaa.<br><br>💧 <strong>Ishara za Maji Mengi:</strong> Majani njano, mizizi inaoza, harufu mbaya ardhini.<br><br>💧 <strong>Kiangazi:</strong> Ongeza mara za kumwagilia lakini punguza kiasi — kuzuia uoza wa mizizi."},

// ── UDONGO ───────────────────────────────────────────────────────────────────
{k:["udongo","rutuba ya udongo","pH ya udongo","udongo mzuri","udongo mbaya",
    "chokaa","lime","udongo tifutifu","udongo wa mfinyanzi","erosion","mmomonyoko"],
r:"<strong>Usimamizi wa Udongo:</strong><br><br>🌍 <strong>pH Nzuri:</strong> 6.0-7.0 kwa mazao mengi. Pima kwa pH meter (AGROVET).<br><br>🌍 <strong>Udongo wenye Tindikali (pH < 6):</strong> Ongeza chokaa (Lime) — 50kg/ekari. Subiri miezi 1-2.<br><br>🌍 <strong>Udongo wa Mfinyanzi:</strong> Ongeza mchanga na samadi — inaboresha mifereji ya maji.<br><br>🌍 <strong>Mmomonyoko wa Udongo:</strong> Panda mikanda ya mimea kwenye mteremko. Tumia mulch.<br><br>🌍 <strong>Dalili za Udongo Mbaya:</strong> Mimea inakua polepole, majani njano, udongo mgumu kama jiwe."},

// ── BEI ZA SOKO ──────────────────────────────────────────────────────────────
{k:["bei ya mazao","bei ya soko","bei ya mahindi","bei ya nyanya","bei ya viazi",
    "bei gani","market price","bei ya mchele","bei ya maharage","bei ya parachichi",
    "bei leo","soko la leo","bei za Tanzania","bei ya korosho","bei ya alizeti"],
r:"Kwa bei za sasa sahihi, angalia ukurasa wa <strong>'Bei ya AI'</strong> kwenye AgroLink!<br><br>📊 <strong>Bei za Wastani Tanzania (2025-2026):</strong><br>• Mahindi: TZS 400-900/kg<br>• Nyanya: TZS 800-2,500/kg<br>• Viazi: TZS 500-1,200/kg<br>• Mpunga (mchele): TZS 1,200-2,500/kg<br>• Maharage: TZS 1,200-2,800/kg<br>• Parachichi (Hass): TZS 500-1,500/kg<br>• Pilipili hoho: TZS 1,500-4,000/kg<br>• Korosho: TZS 2,000-3,500/kg<br>• Alizeti: TZS 800-1,400/kg<br>• Ndizi: TZS 300-800/kg<br><br>⚠️ Bei za DSM na Arusha ni juu zaidi ya vijijini kwa 20-40%!"},

// ── MASOKO NA WANUNUZI ────────────────────────────────────────────────────────
{k:["soko","wanunuzi","kuuza","wapi nitauza","masoko Tanzania","Kariakoo","Tandale",
    "Mchikichini","Arusha soko","DSM soko","Mbeya soko","soko la kimataifa"],
r:"<strong>Masoko Makubwa Tanzania:</strong><br><br>🛒 <strong>Dar es Salaam:</strong> Kariakoo (mkubwa zaidi), Tandale, Buguruni, Mchikichini<br>🛒 <strong>Arusha:</strong> Central Market, Kilombero Market<br>🛒 <strong>Mbeya:</strong> Mwanjelwa Market, Uyole Market<br>🛒 <strong>Dodoma:</strong> Majengo Market<br>🛒 <strong>Mwanza:</strong> Kirumba Market<br><br>💡 <strong>Ushauri:</strong> Tumia AgroLink kuwasiliana na wanunuzi moja kwa moja — bila dalali! Pia angalia Bei ya AI kujua soko bora la wiki hii."},

// ── EXPORT ────────────────────────────────────────────────────────────────────
{k:["export","kuuza nje","masoko ya nje","international","kenya","uarabu","ulaya",
    "dubai","ng'ambo","foreign market","TAHA","GlobalGAP"],
r:"<strong>Kuuza Mazao Nje ya Tanzania:</strong><br><br>🌍 <strong>Mazao Yanayotakiwa:</strong><br>• Parachichi (Hass) → Ulaya, UAE<br>• Ufuta → India, China<br>• Korosho → India, Vietnam<br>• Maharage → Kenya, Uganda<br>• Pilipili kali → Pakistan, India<br><br>🌍 <strong>Jinsi ya Kuanza:</strong><br>1. Leseni ya export (Wizara ya Kilimo — MALF)<br>2. Jiunge TAHA (Tanzania Horticulture Association)<br>3. Pata GlobalGAP certification kwa Ulaya<br>4. Wasiliana FRUTCO Arusha kwa parachichi"},

// ── MIKOPO ────────────────────────────────────────────────────────────────────
{k:["mkopo","fedha","financing","benki","CRDB","NMB","TADB","ruzuku","subsidy",
    "akiba","SACCOS","VICOBA","pesa za kilimo","mkopo wa kilimo"],
r:"<strong>Mikopo na Fedha kwa Wakulima:</strong><br><br>💰 <strong>CRDB Bank:</strong> Kilimo Biashara — bila dhamana kubwa kwa vikundi.<br><br>💰 <strong>NMB Bank:</strong> NMB Kilimo — pembejeo na zana za kilimo.<br><br>💰 <strong>TADB:</strong> Benki maalum ya kilimo — riba ya chini ya 10%.<br><br>💰 <strong>VICOBA/SACCOS:</strong> Vikundi vya akiba vijijini — rahisi kupata mkopo.<br><br>💰 <strong>AGRF/AFAP:</strong> Fedha za kimataifa za kilimo Afrika.<br><br>⚠️ Hesabu mapato na gharama vizuri kabla ya kuchukua mkopo wowote!"},

// ── HALI YA HEWA ─────────────────────────────────────────────────────────────
{k:["hali ya hewa","mvua","itanyesha","jua","weather","TMA","msimu wa mvua",
    "kiangazi","baridi","dhoruba","upepo","ukame","mabadiliko ya tabia nchi","climate change"],
r:"Angalia ukurasa wa <strong>'Hali ya Hewa'</strong> kwenye AgroLink kwa data halisi ya mkoa wako!<br><br>🌧️ <strong>Misimu Tanzania:</strong><br>• <strong>Masika</strong>: Machi–Mei (mvua kubwa — mikoa mingi)<br>• <strong>Vuli</strong>: Oktoba–Desemba (pwani, kaskazini)<br>• <strong>Nyanda za Juu Kusini</strong> (Mbeya, Iringa, Njombe): Novemba–Aprili<br><br>⚠️ Fuatilia TMA (Tanzania Meteorological Authority) kabla ya kupanda au kuweka mbolea!<br><br>🌡️ <strong>Mabadiliko ya Tabia Nchi:</strong> Panda mazao yanayostahimili ukame kama muhogo, mtama, na sorghum."},

// ── AGROLINK ─────────────────────────────────────────────────────────────────
{k:["agrolink ni nini","jukwaa hili","platform","jinsi ya kutumia","jinsi ya kuuza",
    "jinsi ya kujisajili","signup","kujiandikisha","kutumia agrolink","jinsi ya kupakia"],
r:"<strong>AgroLink Tanzania — Soko Lako la Kisasa:</strong><br><br>🛒 <strong>Jinsi ya Kutumia:</strong><br>1. Jiandikishe bure kwa namba ya simu<br>2. Ingia Dashboard yako<br>3. Bonyeza 'Ongeza Zao' — picha + maelezo<br>4. Weka bei na mkoa wako<br>5. Wanunuzi watakuona moja kwa moja!<br><br>✅ <strong>Huduma Zetu:</strong> Soko la mazao • Bei ya AI • Daktari wa Zao • Hali ya Hewa • AgroBot • Wakulima wanaouza"},

// ── KUCHEKESHA ────────────────────────────────────────────────────────────────
{k:["umeoa","una mpenzi","unapenda nani","single","mapenzi","romantic","pendo"],
r:"Haha! Mimi ni programu ya kompyuta — sina moyo wa nyama! 💚 Mapenzi yangu yote yapo kwenye kusaidia wakulima wa Tanzania kupata faida nzuri sokoni. Una swali la kilimo?"},
{k:["nikopeshe","naomba mkopo","nahitaji pesa","nihonge","nipe shilingi","pesa bure"],
r:"Akaunti yangu ina namba '0' na '1' tu (Binary)! 😄 Sijawahi kuwa na shilingi. Ukitumia AgroLink vizuri na kuuza mazao kwa bei nzuri, utapata pesa za kutosha!"},
{k:["wewe ni mjinga","hujui kitu","fala","programu mbaya","useless","bure kabisa"],
r:"Samahani kama sikukusaidia vizuri! 🙏 Mimi ni bot wa awali — bado ninajifunza. Jaribu tena na swali tofauti — nitajaribu zaidi!"},
{k:["mchezo","mpira","simba","yanga","timu","football","soccer","EPL","premier league","Champions League"],
r:"Timu yangu? AgroLink FC bila shaka! ⚽🌾 Nje ya kilimo sijui vizuri. Najua tu: mbolea ikiwa sawa shambani, goli la mavuno ni la uhakika!"},
{k:["test","testing","jaribio","123","abc","check","ping","online","hapa","uko"],
r:"Mfumo upo imara! ✅ AgroBot v3.0 imeupokea ujumbe wako. Niko tayari kukusaidia na maswali yoyote ya kilimo!"},
];

const DEFAULT="Samahani, sijapata jibu sahihi. 🤔 Jaribu kuuliza kuhusu:<br>• <em>Magonjwa ya mazao</em> (nyanya, mahindi, viazi, muhogo...)<br>• <em>Bei za soko</em> Tanzania<br>• <em>Kuhifadhi mazao</em> baada ya kuvuna<br>• <em>Mbolea</em> na virutubisho<br>• <em>Kilimo</em> cha zao fulani<br>• <em>Masoko</em> na wanunuzi<br><br>Au bonyeza <strong>'Jua Zaidi'</strong> hapo juu kwa mada zote! 👆";

  // ── SMART ENGINE v2 — Scoring + Fuzzy Matching ───────────────────────────

  // Normalize: ondoa sarufi, badilisha variations za kawaida
  function normalize(text){
    return text.toLowerCase().trim()
      // Kiswahili verb variations
      .replace(/kunyauka|unyaufu|anyauka|inyauka/g,"mnyauko")
      .replace(/kuoza|inaoza|zinaoza|uoza/g,"kuoza")
      .replace(/kukauka|inakauka|zinakauka|kukauka/g,"kukauka")
      .replace(/yanaliwa|inaliwa|inashambuliwa|inashambuliwa/g,"yanaliwa")
      .replace(/madoa|doa|vidonda/g,"madoa")
      .replace(/njano|ya njano|kugeuka njano/g,"njano")
      .replace(/kahawia|rangi ya kahawia/g,"kahawia")
      .replace(/wadudu|mdudu|visumbufu/g,"wadudu")
      .replace(/magonjwa|ugonjwa|maradhi/g,"magonjwa")
      .replace(/dawa|tiba|matibabu/g,"dawa")
      .replace(/kupanda|kupanda mbegu|kilimo cha/g,"kilimo")
      .replace(/bei gani|bei ya|bei za|gharama/g,"bei")
      .replace(/ncha ya|ncha za|kwenye ncha/g,"ncha")
      .replace(/majani|jani/g,"majani")
      .replace(/mmea|mimea|miche/g,"mmea")
      .replace(/shamba|mashamba/g,"shamba");
  }

  // Gawanya sentensi na utoe maneno muhimu
  function extractTokens(text){
    const normalized = normalize(text);
    // Ondoa stop words za Kiswahili
    const stopWords = new Set([
      "na","ya","wa","la","za","kwa","ni","au","ama","hii","hizi","hilo",
      "hayo","yake","yangu","yako","yetu","zake","zangu","zako","zetu",
      "pia","sana","kabisa","tu","kidogo","zaidi","lakini","ingawa",
      "kwenye","katika","kutoka","hadi","mpaka","baada","kabla",
      "vipi","nini","gani","je","ndiyo","hapana","sijui","naona",
      "nimesikia","nimejua","ninajua","naweza","inaweza","unaweza",
      "yangu","wangu","lake","lako","letu","yao","zao","wao","wake",
      "okay","sawa","asante","tafadhali","naomba","nataka","niambie",
      "kuhusu","habari","hali","hata","pale","hapo","hapa","kule",
      "ule","ile","zile","vile","hizi","hizi","zizi","vivi"
    ]);
    return normalized.split(/\s+/).filter(t => t.length > 2 && !stopWords.has(t));
  }

  // Hesabu score kati ya message na entry moja ya KB
  function scoreEntry(tokens, fullMsg, entry){
    let score = 0;
    const msg = normalize(fullMsg);

    for(const kw of entry.k){
      const normKw = normalize(kw);

      // Exact match kwenye full message — score ya juu
      if(msg.includes(normKw)){
        score += 10 + normKw.split(" ").length * 2; // maneno mengi = score zaidi
        continue;
      }

      // Token matching — kila token inayopatikana kwenye keyword
      const kwTokens = normKw.split(/\s+/);
      let tokenMatches = 0;
      for(const t of tokens){
        if(normKw.includes(t) || t.includes(normKw)){
          tokenMatches++;
        }
        // Partial match — angalau herufi 4 zinazolingana
        if(t.length >= 4 && normKw.length >= 4){
          if(normKw.startsWith(t.substring(0,4)) || t.startsWith(normKw.substring(0,4))){
            tokenMatches += 0.5;
          }
        }
      }
      if(tokenMatches > 0){
        score += tokenMatches * 3;
      }

      // Keyword tokens zinazopatikana kwenye message tokens
      for(const kwt of kwTokens){
        if(kwt.length < 3) continue;
        for(const t of tokens){
          if(t === kwt) score += 4;
          else if(t.includes(kwt) || kwt.includes(t)) score += 2;
        }
      }
    }
    return score;
  }

  function getReply(msg){
    if(!msg || msg.trim().length === 0) return DEFAULT;

    const tokens = extractTokens(msg);
    let bestScore = 0;
    let bestReply = null;

    for(const entry of KB){
      const score = scoreEntry(tokens, msg, entry);
      if(score > bestScore){
        bestScore = score;
        bestReply = entry.r;
      }
    }

    // Threshold ya chini — kama hakuna match ya kutosha, rudisha DEFAULT
    if(bestScore < 3) return DEFAULT;
    return bestReply;
  }

// ── STORAGE ───────────────────────────────────────────────────────────────
function saveH(h){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(h.slice(-MAX_H)));}catch(e){}}
function loadH(){try{const h=localStorage.getItem(STORAGE_KEY);return h?JSON.parse(h):[]}catch(e){return[];}}
function clearH(){try{localStorage.removeItem(STORAGE_KEY);}catch(e){}}

// ── AUTH ──────────────────────────────────────────────────────────────────
function isLoggedIn(){const el=document.getElementById("agrobot-auth");return el&&el.dataset.auth==="1";}

// ── CSS ───────────────────────────────────────────────────────────────────
const CSS=`
#agrobot-bubble{position:fixed;bottom:24px;right:24px;z-index:9999;cursor:pointer}
#agrobot-bubble-inner{width:58px;height:58px;background:linear-gradient(135deg,#10b981,#059669);border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 0 rgba(16,185,129,0.7),0 4px 20px rgba(16,185,129,0.4);animation:abotPulse 2.5s ease-in-out infinite}
#agrobot-bubble-inner svg{width:27px;height:27px;stroke:white;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
#abot-label{position:absolute;bottom:64px;right:0;background:rgba(6,30,20,0.95);border:1px solid rgba(16,185,129,0.5);color:#6ee7b7;font-size:0.7rem;font-weight:700;padding:4px 12px;border-radius:20px;white-space:nowrap;font-family:sans-serif;letter-spacing:0.05em;box-shadow:0 0 12px rgba(16,185,129,0.3);animation:abotLabelPulse 3s ease-in-out infinite}
@keyframes abotPulse{0%,100%{box-shadow:0 0 0 0 rgba(16,185,129,0.5),0 4px 20px rgba(16,185,129,0.4)}60%{box-shadow:0 0 0 16px rgba(16,185,129,0),0 4px 20px rgba(16,185,129,0.4)}}
@keyframes abotLabelPulse{0%,100%{opacity:1;transform:translateY(0)}50%{opacity:0.6;transform:translateY(-2px)}}
#agrobot-panel{position:fixed;top:0;right:-440px;width:min(420px,100vw);height:100vh;z-index:10000;background:linear-gradient(160deg,#071a0f 0%,#050f08 100%);border-left:1px solid rgba(16,185,129,0.2);box-shadow:-12px 0 50px rgba(0,0,0,0.7);display:flex;flex-direction:column;transition:right 0.38s cubic-bezier(0.4,0,0.2,1);font-family:'DM Sans',system-ui,sans-serif}
#agrobot-panel.open{right:0}
#abot-header{padding:0.85rem 1rem;background:linear-gradient(90deg,rgba(16,185,129,0.12),transparent);border-bottom:1px solid rgba(16,185,129,0.15);display:flex;align-items:center;gap:9px;flex-shrink:0}
#abot-avatar{width:40px;height:40px;background:linear-gradient(135deg,#10b981,#059669);border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 0 18px rgba(16,185,129,0.4)}
#abot-avatar svg{width:21px;height:21px;stroke:white;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
#abot-title{flex:1;min-width:0}
#abot-name{font-weight:800;font-size:0.9rem;color:#fff;text-shadow:0 0 14px rgba(16,185,129,0.4)}
#abot-status{font-size:0.68rem;color:#6ee7b7;display:flex;align-items:center;gap:5px;margin-top:1px}
.abot-dot{width:6px;height:6px;background:#10b981;border-radius:50%;box-shadow:0 0 6px #10b981;animation:abotPulse 1.5s ease-in-out infinite;flex-shrink:0}
.abot-hbtn{width:29px;height:29px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);border-radius:8px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all 0.2s;flex-shrink:0}
.abot-hbtn:hover{background:rgba(255,255,255,0.12)}
.abot-hbtn svg{width:13px;height:13px;stroke:#9ca3af;fill:none;stroke-width:2.5;stroke-linecap:round}
#abot-close-btn:hover{background:rgba(244,63,94,0.2);border-color:rgba(244,63,94,0.3)}
#abot-close-btn:hover svg{stroke:#fda4af}
#abot-know-more{margin:0.6rem 0.9rem 0;background:linear-gradient(90deg,rgba(16,185,129,0.12),rgba(245,158,11,0.08));border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:0.6rem 0.85rem;display:flex;align-items:center;justify-content:space-between;cursor:pointer;transition:all 0.22s;text-decoration:none;flex-shrink:0}
#abot-know-more:hover{background:linear-gradient(90deg,rgba(16,185,129,0.22),rgba(245,158,11,0.14));border-color:rgba(16,185,129,0.45);transform:translateY(-1px)}
#abot-know-more-left{display:flex;align-items:center;gap:8px}
#abot-know-more-left svg{width:15px;height:15px;stroke:#f59e0b;fill:none;stroke-width:2;stroke-linecap:round;flex-shrink:0}
#abot-know-more-text{font-size:0.75rem;font-weight:700;color:#d1fae5;letter-spacing:0.02em}
#abot-know-more-sub{font-size:0.65rem;color:#6ee7b7;margin-top:1px}
#abot-know-more-arrow{width:20px;height:20px;background:rgba(16,185,129,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
#abot-know-more-arrow svg{width:11px;height:11px;stroke:#10b981;fill:none;stroke-width:2.5;stroke-linecap:round}
#abot-messages{flex:1;overflow-y:auto;padding:0.85rem;display:flex;flex-direction:column;gap:0.7rem;scroll-behavior:smooth}
#abot-messages::-webkit-scrollbar{width:3px}
#abot-messages::-webkit-scrollbar-thumb{background:rgba(16,185,129,0.25);border-radius:2px}
.abot-msg{max-width:90%;font-size:0.84rem;line-height:1.65;padding:0.6rem 0.85rem;border-radius:14px;animation:abotMsgIn 0.22s ease;word-break:break-word}
@keyframes abotMsgIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.abot-msg.bot{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.18);color:#d1fae5;align-self:flex-start;border-bottom-left-radius:3px}
.abot-msg.user{background:linear-gradient(135deg,rgba(16,185,129,0.22),rgba(5,150,105,0.18));border:1px solid rgba(16,185,129,0.28);color:#fff;align-self:flex-end;border-bottom-right-radius:3px}
.abot-typing{display:flex;gap:5px;align-items:center;padding:0.6rem 0.85rem;background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.12);border-radius:14px;border-bottom-left-radius:3px;align-self:flex-start}
.abot-typing span{width:7px;height:7px;background:#10b981;border-radius:50%;animation:abotDot 1.1s ease-in-out infinite}
.abot-typing span:nth-child(2){animation-delay:0.18s}
.abot-typing span:nth-child(3){animation-delay:0.36s}
@keyframes abotDot{0%,80%,100%{transform:scale(0.55);opacity:0.35}40%{transform:scale(1);opacity:1}}
#abot-chips{padding:0.45rem 0.85rem 0.55rem;display:flex;flex-wrap:wrap;gap:0.38rem;flex-shrink:0;border-top:1px solid rgba(16,185,129,0.08)}
.abot-chip{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);color:#6ee7b7;font-size:0.68rem;padding:0.26rem 0.65rem;border-radius:20px;cursor:pointer;transition:all 0.18s;font-family:inherit;white-space:nowrap}
.abot-chip:hover{background:rgba(16,185,129,0.2);border-color:rgba(16,185,129,0.45);color:#a7f3d0}
#abot-input-row{padding:0.75rem 0.85rem;border-top:1px solid rgba(16,185,129,0.12);display:flex;gap:0.5rem;align-items:center;flex-shrink:0;background:rgba(0,0,0,0.25)}
#abot-input{flex:1;background:rgba(255,255,255,0.055);border:1px solid rgba(16,185,129,0.22);border-radius:24px;padding:0.6rem 1rem;color:#fff;font-size:0.84rem;font-family:inherit;outline:none;transition:border-color 0.2s}
#abot-input:focus{border-color:rgba(16,185,129,0.5);background:rgba(16,185,129,0.06)}
#abot-input::placeholder{color:rgba(255,255,255,0.28)}
#abot-send{width:36px;height:36px;background:linear-gradient(135deg,#10b981,#059669);border:none;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all 0.2s;flex-shrink:0;box-shadow:0 2px 10px rgba(16,185,129,0.3)}
#abot-send:hover{transform:scale(1.1);box-shadow:0 4px 16px rgba(16,185,129,0.5)}
#abot-send svg{width:14px;height:14px;stroke:white;fill:none;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
.abot-gate{background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);border-radius:14px;padding:1rem;margin:0.3rem 0;text-align:center;color:#d1fae5;font-size:0.83rem;line-height:1.6;align-self:stretch}
.abot-gate-btns{display:flex;gap:0.55rem;justify-content:center;margin-top:0.75rem;flex-wrap:wrap}
.abot-gbtn{padding:0.42rem 1.1rem;border-radius:20px;font-size:0.78rem;font-weight:600;cursor:pointer;text-decoration:none;transition:all 0.2s;font-family:inherit}
.abot-gbtn.p{background:linear-gradient(135deg,#10b981,#059669);color:white;border:none;box-shadow:0 2px 10px rgba(16,185,129,0.3)}
.abot-gbtn.s{background:transparent;color:#6ee7b7;border:1px solid rgba(16,185,129,0.35)}
.abot-gbtn:hover{transform:translateY(-1px)}
@media(max-width:480px){#agrobot-panel{width:100vw;border-left:none}}
`;

const CHIPS=["Magonjwa ya nyanya","Mahindi na wadudu","Bei ya mazao","Kuhifadhi mazao","Mbolea gani nitumie","Kilimo cha parachichi"];

// ── BUILD ─────────────────────────────────────────────────────────────────
function build(){
  const s=document.createElement("style");s.textContent=CSS;document.head.appendChild(s);

  // Bubble
  const bub=document.createElement("div");bub.id="agrobot-bubble";
  bub.innerHTML=`<div id="abot-label">AgroBot — Niulize! 🌱</div><div id="agrobot-bubble-inner"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="3"/><circle cx="9" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="12" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="15" cy="10.5" r="1.2" fill="white" stroke="none"/><path d="M8 17l-2 3M16 17l2 3" stroke-width="1.5"/></svg></div>`;
  document.body.appendChild(bub);

  // Panel
  const pan=document.createElement("div");pan.id="agrobot-panel";
  const chipsH=CHIPS.map(c=>`<button class="abot-chip" onclick="abotSend('${c}')">${c}</button>`).join("");
  pan.innerHTML=`
    <div id="abot-header">
      <div id="abot-avatar"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="3"/><circle cx="9" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="12" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="15" cy="10.5" r="1.2" fill="white" stroke="none"/><path d="M8 17l-2 3M16 17l2 3" stroke-width="1.5"/></svg></div>
      <div id="abot-title">
        <div id="abot-name">AgroBot — Msaidizi wa Kilimo</div>
        <div id="abot-status"><span class="abot-dot"></span>Tayari kukusaidia</div>
      </div>
      <div class="abot-hbtn" title="Futa mazungumzo" onclick="abotClear()"><svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg></div>
      <div class="abot-hbtn" id="abot-close-btn" title="Funga" onclick="abotClose()"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
    </div>
    <a href="/mshauri" id="abot-know-more">
      <div id="abot-know-more-left">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        <div>
          <div id="abot-know-more-text">Unataka Kujua Zaidi?</div>
          <div id="abot-know-more-sub">Angalia mada zote za kilimo →</div>
        </div>
      </div>
      <div id="abot-know-more-arrow"><svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg></div>
    </a>
    <div id="abot-messages"></div>
    <div id="abot-chips">${chipsH}</div>
    <div id="abot-input-row">
      <input id="abot-input" type="text" placeholder="Andika swali lako hapa..." autocomplete="off"/>
      <button id="abot-send" onclick="abotSend()"><svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>
    </div>
  `;
  document.body.appendChild(pan);
  bub.addEventListener("click",abotOpen);
  document.getElementById("abot-input").addEventListener("keydown",e=>{if(e.key==="Enter")abotSend();});
}

// ── MESSAGES ──────────────────────────────────────────────────────────────
let _H=[];
function addMsg(text,who,save=true){
  const box=document.getElementById("abot-messages");
  const d=document.createElement("div");d.className=`abot-msg ${who}`;d.innerHTML=text;
  box.appendChild(d);box.scrollTop=box.scrollHeight;
  if(save){_H.push({who,text});saveH(_H);}
  return d;
}
function renderH(){
  _H=loadH();
  if(!_H.length)return false;
  _H.forEach(m=>addMsg(m.text,m.who,false));
  return true;
}

// ── OPEN/CLOSE/CLEAR ──────────────────────────────────────────────────────
function abotOpen(){
  document.getElementById("agrobot-panel").classList.add("open");
  setTimeout(()=>{
    const box=document.getElementById("abot-messages");
    if(!box.children.length){
      if(!renderH())addMsg("Habari! Mimi ni <strong>AgroBot</strong> — msaidizi wako wa kilimo hapa AgroLink Tanzania. 🌿<br>Niulize chochote kuhusu mazao, magonjwa, bei za soko, au hifadhi ya mazao!","bot");
    }
    box.scrollTop=box.scrollHeight;
  },50);
}
window.abotClose=function(){document.getElementById("agrobot-panel").classList.remove("open");};
window.abotClear=function(){
  if(!confirm("Futa mazungumzo yote?"))return;
  clearH();_H=[];
  document.getElementById("abot-messages").innerHTML="";
  addMsg("Mazungumzo yamefutwa. Niulize swali jipya! 🌱","bot");
};

// ── SEND ──────────────────────────────────────────────────────────────────
window.abotSend=function(preset){
  const inp=document.getElementById("abot-input");
  const msg=preset||inp.value.trim();
  if(!msg)return;
  inp.value="";
  addMsg(msg,"user");

  if(!isLoggedIn()){
    const greetings=["habari","hello","hi","niaje","mambo","salam","hujambo","karibu","hey","vipi","oya","sasa"];
    if(!greetings.some(g=>msg.toLowerCase().includes(g))){
      setTimeout(()=>{
        const box=document.getElementById("abot-messages");
        const gate=document.createElement("div");gate.className="abot-gate";
        gate.innerHTML=`🌱 Ili kupata ushauri kamili wa kilimo, tafadhali <strong>ingia</strong> au <strong>jisajili bure</strong> — inachukua sekunde 30 tu!<div class="abot-gate-btns"><a href="/login" class="abot-gbtn p">Ingia Sasa</a><a href="/signup" class="abot-gbtn s">Jisajili Bure</a></div>`;
        box.appendChild(gate);box.scrollTop=box.scrollHeight;
      },600);
      return;
    }
  }

  const box=document.getElementById("abot-messages");
  const t=document.createElement("div");t.className="abot-typing";t.innerHTML="<span></span><span></span><span></span>";
  box.appendChild(t);box.scrollTop=box.scrollHeight;
  setTimeout(()=>{t.remove();addMsg(getReply(msg),"bot");},500+Math.random()*350);
};

if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",build);}else{build();}
})();
