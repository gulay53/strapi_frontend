import streamlit as st
import requests

st.set_page_config(page_title="Akıllı Gezi Rehberi 🎉", page_icon="🌍", layout="wide")

BASE_URL = "https://gezi-rehberi-1.onrender.com"
STRAPI_TOKEN = "cf39180c655853eb5774dbc4820709ce10b634e7bdc6d90d4a33f96e11f82186ddd2989c299aa35bf2598d73d1b6716dc37d3994b7b89935ad1d8549dd7fd3ca2b8e80255bd9cdddd6eaa508ba50c96733f50e5c666ee6273374fbc3e99b4b1ebc024c2d676efbf09aa6c2c79ce71c556b40e03a7ff9acac254350226fc275f4"

headers = {
    "Authorization": f"Bearer {STRAPI_TOKEN}",
    "Content-Type": "application/json"
}

def blok_metin_coz(blocks):
    """Strapi Rich Text (Blocks) yapısını güvenli bir şekilde temiz düz metne dönüştürür."""
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
        return "\n".join(metin_parcalari)
    return ""

st.sidebar.markdown("### 🌐 Dil Seçimi / Language")
secilen_dil = st.sidebar.radio("Sitenin Dili / Site Language", ["Türkçe", "English"], label_visibility="collapsed")

strapi_locale = "tr" if secilen_dil == "Türkçe" else "en"

@st.cache_data(ttl=1)
def mekanlari_getir(locale_kodu):
    url = f"{BASE_URL}/api/mekanlars?locale={locale_kodu}&populate=bilesenler,kapak_resmi&sort=createdAt:desc"
    try:
        res = requests.get(url, headers=headers)
        if res.ok:
            return res.json().get("data", [])
    except Exception as e:
        st.error(f"Sunucuya bağlanırken bir hata oluştu: {e}")
    return []

mekanlar_listesi = mekanlari_getir(strapi_locale)

sozluk = {
    "Türkçe": {
        "ana_baslik": "🗺️ Gezi Rehberi",
        "alt_baslik": "Yapay zeka destekli RSS akışları ve dinamik tüyolarla donatılmış mekan rehberiniz.",
        "mekan_sec": "Keşfetmek istediğiniz mekanı seçin:",
        "bos_uyari": "Henüz eklenmiş bir mekan bulunamadı veya sunucunuz şu an uyanıyor. Lütfen birazdan sayfayı yenileyin.",
        "tuyo_baslik": "🧭 Gezgin Tüyoları & Önemli Bilgiler",
        "tuyo_bos": "Bu mekan için henüz dinamik gezgin tüyoları (Dynamic Zone) girilmemiş.",
        "aciklama_bos": "Açıklama bulunmuyor.",
        "kritik": "Kritik Uyarı",
        "altin": "Altın Tavsiye",
        "genel": "Genel Bilgi"
    },
    "English": {
        "ana_baslik": "🗺️ Travel Guide",
        "alt_baslik": "Your travel guide equipped with AI-powered RSS feeds and dynamic tips.",
        "mekan_sec": "Select the place you want to explore:",
        "bos_uyari": "No places found yet or your server is waking up. Please refresh the page in a moment.",
        "tuyo_baslik": "🧭 Traveler Tips & Important Information",
        "tuyo_bos": "No dynamic traveler tips (Dynamic Zone) have been entered for this location yet.",
        "aciklama_bos": "No description available.",
        "kritik": "Critical Warning",
        "altin": "Golden Tip",
        "genel": "General Info"
    }
}

m = sozluk[secilen_dil]

st.title(m["ana_baslik"])
st.write(m["alt_baslik"])
st.write("---")

if not mekanlar_listesi:
    st.info(m["bos_uyari"])
else:
    mekan_isimleri = [oge.get("mekan_adi", "İsimsiz Mekan") for oge in mekanlar_listesi if isinstance(oge, dict)]
        
    st.sidebar.markdown(f"### 📍 {m['mekan_sec']}")
    secilen_mekan_adi = st.sidebar.selectbox("Mekanlar", mekan_isimleri, label_visibility="collapsed")

    for oge in mekanlar_listesi:
        if isinstance(oge, dict) and oge.get("mekan_adi") == secilen_mekan_adi:
            
            puan = oge.get("puan", 5)
            yildizlar = "⭐" * int(puan) if puan else "⭐"
            st.header(f"📍 {oge.get('mekan_adi')} {yildizlar}")
            
            kapak_verisi = oge.get("kapak_resmi")
            if isinstance(kapak_verisi, dict):
                resim_url_kisa = kapak_verisi.get("url", "")
                if resim_url_kisa:
                    tam_resim_url = resim_url_kisa if resim_url_kisa.startswith("http") else f"{BASE_URL}{resim_url_kisa}"
                    st.image(tam_resim_url, use_container_width=True)
            
            st.write("") 
            
            ham_aciklama = oge.get("aciklama")
            temiz_aciklama = blok_metin_coz(ham_aciklama)
            st.write(temiz_aciklama if temiz_aciklama else m["aciklama_bos"])
            st.write("---")
            
            bilesenler = oge.get("bilesenler", [])
            if bilesenler and isinstance(bilesenler, list):
                st.subheader(m["tuyo_baslik"])
                for b in bilesenler:
                    if isinstance(b, dict):
                        tur = b.get("__component") or b.get("component")
                        
                        if tur == "gezi.tuyo-kutusu" or "tuyo-kutusu" in str(tur):
                            tip = b.get("tip", "Bilgi")
                            mesaj_icerigi = b.get("mesaj")
                            mesaj_metni = blok_metin_coz(mesaj_icerigi)
                            
                            if tip == "Uyar":
                                st.error(f"⚠️ **{m['kritik']}:** {mesaj_metni}")
                            elif tip == "Tavsiye":
                                st.success(f"💡 **{m['altin']}:** {mesaj_metni}")
                            elif tip == "Bilgi":
                                st.info(f"ℹ️ **{m['genel']}:** {mesaj_metni}")
            else:
                st.warning(m["tuyo_bos"])
