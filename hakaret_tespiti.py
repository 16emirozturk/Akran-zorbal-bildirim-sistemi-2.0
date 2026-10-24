"""Basit ifade eşleşmesi yardımcısı; kesin karar veya sınıflandırma değildir."""
import re
import unicodedata

# Demo amaçlı, sınırlı örnek liste. Gerçek kişileri veya olayları otomatik
# değerlendirmek için kullanılmamalıdır.
SUPHELI_IFADELER = (
    "aptal",
    "salak",
    "gerizekali",
    "defol",
    "seni dov",
    "seni döverim",
    "tehdit ediyorum",
)


def _norm(metin: str) -> str:
    metin = unicodedata.normalize("NFKC", metin).casefold()
    return re.sub(r"\s+", " ", metin).strip()


def supheli_ifadeleri_bul(metin: str) -> list[str]:
    """Eşleşen demo ifadelerini döndürür; bağlamı ve niyeti anlayamaz."""
    normalized = _norm(metin)
    bulunan = []
    for ifade in SUPHELI_IFADELER:
        needle = _norm(ifade)
        if needle and needle in normalized:
            bulunan.append(ifade)
    return bulunan
