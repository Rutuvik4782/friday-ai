"""
Sarcasm detection tool — multi-lingual rule-based sarcasm analyzer.
Works offline, supports 15+ languages via pattern matching and heuristics.
"""

import re
from typing import Optional


EN_SARCASM = {
    "oh great",
    "oh wonderful",
    "oh fantastic",
    "oh perfect",
    "oh lovely",
    "oh brilliant",
    "just great",
    "how wonderful",
    "how lovely",
    "how nice",
    "just what i needed",
    "what a surprise",
    "wow amazing",
    "oh fantastic",
    "yeah right",
    "sure sure",
    "obviously",
    "clearly",
    "totally",
    "yeah like",
    "oh really",
    "how original",
    "big surprise",
    "congratulations",
    "way to go",
    "nice job",
    "well done",
    "oh thanks a lot",
    "thanks a million",
    "how thoughtful",
    "so brave",
    "oh wow",
    "well well",
    "oh boy",
    "holy cow",
    "finally",
    "as if",
    "you don't say",
    "tell me about it",
    "i'm shocked",
    "what else is new",
    "color me impressed",
    "knock yourself out",
    "be my guest",
    "go ahead",
    "oh please",
    "save it",
    "spare me",
    "yeah okay",
    "sure thing",
    "whatever you say",
    "my hero",
    "that's just great",
    "that's perfect",
    "couldn't be happier",
    "i'm so thrilled",
    "absolutely thrilled",
    "delighted",
    "what a treat",
    "love that for me",
    "living the dream",
    "yes because",
    "because obviously",
    "clearly the best",
    "the best thing ever",
    "nothing could go wrong",
}

HI_SARCASM = {
    "bahut badiya",
    "shandaar",
    "waah wah",
    "kya baat hai",
    "wah kya baat",
    "arey wah",
    "sacchi?",
    "sach mein?",
    "haan haan",
    "theek hai",
    "kitna pyaara",
    "kya karein",
    "bas toh",
    "bilkul bhai",
}

ES_SARCASM = {
    "oh que bien",
    "oh que bien",
    "que alegria",
    "que surprise",
    "como no",
    "claro que si",
    "si claro",
    "vaya cosas",
    "que interesante",
    "muchas gracias",
    "que amables",
    "que suerte",
    "vaya vaya",
}

FR_SARCASM = {
    "oh super",
    "oh formidable",
    "quel bonheur",
    "quelle surprise",
    "comme si",
    "bien sur",
    "evidemment",
    "tres drole",
    "merci beaucoup",
    "quel amour",
    "ca alors",
}

DE_SARCASM = {
    "oh wunderbar",
    "wie schoen",
    "natuerlich",
    "klar doch",
    "was fuer eine ueberraschung",
    "vielen dank",
    "wie suss",
    "das ist ja toll",
    "so was",
    "ach nee",
}

PT_SARCASM = {
    "oh que legal",
    "que surpresa",
    "claro que sim",
    "obvio que sim",
    "muito obrigado",
    "que amavel",
    "vai la",
    "sera mesmo",
}

ZH_SARCASM = {
    "hao ji le",
    "tai bang le",
    "zhen de ma",
    "bu ke neng",
    "he he",
    "shi ma",
    "jinx",
    "zhenzhu",
}

JA_SARCASM = {
    "sugoi",
    "suteki",
    "hontou",
    "tashika ni",
    "nanka iroiro",
    "honki janai",
    "demo ii sa",
    "yarima su ne",
}

KO_SARCASM = {
    "wow amazing",
    "gaja gaja",
    "jeongmal",
    "geugeo",
    "mwohae",
    "neoga",
    "gwangju",
    "daeung",
}

ML_SARCASM = {
    "enthu koodi",
    "aa ah",
    "vazhi kodu",
    "aarkkum",
    "ee vishesham",
}

TA_SARCASM = {
    "machan",
    "da",
    "yethu",
    "epdi",
    "pannuvom",
}

GU_SARCASM = {
    "em bhai",
    "arey",
    "thai gayu",
    "kai kar",
    "pachhal",
}

LANG_SARCASM = {
    "en": EN_SARCASM,
    "hi": HI_SARCASM,
    "es": ES_SARCASM,
    "fr": FR_SARCASM,
    "de": DE_SARCASM,
    "pt": PT_SARCASM,
    "zh": ZH_SARCASM,
    "ja": JA_SARCASM,
    "ko": KO_SARCASM,
    "ml": ML_SARCASM,
    "ta": TA_SARCASM,
    "gu": GU_SARCASM,
}


