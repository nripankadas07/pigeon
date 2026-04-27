"""Built-in plural-form table for common locales.

Sourced from the Translate-Toolkit / gettext canonical strings used by
GNU gettext. Each value parses with :func:`pigeon.parse`.
"""

from __future__ import annotations

# Plural-Forms strings keyed by ISO 639 language code (and a few region forms
# where they differ from the language default).
PLURAL_FORMS: dict[str, str] = {
    # Languages with a single plural form (no plural distinction).
    "ja": "nplurals=1; plural=0;",
    "ko": "nplurals=1; plural=0;",
    "vi": "nplurals=1; plural=0;",
    "th": "nplurals=1; plural=0;",
    "zh": "nplurals=1; plural=0;",
    "id": "nplurals=1; plural=0;",
    "ms": "nplurals=1; plural=0;",
    "tr": "nplurals=2; plural=(n != 1);",
    "fa": "nplurals=2; plural=(n > 1);",
    "en": "nplurals=2; plural=(n != 1);",
    "de": "nplurals=2; plural=(n != 1);",
    "nl": "nplurals=2; plural=(n != 1);",
    "sv": "nplurals=2; plural=(n != 1);",
    "da": "nplurals=2; plural=(n != 1);",
    "no": "nplurals=2; plural=(n != 1);",
    "nb": "nplurals=2; plural=(n != 1);",
    "nn": "nplurals=2; plural=(n != 1);",
    "fi": "nplurals=2; plural=(n != 1);",
    "et": "nplurals=2; plural=(n != 1);",
    "el": "nplurals=2; plural=(n != 1);",
    "he": "nplurals=2; plural=(n != 1);",
    "es": "nplurals=2; plural=(n != 1);",
    "it": "nplurals=2; plural=(n != 1);",
    "pt": "nplurals=2; plural=(n != 1);",
    "bg": "nplurals=2; plural=(n != 1);",
    "ca": "nplurals=2; plural=(n != 1);",
    "eu": "nplurals=2; plural=(n != 1);",
    "hu": "nplurals=2; plural=(n != 1);",
    "fr": "nplurals=2; plural=(n > 1);",
    "pt_BR": "nplurals=2; plural=(n > 1);",
    "ru": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : "
        "n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "uk": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : "
        "n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "be": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : "
        "n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "hr": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : "
        "n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "sr": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : "
        "n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "pl": (
        "nplurals=3; plural=(n==1 ? 0 : "
        "n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "cs": "nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;",
    "sk": "nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;",
    "lt": (
        "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : "
        "n%10>=2 && (n%100<10 || n%100>=20) ? 1 : 2);"
    ),
    "lv": "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n != 0 ? 1 : 2);",
    "ro": "nplurals=3; plural=(n==1 ? 0 : (n==0 || (n%100>0 && n%100<20)) ? 1 : 2);",
    "sl": (
        "nplurals=4; plural=(n%100==1 ? 0 : n%100==2 ? 1 : "
        "n%100==3 || n%100==4 ? 2 : 3);"
    ),
    "ga": (
        "nplurals=5; plural=(n==1 ? 0 : n==2 ? 1 : "
        "(n>=3 && n<=6) ? 2 : (n>=7 && n<=10) ? 3 : 4);"
    ),
    "ar": (
        "nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : "
        "(n%100>=3 && n%100<=10) ? 3 : (n%100>=11 && n%100<=99) ? 4 : 5);"
    ),
}


def normalise_locale(locale: str) -> str:
    if not isinstance(locale, str):
        raise TypeError(f"locale must be a string, got {type(locale).__name__}")
    cleaned = locale.strip()
    if not cleaned:
        raise ValueError("locale must not be empty")
    cleaned = cleaned.split(".", 1)[0]
    cleaned = cleaned.split("@", 1)[0]
    cleaned = cleaned.replace("-", "_")
    return cleaned


def lookup(locale: str) -> str | None:
    cleaned = normalise_locale(locale)
    if cleaned in PLURAL_FORMS:
        return PLURAL_FORMS[cleaned]
    if "_" in cleaned:
        language = cleaned.split("_", 1)[0]
        return PLURAL_FORMS.get(language)
    return None
