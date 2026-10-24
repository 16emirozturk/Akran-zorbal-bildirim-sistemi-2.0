
import hmac
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st
from hakaret_tespiti import supheli_ifadeleri_bul


# =========================================================
# 1. SAYFA AYARLARI VE GÖRÜNÜM
# =========================================================

st.set_page_config(
    page_title="Güvenli Okul | 3.1",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(__file__).with_name("guvenli_okul_demo.db")

DURUMLAR = [
    "İnceleme bekliyor",
    "İnceleniyor",
    "Takip gerekiyor",
    "Sonuçlandırıldı",
]

BIRIMLER = [
    "Henüz atanmadı",
    "Demo rehberlik birimi",
    "Demo yönetim birimi",
    "Demo destek ekibi",
]

OLAY_TURLERI = [
    "Hakaret veya alay",
    "Tehdit",
    "Dışlama",
    "Dijital zorbalık",
    "Fiziksel zorbalık şüphesi",
    "Diğer",
]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --navy: #13243b;
        --blue: #2864dc;
        --cyan: #42c6c5;
        --ink: #17263c;
        --muted: #64748b;
        --line: #e4eaf2;
        --surface: #ffffff;
    }

    .stApp {
        background: linear-gradient(180deg, #f5f8fc 0%, #edf3fa 100%);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] { background: rgba(245,248,252,.82); }
    [data-testid="stSidebar"] {
        background: linear-gradient(165deg, #13243b 0%, #172f50 60%, #21466a 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }
    [data-testid="stSidebar"] * { color: #f3f7ff; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: .42rem .55rem;
        border-radius: 9px;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,.09);
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.16); }

    h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: #17263c; letter-spacing: -.035em; }
    h1 { font-weight: 800 !important; }
    h2, h3 { font-weight: 700 !important; }
    p, label, .stMarkdown { line-height: 1.62; }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.5rem 2.35rem;
        border-radius: 24px;
        background: linear-gradient(120deg, #142844 0%, #24558a 62%, #2e7b9a 100%);
        color: white;
        margin: .35rem 0 1.35rem 0;
        box-shadow: 0 18px 42px rgba(24, 61, 101, .17);
    }
    .hero:after {
        content: '';
        position: absolute;
        width: 250px; height: 250px;
        right: -65px; top: -100px;
        border-radius: 50%;
        border: 34px solid rgba(255,255,255,.08);
        box-shadow: 0 0 0 35px rgba(255,255,255,.035);
    }
    .hero h1 { color: white !important; font-size: clamp(2rem, 4vw, 2.8rem) !important; margin: 0 0 .55rem 0; }
    .hero p { color: #e4efff; font-size: 1.06rem; max-width: 720px; margin: 0; }
    .eyebrow { text-transform: uppercase; letter-spacing: .16em; font-size: .72rem; font-weight: 700; color: #bde9f3; margin-bottom: .7rem; }
    .section-note { color: #64748b; margin-top: -.45rem; margin-bottom: 1rem; }
    .soft-card {
        background: rgba(255,255,255,.92);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 8px 22px rgba(27, 48, 78, .045);
    }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.95);
        border: 1px solid var(--line);
        padding: 1.05rem 1.15rem;
        border-radius: 17px;
        box-shadow: 0 7px 20px rgba(27, 48, 78, .04);
    }
    div[data-testid="stMetricLabel"] { color: #64748b; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #17263c; font-family: 'Manrope', sans-serif; }
    div[data-testid="stForm"] {
        background: rgba(255,255,255,.96);
        padding: 1.35rem;
        border: 1px solid var(--line);
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(27, 48, 78, .045);
    }
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
        border-radius: 11px !important;
        border-color: #d8e1ed !important;
        background: #fbfdff !important;
    }
    .stButton button, .stFormSubmitButton button {
        border-radius: 11px;
        font-weight: 700;
        padding: .55rem 1rem;
        transition: all .18s ease;
    }
    .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {
        background: linear-gradient(100deg, #2864dc, #247fb3);
        border: 0;
        box-shadow: 0 7px 16px rgba(40,100,220,.18);
    }
    .stButton button:hover, .stFormSubmitButton button:hover { transform: translateY(-1px); }
    [data-testid="stExpander"] {
        background: rgba(255,255,255,.92);
        border: 1px solid var(--line);
        border-radius: 14px;
        overflow: hidden;
    }
    [data-testid="stAlert"] { border-radius: 13px; }
    hr { border-color: #e1e8f1; }
    .muted { color: var(--muted); font-size: .9rem; }
    .page-heading { padding: .25rem 0 1.1rem 0; }
    .page-heading h1 { margin: .15rem 0 .35rem 0; font-size: clamp(1.8rem, 3vw, 2.35rem) !important; }
    .page-heading p { margin: 0; color: #64748b; max-width: 760px; }
    .eyebrow-dark { color: #2864dc; font-size: .7rem; font-weight: 800; letter-spacing: .16em; }
    .section-spacer { height: .5rem; }
    .results-strip { display:flex; justify-content:space-between; gap:1rem; padding:.75rem 1rem; margin:.4rem 0 .8rem; border:1px solid #e2e8f0; border-radius:12px; background:#f8fafc; color:#64748b; font-size:.88rem; }
    .results-strip strong { color:#17263c; }
    .record-banner { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:.9rem 1rem; margin-bottom:1rem; border:1px solid #e4eaf2; border-radius:14px; background:linear-gradient(120deg,#f8fbff,#f1f6fc); }
    .record-kicker { color:#64748b; font-size:.68rem; font-weight:800; letter-spacing:.12em; }
    .record-id { color:#17263c; font-family:'Manrope',sans-serif; font-size:1.25rem; font-weight:800; }
    .status-pill { display:inline-block; border-radius:999px; padding:.35rem .7rem; font-size:.76rem; font-weight:800; white-space:nowrap; }
    .status-waiting { color:#8a5700; background:#fff3d6; }
    .status-active { color:#1d4ed8; background:#e4edff; }
    .status-followup { color:#9a3412; background:#ffeadf; }
    .status-done { color:#166534; background:#dcfce7; }
    .access-panel { display:flex; align-items:center; gap:1rem; padding:1.25rem; border:1px solid #dbe5f1; border-radius:16px; background:#fff; box-shadow:0 8px 22px rgba(27,48,78,.04); }
    .access-icon { display:flex; align-items:center; justify-content:center; width:48px; height:48px; flex-shrink:0; border-radius:14px; background:#e9f0ff; font-size:1.35rem; }
    .access-panel strong { color:#17263c; font-size:1.05rem; }
    .access-panel span { color:#64748b; font-size:.9rem; }
    @media (max-width: 700px) {
        .hero { padding: 1.6rem 1.25rem; border-radius: 18px; }
        div[data-testid="stForm"] { padding: .85rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 2. YÖNETİCİ AYARLARI
# Streamlit Cloud > Settings > Secrets
# =========================================================

try:
    ADMIN_USERNAME = str(st.secrets["admin"]["username"])
    ADMIN_PASSWORD = str(st.secrets["admin"]["password"])
except (KeyError, FileNotFoundError):
    ADMIN_USERNAME = ""
    ADMIN_PASSWORD = ""


# =========================================================
# 3. VERİTABANI VE GÜVENLİ ŞEMA GÜNCELLEMESİ
# =========================================================

def baglanti_ac():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def sutun_ekle(conn, tablo, sutun, tanim):
    mevcut = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({tablo})")
    }
    if sutun not in mevcut:
        conn.execute(
            f"ALTER TABLE {tablo} ADD COLUMN {sutun} {tanim}"
        )


def islem_kaydi(conn, takip_no, islem, ayrinti=""):
    conn.execute(
        """
        INSERT INTO islem_gecmisi
        (takip_no, zaman, islem, ayrinti)
        VALUES (?, ?, ?, ?)
        """,
        (
            takip_no,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            islem,
            ayrinti,
        ),
    )


def veritabani_hazirla():
    with baglanti_ac() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bildirimler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                takip_no TEXT UNIQUE NOT NULL,
                olusturma_zamani TEXT NOT NULL,
                olay_turu TEXT NOT NULL,
                ortam TEXT NOT NULL,
                zaman_bilgisi TEXT NOT NULL,
                tekrar_durumu TEXT NOT NULL,
                aciklama TEXT NOT NULL,
                eslesmeler TEXT NOT NULL,
                durum TEXT NOT NULL DEFAULT 'İnceleme bekliyor',
                demo INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        # Eski veritabanını silmeden yeni alanları ekle.
        sutun_ekle(conn, "bildirimler", "anonim", "INTEGER NOT NULL DEFAULT 1")
        sutun_ekle(conn, "bildirimler", "ad", "TEXT NOT NULL DEFAULT ''")
        sutun_ekle(conn, "bildirimler", "soyad", "TEXT NOT NULL DEFAULT ''")
        sutun_ekle(conn, "bildirimler", "sinif", "TEXT NOT NULL DEFAULT ''")
        sutun_ekle(conn, "bildirimler", "birim", "TEXT NOT NULL DEFAULT 'Henüz atanmadı'")
        sutun_ekle(conn, "bildirimler", "son_guncelleme", "TEXT NOT NULL DEFAULT ''")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS inceleme_notlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                takip_no TEXT NOT NULL,
                zaman TEXT NOT NULL,
                not_metni TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS islem_gecmisi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                takip_no TEXT NOT NULL,
                zaman TEXT NOT NULL,
                islem TEXT NOT NULL,
                ayrinti TEXT NOT NULL DEFAULT ''
            )
            """
        )


def demo_kayitlari_ekle():
    """Yalnızca kurgu örnekleri; mevcut kayıtları tekrar eklemez."""
    with baglanti_ac() as conn:
        adet = conn.execute(
            "SELECT COUNT(*) FROM bildirimler"
        ).fetchone()[0]

        if adet:
            return

        ornekler = [
            (
                "DEMO-A102",
                "Hakaret veya alay",
                "Sınıfta",
                "Bugün",
                "Birden fazla kez",
                "Kurgusal örnek: Bir öğrenci sınıf sohbetinde alay edildiğini bildiriyor.",
                "İnsan değerlendirmesi gerekli",
                "İnceleme bekliyor",
            ),
            (
                "DEMO-B204",
                "Dışlama",
                "Okul bahçesinde",
                "Bu hafta",
                "Birkaç kez",
                "Kurgusal örnek: Bir öğrenci grup etkinliklerine alınmadığını düşünüyor.",
                "İnsan değerlendirmesi gerekli",
                "İnceleniyor",
            ),
            (
                "DEMO-C306",
                "Dijital zorbalık",
                "Mesajlaşmada",
                "Dün",
                "Bir kez",
                "Kurgusal örnek: Bir öğrenci rahatsız edici bir mesaj aldığını bildiriyor.",
                "Örnek ifade eşleşmesi yok",
                "İnceleme bekliyor",
            ),
        ]

        for r in ornekler:
            conn.execute(
                """
                INSERT INTO bildirimler (
                    takip_no, olusturma_zamani, olay_turu, ortam,
                    zaman_bilgisi, tekrar_durumu, aciklama,
                    eslesmeler, durum, demo, anonim, birim,
                    son_guncelleme
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
                """,
                (
                    r[0],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    *r[1:],
                    "Henüz atanmadı",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            islem_kaydi(conn, r[0], "Demo kaydı oluşturuldu")


def test_kayitlarini_sifirla():
    """Kullanıcının oluşturduğu test kayıtlarını siler, 3 örneği korur/yeniler."""
    ornek_takip_nolari = ("DEMO-A102", "DEMO-B204", "DEMO-C306")
    placeholders = ", ".join("?" for _ in ornek_takip_nolari)

    with baglanti_ac() as conn:
        # Test bildirimlerine bağlı not ve işlem geçmişini de temizle.
        conn.execute(
            f"DELETE FROM inceleme_notlari WHERE takip_no NOT IN ({placeholders})",
            ornek_takip_nolari,
        )
        conn.execute(
            f"DELETE FROM islem_gecmisi WHERE takip_no NOT IN ({placeholders})",
            ornek_takip_nolari,
        )
        conn.execute(
            f"DELETE FROM bildirimler WHERE takip_no NOT IN ({placeholders})",
            ornek_takip_nolari,
        )

    # Örnek kayıtlar daha önce oluşmadıysa, temizleme sonrası ekle.
    demo_kayitlari_ekle()


def ilk_acilista_kayitlari_temizle():
    """Mevcut test verilerini yalnızca bir kez temizler; sonraki açılışlarda silmez."""
    with baglanti_ac() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS uygulama_ayar (anahtar TEXT PRIMARY KEY, deger TEXT NOT NULL)"
        )
        tamamlandi = conn.execute(
            "SELECT deger FROM uygulama_ayar WHERE anahtar = ?",
            ("ilk_temizlik_tamamlandi_v1",),
        ).fetchone()
        if tamamlandi is None:
            conn.execute("DELETE FROM inceleme_notlari")
            conn.execute("DELETE FROM islem_gecmisi")
            conn.execute("DELETE FROM bildirimler")
            conn.execute(
                "INSERT INTO uygulama_ayar (anahtar, deger) VALUES (?, ?)",
                ("ilk_temizlik_tamamlandi_v1", "evet"),
            )


def kayitlari_getir():
    with baglanti_ac() as conn:
        return [
            dict(row)
            for row in conn.execute(
                "SELECT * FROM bildirimler ORDER BY id DESC"
            ).fetchall()
        ]


def bildirim_ekle(
    olay_turu,
    ortam,
    zaman_bilgisi,
    tekrar_durumu,
    aciklama,
    anonim,
    ad,
    soyad,
    sinif,
):
    bulunanlar = supheli_ifadeleri_bul(aciklama)
    takip_no = "GO-" + uuid.uuid4().hex[:8].upper()
    eslesmeler = (
        ", ".join(bulunanlar)
        if bulunanlar
        else "Belirgin eşleşme yok"
    )
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Anonim bildirimlerde kimlik alanları veritabanına yazılmaz.
    if anonim:
        ad, soyad, sinif = "", "", ""

    with baglanti_ac() as conn:
        conn.execute(
            """
            INSERT INTO bildirimler (
                takip_no, olusturma_zamani, olay_turu, ortam,
                zaman_bilgisi, tekrar_durumu, aciklama,
                eslesmeler, durum, demo, anonim, ad, soyad,
                sinif, birim, son_guncelleme
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
            """,
            (
                takip_no, simdi, olay_turu, ortam,
                zaman_bilgisi, tekrar_durumu, aciklama,
                eslesmeler, "İnceleme bekliyor", int(anonim),
                ad, soyad, sinif, "Henüz atanmadı", simdi,
            ),
        )
        islem_kaydi(conn, takip_no, "Yeni demo bildirimi oluşturuldu")

    return takip_no, bulunanlar


def durum_ve_birim_guncelle(takip_no, yeni_durum, yeni_birim):
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with baglanti_ac() as conn:
        eski = conn.execute(
            "SELECT durum, birim FROM bildirimler WHERE takip_no = ?",
            (takip_no,),
        ).fetchone()

        if not eski:
            return

        if eski["durum"] != yeni_durum:
            islem_kaydi(
                conn, takip_no, "Durum değiştirildi",
                f"{eski['durum']} → {yeni_durum}",
            )

        if eski["birim"] != yeni_birim:
            islem_kaydi(
                conn, takip_no, "Birim ataması değiştirildi",
                f"{eski['birim']} → {yeni_birim}",
            )

        conn.execute(
            """
            UPDATE bildirimler
            SET durum = ?, birim = ?, son_guncelleme = ?
            WHERE takip_no = ?
            """,
            (yeni_durum, yeni_birim, simdi, takip_no),
        )


def not_ekle(takip_no, metin):
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with baglanti_ac() as conn:
        conn.execute(
            """
            INSERT INTO inceleme_notlari (takip_no, zaman, not_metni)
            VALUES (?, ?, ?)
            """,
            (takip_no, simdi, metin),
        )
        islem_kaydi(conn, takip_no, "İnceleme notu eklendi")


def notlari_getir(takip_no):
    with baglanti_ac() as conn:
        return [
            dict(r) for r in conn.execute(
                """
                SELECT zaman, not_metni
                FROM inceleme_notlari
                WHERE takip_no = ?
                ORDER BY id DESC
                """,
                (takip_no,),
            ).fetchall()
        ]


def gecmisi_getir(takip_no):
    with baglanti_ac() as conn:
        return [
            dict(r) for r in conn.execute(
                """
                SELECT zaman, islem, ayrinti
                FROM islem_gecmisi
                WHERE takip_no = ?
                ORDER BY id DESC
                """,
                (takip_no,),
            ).fetchall()
        ]


veritabani_hazirla()
ilk_acilista_kayitlari_temizle()


# =========================================================
# 4. YAN MENÜ VE YÖNETİCİ OTURUMU
# =========================================================

if "yonetici_giris" not in st.session_state:
    st.session_state.yonetici_giris = False

st.sidebar.markdown("# 🛡️ Güvenli Okul")
st.sidebar.caption("Akran zorbalığı bildirim ve inceleme demosu")
st.sidebar.divider()


sayfa = st.sidebar.radio(
    "MENÜ",
    [
        "Genel bakış",
        "Yeni bildirim",
        "Yönetici girişi",
        "Bildirim inceleme",
        "İstatistikler",
        "Araştırma ve test",
        "Güvenli kullanım",
    ]
)



st.sidebar.divider()
st.sidebar.info(
    "3.1 DEMO\n\nGerçek bir okul sistemine bağlı değildir. "
    "Gerçek öğrenci bilgileri girmeyin."
)

if st.session_state.yonetici_giris:
    st.sidebar.success("Yönetici oturumu açık")
    if st.sidebar.button("Güvenli çıkış yap", use_container_width=True):
        st.session_state.yonetici_giris = False
        st.rerun()


# =========================================================
# 5. GENEL BAKIŞ
# Bu sayfada yalnızca genel, hassas olmayan bilgi gösterilir.
# =========================================================

if sayfa == "Genel bakış":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">GÜVENLİ OKUL · DEMO PLATFORMU</div>
            <h1>Her öğrenci, güvenli bir okul ortamını hak eder.</h1>
            <p>Bildirim süreçlerini düzenli biçimde modellemek, inceleme adımlarını takip etmek ve güvenli okul kültürünü desteklemek için hazırlanmış bir prototip.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Bu uygulama bir prototiptir. Buradan gerçek okula veya rehberlik servisine bildirim gönderilmez; yalnızca kurgusal test verileri kullanın."
    )

    st.subheader("Platforma genel bakış")
    st.markdown('<p class="section-note">Güvenli ve anlaşılır bir bildirim iş akışı için temel araçlar.</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Sürüm", "3.0", help="Güvenli Okul demo sürümü")
    c2.metric("İnceleme yaklaşımı", "İnsan denetimli")
    c3.metric("Gerçek öğrenci verisi", "Kullanılmıyor")

    st.subheader("Nasıl kullanılır?")
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown(
            """
            <div class="soft-card">
                <div style="font-size:1.55rem;margin-bottom:.45rem">📝</div>
                <h3 style="margin:.1rem 0 .45rem 0;font-size:1.12rem">Demo bildirimi oluştur</h3>
                <p style="color:#64748b;margin:0">Kurgusal bir senaryo girerek formun ve takip kodu üretiminin nasıl çalıştığını test et.</p>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button("Yeni bildirim sayfasına git", type="primary", use_container_width=True):
            st.info("Yeni bildirim sayfasını sol menüden açabilirsin.")
    with b:
        st.markdown(
            """
            <div class="soft-card">
                <div style="font-size:1.55rem;margin-bottom:.45rem">🔎</div>
                <h3 style="margin:.1rem 0 .45rem 0;font-size:1.12rem">İnceleme akışını keşfet</h3>
                <p style="color:#64748b;margin:0">Yetkili demo oturumuyla durumları, demo birim atamalarını ve işlem geçmişini incele.</p>
            </div>
            """, unsafe_allow_html=True
        )
        if st.button("Yönetici girişine git", use_container_width=True):
            st.info("Yönetici girişi sayfasını sol menüden açabilirsin.")

    st.subheader("Güvenlik ilkeleri")
    g1, g2, g3 = st.columns(3, gap="medium")
    with g1:
        st.markdown("**🔒 Gizlilik**\n\nAnonim demo seçeneği ve yöneticiye özel inceleme alanı.")
    with g2:
        st.markdown("**🧭 İnsan değerlendirmesi**\n\nOtomatik ifade eşleşmeleri kesin karar veya kanıt değildir.")
    with g3:
        st.markdown("**🧪 Güvenli test**\n\nÖrnekler kurgusaldır; gerçek kişisel bilgiler kullanılmamalıdır.")


# =========================================================
# 6. YENİ BİLDİRİM
# Yönetici girişi gerektirmez; yönetim kayıtları gösterilmez.
# =========================================================

elif sayfa == "Yeni bildirim":
    st.title("📝 Yeni demo bildirimi")
    st.write("Lütfen yalnızca kurgusal test bilgileri kullan.")

    st.warning(
        "Bu sürüm gerçek ve gizli bildirimler için tasarlanmamıştır. "
        "Gerçek ad, okul numarası, telefon, adres veya başka bir "
        "öğrenciyi tanımlayan bilgi girmeyin."
    )

    # Checkbox formun DIŞINDA olmalı: Streamlit form içindeki
    # checkbox değişikliklerinde anında yeniden çalışmaz. Dışarıda
    # olunca anonim seçimi değiştiğinde alanlar hemen açılıp kapanır.
    anonim = st.checkbox(
        "Anonim demo bildirimi oluştur",
        value=True,
        key="anonim_demo_secimi",
        help="Açıksa ad, soyad ve sınıf kayda alınmaz.",
    )

    st.caption(
        "Anonim seçenek açıkken ad, soyad ve sınıf alanları "
        "devre dışıdır ve veritabanına kaydedilmez."
    )

    with st.form("bildirim_formu", clear_on_submit=True):
        ad = st.text_input(
            "Ad (yalnızca kurgusal test bilgisi)",
            max_chars=40,
            disabled=anonim,
        )
        soyad = st.text_input(
            "Soyad (yalnızca kurgusal test bilgisi)",
            max_chars=40,
            disabled=anonim,
        )
        sinif = st.selectbox(
            "Sınıf / şube (demo)",
            ["Seçilmedi", "9/A", "9/B", "10/A", "10/B",
             "11/A", "11/B", "12/A", "12/B"],
            disabled=anonim,
        )

        olay_turu = st.selectbox("Olay türü", OLAY_TURLERI)

        ortam = st.selectbox(
            "Olayın gerçekleştiği ortam",
            [
                "Sınıfta", "Okul bahçesinde", "Koridorda",
                "Sosyal medyada", "Mesajlaşmada", "Diğer",
            ],
        )

        zaman_bilgisi = st.selectbox(
            "Yaklaşık zaman",
            ["Bugün", "Dün", "Bu hafta", "Daha önce", "Emin değilim"],
        )

        tekrar_durumu = st.radio(
            "Tekrarlanma durumu",
            ["Bir kez", "Birkaç kez", "Birden fazla kez", "Emin değilim"],
            horizontal=True,
        )

        aciklama = st.text_area(
            "Olay açıklaması (kurgu test metni)",
            placeholder="Örnek: Kurgusal bir öğrenci grup sohbetinde alay edildiğini söylüyor.",
            max_chars=3000,
            height=150,
        )

        onay = st.checkbox(
            "Yalnızca kurgusal demo verisi girdiğimi onaylıyorum."
        )

        gonder = st.form_submit_button(
            "Demo bildirimini oluştur",
            type="primary",
            use_container_width=True,
        )

    if gonder:
        if not aciklama.strip():
            st.error("Lütfen kurgusal bir test açıklaması gir.")
        elif not onay:
            st.error("Önce demo verisi onayını işaretle.")
        elif not anonim and not ad.strip():
            st.error("Anonim olmayan demo için kurgusal bir ad gir.")
        elif not anonim and not soyad.strip():
            st.error("Anonim olmayan demo için kurgusal bir soyad gir.")
        elif not anonim and sinif == "Seçilmedi":
            st.error("Kimlik bilgili demo için bir örnek sınıf seç.")
        else:
            try:
                takip_no, bulunanlar = bildirim_ekle(
                    olay_turu,
                    ortam,
                    zaman_bilgisi,
                    tekrar_durumu,
                    aciklama.strip(),
                    anonim,
                    ad.strip(),
                    soyad.strip(),
                    "" if sinif == "Seçilmedi" else sinif,
                )

                st.success("Kurgusal demo bildirimi oluşturuldu.")
                st.write("Takip kodun:")
                st.code(takip_no)

                st.info(
                    "Bu kod bir demo referansıdır. Gerçek bir kuruma "
                    "bildirim gönderilmedi."
                )

                if bulunanlar:
                    st.warning(
                        "İnsan incelemesine yardımcı olabilecek "
                        "ifade eşleşmeleri: " + ", ".join(bulunanlar)
                    )
                else:
                    st.caption(
                        "Belirgin ifade eşleşmesi bulunmadı. "
                        "Bu, zorbalık olmadığı anlamına gelmez."
                    )

            except sqlite3.Error:
                st.error("Demo kaydı oluşturulamadı. Uygulama günlüklerini kontrol et.")


# =========================================================
# 7. YÖNETİCİ GİRİŞİ
# =========================================================

elif sayfa == "Yönetici girişi":
    st.markdown(
        """
        <div class="hero">
            <h1>🔐 Yönetici girişi</h1>
            <p>Bildirim inceleme alanı yalnızca yetkili demo oturumuna açıktır.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.yonetici_giris:
        st.success("Yönetici oturumu zaten açık.")
        st.write("Bildirim inceleme menüsünü açabilirsin.")
    elif not ADMIN_USERNAME or not ADMIN_PASSWORD:
        st.error(
            "Yönetici bilgileri ayarlanmamış. "
            "Streamlit Cloud > Settings > Secrets bölümünü yapılandır."
        )
    else:
        with st.form("yonetici_giris_formu"):
            kullanici = st.text_input("Kullanıcı adı")
            parola = st.text_input("Parola", type="password")
            giris_yap = st.form_submit_button(
                "Giriş yap",
                type="primary",
                use_container_width=True,
            )

        if giris_yap:
            kullanici_dogru = hmac.compare_digest(
                kullanici, ADMIN_USERNAME
            )
            parola_dogru = hmac.compare_digest(
                parola, ADMIN_PASSWORD
            )

            if kullanici_dogru and parola_dogru:
                st.session_state.yonetici_giris = True
                st.success("Demo yönetici girişi başarılı.")
                st.rerun()
            else:
                st.error("Kullanıcı adı veya parola hatalı.")


# =========================================================
# 8. YÖNETİCİ İNCELEME PANELİ
# Kayıtları getirme işlemi yalnızca oturum kontrolünden sonra.
# =========================================================

elif sayfa == "Bildirim inceleme":
    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow-dark">OPERASYON MERKEZİ · DEMO</div>
            <h1>Bildirim inceleme merkezi</h1>
            <p>Kayıtları sırala, inceleme durumunu güncelle ve yapılan işlemleri tek yerden takip et.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.yonetici_giris:
        st.markdown(
            """
            <div class="access-panel">
                <div class="access-icon">🔐</div>
                <div><strong>Yönetici erişimi gerekli</strong><br>
                <span>Bu çalışma alanı yalnızca demo yönetici oturumu açıldığında görüntülenir.</span></div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Yönetici girişine git", type="primary"):
            st.session_state["_yonetici_giris_yonlendir"] = True
            st.rerun()
        st.stop()

    kayitlar = kayitlari_getir()
    bekleyen = sum(k["durum"] == "İnceleme bekliyor" for k in kayitlar)
    incelenen = sum(k["durum"] == "İnceleniyor" for k in kayitlar)
    takip = sum(k["durum"] == "Takip gerekiyor" for k in kayitlar)
    sonuclanan = sum(k["durum"] == "Sonuçlandırıldı" for k in kayitlar)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOPLAM BİLDİRİM", len(kayitlar))
    m2.metric("İLK İNCELEME", bekleyen)
    m3.metric("AKTİF TAKİP", incelenen + takip)
    m4.metric("TAMAMLANAN", sonuclanan)

    st.markdown("<div class='section-spacer'></div>", unsafe_allow_html=True)
    st.markdown("### Kayıt kuyruğu")
    st.caption("Takip kodu üzerinden çalış. Gereksiz kişisel bilgileri notlara ekleme; yalnızca kurgusal demo içeriği kullan.")

    f1, f2, f3 = st.columns([1.6, 1, 1])
    with f1:
        arama = st.text_input(
            "Kayıt ara",
            placeholder="Takip kodu veya olay türü…",
            label_visibility="collapsed",
        )
    with f2:
        durum_filtresi = st.selectbox(
            "Durum filtresi", ["Tüm durumlar"] + DURUMLAR,
            label_visibility="collapsed",
        )
    with f3:
        anonim_filtresi = st.selectbox(
            "Bildirim türü", ["Tümü", "Anonim", "Kimlik bilgisi belirtilmiş"],
            label_visibility="collapsed",
        )

    gorunen = []
    for k in kayitlar:
        if durum_filtresi != "Tüm durumlar" and k["durum"] != durum_filtresi:
            continue
        if anonim_filtresi == "Anonim" and not k["anonim"]:
            continue
        if anonim_filtresi == "Kimlik bilgisi belirtilmiş" and k["anonim"]:
            continue
        if arama.strip():
            aranacak = (str(k["takip_no"]) + " " + str(k["olay_turu"])).casefold()
            if arama.strip().casefold() not in aranacak:
                continue
        gorunen.append(k)

    st.markdown(
        f"<div class='results-strip'><span><strong>{len(gorunen)}</strong> kayıt listeleniyor</span><span>Toplam kayıt: {len(kayitlar)}</span></div>",
        unsafe_allow_html=True,
    )

    if not gorunen:
        st.info("Bu filtrelerle eşleşen kayıt bulunamadı. Yeni bir arama deneyebilirsin.")

    for k in gorunen:
        durum = k["durum"]
        durum_sinifi = {
            "İnceleme bekliyor": "status-waiting",
            "İnceleniyor": "status-active",
            "Takip gerekiyor": "status-followup",
            "Sonuçlandırıldı": "status-done",
        }.get(durum, "status-waiting")
        baslik = f"{k['takip_no']}   ·   {k['olay_turu']}   ·   {durum}"
        with st.expander(baslik, expanded=(len(gorunen) == 1)):
            st.markdown(
                f"<div class='record-banner'><div><div class='record-kicker'>BİLDİRİM KODU</div><div class='record-id'>{k['takip_no']}</div></div><div class='status-pill {durum_sinifi}'>{durum}</div></div>",
                unsafe_allow_html=True,
            )
            left, right = st.columns([1.15, 1])
            with left:
                st.markdown("#### Bildirim özeti")
                d1, d2 = st.columns(2)
                d1.markdown(f"**Olay türü**  \n{k['olay_turu']}")
                d2.markdown(f"**Ortam**  \n{k['ortam']}")
                d1.markdown(f"**Yaklaşık zaman**  \n{k['zaman_bilgisi']}")
                d2.markdown(f"**Tekrarlanma**  \n{k['tekrar_durumu']}")
                st.markdown(f"**Oluşturulma zamanı**  \n{k['olusturma_zamani']}")
                st.markdown("**Bildirim açıklaması**")
                st.write(k["aciklama"])
            with right:
                st.markdown("#### Kayıt ve yönlendirme")
                st.markdown(f"**Bildirim türü**  \n{'Anonim' if k['anonim'] else 'Kimlik bilgisi belirtilmiş'}")
                if not k["anonim"]:
                    st.markdown(f"**Ad soyad**  \n{(k['ad'] or 'Belirtilmedi')} {(k['soyad'] or '')}")
                    st.markdown(f"**Sınıf**  \n{k['sinif'] or 'Belirtilmedi'}")
                st.markdown(f"**Atanan demo birim**  \n{k['birim']}")
                st.markdown("**İfade eşleşmeleri**")
                st.write(k["eslesmeler"] or "Eşleşme yok")
                st.caption("Otomatik ifade eşleşmeleri kanıt veya karar değildir. Her zaman insan değerlendirmesi gerekir.")

            st.divider()
            st.markdown("#### İnceleme işlemi")
            with st.form(f"inceleme_{k['takip_no']}"):
                edit1, edit2 = st.columns(2)
                with edit1:
                    secili_durum = st.selectbox(
                        "İnceleme durumu", DURUMLAR,
                        index=DURUMLAR.index(k["durum"]) if k["durum"] in DURUMLAR else 0,
                    )
                with edit2:
                    secili_birim = st.selectbox(
                        "Sorumlu demo birim", BIRIMLER,
                        index=BIRIMLER.index(k["birim"]) if k["birim"] in BIRIMLER else 0,
                    )
                kaydet = st.form_submit_button("Değişiklikleri kaydet", type="primary", use_container_width=True)
            if kaydet:
                try:
                    durum_ve_birim_guncelle(k["takip_no"], secili_durum, secili_birim)
                    st.success("İnceleme bilgileri kaydedildi.")
                    st.rerun()
                except sqlite3.Error:
                    st.error("Değişiklik kaydedilemedi. Veritabanı bağlantısını kontrol et.")

            note_col, history_col = st.columns([1, 1])
            with note_col:
                st.markdown("#### İnceleme notu")
                with st.form(f"not_{k['takip_no']}"):
                    not_metni = st.text_area(
                        "Yeni not", max_chars=1000,
                        placeholder="Yalnızca kurgusal test notu yaz…",
                        key=f"not_metni_{k['takip_no']}",
                        label_visibility="collapsed",
                    )
                    not_gonder = st.form_submit_button("Notu ekle", use_container_width=True)
                if not_gonder:
                    if not not_metni.strip():
                        st.error("Boş not eklenemez.")
                    else:
                        try:
                            not_ekle(k["takip_no"], not_metni.strip())
                            st.success("Not eklendi.")
                            st.rerun()
                        except sqlite3.Error:
                            st.error("Not kaydedilemedi.")
                notlar = notlari_getir(k["takip_no"])
                if not notlar:
                    st.caption("Henüz inceleme notu yok.")
                else:
                    for n in notlar:
                        st.markdown(f"**{n['zaman']}**")
                        st.write(n["not_metni"])
                        st.markdown("---")
            with history_col:
                st.markdown("#### İşlem geçmişi")
                gecmis = gecmisi_getir(k["takip_no"])
                if not gecmis:
                    st.caption("Henüz işlem geçmişi yok.")
                else:
                    for g in gecmis:
                        st.markdown(f"**{g['islem']}**")
                        st.caption(g["zaman"])
                        if g["ayrinti"]:
                            st.write(g["ayrinti"])


# =========================================================
# 9. İSTATİSTİKLER
# Yalnızca toplulaştırılmış demo verisi gösterilir.
# =========================================================

elif sayfa == "İstatistikler":
    st.title("📊 Demo istatistikleri")
    st.caption("Grafikler yalnızca bu prototipte oluşturulan test kayıtlarını özetler.")
    kayitlar = kayitlari_getir()

    if not kayitlar:
        st.info("Henüz kayıt yok. İstatistikleri görmek için Yeni bildirim bölümünde kurgusal test kayıtları oluştur.")
    else:
        toplam = len(kayitlar)
        bekleyen = sum(k["durum"] == "İnceleme bekliyor" for k in kayitlar)
        takip_sayisi = sum(k["durum"] == "Takip gerekiyor" for k in kayitlar)
        sonuclanan = sum(k["durum"] == "Sonuçlandırıldı" for k in kayitlar)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Toplam demo kaydı", toplam)
        m2.metric("İnceleme bekliyor", bekleyen)
        m3.metric("Takip gerekiyor", takip_sayisi)
        m4.metric("Sonuçlandırıldı", sonuclanan)

        st.subheader("Durum dağılımı")
        durum_sayilari = {d: sum(k["durum"] == d for k in kayitlar) for d in DURUMLAR}
        st.bar_chart(durum_sayilari, horizontal=True)

        st.subheader("Olay türü dağılımı")
        tur_sayilari = {t: sum(k["olay_turu"] == t for k in kayitlar) for t in OLAY_TURLERI}
        st.bar_chart(tur_sayilari, horizontal=True)

        st.subheader("Anonim bildirim oranı")
        anonim_sayisi = sum(bool(k["anonim"]) for k in kayitlar)
        st.progress(anonim_sayisi / toplam, text=f"{anonim_sayisi} / {toplam} kayıt anonim demo olarak oluşturulmuş")

        st.info("Bu sayılar gerçek okul geneli hakkında sonuç çıkarmaz. Küçük, kurgusal ve seçilmiş demo kayıtlarından oluşur; kişi veya sınıf sıralaması yapılmaz.")


# =========================================================
# 10. ARAŞTIRMA VE TEST
# =========================================================

elif sayfa == "Araştırma ve test":
    st.title("🧪 Araştırma ve test planı")
    st.write("Bu bölüm, prototipin işlevsel ve kullanılabilirlik açısından sistematik değerlendirilmesine yardımcı olur.")

    st.subheader("Önerilen test senaryoları")
    testler = [
        ("T01", "Anonim bildirim", "Anonim seçenek açıkken ad/soyad/sınıf kaydedilmemeli."),
        ("T02", "Sınıf seçenekleri", "9/A, 9/B, 10/A, 10/B, 11/A, 11/B, 12/A, 12/B seçenekleri görünmeli."),
        ("T03", "Takip kodu", "Her yeni kayıt benzersiz bir demo takip kodu üretmeli."),
        ("T04", "Yetkisiz erişim", "Yönetici girişi olmadan inceleme kayıtları gösterilmemeli."),
        ("T05", "Durum güncelleme", "Durum ve demo birim değişikliği kaydedilmeli ve geçmişe eklenmeli."),
        ("T06", "Not geçmişi", "İnceleme notu kaydedilmeli ve ilgili kayıtta görünmeli."),
        ("T07", "Boş form", "Açıklama veya gerekli onay yoksa kayıt oluşturulmamalı."),
        ("T08", "Temiz başlangıç", "Yeni kurulumda otomatik örnek kayıt olmamalı; kayıtlar yeniden başlatmada sebepsiz silinmemeli."),
        ("T09", "İstatistikler", "Grafik toplamları kayıt sayılarıyla uyumlu olmalı."),
        ("T10", "Güvenli metin", "Arayüz gerçek kişisel veri kullanılmaması gerektiğini açıkça belirtmeli."),
    ]
    for kod, baslik, aciklama in testler:
        with st.expander(f"{kod} · {baslik}"):
            st.write(aciklama)
            st.checkbox("Bu senaryoyu test ettim", key=f"test_{kod}")

    tamamlanan = sum(bool(st.session_state.get(f"test_{kod}", False)) for kod, _, _ in testler)
    st.progress(tamamlanan / len(testler), text=f"İşaretlenen test: {tamamlanan}/{len(testler)}")

    st.subheader("Bilimsel değerlendirme çerçevesi")
    st.markdown("""
    1. **Amaç:** Formun anlaşılabilirliğini, temel işlevlerin doğruluğunu ve güvenli kullanım uyarılarının görünürlüğünü değerlendirmek.
    2. **Yöntem:** Önceden belirlenmiş senaryoları aynı sırayla uygulamak; her test için başarılı/başarısız sonucu ve gözlemi kaydetmek.
    3. **Ölçütler:** Başarı oranı, tamamlanma süresi, bulunan hata sayısı ve kullanıcıların yönergeleri doğru anlayıp anlamadığı.
    4. **Sınırlılıklar:** Demo kayıtları gerçek zorbalık olaylarını temsil etmez. Küçük bir test, etkinlik veya güvenlik konusunda bilimsel kanıt sağlamaz.
    5. **Etik:** Gerçek öğrencilerden veri toplanacaksa önceden okul/veli onayı, gönüllülük, veri minimizasyonu ve güvenli saklama planı gerekir. Bu prototipte gerçek öğrenci verisi kullanmayın.
    """)
    st.warning("Bu sayfadaki işaretler yalnızca mevcut oturumda tutulan kontrol listesidir; resmi test raporu veya bilimsel doğrulama yerine geçmez.")


# =========================================================
# 11. GÜVENLİ KULLANIM
# =========================================================

elif sayfa == "Güvenli kullanım":
    st.title("ℹ️ Güvenli kullanım")

    st.subheader("Bu demo neler yapar?")
    st.markdown(
        """
        - Kurgusal bildirim oluşturur.
        - Anonim demo bildirimi seçeneği sunar.
        - Yönetici girişinden sonra kayıtları listeler.
        - Durum ve sorumlu demo birimini günceller.
        - İnceleme notlarını ve işlem geçmişini saklar.
        - İfade eşleşmelerini yalnızca yardımcı sinyal olarak gösterir.
        """
    )

    st.subheader("Sınırlar")
    st.markdown(
        """
        - Gerçek bir okul veya rehberlik servisine bağlı değildir.
        - Acil yardım veya resmi bildirim hizmeti değildir.
        - Zorbalık hakkında otomatik kesin karar vermez.
        - Demo oturumu, tek başına üretim düzeyinde kimlik doğrulama değildir.
        - Yerel SQLite dosyasının bulut ortamında kalıcı olacağı garanti edilmez.
        """
    )

    st.warning(
        "Gerçek öğrenci verileri kullanılmadan önce okul onayı, "
        "veri koruma planı, güçlü erişim kontrolü, güvenli yedekleme "
        "ve saklama/silme politikaları gerekir."
    )


# =========================================================
# 10. ALT BİLGİ
# =========================================================

st.divider()
st.caption(
    "🛡️ Güvenli Okul 3.1 · Araştırma ve demo prototipi · "
    "Gerçek okul sistemi değildir."
)
