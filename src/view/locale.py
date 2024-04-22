import os
from babel.support import Translations
from enum import Enum
from dataclasses import dataclass
import streamlit as st
from logging import getLogger

logger = getLogger(__name__)


class Lang(Enum):
    pl: str = "pl"
    en: str = "en"


@dataclass
class Locale:
    lang: Lang
    code: str
    search_term: str


pl = Locale(lang=Lang.pl.value, code="pl_PL", search_term="pl")
en = Locale(lang=Lang.en.value, code="en_US", search_term="en-US")
VALID_LOCALES = [pl, en]


def set_locale(headers: dict, default_locale: Locale = pl):
    locale = default_locale
    if "Accept-Language" in headers:
        accept_header = headers.get("Accept-Language", None)
        language = accept_header.split(",")[0].split(";")[0]

        for valid_locale in VALID_LOCALES:
            # compare with language search term case insensitive
            if valid_locale.search_term.lower() in language.lower():
                locale = valid_locale
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
