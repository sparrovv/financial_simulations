import os
from babel.support import Translations
from enum import Enum
from dataclasses import dataclass
import streamlit as st


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


def set_locale(
    headers: dict, default_locale: Locale = Locale(lang=Lang.pl.value, code="pl_PL")
):
    locale = default_locale
    if "Accept-Language" in headers:
        h = headers.get("Accept-Language", None)
        # split the languages
        langs = h.split(",")

        for lang in langs:
            if lang in map(lambda x: x.lang, VALID_LOCALES):
                locale = VALID_LOCALES[lang]
                break

    st.session_state.locale = locale
    return locale


def load_translations(locale):
    translations_directory = os.path.join(os.getcwd(), "locale")
    return Translations.load(translations_directory, [locale])


def _(text):
    code = st.session_state.locale.code
    translations = load_translations(code)
    return translations.gettext(text)