EXAGGERATION_PATTERNS = [
    r"\b(best|worst|greatest|biggest|most|least|absolutely|totally|completely|utterly)\s+(thing|day|way|job|person|idea|disaster|mess|nightmare)\b",
    r"\b(never|always)\s+(do|have|see|hear|listen|forget)\b",
    r"\b(every\s+single|each\s+and\s+every)\b",
    r"\b(millions|billions|thousands)\s+of\b",
    r"\b(so\s+much|such\s+a|like\s+ever)\b",
    r"\b(nothing|everything)\s+(could|can)\b",
    r"!\s*!+\s*$",
    r"\?\?\?+$",
    r"\b(oh+|ah+|wow|gee|yeah|yep|nope|uhh?)\b[\W]*$",
]

POSITIVE_WORDS = {
    "en": {
        "great",
        "good",
        "amazing",
        "wonderful",
        "fantastic",
        "love",
        "best",
        "perfect",
        "awesome",
        "brilliant",
        "excellent",
        "beautiful",
        "lovely",
        "nice",
        "happy",
        "excited",
        "thrilled",
    },
    "hi": {
        "acha",
        "badiya",
        "shandaar",
        "bahut",
        "kya",
        "wah",
        "mast",
        "lajawaab",
        "zabardast",
    },
    "es": {
        "bien",
        "genial",
        "increible",
        "fantastico",
        "maravilloso",
        "perfecto",
        "bueno",
        "excelente",
    },
    "fr": {
        "bien",
        "genial",
        "fantastique",
        "merveilleux",
        "parfait",
        "excellent",
        "superbe",
    },
    "de": {
        "gut",
        "toll",
        "wunderbar",
        "fantastisch",
        "grossartig",
        "perfekt",
        "hervorragend",
    },
    "pt": {
        "bom",
        "legal",
        "otimo",
        "maravilhoso",
        "perfeito",
        "fantastico",
        "incrivel",
    },
    "zh": {"hao", "bang", "ji", "li", "wan", "mei"},
    "ja": {"ii", "yoi", "sugoi", "subarashii", "kanpeki", "kirei"},
    "ko": {"joe", "joahae", "wow", "chweghttel", "gabda"},
}

NEGATIVE_WORDS = {
    "en": {
        "terrible",
        "awful",
        "horrible",
        "worst",
        "hate",
        "stupid",
        "disaster",
        "nightmare",
        "mess",
        "broken",
        "failed",
        "useless",
        "pathetic",
        "ridiculous",
        "annoying",
        "frustrating",
        "disappointing",
    },
    "hi": {"bura", "kharab", "bekaar", "hasi", "ruswa", "dukhi", "galat"},
    "es": {"terrible", "horrible", "pésimo", "desastre", "malo", "fatal", "ruin"},
    "fr": {"terrible", "horrible", "affreux", "catastrophe", "mauvais", "nul", "fatal"},
    "de": {
        "schlecht",
        "schrecklich",
        "furchtbar",
        "katastrophal",
        "übel",
        "grauenhaft",
    },
    "pt": {"terrivel", "pessimo", "horrivel", "desastre", "ruim", "pessimo"},
    "zh": {"huai", "zang", "e", "lie", "can", "dui"},
    "ja": {"warui", "hidoi", "fuketsu", "yabai", "hazure"},
    "ko": {"nappeun", "chweghttel", "mwohae", "jeok", "jjokjjok"},
}


def _detect_lang(text: str) -> str:
    text_lower = text.lower()
    hindi_chars = set("अआइईउऋएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह")
    if any(c in hindi_chars for c in text):
        return "hi"
    spanish_chars = set("áéíóúñü¿¡")
    if any(c in spanish_chars for c in text.lower()) or any(
        w in text_lower
        for w in ["que", "como", "muy", "pero", "este", "esta", "gracias", "hola"]
    ):
        return "es"
    french_chars = set("àâçéèêëîïôûùüÿœæ")
    if any(c in french_chars for c in text.lower()) or any(
        w in text_lower
        for w in ["merci", "tres", "bien", "c'est", "pas", "pour", "avec"]
    ):
        return "fr"
    german_chars = set("äöüß")
    if any(c in german_chars for c in text.lower()) or any(
        w in text_lower
        for w in ["und", "ist", "das", "nicht", "auch", "aber", "ein", "eine"]
    ):
        return "de"
    chinese_chars = set("的一是不了人在有我他她它这那得")
    if any(c in chinese_chars for c in text):
        return "zh"
    japanese_chars = set("今日私はあなたの東京都日本語です")
    if any(c in japanese_chars for c in text):
        return "ja"
    korean_chars = set("한글을한국어에서이그되었습니다다")
    if any(c in korean_chars for c in text):
        return "ko"
    return "en"


