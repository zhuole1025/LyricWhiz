import re
import numpy as np
import unicodedata

from num2words import num2words
import jiwer

def remove_emoji(text):
    # Emoji ranges in Unicode
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def get_song_list(songlist_file):
    songs = []
    with open(songlist_file, 'r') as f_in:
        for line in f_in.readlines():
            songs.append(line.strip())
    return songs

def compute_wer(hyp="",ref=""):
    # mat is for storing prev edit distance
    mat = np.zeros((len(ref)+1, len(hyp)+1), dtype=np.int32)
    mat[:, 0] = np.arange(0, len(ref)+1)
    mat[0, :] = np.arange(0, len(hyp)+1)

    for i in range(1, mat.shape[0]):
        for j in range(1, mat.shape[1]):
            if ref[i-1] == hyp[j-1]:
                mat[i, j] = mat[i-1, j-1]
            else:
                sub_ = mat[i-1, j-1] + 1
                del_ = mat[i, j-1] + 1
                ins_ = mat[i-1, j] + 1
                mat[i, j] = min(sub_, del_, ins_)               

    return mat[-1, -1] / len(ref)

def convert_digits_to_words(words):
    # Loop over the words and convert any digits to words
    for i, word in enumerate(words):
        if word.isdigit():
            words[i] = num2words(int(word))
    return words

def normalize_text(text, language):
    # 将文本转换为小写形式
    text = text.lower()

    # 使用NFKC（兼容组合分解）进行Unicode规范化
    text = unicodedata.normalize("NFKC", text)

    # 根据语言移除不需要的字符
    if language in ["de", "es", "it", "fr"]:
        # 只保留字母（不包括重音符号）、数字和空格
        text = re.sub(r"[^a-z0-9\s]+", "", text)
    elif language == "ru":
        # 只保留西里尔字母、数字和空格
        text = re.sub(r"[^а-яё0-9\s]+", "", text)
    else:
        raise ValueError("Unsupported language")

    # 去除多余的空格
    text = re.sub(r"\s+", " ", text).strip()

    return text


transformation = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.SentencesToListOfWords(word_delimiter=" "),
    jiwer.RemovePunctuation(),
    jiwer.RemoveEmptyStrings(),
])

LANGUAGES = {
    "en": "english",
    "zh": "chinese",
    "de": "german",
    "es": "spanish",
    "ru": "russian",
    "ko": "korean",
    "fr": "french",
    "ja": "japanese",
    "pt": "portuguese",
    "tr": "turkish",
    "pl": "polish",
    "ca": "catalan",
    "nl": "dutch",
    "ar": "arabic",
    "sv": "swedish",
    "it": "italian",
    "id": "indonesian",
    "hi": "hindi",
    "fi": "finnish",
    "vi": "vietnamese",
    "he": "hebrew",
    "uk": "ukrainian",
    "el": "greek",
    "ms": "malay",
    "cs": "czech",
    "ro": "romanian",
    "da": "danish",
    "hu": "hungarian",
    "ta": "tamil",
    "no": "norwegian",
    "th": "thai",
    "ur": "urdu",
    "hr": "croatian",
    "bg": "bulgarian",
    "lt": "lithuanian",
    "la": "latin",
    "mi": "maori",
    "ml": "malayalam",
    "cy": "welsh",
    "sk": "slovak",
    "te": "telugu",
    "fa": "persian",
    "lv": "latvian",
    "bn": "bengali",
    "sr": "serbian",
    "az": "azerbaijani",
    "sl": "slovenian",
    "kn": "kannada",
    "et": "estonian",
    "mk": "macedonian",
    "br": "breton",
    "eu": "basque",
    "is": "icelandic",
    "hy": "armenian",
    "ne": "nepali",
    "mn": "mongolian",
    "bs": "bosnian",
    "kk": "kazakh",
    "sq": "albanian",
    "sw": "swahili",
    "gl": "galician",
    "mr": "marathi",
    "pa": "punjabi",
    "si": "sinhala",
    "km": "khmer",
    "sn": "shona",
    "yo": "yoruba",
    "so": "somali",
    "af": "afrikaans",
    "oc": "occitan",
    "ka": "georgian",
    "be": "belarusian",
    "tg": "tajik",
    "sd": "sindhi",
    "gu": "gujarati",
    "am": "amharic",
    "yi": "yiddish",
    "lo": "lao",
    "uz": "uzbek",
    "fo": "faroese",
    "ht": "haitian creole",
    "ps": "pashto",
    "tk": "turkmen",
    "nn": "nynorsk",
    "mt": "maltese",
    "sa": "sanskrit",
    "lb": "luxembourgish",
    "my": "myanmar",
    "bo": "tibetan",
    "tl": "tagalog",
    "mg": "malagasy",
    "as": "assamese",
    "tt": "tatar",
    "haw": "hawaiian",
    "ln": "lingala",
    "ha": "hausa",
    "ba": "bashkir",
    "jw": "javanese",
    "su": "sundanese",
}