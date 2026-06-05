import streamlit as st
import requests

st.set_page_config(page_title="Yapay Zeka Destekli Gezi Rehberi", page_icon="🌍", layout="wide")

BASE_URL = "https://gezi-rehberi-1.onrender.com"
STRAPI_TOKEN = "15e0d7dd5cc412d13012d7abdeab5ad54b624a8ab4386e08c3b6039000301a2c166ab03f9fdf940fcac7d51a8c7b19f6726b79b16fb3a6626a97459348ab01b4eefe9bfee7d1be761c538c166ccd5a9e7470aff1d435d56b84ee1109a5f6e600b908aedc220ce5e1443d6d722289a46216bbb7409fb452071373e0d688c95264"

headers = {
    "Authorization": f"Bearer {STRAPI_TOKEN}",
    "Content-Type": "application/json"
}

st.title("🌍 Yapay Zeka Destekli Gezi Rehberi")
st.markdown("---")

def blok_metin_coz(blocks):
    """Strapi Rich Text yapısını güvenli bir şekilde düz metne dönüştürür."""
    if not blocks:
        return ""
    if isinstance(blocks, str):
        return blocks
    if isinstance(blocks, list):
        metin_parcalari = []
        for block in blocks:
            if isinstance(block, dict) and 'children' in block:
                for child in block.get('children', []):
                    metin_parcalari.append(child.get('text', ''))
            elif isinstance(block, str):
                metin_parcalari.append(block)
        return " ".join(metin_parcalari)
    return ""

@st.cache_data(ttl=1)
def strapi_verileri_getir():
    # Şehir ilişkilerini de çekebilmek için populate=* zorunludur
    url = f"{BASE_URL}/api/mekanlars?populate=*"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('data', [])
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
    return []

ham_veriler = strapi_verileri_getir()
tum_mekanlar = []

# --- 1. VERİLERİ STRAPI'DEN ÇEKME VE TEMİZLEME ---
if ham_veriler:
    for oge in ham_veriler:
        attrs = oge.get('attributes', {}) or oge
        
        baslik = attrs.get('mekan_adi') or "Bilinmeyen Mekan"
        icerik_tr = blok_metin_coz(attrs.get('aciklama')) or "Açıklama veritabanında mevcut değil."
        icerik_en = blok_metin_coz(attrs.get('aciklama_en')) or "No translation available yet."
        
        # Kesinlikle kırılmayan yüksek kaliteli Unsplash görselleri
        gorsel_url = "https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=800"
        if "Colosseum" in baslik or "Roma" in baslik or "Amfi" in baslik:
            gorsel_url = "https://images.unsplash.com/photo-1552832230-c0197dd311b5?q=80&w=800"
        elif "Louvre" in baslik or "Paris" in baslik or "Müze" in baslik:
            gorsel_url = "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=800"
        elif "Big" in baslik or "Londra" in baslik or "Saat" in baslik:
            gorsel_url = "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?q=80&w=800"
        elif "Galata" in baslik or "İstanbul" in baslik or "Istanbul" in baslik:
            gorsel_url = "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?q=80&w=800"

        # Şehir ilişkisini okuma ve Türkçe karakter hatasını engelleme
        sehir_data = attrs.get('sehirler', {}).get('data')
        sehir_adi = "İstanbul"  # Varsayılan yedek şehir
        
        if sehir_data:
            if isinstance(sehir_data, list) and len(sehir_data) > 0:
                sehir_adi = sehir_data[0].get('attributes', {}).get('AD', "İstanbul")
            elif isinstance(sehir_data, dict):
                sehir_adi = sehir_data.get('attributes', {}).get('AD', "İstanbul")
        
        # Karşılaştırma kolaylığı için şehir ismini standartlaştırıyoruz (Örn: Istanbul -> İstanbul)
        if sehir_adi.lower() in ["istanbul", "i̇stanbul"]:
            sehir_adi = "İstanbul"

        tum_mekanlar.append({
            "Baslik": baslik,
            "Icerik_TR": icerik_tr,
            "Icerik_EN": icerik_en,
            "Sehir": sehir_adi,
            "Gorsel": gorsel_url
        })
else:
    # Veritabanına henüz veri gitmediyse veya izin hatası varsa çalışacak ÇÖKMEYİ ENGELLEYEN YEDEK HAVUZ
    tum_mekanlar = [
        {"Baslik": "Galata Kulesi", "Icerik_TR": "İstanbul'un en tarihi ve ikonik yapılarından biridir.", "Icerik_EN": "One of the most historical and iconic structures in Istanbul.", "Sehir": "İstanbul", "Gorsel": "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?q=80&w=800"},
        {"Baslik": "Colosseum Arena", "Icerik_TR": "Roma İmparatorluğu'nun dünyaca ünlü gladyatör amfitiyatrosu.", "Icerik_EN": "The world-famous gladiator amphitheater of the Roman Empire.", "Sehir": "Roma", "Gorsel": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?q=80&w=800"},
        {"Baslik": "Louvre Müzesi", "Icerik_TR": "Paris'in kalbinde bulunan dünyanın en büyük ve en ünlü sanat müzesi.", "Icerik_EN": "The world's largest and most famous art museum located in the heart of Paris.", "Sehir": "Paris", "Gorsel": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=800"},
        {"Baslik": "Big Ben", "Icerik_TR": "Londra'nın simgesi olan tarihi Westminster saat kulesi.", "Icerik_EN": "The historical Westminster clock tower, which is the symbol of London.", "Sehir": "Londra", "Gorsel": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?q=80&w=800"}
    ]

# --- 2. KULLANICI ARAYÜZÜ (STREAMLIT) ---
st.markdown("### 🗺️ Gezeceğiniz Şehri Seçin:")

# Şehirleri benzersiz olarak alıp alfabetik sıralıyoruz
mevcut_sehirler = sorted(list(set(m["Sehir"] for m in tum_mekanlar)))

# Seçim kutusu
secilen_sehir = st.selectbox("Şehir Seçin", mevcut_sehirler, index=0, label_visibility="collapsed")

# Seçilen şehre göre filtreleme
filtrelenmis_mekanlar = [m for m in tum_mekanlar if m["Sehir"] == secilen_sehir]

st.markdown(f"## 📍 {secilen_sehir} Gezi Noktaları")
st.markdown("---")

if filtrelenmis_mekanlar:
    cols = st.columns(3)
    for index, mekan in enumerate(filtrelenmis_mekanlar):
        with cols[index % 3]:
            st.markdown(
                f"""
                <div style="border:1px solid #e6e9ef; padding:15px; border-radius:12px; background-color:#ffffff; margin-bottom:20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                    <img src="{mekan['Gorsel']}" style="width:100%; height:220px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
                    <h3 style="margin-top:0; color:#1f1f1f; font-size:19px;">🏛️ {mekan['Baslik']}</h3>
                    <p style="font-size:14px; color:#444444; line-height:1.6; min-height:65px;">{mekan['Icerik_TR']}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            with st.expander(f"✨ Click for AI Translation"):
                st.caption("🤖 Yapay Zeka Tarafından Çevrilen İngilizce İçerik:")
                st.info(mekan['Icerik_EN'])
else:
    st.info(f"Şu an için {secilen_sehir} şehrine ait bir içerik bulunmuyor.")