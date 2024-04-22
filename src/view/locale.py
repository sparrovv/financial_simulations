import os
from babel.support import Translations
from enum import Enum
from dataclasses import dataclass


class Lang(Enum):
    pl: str = "pl"
    en: str = "en"


@dataclass
class Locale:
    lang: Lang
    code: str


VALID_LOCALES = [
    Locale(lang=Lang.pl.value, code="pl_PL"),
    Locale(lang=Lang.en.value, code="en_US"),
]
# CURRENT_LOCALE = Locale(lang=Lang.en.value, code="en_US")
CURRENT_LOCALE = Locale(lang=Lang.pl.value, code="pl_PL")


def set_locale(headers):
    global CURRENT_LOCALE
    if "Accept-Language" in headers:
        h = headers.get("Accept-Language", None)
        # split the languages
        langs = h.split(",")

        for lang in langs:
            if lang in map(lambda x: x.lang, VALID_LOCALES):
                CURRENT_LOCALE = VALID_LOCALES[lang]
                break

    return CURRENT_LOCALE


def load_translations(locale):
    translations_directory = os.path.join(os.getcwd(), "locale")
    return Translations.load(translations_directory, [locale])


def _(text):
    translations = load_translations(CURRENT_LOCALE.code)
    return translations.gettext(text)
