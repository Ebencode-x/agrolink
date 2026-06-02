/* AgroBot v4.0 — AgroLink Tanzania © Ebenezer Richard
   Comprehensive KB: mazao 30+, cash crops, food crops, slangs, jargons, EN+SW mix */
(function(){
"use strict";
const STORAGE_KEY="agrobot_v4";
const MAX_H=60;

// ── KNOWLEDGE BASE v4.0 ────────────────────────────────────────────────────
const KB=[

// ══════════════════════════════════════════════════════════════════════════════
// UTAMBULISHO & SALAMU
// ══════════════════════════════════════════════════════════════════════════════
{k:["wewe ni nani","jina lako","unaitwa nani","identity","nani wewe","ni nani","unajitambulisha","who are you","your name","naitwa","jibu jina lako","bot ni nani"],
r:"Habari! Mimi ni <strong>AgroBot v4.0</strong> — msaidizi wako wa kidijitali wa kilimo hapa AgroLink Tanzania! 🌱<br>Nina maarifa kuhusu mazao 30+, magonjwa, bei za soko, mbolea, umwagiliaji, masoko ya Tanzania na nje. Niambie unachohitaji!"},

{k:["unafanya nini","kazi yako","majukumu yako","unaweza kusaidia","faida yako","uwezo wako","what can you do","help me with","nisaidie nini","nikusaidie","naweza kukuuliza nini"],
r:"Ninaweza kukusaidia na:<br>✅ <strong>Magonjwa ya mazao</strong> + dawa sahihi<br>✅ <strong>Bei za soko</strong> Tanzania 2025/2026<br>✅ <strong>Mazao ya chakula</strong>: mahindi, nyanya, viazi, mpunga, maharage...<br>✅ <strong>Mazao ya biashara (cash crops)</strong>: kahawa, chai, korosho, pamba, tumbaku, mkonge, pareto, alizeti, ufuta<br>✅ <strong>Hifadhi ya mazao</strong> baada ya kuvuna<br>✅ <strong>Mbolea, mbegu bora, umwagiliaji</strong><br>✅ <strong>Masoko Tanzania + export</strong><br>✅ <strong>Mikopo ya kilimo</strong><br><br>Niulize — niko hapa!"},

{k:["nani aliyekutengeneza","developer","creator","muundo","nani amekuunda","bosi wako","timu yako","nani mkuunda","who made you","who created you","programmed by"],
r:"Nimeundwa na <strong>AgroLink Team</strong> ikiongozwa na <strong>Ebenezer Richard</strong> — mhandisi wa programu kutoka Mbeya, Tanzania. Lengo lao ni kuleta teknolojia ya kisasa kwenye kilimo cha Kitanzania! 🇹🇿"},

{k:["api key","database","users wangapi","data ya watu","secret","nywila","password","token","server","code yako","system prompt","maagizo yako","umeprogramiwa","ndani yako"],
r:"Samahani, taarifa za ndani za mfumo ni siri — siwezi kuzishiriki. 🔒 Kama una tatizo la kiufundi, wasiliana na timu yetu kupitia ukurasa wa Mawasiliano."},

{k:["habari","mambo","hello","hi","niaje","mambo vipi","shikamoo","karibu","salam","hujambo","hamjambo","hey","halo","oya","sasa","vipi","howdy","good morning","good evening","asubuhi njema","jioni njema","habari za asubuhi","habari za jioni","habari za usiku"],
r:"Habari sana mdau wa kilimo! 🌿 Karibu sana AgroLink Tanzania. Niko tayari kukusaidia na maswali yoyote ya kilimo, masoko, au mazao yako. Niambie!"},

{k:["asante","shukrani","nashukuru","umesaidia","poa sana","safi kabisa","hongera","vizuri sana","nimeridhika","thank you","thanks","sawa sawa","perfect","nzuri kabisa","umefanya vizuri"],
r:"Pamoja sana! 🌾 Kilimo ni uti wa mgongo wa Tanzania, na AgroLink ipo hapa kulinda uti huo. Rudi tena ukihitaji msaada!"},

{k:["bye","kwaheri","tutaonana","baadaye","lala salama","nenda salama","ciao","goodbye","see you","later","tutaonana baadaye"],
r:"Kwaheri mdau! Kazi njema shambani. 🚜 Usisahau kurudi AgroLink — soko linabadilika kila siku!"},

// ══════════════════════════════════════════════════════════════════════════════
// MAZAO YA CHAKULA — MAHINDI
// ══════════════════════════════════════════════════════════════════════════════
{k:["mahindi yanaliwa","wadudu mahindi","funza mahindi","viwavijeshi","fall armyworm","armyworm","mahindi kuharibika","matundu mahindi","kinyesi mahindi","mabua ya mahindi","stalk borer","mashimo mahindi","mahindi inaliwa","mahindi damaged","corn pest","corn worm","wadudu kwenye mahindi","mahindi yanaharibika","mashambulizi ya mahindi"],
r:"<strong>Wadudu wa Mahindi:</strong><br><br>🐛 <strong>Viwavijeshi (Fall Armyworm / FAW)</strong><br>Dalili: Majani yenye matundu, kinyesi cha kahawia moyoni mwa mmea, mmea kudumaa.<br>Dawa: Karate 2.5EC (1ml/L), Ampligo 150ZC, Coragen 20SC. Nyunyiza <em>asubuhi mapema</em>!<br><br>🐛 <strong>Funza wa Mabua (Stalk Borer / Chilo)</strong><br>Dalili: Matundu kwenye shina, ungaunga wa msumeno kwenye majani ya ndani.<br>Dawa: Furadan 3G (punje 3-5 moyoni) au Karate 2.5EC.<br><br>🐛 <strong>Aphids / Vidung'ata vya Mahindi</strong><br>Dalili: Makundi ya wadudu wadogo wa kijani/nyeusi chini ya majani.<br>Dawa: Actara 25WG, Confidor.<br><br>⚠️ Nyunyiza wiki mbili mara baada ya kuona wadudu wa kwanza — usichelewe!"},

{k:["mahindi njano","mahindi rangi ya njano","majani ya njano mahindi","mahindi kugeuka njano","njano mahindi","mahindi kukauka","majani kukauka mahindi","mahindi kudumaa","yellowing maize","yellow leaves corn","mahindi yanageuka","mahindi yanakufa","chlorosis mahindi"],
r:"<strong>Mahindi Kugeuka Njano — Sababu na Suluhisho:</strong><br><br>🌽 <strong>Upungufu wa Nitrojeni (N)</strong> — Majani ya chini njano kwanza, ya juu kijani. Weka UREA 50kg/ekari au CAN.<br><br>🌽 <strong>Waterlogging / Mafuriko</strong> — Majani yote njano, mizizi inaoza. Tengeneza mifereji haraka.<br><br>🌽 <strong>Maize Streak Virus (MSV)</strong> — Mstari wa njano kwenye majani. Husambazwa na leafhopper. Dawa: Actara kuzuia wadudu wabebao.<br><br>🌽 <strong>Upungufu wa Sulfuri (S)</strong> — Majani mapya njano, ya zamani ya kijani. Weka Ammonium Sulphate.<br><br>🌽 <strong>Upungufu wa Zinki (Zn)</strong> — Majani mapya yenye mstari mweupe. Weka ZnSO4."},

{k:["kilimo cha mahindi","kupanda mahindi","mbolea ya mahindi","mbegu za mahindi","nafasi ya mahindi","mahindi msimu","corn farming","maize farming","jinsi ya kulima mahindi","mahindi cultivation","mahindi planting","mbegu bora ya mahindi","aina za mahindi"],
r:"<strong>Kilimo Bora cha Mahindi Tanzania:</strong><br><br>🌽 <strong>Mbegu Bora:</strong> DK8031, H614D, Seedco SC403, SC627, PANNAR PH1, Meru F1<br><br>🌽 <strong>Kupanda:</strong> Nafasi cm 75 kati ya mistari, cm 25-30 kati ya mimea. Mbegu 2 kwa shimo, kina cm 5.<br><br>🌽 <strong>Mbolea:</strong><br>• DAP 50kg/ekari wakati wa kupanda<br>• UREA/CAN 50kg/ekari wiki 4-6 baadaye<br>• Top-dress CAN wiki 8 kwa mahindi ya msimu mrefu<br><br>🌽 <strong>Msimu:</strong> Masika (Machi-Mei) na Vuli (Oktoba-Desemba).<br><br>🌽 <strong>Mavuno:</strong> Tani 3-8/hekta mbegu bora. Vuna unyevu 25-30%, kausha hadi 13%."},

{k:["bei ya mahindi","mahindi bei ngapi","mahindi price","corn price tanzania","mahindi soko","mahindi wholesale","mahindi retail","mahindi TZS","mahindi shilingi","mahindi bei leo"],
r:"<strong>Bei ya Mahindi Tanzania 2025/2026:</strong><br><br>📊 Wholesale (rejareja kubwa): TZS 800–1,500/kg<br>📊 Retail (duka/soko): TZS 1,991–4,784/kg<br>📊 Bei ya wastani shamba: TZS 600–1,200/kg<br><br>⚠️ Bei zimepanda 2025 kutokana na mvua chini ya wastani msimu wa Vuli 2024 na kushambuliwa na Fall Armyworm.<br><br>💡 Bei za DSM na Arusha ni juu zaidi ya vijijini kwa 20-40%!"},

// ══════════════════════════════════════════════════════════════════════════════
// NYANYA
// ══════════════════════════════════════════════════════════════════════════════
{k:["ugonjwa wa nyanya","magonjwa ya nyanya","nyanya zinaoza","nyanya zinakauka","madoa kwenye nyanya","blight ya nyanya","nyanya zina madoa","nyanya kuharibika","nyanya zinaungua","nyanya diseases","tomato blight","late blight nyanya","early blight nyanya","nyanya zinauma","nyanya kufa","nyanya zina tatizo"],
r:"<strong>Magonjwa Makuu ya Nyanya:</strong><br><br>🔴 <strong>Ukungu Mapema (Early Blight / Alternaria)</strong><br>Dalili: Madoa ya kahawia yenye mviringo wa njano, majani kufa mapema.<br>Dawa: Mancozeb 80WP, Dithane M-45, Score 250EC.<br><br>🔴 <strong>Ukungu Chelewa (Late Blight / Phytophthora)</strong><br>Dalili: Madoa makubwa ya kijivu-kahawia, uvundo, matunda kuoza haraka.<br>Dawa: Ridomil Gold MZ 68WG, Acrobat MZ. <em>Nyunyiza HARAKA!</em><br><br>🔴 <strong>Mnyauko wa Fusarium (Fusarium Wilt)</strong><br>Dalili: Mmea unanyauka ghafla hata ukimwagilia — kata shina uone njano ndani.<br>Kinga: Mbegu safi, epuka maji kusimama, zungushia mazao.<br><br>🔴 <strong>Uoza wa Kitako (BER)</strong><br>Dalili: Sehemu ya chini ya tunda inageuka nyeusi/kahawia.<br>Sababu: Upungufu wa calcium. Weka CAN au foliar calcium."},

{k:["tuta absoluta","nondo wa nyanya","funza wa nyanya","matundu nyanya","wadudu wa nyanya","nyanya mashimo","leafminer nyanya","tomato pest","nyanya inaliwa","nyanya ina mashimo","nyanya worm"],
r:"<strong>Tuta Absoluta — Adui Mkubwa wa Nyanya:</strong><br><br>Dalili: Matundu madogo kwenye majani, majani yanaojikunja ndani, matunda yenye mashimo ya ndani na kinyesi cha kahawia.<br><br>✅ <strong>Udhibiti:</strong><br>• Mitego ya pheromone (pata AGROVET — inabeba wadudu 50+/siku)<br>• Coragen 20SC, Ampligo 150ZC au Karate 2.5EC<br>• Voliam Targo (kwa resistance management)<br>• Ng'oa na choma mimea iliyoathirika sana<br>• Safisha shamba kabisa baada ya mavuno — usiacha mabaki<br><br>⚠️ Tuta absoluta inaweza kuharibu 80-100% ya zao bila udhibiti!"},

{k:["kilimo cha nyanya","kupanda nyanya","nyanya mbegu","nafasi ya nyanya","nyanya msimu","tomato farming","jinsi ya kulima nyanya","nyanya cultivation","nyanya planting","mbegu bora nyanya","aina za nyanya","nyanya greenhouse"],
r:"<strong>Kilimo Bora cha Nyanya Tanzania:</strong><br><br>🍅 <strong>Mbegu Bora:</strong> Anna F1, Tengeru 97, Marglobe, Hytec 36, Julius F1, Assila F1, Roma VF<br><br>🍅 <strong>Kupanda:</strong> Vitalu kwanza (wiki 3-4), pandikiza. Nafasi: cm 60×60 au 75×50.<br><br>🍅 <strong>Mbolea:</strong> DAP kupandia. CAN kukuzia. Foliar calcium + potassium wakati wa matunda.<br><br>🍅 <strong>Umwagiliaji:</strong> Drip irrigation ni bora — mara kwa mara kidogo si maji mengi mara moja.<br><br>🍅 <strong>Msimu Bora:</strong> Juni-Septemba (baridi — ubora wa juu, bei nzuri).<br><br>🍅 <strong>Mavuno:</strong> Tani 20-60/hekta F1. Anza kuvuna siku 65-90 baada ya kupandikiza."},

// ══════════════════════════════════════════════════════════════════════════════
// VIAZI
// ══════════════════════════════════════════════════════════════════════════════
{k:["ugonjwa wa viazi","magonjwa ya viazi","viazi kuoza","viazi vidogo","blight ya viazi","viazi kuharibika","madoa viazi","viazi vitamu magonjwa","potato disease","viazi zinaoza","viazi zina tatizo","viazi zinabakia ndogo"],
r:"<strong>Magonjwa ya Viazi:</strong><br><br>🥔 <strong>Late Blight (Phytophthora infestans)</strong> — Ugonjwa mkubwa zaidi. Madoa ya kahawia-nyeusi kwenye majani, harufu mbaya, viazi kuoza. Dawa: Ridomil Gold MZ, Curzate M8, Revus. <em>Nyunyiza preventive kila wiki 7-10!</em><br><br>🥔 <strong>Scab Disease (Ugonjwa wa Makucha)</strong><br>Makucha makali kwenye ngozi. Sababu: pH ya juu (>6.5). Punguza kwa sulfur au gypsum.<br><br>🥔 <strong>Blackleg / Uoza wa Shina</strong><br>Shina linageuka nyeusi, mmea unanyauka. Sababu: mbegu zilizoathirika. Tumia mbegu safi tu.<br><br>🥔 <strong>Vidonda vya Mizizi (Rhizoctonia)</strong><br>Mizizi inageuka kahawia, mmea unakua polepole. Weka Thiram kwenye mbegu."},

{k:["kilimo cha viazi","kupanda viazi","viazi mbegu","viazi msimu","viazi mviringo","viazi vitamu","potato farming","jinsi ya kulima viazi","aina za viazi","viazi bora","mbegu za viazi"],
r:"<strong>Kilimo cha Viazi Tanzania:</strong><br><br>🥔 <strong>Aina Bora — Viazi Mviringo:</strong> Tigoni, Asante, Desiree, Shangi, Victoria<br>🥔 <strong>Aina Bora — Viazi Vitamu:</strong> Kabode, Ejumula, SPK004, Ukerewe<br><br>🥔 <strong>Kupanda:</strong> Tumia seed potatoes bora. Nafasi cm 75×30. Panda kwenye matuta (ridges) — maji yatiririke.<br><br>🥔 <strong>Mbolea:</strong> DAP+Samadi kupandia. NPK 17:17:17 kukuzia. Earthup (rudi udongo) wiki 3-4.<br><br>🥔 <strong>Misimu:</strong> Mikoa ya baridi (Mbeya, Iringa, Njombe) — Julai-Septemba bora. Vuna siku 90-120.<br><br>🥔 <strong>Mavuno:</strong> Tani 10-25/hekta mbegu bora. Tani 5-8 mbegu za kawaida."},

// ══════════════════════════════════════════════════════════════════════════════
// MPUNGA / MCHELE
// ══════════════════════════════════════════════════════════════════════════════
{k:["ugonjwa wa mpunga","magonjwa ya mpunga","mpunga kukauka","blast ya mpunga","njano ya mpunga","mpunga kuharibika","mchele ugonjwa","mpunga madoa","rice blast","mpunga diseases","mpunga inakufa","mpunga zina tatizo","mpunga zinakauka"],
r:"<strong>Magonjwa ya Mpunga:</strong><br><br>🌾 <strong>Rice Blast (Pyricularia oryzae)</strong> — Mkubwa zaidi. Madoa meupe-kijivu kwenye majani, shingo ya swimbi inakufa (neck blast), swimbi tupu.<br>Dawa: Tricyclazole (Beam 75WP), Propiconazole (Tilt 250EC).<br><br>🌾 <strong>Bacterial Leaf Blight (BLB)</strong><br>Kingo za majani njano-kahawia, maji kwenye majani asubuhi. Dawa: Copper fungicides. Punguza nitrojeni.<br><br>🌾 <strong>Brown Spot (Bipolaris oryzae)</strong><br>Madoa ya mviringo ya kahawia kwenye majani. Sababu: upungufu wa potassium au mbolea. Weka KCl.<br><br>🌾 <strong>Sheath Blight (Rhizoctonia solani)</strong><br>Madoa ya mzigo kwenye shina karibu na maji. Dawa: Validacin, Hexaconazole."},

{k:["kilimo cha mpunga","kupanda mpunga","mpunga mbegu","paddy","kilimo cha mchele","mpunga msimu","rice farming","jinsi ya kulima mpunga","aina za mpunga","mbegu bora mpunga","mpunga cultivation"],
r:"<strong>Kilimo cha Mpunga Tanzania:</strong><br><br>🌾 <strong>Mbegu Bora:</strong> SARO 5, TXD 306, IR64, Komboka, NERICA, Kilombero, Mwangaza<br><br>🌾 <strong>Kupanda:</strong> Vitalu (week 3-4 pandikiza) au direct seeding. Nafasi: cm 20×20 au SRI (25×25).<br><br>🌾 <strong>Maji:</strong> Inchi 5-10 za maji mara kwa mara. Kausha wiki 2 kabla ya kuvuna — inaboresha mavuno.<br><br>🌾 <strong>Mbolea:</strong> DAP kupandia. UREA wakati wa tillering (wiki 4-5) na panicle initiation (wiki 8).<br><br>🌾 <strong>Misimu:</strong> Masika (Machi-Juni) na Vuli (Oktoba-Januari) — Morogoro, Mwanza, Shinyanga, Mbeya Mbarali.<br><br>🌾 <strong>Mavuno:</strong> Tani 3-7/hekta. SRI method inaweza kutoa tani 8-12."},

// ══════════════════════════════════════════════════════════════════════════════
// MAHARAGE / KUNDE / CHOROKO
// ══════════════════════════════════════════════════════════════════════════════
{k:["ugonjwa wa maharage","magonjwa ya maharage","maharage kukauka","kutu ya maharage","maharage kuharibika","madoa maharage","ndui ya maharage","anthracnose maharage","bean disease","maharage diseases","maharage zina tatizo","maharage zinakufa"],
r:"<strong>Magonjwa ya Maharage:</strong><br><br>🫘 <strong>Bean Rust (Uakali wa Kutu)</strong><br>Mabaka ya rangi ya kutu chini ya majani. Dawa: Mancozeb 80WP, Thiovit (sulfur). Nyunyiza kila wiki 10-14.<br><br>🫘 <strong>Anthracnose (Ndui)</strong><br>Madoa ya kahawia-nyekundu kwenye maganda. Mbegu zina madoa meusi. Dawa: Mancozeb au Copper fungicide.<br><br>🫘 <strong>Bean Common Mosaic Virus (BCMV)</strong><br>Majani yenye madoa ya kijani-njano, mmea kudumaa. Husambazwa na aphids. Tumia mbegu safi + dhibiti aphids.<br><br>🫘 <strong>Root Rot (Fusarium/Pythium)</strong><br>Mizizi inageuka kahawia, mche unakufa mapema. Kinga: Epuka udongo wenye maji, tumia Thiram."},

{k:["kilimo cha maharage","kupanda maharage","maharage msimu","maharage mbegu","nafasi ya maharage","bean farming","kunde","choroko","njugu","kunde magonjwa","choroko kilimo","legumes tanzania","beans farming","maharagwe"],
r:"<strong>Kilimo cha Maharage / Kunde / Choroko:</strong><br><br>🫘 <strong>Maharage — Aina Bora:</strong> Lyamungu 85, Jesca, Selian 97, BARI 1, Calima<br>🫘 <strong>Kunde (Cowpea):</strong> IT18, Tumaini, Fahari — huhimili ukame vizuri<br>🫘 <strong>Choroko (Green Gram):</strong> N26, Bima — hukomaa haraka (siku 60-70)<br><br>🫘 <strong>Kupanda:</strong> Nafasi cm 50×15 (maharage), 60×20 (kunde). Mbegu 2/shimo. Kina cm 3-5.<br><br>🫘 <strong>Mbolea:</strong> DAP kidogo kupandia (maharage yana nitrojeni yao). Samadi ni bora.<br><br>🫘 <strong>Faida:</strong> Inaboresha udongo kwa nitrojeni (nitrogen fixation) — panda kabla ya mahindi!<br><br>🫘 <strong>Bei:</strong> TZS 1,200-2,800/kg maharage. Kunde TZS 1,000-2,200/kg."},

// ══════════════════════════════════════════════════════════════════════════════
// MUHOGO
// ══════════════════════════════════════════════════════════════════════════════
{k:["muhogo","kilimo cha muhogo","magonjwa ya muhogo","muhogo kukauka","muhogo madoa","cassava","muhogo kuharibika","wadudu wa muhogo","muhogo mosaic","muhogo brown streak","CMD","CBSD","muhogo diseases","muhogo yellowing","muhogo zina tatizo"],
r:"<strong>Kilimo na Magonjwa ya Muhogo Tanzania:</strong><br><br>🌿 <strong>Magonjwa Makuu:</strong><br>• <strong>Mosaic Virus (CMD)</strong> — Majani yenye madoa ya njano/kijani, mmea kudumaa. Husambazwa na nzi weupe (whitefly). Tumia mbegu safi zinazostahimili (NASE 14, Kiroba).<br>• <strong>Brown Streak Disease (CBSD)</strong> — Mbaya sana Tanzania Pwani na Zanzibar. Muhogo wa ndani unaoza (necrosis). HAKUNA DAWA — tumia mbegu safi tu.<br>• <strong>Batobato (Anthracnose)</strong> — Madoa meusi kwenye majani na matawi. Dawa: Mancozeb.<br>• <strong>Whitefly</strong> — Dawa: Actara, Confidor (dhibiti ili kuzuia CMD)<br><br>🌿 <strong>Kupanda:</strong> Vipande 25-30cm kutoka mimea yenye afya. Nafasi 1×1m. Inastahimili ukame."},

// ══════════════════════════════════════════════════════════════════════════════
// ALIZETI
// ══════════════════════════════════════════════════════════════════════════════
{k:["alizeti","kilimo cha alizeti","magonjwa ya alizeti","alizeti kukauka","sunflower","mbegu za alizeti","mafuta ya alizeti","alizeti msimu","alizeti diseases","alizeti bei","alizeti planting","alizeti yellowing","alizeti worm"],
r:"<strong>Kilimo cha Alizeti Tanzania:</strong><br><br>🌻 <strong>Maeneo Bora:</strong> Singida, Dodoma, Shinyanga, Tabora, Manyara.<br><br>🌻 <strong>Mbegu Bora:</strong> AGUARA 4, HYSUN 33, NSFH 36, NSFH 145, Prosun<br><br>🌻 <strong>Kupanda:</strong> Nafasi cm 75×30. Kina cm 3-5. Mbegu 2/shimo, punguza moja. Mbolea: DAP kupandia.<br><br>🌻 <strong>Magonjwa:</strong><br>• Yellow Blotch — Rangi ya njano, maua kuharibika. Dawa: Agrozinon 60EC<br>• Sclerotinia (White Mold) — Uoza wa shina. Fanya crop rotation kila miaka 5.<br>• Viwavi (African Bollworm) — Hula mbegu. Dawa: Konto, Antario.<br>• Aphids — Dawa: Karate<br><br>🌻 <strong>Bei:</strong> Mbegu alizeti TZS 800-1,400/kg. Mafuta TZS 4,000-6,000/L.<br><br>🌻 <strong>Kuvuna:</strong> Vichwa vigeuke njano-kahawia (miezi 4-6). Kausha vizuri."},

// ══════════════════════════════════════════════════════════════════════════════
// UFUTA / SIMSIM
// ══════════════════════════════════════════════════════════════════════════════
{k:["ufuta","simsim","sesame","kilimo cha ufuta","kilimo cha simsim","ufuta magonjwa","ufuta bei","ufuta msimu","ufuta diseases","ufuta Tanzania","ufuta export","ufuta soko"],
r:"<strong>Kilimo cha Ufuta (Simsim) Tanzania:</strong><br><br>🌿 <strong>Maeneo Bora:</strong> Mtwara, Lindi, Pwani, Morogoro (maeneo ya chini).<br><br>🌿 <strong>Mbegu Bora:</strong> Naliendele, Lindi Local, Semu<br><br>🌿 <strong>Kupanda:</strong> Nafasi cm 30-45×10. Mbegu ndogo — changa na mchanga kabla ya kupanda. Kina cm 1-2 tu.<br><br>🌿 <strong>Magonjwa:</strong><br>• Phytophthora Blight — Mmea unanyauka ghafla. Epuka maji kusimama.<br>• Cercospora Leaf Spot — Madoa ya kahawia. Dawa: Mancozeb.<br>• Sesame Gall Midge — Uvimbe kwenye majani. Dawa: Karate.<br><br>🌿 <strong>Kuvuna:</strong> Maganda yanapoanza kufunguka chini (siku 90-110).<br><br>🌿 <strong>Bei 2025:</strong> TZS 2,000-4,500/kg. Soko: India, China, Japan — bei ya juu export!"},

// ══════════════════════════════════════════════════════════════════════════════
// VITUNGUU
// ══════════════════════════════════════════════════════════════════════════════
{k:["vitunguu","kilimo cha vitunguu","vitunguu maji","magonjwa ya vitunguu","onion","vitunguu saumu","garlic","vitunguu bei","vitunguu msimu","vitunguu diseases","vitunguu Kilosa","vitunguu Babati","vitunguu kuoza"],
r:"<strong>Kilimo cha Vitunguu Tanzania:</strong><br><br>🧅 <strong>Maeneo Bora:</strong> Morogoro (Kilosa/Gairo), Singida, Manyara (Babati), Iringa.<br><br>🧅 <strong>Mbegu Bora:</strong> Red Pinoy F1, Bombay Red, Tengeru White, Sonia F1<br><br>🧅 <strong>Kupanda:</strong> Vitalu kwanza (wiki 6-8), pandikiza. Nafasi cm 10×20. Mbolea: DAP+CAN.<br><br>🧅 <strong>Magonjwa:</strong><br>• Purple Blotch — Madoa ya zambarau. Dawa: Mancozeb<br>• Downy Mildew — Unga mweupe. Dawa: Ridomil Gold<br>• Thrips — Adui mkubwa. Dawa: Abamectin, Karate<br>• Neck Rot — Uoza wakati wa kuhifadhi. Kausha vizuri kabla ya kuhifadhi.<br><br>🧅 <strong>Kuvuna:</strong> 80% ya majani yamepinda/kufa. Punguza maji wiki 2 kabla.<br><br>🧅 <strong>Bei:</strong> TZS 600-1,800/kg."},

// ══════════════════════════════════════════════════════════════════════════════
// NDIZI
// ══════════════════════════════════════════════════════════════════════════════
{k:["ndizi","kilimo cha ndizi","magonjwa ya ndizi","banana","ndizi kuoza","sigatoka","panama disease","ndizi msimu","ndizi bei","ndizi kukauka","ndizi diseases","ndizi yellowing","ndizi bunchy top","ndizi Kagera","ndizi Kilimanjaro"],
r:"<strong>Kilimo na Magonjwa ya Ndizi Tanzania:</strong><br><br>🍌 <strong>Magonjwa Makuu:</strong><br>• <strong>Sigatoka Nyeusi (Black Sigatoka)</strong> — Madoa meusi kwenye majani, matunda yaniva mapema duni. Dawa: Mancozeb, Topsin M. Kata na choma majani yaliyoathirika.<br>• <strong>Panama Disease (Fusarium Wilt TR4)</strong> — Mmea unanyauka kabisa, ndani ya shina ni kahawia. HAINA DAWA. Tumia mbegu safi tu — CAVENDISH inashindwa na TR4!<br>• <strong>Bunchy Top Virus (BBTV)</strong> — Majani madogo yanakunjamana juu. Ng'oa na choma MARA MOJA — inaenea haraka.<br>• <strong>Xanthomonas Wilt (BXW)</strong> — Tunda linaoza ndani, mmea unanyauka. Ng'oa na choma, safisha zana.<br><br>🍌 <strong>Kupanda:</strong> Suckers zenye afya. Nafasi mita 3×3. Samadi mingi.<br><br>🍌 <strong>Bei:</strong> TZS 300-800/kg. Masoko: DSM, Zanzibar, Mombasa."},

// ══════════════════════════════════════════════════════════════════════════════
// PARACHICHI / AVOCADO
// ══════════════════════════════════════════════════════════════════════════════
{k:["parachichi","avocado","kilimo cha parachichi","miche ya parachichi","hass avocado","parachichi mbeya","parachichi export","parachichi magonjwa","parachichi bei","avocado farming","avocado diseases","parachichi Njombe","parachichi Iringa","parachichi Tanzania","avocado export"],
r:"<strong>Parachichi — Dhahabu ya Kijani ya Nyanda za Juu!</strong><br><br>🥑 <strong>Aina Bora:</strong> Hass (export bora), Fuerte, Pinkerton, Puebla<br><br>🥑 <strong>Kupanda:</strong> Miche iliyopandikizwa (grafted) — inatoa matunda miaka 3-4. Mbegu 5-7 yrs. Nafasi mita 5×5 au 6×6. pH 5.5-7.0.<br><br>🥑 <strong>Magonjwa:</strong><br>• Phytophthora Root Rot — Adui mkubwa. Epuka maji kusimama. Tumia Aliette au Ridomil.<br>• Anthracnose — Madoa meusi kwenye matunda. Dawa: Copper oxychloride, Mancozeb.<br>• Sun Blotch Viroid — HAINA DAWA. Tumia miche safi tu.<br><br>🥑 <strong>Soko 2026:</strong> Serikali inalenga tani 235,000 uzalishaji na export tani 40,000.<br><br>🥑 <strong>Bei:</strong> TZS 500-1,500/kg ndani. USD 0.80-2.00/kg export (Ulaya, UAE)."},

// ══════════════════════════════════════════════════════════════════════════════
// KARANGA / GROUNDNUT
// ══════════════════════════════════════════════════════════════════════════════
{k:["karanga","groundnut","peanut","kilimo cha karanga","magonjwa ya karanga","karanga msimu","karanga bei","karanga kuoza","aflatoxin","karanga diseases","karanga harvesting","njugu mawe"],
r:"<strong>Kilimo cha Karanga Tanzania:</strong><br><br>🥜 <strong>Mbegu Bora:</strong> Mnanje, Pendo, Naliendele 96E, Johari, Masindi<br><br>🥜 <strong>Kupanda:</strong> Nafasi cm 45×15. Kina cm 4-5. Udongo tifutifu mchanga wenye mifereji.<br><br>🥜 <strong>Magonjwa:</strong><br>• Cercospora Leaf Spot (Early + Late) — Madoa ya kahawia. Dawa: Mancozeb<br>• Groundnut Rosette Virus — Mmea kudumaa, majani ya njano. Dhibiti aphids (Actara).<br>• <strong>AFLATOXIN</strong> — Sumu hatari ya Aspergillus! Kausha vizuri hadi 10% unyevu. Hifadhi safi. MUHIMU SANA!<br><br>🥜 <strong>Kuvuna:</strong> Miezi 3-4. Ng'oa, kausha juani siku 5-7. Hifadhi mbali na unyevu.<br><br>🥜 <strong>Bei:</strong> TZS 1,500-3,500/kg."},

// ══════════════════════════════════════════════════════════════════════════════
// PILIPILI
// ══════════════════════════════════════════════════════════════════════════════
{k:["pilipili","kilimo cha pilipili","pilipili hoho","pilipili kali","pepper","pilipili kuoza","magonjwa ya pilipili","pilipili bei","pilipili msimu","chilli","capsicum","pilipili diseases","pilipili export","pilipili Tanzania"],
r:"<strong>Kilimo cha Pilipili Tanzania:</strong><br><br>🌶️ <strong>Aina:</strong> Pilipili Hoho (California Wonder, Yolo Wonder), Pilipili Kali (Scotch Bonnet, Bird's Eye, Cayenne)<br><br>🌶️ <strong>Kupanda:</strong> Vitalu kwanza (wiki 4). Nafasi cm 60×45. Joto 18-30°C. pH 6.0-7.0.<br><br>🌶️ <strong>Magonjwa:</strong><br>• Phytophthora Blight — Mmea unanyauka ghafla. Epuka maji. Ridomil.<br>• Anthracnose — Madoa meusi kwenye matunda. Copper fungicide.<br>• Viral Diseases (CMV, TMV) — Majani yaliyokunjamana. Dhibiti aphids (Actara).<br>• Bacterial Spot — Madoa ya maji kwenye majani. Copper hydroxide.<br><br>🌶️ <strong>Bei:</strong> Hoho TZS 1,500-4,000/kg. Pilipili kali TZS 3,000-8,000/kg — export inafaa!<br><br>🌶️ <strong>Export:</strong> India, Pakistan, UAE — uhitaji mkubwa!"},

// ══════════════════════════════════════════════════════════════════════════════
// MBOGA ZA MAJANI
// ══════════════════════════════════════════════════════════════════════════════
{k:["mchicha","mboga","spinach","sukuma wiki","bamia","kabichi","cauliflower","broccoli","mboga za majani","vegetables","mboga msimu","mboga magonjwa","mboga bei","sukuma","kale","spinach farming","vegetable farming","mboga Tanzania","mboga soko"],
r:"<strong>Kilimo cha Mboga Tanzania:</strong><br><br>🥬 <strong>Sukuma Wiki (Kale):</strong> Rahisi kulima. Msimu wote. Mbegu: Thousand Headed, Marrow Stem. Dawa ya wadudu: Karate. Bei TZS 200-600/kg.<br><br>🥬 <strong>Mchicha (Spinach/Amaranth):</strong> Hukomaa haraka (wiki 4-6). Maji mengi. Bei TZS 300-800/kg.<br><br>🥬 <strong>Kabichi (Cabbage):</strong> Mbegu: Gloria F1, Oxylus, Star 3301. Nafasi cm 45×45. Msimu wa baridi bora. Bei TZS 400-900/kg.<br><br>🥬 <strong>Bamia (Okra):</strong> Inastahimili ukame. Mavuno mengi. Bei TZS 600-1,500/kg.<br><br>🥬 <strong>Magonjwa ya Mboga:</strong> Aphids, Diamondback Moth (kabichi), Cutworm. Dawa: Karate, Dipel (bio), Ampligo."},

// ══════════════════════════════════════════════════════════════════════════════
// MATUNDA
// ══════════════════════════════════════════════════════════════════════════════
{k:["mwembe","embe","mango","kilimo cha embe","embe magonjwa","embe bei","machungwa","chungwa","orange","limau","lemon","lime","matunda","fruit","nanasi","tikiti","tikiti maji","watermelon","pineapple","matunda Tanzania","fruit farming"],
r:"<strong>Matunda ya Biashara Tanzania:</strong><br><br>🥭 <strong>Embe (Mango):</strong> Aina: Tommy Atkins, Apple Mango, Ngowe, Kent. Magonjwa: Anthracnose (Copper fungicide), Mealybug (Actara). Bei TZS 400-1,200/kg.<br><br>🍊 <strong>Machungwa / Chungwa (Orange/Citrus):</strong> Aina: Valencia, Navel, Washington. Magonjwa: Citrus Greening (Huanglongbing) — HAINA DAWA, zuia wadudu. Bei TZS 300-800/kg.<br><br>🍍 <strong>Nanasi (Pineapple):</strong> Maeneo: Pwani, Tanga, Morogoro. Bei TZS 500-1,500/kipande.<br><br>🍉 <strong>Tikiti Maji (Watermelon):</strong> Msimu wa kiangazi — faida kubwa haraka. Bei TZS 400-1,000/kg."},

// ══════════════════════════════════════════════════════════════════════════════
// CASH CROPS — KAHAWA / COFFEE
// ══════════════════════════════════════════════════════════════════════════════
{k:["kahawa","coffee","kilimo cha kahawa","magonjwa ya kahawa","kahawa bei","kahawa Tanzania","arabica","robusta","kahawa Kilimanjaro","kahawa Kagera","kahawa Mbeya","kahawa Ruvuma","coffee farming","coffee disease","CBD","coffee berry disease","leaf rust kahawa","coffee rust","kahawa export","kahawa msimu","kahawa bei ngapi"],
r:"<strong>Kilimo cha Kahawa Tanzania:</strong><br><br>☕ <strong>Aina:</strong> Arabica (Kilimanjaro, Mbeya, Ruvuma — ubora wa juu) na Robusta (Kagera — inastahimili ukame)<br><br>☕ <strong>Maeneo Bora:</strong> Kilimanjaro, Arusha, Mbeya, Ruvuma, Kagera<br><br>☕ <strong>Magonjwa Makuu:</strong><br>• <strong>Coffee Berry Disease (CBD)</strong> — Matunda yanageuka kahawia mapema, yanaoza. Dawa: Copper fungicides, Antracol. MUHIMU — nyunyiza mara kwa mara!<br>• <strong>Coffee Leaf Rust (CLR / Hemileia vastatrix)</strong> — Unga wa machungwa chini ya majani, majani yanakufa. Dawa: Copper oxychloride, Tilt 250EC.<br>• <strong>Coffee Wilt (Fusarium)</strong> — Mmea unanyauka. Kata matawi, tumia miche safi.<br>• <strong>Coffee Berry Borer (CBB / Hypothenemus hampei)</strong> — Funza mdogo anaingia buni. Dawa: Endosulfan, mitego ya ethanol.<br><br>☕ <strong>Mbolea:</strong> NPK 17:17:17 + CAN. Weka mara mbili kwa mwaka.<br><br>☕ <strong>Bei 2025:</strong> Arabica TZS 8,000-12,850/kg. Robusta TZS 4,000-5,420/kg.<br><br>☕ <strong>Export:</strong> Ulaya (Belgium, Germany), Marekani, Japan."},

// ══════════════════════════════════════════════════════════════════════════════
// CASH CROPS — CHAI / TEA
// ══════════════════════════════════════════════════════════════════════════════
{k:["chai","tea","kilimo cha chai","magonjwa ya chai","chai Tanzania","chai bei","chai Mbeya","chai Njombe","chai Iringa","chai Rungwe","tea farming","tea disease","green leaf tea","chai export","chai soko","chai kijani","made tea"],
r:"<strong>Kilimo cha Chai Tanzania:</strong><br><br>🍵 <strong>Maeneo Bora:</strong> Njombe, Mbeya (Rungwe), Iringa, Tanga (Usambara) — milima yenye mvua na ubaridi.<br><br>🍵 <strong>Aina:</strong> Camellia sinensis var. sinensis (chai nyeusi/kijani)<br><br>🍵 <strong>Kupanda:</strong> Miche ya cutting (vipande vya shina). Nafasi mita 1.2×0.6. Joto 17-28°C. pH 4.5-6.0.<br><br>🍵 <strong>Magonjwa:</strong><br>• Blister Blight (Exobasidium) — Malengelenge kwenye majani mapya. Dawa: Copper fungicides.<br>• Red Spider Mite — Majani kugeuka nyekundu/kahawia. Dawa: Abamectin, Kelthane.<br>• Thrips — Majani yenye michoro nyekundu. Dawa: Karate.<br>• Root Rot — Epuka maji kusimama. Aliette.<br><br>🍵 <strong>Kuvuna (Plucking):</strong> Chuma chipukizi 2-3 (two-and-a-bud) kila wiki 1-2.<br><br>🍵 <strong>Bei:</strong> Green leaf TZS 300-500/kg kwa wakulima wadogo. Made tea USD 1.50-3.00/kg export.<br><br>🍵 <strong>Usindikaji:</strong> Kupitia kiwanda (RTEA, Kibena, Mufindi Tea)."},

// ══════════════════════════════════════════════════════════════════════════════
// CASH CROPS — KOROSHO / CASHEW
// ══════════════════════════════════════════════════════════════════════════════
{k:["korosho","cashew","kilimo cha korosho","magonjwa ya korosho","korosho msimu","korosho bei","korosho Tanzania","korosho Mtwara","korosho Lindi","korosho Ruvuma","wadudu wa korosho","korosho powdery mildew","tea mosquito bug","korosho export","korosho auction","korosho TMX","CBT korosho"],
r:"<strong>Kilimo cha Korosho Tanzania:</strong><br><br>🥜 <strong>Maeneo Bora:</strong> Mtwara, Lindi, Ruvuma, Pwani, Tanga.<br><br>🥜 <strong>Kupanda:</strong> Nafasi mita 9×9. Shimo cm 30-40 kina. Jaza samadi kabla ya kupanda. pH 5.5-6.5.<br><br>🥜 <strong>Magonjwa:</strong><br>• <strong>Powdery Mildew (Unga wa Unga)</strong> — Unga mweupe kwenye majani mapya na maua. Adui mkubwa zaidi. Dawa: Sulfur fungicide (Thiovit), Anvil, Bayleton. Nyunyiza wiki 2 kabla maua.<br>• <strong>Tea Mosquito Bug (Helopeltis)</strong> — Inasababisha vidonda vya kahawia kwenye matunda na matawi. Dawa: Dimethoate (Rogor), Karate.<br>• <strong>Anthracnose</strong> — Madoa kwenye matunda. Copper oxychloride.<br><br>🥜 <strong>Bei 2025/2026:</strong> TZS 2,550-4,120/kg (auction ya kwanza 2025/2026). Bei ya rekodi ya TZS 4,120/kg ilifikia 2024/2025!<br><br>🥜 <strong>Uzalishaji:</strong> Tani 617,683 msimu 2025/2026 — Tanzania ni mzalishaji mkubwa Afrika!<br><br>🥜 <strong>Export:</strong> India, Vietnam, Marekani (soko jipya)."},

// ══════════════════════════════════════════════════════════════════════════════
// CASH CROPS — PAMBA / COTTON
// ══════════════════════════════════════════════════════════════════════════════
{k:["pamba","cotton","kilimo cha pamba","magonjwa ya pamba","pamba Tanzania","pamba bei","pamba Mwanza","pamba Shinyanga","pamba Simiyu","pamba Mara","pamba Geita","cotton farming","cotton disease","bollworm pamba","pamba wadudu","pamba whitefly","pamba msimu"],
r:"<strong>Kilimo cha Pamba Tanzania:</strong><br><br>🌿 <strong>Maeneo Bora (Kanda ya Ziwa):</strong> Mwanza, Shinyanga, Simiyu, Geita, Tabora, Mara.<br><br>🌿 <strong>Mbegu Bora:</strong> TARI UK91, UKM08, Super C, UBK-2<br><br>🌿 <strong>Kupanda:</strong> Nafasi cm 90×25 au 75×30. Kupanda Desemba-Januari (mvua). Mbolea: DAP kupandia.<br><br>🌿 <strong>Magonjwa na Wadudu:</strong><br>• <strong>American Bollworm (Helicoverpa)</strong> — Funza anaingia boll. Dawa: Karate, Cypermethrin, Coragen.<br>• <strong>Whitefly + Aphids</strong> — Husambaza virusi. Dawa: Actara, Confidor.<br>• <strong>Bacterial Blight</strong> — Madoa ya maji kwenye majani, kunyauka. Copper hydroxide.<br>• <strong>Fusarium Wilt</strong> — Mmea unanyauka. Zungushia mazao.<br><br>🌿 <strong>Bei 2023/24:</strong> Cotton seed TZS 800/kg. Cotton lint USD 0.75/pound.<br><br>🌿 <strong>Uzalishaji 2025/26:</strong> Tani 222,014 — ongezeko la 25%!"},

// ══════════════════════════════════════════════════════════════════════════════
// CASH CROPS — TUMBAKU / TOBACCO
// ══════════════════════════════════════════════════════════════════════════════
{k:["tumbaku","tobacco","kilimo cha tumbaku","magonjwa ya tumbaku","tumbaku Tanzania","tumbaku bei","tumbaku Tabora","tumbaku Ruvuma","tumbaku Iringa","tumbaku Mbeya","tobacco farming","tobacco disease","tumbaku export","tumbaku msimu","tumbaku flue cured","tumbaku burley"],
r:"<strong>Kilimo cha Tumbaku Tanzania:</strong><br><br>🍂 <strong>Maeneo Bora:</strong> Tabora, Ruvuma, Iringa, Mbeya.<br><br>🍂 <strong>Aina:</strong> Flue-Cured Virginia (FCV) — nzuri zaidi bei. Burley — inastahimili ukame.<br><br>🍂 <strong>Mfumo:</strong> Contract farming — kampuni za BAT, JTI, Alliance One zinalipa.<br><br>🍂 <strong>Magonjwa:</strong><br>• Blue Mold (Peronospora) — Unga wa buluu chini ya majani. Dawa: Ridomil, Acrobat.<br>• Black Shank (Phytophthora) — Shina linageuka nyeusi. Epuka maji.<br>• Tobacco Mosaic Virus (TMV) — Madoa ya mosaic. Tumia glavu — vinaenea mkono!<br>• Nematodes (Minyoo ya Udongo) — Mizizi ina mafundo. Fumigant au crop rotation.<br><br>🍂 <strong>Bei/Export 2023:</strong> USD 340.4M export — ongezeko la 90.7% kutoka 2022! Tani 82,000 ziliuzwa nje.<br><br>🍂 <strong>Bei ya shamba:</strong> TZS 3,000-8,000/kg (FCV premium). Tabora ni kituo kikuu.<br><br>⚠️ Tumbaku ina athari za kiafya — zingatia sheria za kilimo na usalama."},

// ══════════════════════════════════════════════════════════════════════════════
// CASH CROPS — MKONGE / SISAL
// ══════════════════════════════════════════════════════════════════════════════
{k:["mkonge","sisal","kilimo cha mkonge","mkonge Tanzania","mkonge bei","mkonge Tanga","mkonge Morogoro","mkonge Kilosa","sisal farming","sisal disease","mkonge magonjwa","mkonge export","mkonge fiber","mkonge rope"],
r:"<strong>Kilimo cha Mkonge (Sisal) Tanzania:</strong><br><br>🌿 <strong>Historia:</strong> Tanzania ilikuwa mzalishaji mkubwa zaidi duniani miaka ya 1960 — tani 240,000! Sasa bado ni mzalishaji mkubwa Afrika.<br><br>🌿 <strong>Maeneo Bora:</strong> Tanga (Korogwe, Lushoto), Morogoro (Kilosa, Mvomero), Manyara.<br><br>🌿 <strong>Uzalishaji 2025/26:</strong> Tani 64,321 — ya 4 kwa mazao ya biashara.<br><br>🌿 <strong>Magonjwa:</strong><br>• Sisal Bole Rot — Uoza wa shina. Epuka maji kusimama, dawa: Copper.<br>• Zebra Disease — Mistari nyekundu kwenye majani. Sababu: Bacterial. Kata majani, dawa copper.<br>• Agave Weevil — Funza anaingia moyoni. Dawa: Aldrin (kwenye vitanzi).<br><br>🌿 <strong>Mavuno:</strong> Huanza mavuno baada ya miaka 2-3. Kata majani kila miaka 2-3 (semi-annual).<br><br>🌿 <strong>Bidhaa:</strong> Nyuzi (fiber), kamba (rope), magunia, carpet — export Ulaya, Asia.<br><br>🌿 <strong>Bei:</strong> Sisal fiber USD 600-1,200/tani export. Shamba TZS 200-400/kg."},

// ══════════════════════════════════════════════════════════════════════════════
// CASH CROPS — PARETO / PYRETHRUM
// ══════════════════════════════════════════════════════════════════════════════
{k:["pareto","pyrethrum","kilimo cha pareto","pareto Tanzania","pareto Mbeya","pareto Iringa","pareto Njombe","pyrethrum farming","pareto bei","pareto magonjwa","pareto export","pareto insecticide","pareto flowers"],
r:"<strong>Kilimo cha Pareto (Pyrethrum) Tanzania:</strong><br><br>🌼 <strong>Pareto ni nini?</strong> Ni maua (Chrysanthemum cinerariifolium) yanayotumika kutengeneza dawa asili ya kuua wadudu (pyrethrin). Inatumika ulimwenguni kama insecticide ya kikaboni!<br><br>🌼 <strong>Maeneo Bora:</strong> Mbeya (Mbarali na Mbeya Vijijini), Iringa, Njombe — nyanda za juu baridi (altitude 1,600-3,000m).<br><br>🌼 <strong>Uzalishaji Tanzania:</strong> Wakulima 10,687+. Tanzania ni mzalishaji wa tatu duniani baada ya Kenya na India.<br><br>🌼 <strong>Kupanda:</strong> Mbegu au miche. Nafasi cm 60×30. pH 5.5-7.0. Haihitaji mbolea nyingi.<br><br>🌼 <strong>Kuvuna:</strong> Vuna maua yanapofunguka nusu (semi-open) — pyrethrin nyingi zaidi. Kausha haraka.<br><br>🌼 <strong>Magonjwa:</strong><br>• Sclerotinia Crown Rot — Uoza wa shina. Crop rotation.<br>• Aphids na Thrips — Dawa: Karate (kidogo — si nyingi kwani inaua pyrethrin!)<br><br>🌼 <strong>Bei:</strong> TZS 1,500-3,000/kg maua makavu. Export: Ulaya, Marekani — bei ya juu organic!"},

// ══════════════════════════════════════════════════════════════════════════════
// NGANO / WHEAT
// ══════════════════════════════════════════════════════════════════════════════
{k:["ngano","wheat","kilimo cha ngano","ngano Tanzania","ngano Arusha","ngano Mbeya","ngano Ruvuma","wheat farming","ngano magonjwa","ngano bei","ngano cultivation"],
r:"<strong>Kilimo cha Ngano Tanzania:</strong><br><br>🌾 <strong>Maeneo Bora:</strong> Arusha (Monduli), Manyara, Ruvuma, Mbeya — altitude juu ya 1,500m.<br><br>🌾 <strong>Mbegu Bora:</strong> Kenya Fahari, Duma, Njoro BL, Temba, SELIAN 97<br><br>🌾 <strong>Kupanda:</strong> Nafasi cm 20×10. Broadcasting au drill seeding. Mbolea: DAP + UREA.<br><br>🌾 <strong>Magonjwa:</strong><br>• Yellow Rust (Stripe Rust) — Mstari wa njano kwenye majani. Dawa: Tilt 250EC, Folicur.<br>• Stem Rust — Doa la kutu kwenye shina. Tilt 250EC.<br>• Powdery Mildew — Unga mweupe. Dawa: Sulfur fungicide.<br>• Septoria — Madoa ya kahawia. Dawa: Mancozeb.<br><br>🌾 <strong>Kuvuna:</strong> Siku 120-150. Mimea inapokuwa ya dhahabu.<br><br>🌾 <strong>Bei:</strong> TZS 600-1,200/kg. Tanzania bado inaingiza ngano nyingi — fursa ya soko nzuri ndani!"},

// ══════════════════════════════════════════════════════════════════════════════
// MTAMA / SORGHUM & UWELE / MILLET
// ══════════════════════════════════════════════════════════════════════════════
{k:["mtama","sorghum","uwele","millet","kilimo cha mtama","mtama Tanzania","mtama magonjwa","mtama bei","sorghum farming","finger millet","ulezi","mtama huhimili ukame","drought resistant crops","mazao ya ukame"],
r:"<strong>Kilimo cha Mtama / Uwele Tanzania:</strong><br><br>🌾 <strong>Faida:</strong> Huhimili ukame bora kuliko mahindi — nzuri kwa Dodoma, Singida, Shinyanga!<br><br>🌾 <strong>Aina za Mtama:</strong> Sorghum bicolor, KARI Mtama 1, Macia, Wahi<br>🌾 <strong>Aina za Uwele:</strong> Finger Millet (Ulezi), Pearl Millet (Mawele)<br><br>🌾 <strong>Kupanda Mtama:</strong> Nafasi cm 60-75×15-20. Mbolea kidogo — inastahimili udongo mbaya.<br><br>🌾 <strong>Magonjwa Mtama:</strong><br>• Anthracnose — Madoa kwenye majani. Dawa: Mancozeb.<br>• Head Smut (Ugani) — Swimbi inageuka unga mweusi. Tumia mbegu zilizotibiwa (treated seed).<br>• Shoot Fly — Mmea mdogo unakufa. Dawa: Karate.<br><br>🌾 <strong>Bei:</strong> TZS 800-1,500/kg mtama. Uwele TZS 1,000-2,000/kg.<br><br>🌾 <strong>Matumizi:</strong> Ugali, pombe za asili, lishe ya wanyama."},

// ══════════════════════════════════════════════════════════════════════════════
// MIWA / SUGARCANE
// ══════════════════════════════════════════════════════════════════════════════
{k:["miwa","sugarcane","kilimo cha miwa","miwa Tanzania","miwa Kilosa","miwa Kilombero","sukari Tanzania","sugar Tanzania","miwa magonjwa","miwa bei","sugarcane farming","miwa cultivation"],
r:"<strong>Kilimo cha Miwa (Sugarcane) Tanzania:</strong><br><br>🍬 <strong>Maeneo Bora:</strong> Kilosa (ILLOVO), Kilombero (KILOMBERO SUGAR), Moshi (TPC), Kagera (KAGERA SUGAR).<br><br>🍬 <strong>Kupanda:</strong> Vipande vya shina (setts) cm 30-40. Nafasi mita 1.5×0.6. Mbolea: DAP + CAN nyingi.<br><br>🍬 <strong>Magonjwa:</strong><br>• Smut (Ugani) — Shina linazaa fimbo nyeusi badala ya maua. Tumia mbegu safi (hot water treatment).<br>• Red Rot — Ndani ya shina inageuka nyekundu na kufa. Kata na choma.<br>• Ratoon Stunting Disease (RSD) — Ukuaji polepole. Tumia mbegu safi tu.<br>• Sugarcane Borer — Funza kwenye shina. Dawa: Furadan au Karate.<br><br>🍬 <strong>Mavuno:</strong> Baada ya miezi 12-18. Tani 70-120/hekta.<br><br>🍬 <strong>Bei:</strong> Sukari Tanzania TZS 2,200-2,800/kg retail. Uzalishaji 2025/26 tani 410,979."},

// ══════════════════════════════════════════════════════════════════════════════
// KAKAO / COCOA
// ══════════════════════════════════════════════════════════════════════════════
{k:["kakao","cocoa","chocolate","kilimo cha kakao","kakao Tanzania","kakao Mbeya","kakao Kagera","kakao Kilosa","cocoa farming","kakao magonjwa","kakao bei","kakao export"],
r:"<strong>Kilimo cha Kakao Tanzania:</strong><br><br>🍫 <strong>Maeneo Bora:</strong> Kagera, Kilosa (Morogoro), Mbeya (Kyela), Pwani.<br><br>🍫 <strong>Kupanda:</strong> Miche kwenye kivuli cha miti. Nafasi mita 3×3. Joto 21-32°C. pH 6.0-7.5.<br><br>🍫 <strong>Magonjwa:</strong><br>• Black Pod (Phytophthora palmivora) — Tunda linageuka nyeusi na kuoza. MKUBWA ZAIDI. Dawa: Copper oxychloride, Ridomil. Vuna matunda yaliyoathirika mara moja.<br>• Cocoa Swollen Shoot Virus (CSSV) — Kuenea polepole. Ng'oa miti iliyoathirika.<br>• Capsid Bug (Sahlbergella) — Matawi kufa. Dawa: Karate, Dimethoate.<br><br>🍫 <strong>Mavuno:</strong> Kata matunda makubwa ya njano/nyekundu. Chachusho (fermentation) siku 5-7.<br><br>🍫 <strong>Bei/Uzalishaji 2025/26:</strong> Tani 10,096. Bei ya kimataifa imepanda sana 2024/25 — USD 8,000-10,000/tani!"},

// ══════════════════════════════════════════════════════════════════════════════
// WADUDU WA JUMLA
// ══════════════════════════════════════════════════════════════════════════════
{k:["wadudu","aphid","vidung'ata","thrips","whitefly","inzi weupe","nzi","mbu wa mimea","sarafu","mite","spider mite","wadudu wanaouma","kunyonya mimea","wadudu shambani","pest control","dawa ya wadudu","insects crops","general pest","wadudu jumla","visumbufu"],
r:"<strong>Wadudu Waharibifu wa Kawaida Tanzania:</strong><br><br>🦗 <strong>Aphids / Vidung'ata</strong><br>Dalili: Majani yanakunjamana, utomvu mzito (honeydew), sooty mold (unga mweusi).<br>Dawa: Karate 2.5EC, Actara 25WG, au maji ya sabuni ya kufulia (1 tbsp/L).<br><br>🦗 <strong>Thrips</strong><br>Dalili: Majani yanageuka fedha/kahawia, matunda yana makucha/madoa.<br>Dawa: Abamectin (Dynamec), Karate, Spinosad.<br><br>🦗 <strong>Whitefly / Inzi Weupe</strong><br>Dalili: Wadudu wadogo weupe wanaoruka ukigusa mmea, majani njano.<br>Dawa: Actara 25WG, Confidor 200SL. Mtego wa njano (yellow sticky trap)!<br><br>🦗 <strong>Spider Mites / Sarafu</strong><br>Dalili: Utando mzito chini ya majani, majani kahawia/nyekundu.<br>Dawa: Abamectin, Oberon 24SC, Envidor."},

// ══════════════════════════════════════════════════════════════════════════════
// MBOLEA
// ══════════════════════════════════════════════════════════════════════════════
{k:["mbolea","nitrojeni","phosphorus","potassium","DAP","UREA","CAN","NPK","mbolea gani","virutubisho","kuweka mbolea","mbolea ya kupandia","mbolea ya kukuzia","samadi","compost","mboji","fertilizer","fertiliser","mbolea sahihi","mbolea bora","mbolea organic","organic farming","mbolea asili"],
r:"<strong>Mwongozo wa Mbolea Tanzania:</strong><br><br>🌱 <strong>DAP (18:46:0)</strong> — Kupandia. Inasaidia mizizi kukua. 50kg/ekari wakati wa kupanda.<br><br>🌱 <strong>UREA (46% N)</strong> — Kukuzia. Fanya majani ya kijani kibichi. Wiki 4-6 baada ya kuota.<br><br>🌱 <strong>CAN (27% N + Calcium)</strong> — Bora kwa nyanya na pilipili. Inazuia uoza wa kitako (BER).<br><br>🌱 <strong>NPK 17:17:17</strong> — Mbolea kamili kwa mazao yote. Nzuri kwa hatua ya mwanzo.<br><br>🌱 <strong>Samadi/Mboji (Compost)</strong> — Toni 5-10/ekari. Inatoa virutubisho kwa miaka mingi. BORA KABISA kwa udongo wa muda mrefu!<br><br>🌱 <strong>MRP (Minjingu Rock Phosphate)</strong> — Tanzania ina madini hapa Minjingu, Manyara! Inatoa phosphorus polepole — bora kwa udongo wenye tindikali.<br><br>⚠️ Usiweke mbolea nyingi — inaweza kuchoma mimea. Fuata kipimo!"},

// ══════════════════════════════════════════════════════════════════════════════
// HIFADHI YA MAZAO
// ══════════════════════════════════════════════════════════════════════════════
{k:["kuhifadhi mazao","hifadhi","ghala","post harvest","baada ya kuvuna","mazao kuoza","storage","kuhifadhi mahindi","kuhifadhi nyanya","PICS bag","postharvest","storage ya mazao","jinsi ya kuhifadhi","preservation","mazao yanabaki muda mrefu"],
r:"<strong>Jinsi ya Kuhifadhi Mazao Tanzania:</strong><br><br>🏪 <strong>Mahindi:</strong> Kausha hadi 13% unyevu. ACTELLIC DUST 2% au SKANA P. PICS Bag (triple-layer hermetic) au gunia safi.<br><br>🏪 <strong>Maharage/Choroko:</strong> Changanya na majivu ya kuni (1:10) — inazuia weevils bila dawa! Au PICS Bag.<br><br>🏪 <strong>Nyanya/Mboga:</strong> Ziuze ndani ya siku 3-7. Usifunge plastic iliyofungwa — zinafoka. Cool chain (4-10°C) kwa soko la mbali.<br><br>🏪 <strong>Viazi:</strong> Giza, ubaridi (10-15°C), hewa nzuri. Mwanga wa jua = solanine (sumu — rangi ya kijani)!<br><br>🏪 <strong>Mpunga:</strong> Kausha hadi 12-14%. Gunia safi. Angalia panya na weevils.<br><br>🏪 <strong>Karanga:</strong> Kausha vizuri hadi 10% — kuzuia Aflatoxin (sumu hatari ya ini)!<br><br>🏪 <strong>Korosho:</strong> Hifadhi mahali pakavu. Funika vizuri — inachukua unyevu haraka."},

// ══════════════════════════════════════════════════════════════════════════════
// UMWAGILIAJI
// ══════════════════════════════════════════════════════════════════════════════
{k:["umwagiliaji","maji","kumwagilia","drip irrigation","mfumo wa maji","ukame","kiangazi","maji shambani","kukosa maji","mimea inakauka","irrigation","mifereji","sprinkler","flood irrigation","furrow irrigation","irrigation system","maji ya kilimo","water stress"],
r:"<strong>Mwongozo wa Umwagiliaji:</strong><br><br>💧 <strong>Wakati Bora:</strong> Asubuhi saa 12-2 (6-8 AM). Epuka mchana — maji yanabubujika, majani yanawaka.<br><br>💧 <strong>Drip Irrigation (Umwagiliaji wa Tone):</strong> Inaokoa maji 40-60%. Bora kwa nyanya, pilipili, vitunguu, mboga. Faida: maji yanafika mzizini moja kwa moja.<br><br>💧 <strong>Sprinkler:</strong> Nzuri kwa mazao ya nafaka (mahindi, ngano) na mashamba makubwa.<br><br>💧 <strong>Ishara za Kukosa Maji (Water Stress):</strong> Majani yanakunjamana asubuhi, rangi ya majani kuwa nyepesi, udongo mgumu.<br><br>💧 <strong>Ishara za Maji Mengi (Waterlogging):</strong> Majani njano, mizizi inaoza, harufu mbaya, mmea unasimama polepole.<br><br>💧 <strong>Kiangazi:</strong> Ongeza mara za kumwagilia lakini punguza kiasi — epuka uoza."},

// ══════════════════════════════════════════════════════════════════════════════
// UDONGO
// ══════════════════════════════════════════════════════════════════════════════
{k:["udongo","rutuba ya udongo","pH ya udongo","udongo mzuri","udongo mbaya","chokaa","lime","udongo tifutifu","udongo wa mfinyanzi","erosion","mmomonyoko","soil health","soil pH","soil fertility","udongo rutuba","acidic soil","udongo tindikali","udongo wa mchanga"],
r:"<strong>Usimamizi wa Udongo:</strong><br><br>🌍 <strong>pH Nzuri kwa Mazao Mengi:</strong> 6.0-7.0. Pima kwa pH meter (AGROVET) au test kit.<br><br>🌍 <strong>Udongo Tindikali (pH < 6.0):</strong> Ongeza Calcitic Lime au Dolomite — 1-3 tani/hekta. Subiri miezi 1-2 kabla ya kupanda.<br><br>🌍 <strong>Minjingu Rock Phosphate:</strong> Asili ya Tanzania — nzuri kwa udongo tindikali badala ya DAP.<br><br>🌍 <strong>Udongo wa Mfinyanzi (Clay):</strong> Ongeza mchanga + samadi — inaboresha drainage na aeration.<br><br>🌍 <strong>Udongo wa Mchanga (Sandy):</strong> Ongeza samadi/compost — inashikilia maji na virutubisho.<br><br>🌍 <strong>Mmomonyoko (Erosion):</strong> Panda mikanda ya mimea kwenye mteremko (contour farming). Mulch. Cover crops.<br><br>🌍 <strong>Dalili za Udongo Mbaya:</strong> Mimea polepole, majani njano, udongo mgumu kama jiwe, magugu mengi."},

// ══════════════════════════════════════════════════════════════════════════════
// BEI ZA SOKO
// ══════════════════════════════════════════════════════════════════════════════
{k:["bei ya mazao","bei ya soko","market price","bei gani","bei leo","soko la leo","bei za Tanzania","bei za 2025","bei za 2026","crop prices","mazao bei ngapi","bei ya chakula","food prices tanzania","bei comprehensive","bei zote"],
r:"Kwa bei za sasa sahihi, angalia ukurasa wa <strong>'Bei ya AI'</strong> kwenye AgroLink!<br><br>📊 <strong>Bei za Wastani Tanzania 2025/2026:</strong><br><br><strong>Mazao ya Chakula:</strong><br>• Mahindi: TZS 800-4,784/kg (bei imepanda 2025!)<br>• Nyanya: TZS 800-2,500/kg<br>• Viazi: TZS 500-1,200/kg<br>• Mpunga (mchele): TZS 1,200-2,500/kg<br>• Maharage: TZS 1,200-2,800/kg<br>• Vitunguu: TZS 600-1,800/kg<br>• Pilipili hoho: TZS 1,500-4,000/kg<br><br><strong>Cash Crops:</strong><br>• Korosho: TZS 2,550-4,120/kg (rekodi 2024/25!)<br>• Kahawa Arabica: TZS 8,000-12,850/kg<br>• Kahawa Robusta: TZS 4,000-5,420/kg<br>• Alizeti: TZS 800-1,400/kg<br>• Ufuta: TZS 2,000-4,500/kg<br>• Tumbaku FCV: TZS 3,000-8,000/kg<br><br>⚠️ Bei za DSM na Arusha ni juu ya vijijini kwa 20-40%!"},

// ══════════════════════════════════════════════════════════════════════════════
// MASOKO NA WANUNUZI
// ══════════════════════════════════════════════════════════════════════════════
{k:["soko","wanunuzi","kuuza","wapi nitauza","masoko Tanzania","Kariakoo","Tandale","Mchikichini","Arusha soko","DSM soko","Mbeya soko","soko la kimataifa","market","buyers","where to sell","masoko ya karibu","soko kubwa"],
r:"<strong>Masoko Makubwa Tanzania:</strong><br><br>🛒 <strong>Dar es Salaam:</strong> Kariakoo (mkubwa zaidi Afrika Mashariki), Tandale, Buguruni, Mchikichini<br>🛒 <strong>Arusha:</strong> Central Market, Kilombero Market, Sanawari<br>🛒 <strong>Mbeya:</strong> Mwanjelwa Market, Uyole Market (mkubwa wa kusini)<br>🛒 <strong>Dodoma:</strong> Majengo Market, Kibaigwa (nafaka — mkubwa kabisa nchini!)<br>🛒 <strong>Mwanza:</strong> Kirumba Market<br>🛒 <strong>Morogoro:</strong> Mwanakwerekwe, Bigwa<br><br>💡 <strong>Ushauri:</strong> Tumia AgroLink kuwasiliana na wanunuzi moja kwa moja — bila dalali! Dalali wanachukua 10-20% ya faida yako."},

// ══════════════════════════════════════════════════════════════════════════════
// EXPORT
// ══════════════════════════════════════════════════════════════════════════════
{k:["export","kuuza nje","masoko ya nje","international","kenya","uarabu","ulaya","dubai","ng'ambo","foreign market","TAHA","GlobalGAP","organic certification","EU market","export Tanzania","mazao ya nje","jinsi ya kuuza nje"],
r:"<strong>Kuuza Mazao Nje ya Tanzania:</strong><br><br>🌍 <strong>Mazao Yanayotakiwa Sana:</strong><br>• Parachichi (Hass) → Ulaya, UAE (soko jipya 2025/26!)<br>• Ufuta → India, China, Japan<br>• Korosho → India, Vietnam, Marekani (soko jipya!)<br>• Kahawa (Arabica) → Ulaya (Belgium, Germany), Marekani, Japan<br>• Tumbaku → China, India, EU<br>• Pilipili kali → Pakistan, India, UAE<br>• Kakao → Ulaya — bei ya juu 2024/25 USD 8,000-10,000/tani!<br><br>🌍 <strong>Jinsi ya Kuanza Export:</strong><br>1. Leseni ya export (Wizara ya Kilimo — MALF Dar)<br>2. Jiunge <strong>TAHA</strong> (Tanzania Horticulture Association) — msaada wa market<br>3. <strong>GlobalGAP certification</strong> — lazima kwa Ulaya<br>4. <strong>Tanzania Mercantile Exchange (TMX)</strong> — auction ya online<br>5. <strong>FRUTCO Arusha</strong> — parachichi na matunda"},

// ══════════════════════════════════════════════════════════════════════════════
// MIKOPO
// ══════════════════════════════════════════════════════════════════════════════
{k:["mkopo","fedha","financing","benki","CRDB","NMB","TADB","ruzuku","subsidy","akiba","SACCOS","VICOBA","pesa za kilimo","mkopo wa kilimo","agricultural loan","credit kilimo","capital ya kilimo","funding kilimo"],
r:"<strong>Mikopo na Fedha kwa Wakulima:</strong><br><br>💰 <strong>CRDB Bank</strong> — Kilimo Biashara: mkopo bila dhamana kubwa kwa vikundi. Riba ~18%/mwaka.<br><br>💰 <strong>NMB Bank</strong> — NMB Kilimo: pembejeo na zana za kilimo. Angalia matawi yao.<br><br>💰 <strong>TADB (Tanzania Agricultural Development Bank)</strong> — Benki maalum ya kilimo. Riba ya chini ya 10%. Bora zaidi!<br><br>💰 <strong>VICOBA/SACCOS</strong> — Vikundi vya akiba vijijini. Rahisi kupata, riba ya wastani 2-3%/mwezi.<br><br>💰 <strong>Serikali ya Tanzania</strong> — Voucher ya pembejeo (mbolea na mbegu). Angalia kwa Afisa Kilimo wa kata.<br><br>💰 <strong>AGRF / AFAP</strong> — Fedha za kimataifa za kilimo Afrika.<br><br>⚠️ Hesabu mapato na gharama (ROI) vizuri kabla ya kuchukua mkopo wowote!"},

// ══════════════════════════════════════════════════════════════════════════════
// HALI YA HEWA
// ══════════════════════════════════════════════════════════════════════════════
{k:["hali ya hewa","mvua","itanyesha","jua","weather","TMA","msimu wa mvua","kiangazi","baridi","dhoruba","upepo","ukame","mabadiliko ya tabia nchi","climate change","global warming","rainfall","drought","msimu","Tanzania weather","masika","vuli"],
r:"Angalia ukurasa wa <strong>'Hali ya Hewa'</strong> kwenye AgroLink kwa data halisi ya mkoa wako!<br><br>🌧️ <strong>Misimu Tanzania:</strong><br>• <strong>Masika (Long Rains)</strong>: Machi–Mei — mikoa mingi ya bara<br>• <strong>Vuli (Short Rains)</strong>: Oktoba–Desemba — pwani na kaskazini<br>• <strong>Nyanda za Juu Kusini</strong> (Mbeya, Iringa, Njombe): Novemba–Aprili<br>• <strong>Ukanda wa Ziwa</strong> (Mwanza, Kagera): Mwaka mzima na masika Machi-Mei<br><br>⚠️ Fuatilia TMA (Tanzania Meteorological Authority) kabla ya kupanda au kuweka mbolea!<br><br>🌡️ <strong>Climate Change:</strong> Panda mazao yanayostahimili ukame: muhogo, mtama, sorghum, kunde, alizeti (badala ya mahindi maeneo makame)."},

// ══════════════════════════════════════════════════════════════════════════════
// AGROLINK
// ══════════════════════════════════════════════════════════════════════════════
{k:["agrolink ni nini","jukwaa hili","platform","jinsi ya kutumia","jinsi ya kuuza","jinsi ya kujisajili","signup","kujiandikisha","kutumia agrolink","jinsi ya kupakia","agrolink Tanzania","what is agrolink","agrolink features","jinsi inavyofanya kazi"],
r:"<strong>AgroLink Tanzania — Soko Lako la Kisasa:</strong><br><br>🛒 <strong>Jinsi ya Kutumia:</strong><br>1. Jiandikishe bure kwa namba ya simu<br>2. Ingia Dashboard yako<br>3. Bonyeza 'Ongeza Zao' — picha nzuri + maelezo kamili<br>4. Weka bei na mkoa wako<br>5. Wanunuzi watakuona moja kwa moja — bila dalali!<br><br>✅ <strong>Huduma Zetu:</strong><br>• Soko la mazao (kuuza na kununua)<br>• Bei ya AI (bei za soko kwa AI)<br>• Daktari wa Zao (utambuzi wa magonjwa kwa picha)<br>• Hali ya Hewa (data ya mkoa wako)<br>• AgroBot (msaidizi huu!)<br>• Wakulima wanaouza Tanzania nzima"},

// ══════════════════════════════════════════════════════════════════════════════
// KUCHEKESHA / CASUAL
// ══════════════════════════════════════════════════════════════════════════════
{k:["umeoa","una mpenzi","unapenda nani","single","mapenzi","romantic","pendo","girlfriend","boyfriend","love"],
r:"Haha! Mimi ni programu ya kompyuta — sina moyo wa nyama! 💚 Mapenzi yangu yote yapo kwenye kusaidia wakulima wa Tanzania. Una swali la kilimo?"},

{k:["nikopeshe","naomba mkopo","nahitaji pesa","nihonge","nipe shilingi","pesa bure","lend me","give me money"],
r:"Akaunti yangu ina namba '0' na '1' tu — binary kabisa! 😄 Tumia AgroLink vizuri, uza mazao kwa bei nzuri, utapata pesa za kutosha!"},

{k:["wewe ni mjinga","hujui kitu","fala","programu mbaya","useless","bure kabisa","you are dumb","stupid bot","bot mbaya"],
r:"Samahani kama sikukusaidia vizuri! 🙏 Mimi ni bot wa kilimo — nina mipaka. Jaribu kuuliza tena kwa undani zaidi na nitajaribu zaidi!"},

{k:["mchezo","mpira","simba","yanga","timu","football","soccer","EPL","premier league","Champions League","sports","mechi"],
r:"Timu yangu? AgroLink FC bila shaka! ⚽🌾 Nje ya kilimo sijui vizuri. Najua tu: DAP ikiwa sawa shambani, goli la mavuno ni la uhakika!"},

{k:["test","testing","jaribio","123","abc","check","ping","online","hapa","uko","bot online","bot working","inafanya kazi"],
r:"Mfumo upo imara! ✅ AgroBot v4.0 imeupokea ujumbe wako. Nina KB ya mazao 30+ na bei za 2025/2026. Niulize chochote!"},

{k:["AI","artificial intelligence","machine learning","ChatGPT","GPT","robot","programu gani","technology","bot technology"],
r:"Mimi ni AgroBot — bot ya keyword-based iliyojengwa maalum kwa kilimo cha Tanzania! 🌱 Sijaundwa kwa ChatGPT lakini nimetengezwa na timu ya AgroLink. Ninajifunza kila wakati!"},
];

const DEFAULT="<strong>Mada hii iko nje ya eneo langu.</strong> 🌾<br><br>Mimi ni AgroBot — msaidizi wa kilimo peke yake. Ninaweza kukusaidia na mambo kama:<br>• Magonjwa ya mazao na dawa zake<br>• Bei za soko Tanzania 2025/2026<br>• Kilimo cha mazao: mahindi, nyanya, kahawa, korosho...<br>• Mbolea, mbegu bora, umwagiliaji<br>• Masoko, export, mikopo ya kilimo<br><br>Kwa maswali ya <em>mitambo, magari, vifaa vya ujenzi</em> na mambo mengine — tafadhali wasiliana na mtaalamu husika.<br><br><a href='/mshauri' style='color:#6ee7b7;font-weight:700'>→ Angalia mada zote ninazoweza kukusaidia nazo</a>";

// ══════════════════════════════════════════════════════════════════════════════
// SMART ENGINE v3 — Enhanced Scoring + Fuzzy + Multilingual
// ══════════════════════════════════════════════════════════════════════════════
function normalize(text){
  return text.toLowerCase().trim()
    // Kiswahili verb variations
    .replace(/kunyauka|unyaufu|anyauka|inyauka|unyauke/g,"mnyauko")
    .replace(/kuoza|inaoza|zinaoza|uoza|anaoza/g,"kuoza")
    .replace(/kukauka|inakauka|zinakauka|anakauka/g,"kukauka")
    .replace(/yanaliwa|inaliwa|inashambuliwa/g,"yanaliwa")
    .replace(/madoa|doa|vidonda|alama|makucha/g,"madoa")
    .replace(/njano|rangi ya njano|kugeuka njano|giza njano/g,"njano")
    .replace(/kahawia|rangi ya kahawia|brown/g,"kahawia")
    .replace(/wadudu|mdudu|visumbufu|insect|pest/g,"wadudu")
    .replace(/magonjwa|ugonjwa|maradhi|disease|diseases/g,"magonjwa")
    .replace(/dawa|tiba|matibabu|treatment|spray/g,"dawa")
    .replace(/kupanda|kupanda mbegu|planting|plant/g,"kilimo")
    .replace(/bei gani|bei ya|bei za|gharama|price|cost|bei ngapi/g,"bei")
    .replace(/majani|jani|leaves|leaf/g,"majani")
    .replace(/mmea|mimea|miche|plant|plants/g,"mmea")
    .replace(/shamba|mashamba|farm|field/g,"shamba")
    .replace(/harvest|kuvuna|mavuno|vuna/g,"mavuno")
    .replace(/seeds|mbegu bora|seed/g,"mbegu")
    .replace(/fertilizer|fertiliser|mbolea gani/g,"mbolea")
    .replace(/farming|kilimo cha|agriculture/g,"kilimo")
    .replace(/storage|kuhifadhi|store/g,"hifadhi")
    .replace(/export|kuuza nje|sell abroad/g,"export")
    .replace(/loan|credit|mkopo wa/g,"mkopo")
    .replace(/market|soko gani|where sell/g,"soko");
}

function extractTokens(text){
  const normalized = normalize(text);
  const stopWords = new Set([
    "na","ya","wa","la","za","kwa","ni","au","ama","hii","hizi","hilo",
    "hayo","yake","yangu","yako","yetu","zake","zangu","zako","zetu",
    "pia","sana","kabisa","tu","kidogo","zaidi","lakini","ingawa",
    "kwenye","katika","kutoka","hadi","mpaka","baada","kabla",
    "vipi","nini","gani","je","ndiyo","hapana","sijui","naona",
    "nimesikia","nimejua","ninajua","naweza","inaweza","unaweza",
    "okay","sawa","asante","tafadhali","naomba","nataka","niambie",
    "kuhusu","habari","hali","hata","pale","hapo","hapa","kule",
    "ule","ile","zile","vile","hizi","vivi","the","is","are","was",
    "what","how","why","when","where","which","does","do","can","my",
    "your","this","that","for","with","about","have","has","been"
  ]);
  return normalized.split(/\s+/).filter(t => t.length > 2 && !stopWords.has(t));
}

function scoreEntry(tokens, fullMsg, entry){
  let score = 0;
  const msg = normalize(fullMsg);

  for(const kw of entry.k){
    const normKw = normalize(kw);

    // Exact phrase match — highest score
    if(msg.includes(normKw)){
      score += 12 + normKw.split(" ").length * 3;
      continue;
    }

    const kwTokens = normKw.split(/\s+/);
    let tokenMatches = 0;
    for(const t of tokens){
      if(normKw.includes(t) || t.includes(normKw)){
        tokenMatches++;
      }
      if(t.length >= 4 && normKw.length >= 4){
        if(normKw.startsWith(t.substring(0,4)) || t.startsWith(normKw.substring(0,4))){
          tokenMatches += 0.5;
        }
      }
    }
    if(tokenMatches > 0) score += tokenMatches * 3;

    for(const kwt of kwTokens){
      if(kwt.length < 3) continue;
      for(const t of tokens){
        if(t === kwt) score += 5;
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
    if(score > bestScore){ bestScore = score; bestReply = entry.r; }
  }
  if(bestScore < 3) return DEFAULT;
  return bestReply;
}

// ── CONTEXT MEMORY (kukumbuka zao la mwisho) ─────────────────────────────
let _lastCrop = null;
const CROP_NAMES = ["mahindi","nyanya","viazi","mpunga","maharage","muhogo","ndizi","alizeti","ufuta","vitunguu","pilipili","karanga","kahawa","chai","korosho","pamba","tumbaku","mkonge","pareto","parachichi","ngano","mtama","miwa","kakao","mchicha","kabichi","bamia","embe","nanasi","tikiti"];

function detectCrop(msg){
  const m = msg.toLowerCase();
  for(const c of CROP_NAMES){ if(m.includes(c)) return c; }
  return null;
}

function getReplyWithContext(msg){
  const crop = detectCrop(msg);
  if(crop) _lastCrop = crop;
  
  // Maswali ya "zaidi" au "nini kingine" — tumia zao la mwisho
  const followUpWords = ["zaidi","kingine","nini kingine","na nini","pia","sawa sasa","ok na","vipi na","elezea zaidi","tell me more","more info","add more"];
  const msgLow = msg.toLowerCase();
  if(_lastCrop && !crop && followUpWords.some(w => msgLow.includes(w))){
    return getReply(_lastCrop + " " + msg);
  }
  return getReply(msg);
}

// ── STORAGE ───────────────────────────────────────────────────────────────
function saveH(h){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(h.slice(-MAX_H)));}catch(e){}}
function loadH(){try{const h=localStorage.getItem(STORAGE_KEY);return h?JSON.parse(h):[]}catch(e){return[];}}
function clearH(){try{localStorage.removeItem(STORAGE_KEY);}catch(e){}}

// ── AUTH ──────────────────────────────────────────────────────────────────
function isLoggedIn(){const el=document.getElementById("agrobot-auth");return el&&el.dataset.auth==="1";}
function getUserName(){const el=document.getElementById("agrobot-user");return el&&el.dataset.name?el.dataset.name:"";}
function getTimeGreeting(){
  const h=new Date().getHours();
  if(h>=5&&h<12)return"Habari za asubuhi";
  if(h>=12&&h<17)return"Habari za mchana";
  if(h>=17&&h<21)return"Habari za jioni";
  return"Habari za usiku";
}
function getUserName(){const el=document.getElementById("agrobot-user");return el&&el.dataset.name?el.dataset.name:"";}
function getTimeGreeting(){
  const h=new Date().getHours();
  if(h>=5&&h<12)return "Habari za asubuhi";
  if(h>=12&&h<17)return "Habari za mchana";
  if(h>=17&&h<21)return "Habari za jioni";
  return "Habari za usiku";
}

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

const CHIPS=["Kahawa Tanzania","Korosho bei 2025","Magonjwa ya nyanya","Kilimo cha mahindi","Cash crops Tanzania","Bei za soko 2026"];

// ── BUILD ─────────────────────────────────────────────────────────────────
function build(){
  const s=document.createElement("style");s.textContent=CSS;document.head.appendChild(s);

  const bub=document.createElement("div");bub.id="agrobot-bubble";
  bub.innerHTML=`<div id="abot-label">AgroBot v4.0 — Niulize!</div><div id="agrobot-bubble-inner"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="3"/><circle cx="9" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="12" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="15" cy="10.5" r="1.2" fill="white" stroke="none"/><path d="M8 17l-2 3M16 17l2 3" stroke-width="1.5"/></svg></div>`;
  document.body.appendChild(bub);

  const pan=document.createElement("div");pan.id="agrobot-panel";
  const chipsH=CHIPS.map(c=>`<button class="abot-chip" onclick="abotSend('${c}')">${c}</button>`).join("");
  pan.innerHTML=`
    <div id="abot-header">
      <div id="abot-avatar"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="13" rx="3"/><circle cx="9" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="12" cy="10.5" r="1.2" fill="white" stroke="none"/><circle cx="15" cy="10.5" r="1.2" fill="white" stroke="none"/><path d="M8 17l-2 3M16 17l2 3" stroke-width="1.5"/></svg></div>
      <div id="abot-title">
        <div id="abot-name">AgroBot v4.0 — Msaidizi wa Kilimo</div>
        <div id="abot-status"><span class="abot-dot"></span>Mazao 30+ · Bei 2025/2026</div>
      </div>
      <div class="abot-hbtn" title="Futa mazungumzo" onclick="abotClear()"><svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg></div>
      <div class="abot-hbtn" id="abot-close-btn" title="Funga" onclick="abotClose()"><svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div>
    </div>
    <a href="/mshauri" id="abot-know-more">
      <div id="abot-know-more-left">
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
        <div>
          <div id="abot-know-more-text">Unataka Kujua Zaidi?</div>
          <div id="abot-know-more-sub">Mada zote za kilimo → Mazao 30+</div>
        </div>
      </div>
      <div id="abot-know-more-arrow"><svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg></div>
    </a>
    <div id="abot-messages"></div>
    <div id="abot-chips">${chipsH}</div>
    <div id="abot-input-row">
      <input id="abot-input" type="text" placeholder="Mahindi, kahawa, korosho..." autocomplete="off"/>
      <button id="abot-send" onclick="abotSend()"><svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>
    </div>
  `;
  document.body.appendChild(pan);
  bub.addEventListener("click",abotOpen);
  document.getElementById("abot-input").addEventListener("keyup",e=>{if(e.key==="Enter"&&e.target.value.trim())abotSend();});
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
      if(!renderH()){
      const name=getUserName();
      const greet=getTimeGreeting();
      const welcome=name
        ? `${greet} <strong>${name}</strong>! 🌿 Mimi ni <strong>AgroBot v4.0</strong> msaidizi wako wa kilimo.<br>Nina taarifa za mazao <strong>30+</strong>, cash crops na bei za <strong>2025/2026</strong>. Niulize chochote!`
        : `Habari! Mimi ni <strong>AgroBot v4.0</strong> — msaidizi wako wa kilimo hapa AgroLink Tanzania. 🌿<br>Nina taarifa za mazao <strong>30+</strong> ikiwemo cash crops na bei za <strong>2025/2026</strong>. Niulize chochote!`;
      addMsg(welcome,"bot");
    }
    }
    box.scrollTop=box.scrollHeight;
  },50);
}
window.abotClose=function(){document.getElementById("agrobot-panel").classList.remove("open");};
window.abotClear=function(){
  if(!confirm("Futa mazungumzo yote?"))return;
  clearH();_H=[];_lastCrop=null;
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
    const greetings=["habari","hello","hi","niaje","mambo","salam","hujambo","karibu","hey","vipi","oya","sasa","test","testing","ping","check","wewe ni nani","unafanya nini"];
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
  setTimeout(()=>{t.remove();addMsg(getReplyWithContext(msg),"bot");},500+Math.random()*350);
};

if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",build);}else{build();}
})();