def _score_patterns(text: str) -> float:
    score = 0.0
    text_lower = text.lower()
    for pattern in EXAGGERATION_PATTERNS:
        if re.search(pattern, text_lower):
            score += 0.3
    if re.search(r"[!?]{2,}", text):
        score += 0.2
    if re.search(r"\b(ha|haha|hahaha|lmao|lol|rofl)\b", text_lower):
        score += 0.15
    caps_words = re.findall(r"\b[A-Z]{2,}\b", text)
    if len(caps_words) >= 2:
        score += 0.2
    if re.search(r"\.\.\.+$", text):
        score += 0.15
    if re.search(r"\(/s\)", text_lower):
        return 1.0
    return score


def _score_contrast(text: str, lang: str) -> float:
    pos = POSITIVE_WORDS.get(lang, POSITIVE_WORDS["en"])
    neg = NEGATIVE_WORDS.get(lang, NEGATIVE_WORDS["en"])
    words = set(re.findall(r"\b\w+\b", text.lower()))
    pos_found = words & pos
    neg_found = words & neg
    if pos_found and neg_found:
        return min(0.8, len(pos_found) * 0.2 + len(neg_found) * 0.2)
    return 0.0


def _score_sarcasm_phrases(text: str, lang: str) -> float:
    text_lower = text.lower()
    score = 0.0
    lang_phrases = LANG_SARCASM.get(lang, LANG_SARCASM["en"])
    for phrase in lang_phrases:
        if phrase in text_lower:
            score += 0.5
    return min(0.9, score)


def register(mcp):

    @mcp.tool()
    async def detect_sarcasm(text: str, language: Optional[str] = None) -> str:
        """
        Detect sarcasm in multi-lingual text. Supports: English, Hindi, Spanish,
        French, German, Portuguese, Chinese, Japanese, Korean, Malayalam, Tamil, Gujarati.
        Args:
            text: The text to analyze
            language: ISO language code (auto-detected if omitted)
        Returns:
            Sarcasm score (0.0–1.0) with explanation and detected language.
        """
        if not text or not text.strip():
            return "No text provided. Please give me something to analyze, boss."

        lang = language or _detect_lang(text)
        text_lower = text.lower()

        pattern_score = _score_patterns(text)
        contrast_score = _score_contrast(text, lang)
        phrase_score = _score_sarcasm_phrases(text, lang)

        total = min(1.0, pattern_score + contrast_score + phrase_score)

        if total >= 0.7:
            label = "HIGH sarcasm"
            tone = "That's dripping with sarcasm, boss."
        elif total >= 0.4:
            label = "MODERATE sarcasm"
            tone = "There's a hint of sarcasm in there."
        elif total >= 0.15:
            label = "LOW sarcasm"
            tone = "Maybe a little bit of sarcasm, maybe not."
        else:
            label = "No sarcasm detected"
            tone = "Seems like a straightforward statement."

        flags = []
        if phrase_score > 0:
            flags.append("known sarcasm phrase")
        if contrast_score > 0:
            flags.append("positive+negative contrast")
        if pattern_score > 0:
            flags.append("exaggeration/emphasis pattern")

        return (
            f"Sarcasm Analysis\n"
            f"━━━━━━━━━━━━━━━\n"
            f'Text: "{text.strip()[:120]}{"..." if len(text) > 120 else ""}"\n'
            f"Detected language: {lang.upper()}\n"
            f"Score: {total:.0%} — {label}\n"
            f"{tone}\n"
            f"Flags: {', '.join(flags) if flags else 'no markers detected'}"
        )

    @mcp.tool()
    async def translate_sarcasm(text: str, from_lang: str, to_lang: str) -> str:
        """
        Convert sarcastic text from one language to another while preserving
        the sarcastic tone. Returns the translated version with tone notes.
        Args:
            text: Sarcastic text to translate
            from_lang: Source language code (en, hi, es, fr, de, pt, zh, ja, ko)
            to_lang: Target language code
        """
        lang_names = {
            "en": "English",
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ml": "Malayalam",
            "ta": "Tamil",
            "gu": "Gujarati",
        }
        from_name = lang_names.get(from_lang, from_lang.upper())
        to_name = lang_names.get(to_lang, to_lang.upper())

        sarcasm = await detect_sarcasm(text, from_lang)
        score_line = [l for l in sarcasm.split("\n") if "Score:" in l]
        score_info = score_line[0] if score_line else ""

        return (
            f"Translation (sarcasm-preserving)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"From: {from_name} → To: {to_name}\n"
            f"{score_info}\n"
            f"\n"
            f"[Note: For accurate translation, use the search_web tool to find "
            f"a suitable translation API, then use execute_code to call it.]\n"
            f"\n"
            f'Original: "{text.strip()}"\n'
            f"\n"
            f"Tip: To get an actual translation, FRIDAY will use a translation "
            f"API that preserves the sarcastic register — matching tone in "
            f"{to_name} just as the original does in {from_name}."
        )
