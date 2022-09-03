""" from https://github.com/keithito/tacotron """

'''
Cleaners are transformations that run over the input text at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English text
  2. "transliteration_cleaners" for non-English text that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
from phonemizer import phonemize
import pyopenjtalk
from pypinyin import pinyin, Style
import eng_to_ipa as ipa

'''Chinese cleaners'''

_tones = ["1", "2", "3", "4"]

_revision_ch = {
    "ang": "aŋ",
    "eng": "əŋ",
    "ing": "iŋ",
    "ong": "ɔŋ",

    "ai": "aɪ",
    "ei": "ɛɪ",
    "ui": "uɛɪ",
    "iu": "iɔu",
    "ie": "iɛ",
    "ue": "üɛ",
    "an": "æn",
    "en": "ən",
    # ü前有j,q,x或y时会被去掉两点
    "ju": "jü",
    "jue": "jüɛ",
    "jun": "jün",
    "juan": "jüæn",
    "qu": "qü",
    "que": "qüɛ",
    "qun": "qün",
    "quan": "qüæn",
    "xu": "xü",
    "xue": "xüɛ",
    "xun": "xün",
    "xuan": "xüæn",
    "yu": "yü",
    "yue": "yüɛ",
    "yun": "yün",
    "yuan": "yüæn",

    "un": "uən",
    "zhi": "dʒI",
    "chi": "tʃI",
    "shi": "ʃI",
    "zh": "dʒ",
    "ch": "tʃ",
    "sh": "ʃ",
    "zi": "zI",
    "ci": "tsI",
    "si": "sI",
    "c": "ts",
    "v": "ü",
    "e": "ə",
    "o": "ɔ"
}

def chinese_cleaner_pipe(text):
  phones = []
  for phone in pinyin(text, style=Style.TONE3):
    phone = phone[0]
    for item in _revision_ch.items():
      old = item[0]
      new = item[1]
      phone = phone.replace(old, new)
    phones.append(phone)
    text = " ".join(phones)

  return text

'''Japanese cleaners'''

# Regular expression matching Japanese without punctuation marks:
_japanese_characters = re.compile(
    r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# Regular expression matching non-Japanese characters or punctuation marks:
_japanese_marks = re.compile(
    r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

_japanese_vowels = ['a', 'i', 'u', 'e', 'o']

_hatsuon = ['N']

_revision_jp = {
    "u": "ʊ",
    "o": "ɔ",
    "shi": "xi",
    "r": "l",
    "sha": "ʃya",
    "shu": "ʃyu",
    "sho": "ʃyɔ",
    "cha": "tʃya",
    "chu": "tʃyu",
    "cho": "tʃyɔ",
    "ch": "q",
    'N': 'ŋ',
}

def japanese_cleaner_1(text):
    '''Pipeline for notating accent in Japanese text.'''
    '''Reference https://r9y9.github.io/ttslearn/latest/notebooks/ch10_Recipe-Tacotron.html'''
    sentences = re.split(_japanese_marks, text)
    marks = re.findall(_japanese_marks, text)
    text = ''
    for i, sentence in enumerate(sentences):
        if re.match(_japanese_characters, sentence):
            if text != '':
                text += '#'
            labels = pyopenjtalk.extract_fullcontext(sentence)
            for n, label in enumerate(labels):
                phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
                if phoneme not in ['sil', 'pau']:
                    text += phoneme.replace('cl', 'Q ')
                else:
                    continue
                n_moras = int(re.search(r'/F:(\d+)_', label).group(1))
                a1 = int(re.search(r"/A:(\-?[0-9]+)\+", label).group(1))
                a2 = int(re.search(r"\+(\d+)\+", label).group(1))
                a3 = int(re.search(r"\+(\d+)/", label).group(1))
                if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil', 'pau']:
                    a2_next = -1
                else:
                    a2_next = int(re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
                # Accent phrase boundary
                if a3 == 1 and a2_next == 1:
                    text += '#'
                # Falling
                elif a1 == 0 and a2_next == a2 + 1 and a2 != n_moras:
                    text += '↓'
                # Rising
                elif a2 == 1 and a2_next == 2:
                    text += '↑'
        if i < len(marks):
            text += unidecode(marks[i])
    if re.match('[A-Za-z]', text[-1]):
        text += '.'

    text = text.replace('......', ', ')
    return text


def japanese_cleaner_2(text):
    new_text = ''
    for i, char in enumerate(text):
        char = char.replace('A', 'a').replace('I', 'i').replace('U', 'u').replace('E', 'e').replace('O', 'o')
        new_text += char
        if (i + 1 < length) and char in _japanese_vowels:
            new_text += ' '
        elif char == 'N':
            new_text += ' '
        else:
            continue
    return new_text


def add_tone(text, low=True):
    new_text = []
    length = len(text)
    for i, char in enumerate(text):
        new_text.append(char)
        if char in (_japanese_vowels + _hatsuon):
            if low:
                new_text.append('1')
            else:
                new_text.append('3')
        else:
            continue
    return ''.join(new_text)


def japanese_cleaner_3(text):
    parts = text.split('#')
    new_text = ''
    print(parts)
    for part in parts:
        # low high
        if '↑' in part and '↓' not in part:
            sub_parts = part.split('↑')
            sub_part1 = add_tone(sub_parts[0], True)
            sub_part2 = add_tone(sub_parts[1], False)
            sub_text = sub_part1 + sub_part2
            new_text += sub_text
        # high low
        elif '↑' not in part and '↓' in part:
            sub_parts = part.split('↓')
            sub_part1 = add_tone(sub_parts[0], False)
            sub_part2 = add_tone(sub_parts[1], True)
            sub_text = sub_part1 + sub_part2
            new_text += sub_text
        # low high low
        elif '↑' in part and '↓' in part:
            sub_parts = re.split('↑|↓', part)
            sub_part1 = add_tone(sub_parts[0], True)
            sub_part2 = add_tone(sub_parts[1], False)
            sub_part3 = add_tone(sub_parts[2], True)
            sub_text = sub_part1 + sub_part2 + sub_part3
            new_text += sub_text
        else:
            new_text += part

    # revision
    for item in _revision_jp.items():
        old = item[0]
        new = item[1]
        new_text = new_text.replace(old, new)

    return new_text


def japanese_cleaner_pipe(text):
    text = japanese_cleaner_1(text)
    text = japanese_cleaner_2(text)
    text = japanese_cleaner_3(text)

    return text

'''English cleaners'''

import eng_to_ipa as ipa

_revision_en = {
    "ɑ", "a",
    "eɪ", "ɛɪ",
}

# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
    ('mrs', 'misess'),
    ('mr', 'mister'),
    ('dr', 'doctor'),
    ('st', 'saint'),
    ('co', 'company'),
    ('jr', 'junior'),
    ('maj', 'major'),
    ('gen', 'general'),
    ('drs', 'doctors'),
    ('rev', 'reverend'),
    ('lt', 'lieutenant'),
    ('hon', 'honorable'),
    ('sgt', 'sergeant'),
    ('capt', 'captain'),
    ('esq', 'esquire'),
    ('ltd', 'limited'),
    ('col', 'colonel'),
    ('ft', 'fort'),
]]


def expand_abbreviations(text):
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text


def lowercase(text):
    return text.lower()


def collapse_whitespace(text):
    return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
    return unidecode(text)


def basic_cleaners(text):
    '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def transliteration_cleaners(text):
    '''Pipeline for non-English text that transliterates to ASCII.'''
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def english_cleaners(text):
    '''Pipeline for English text, including abbreviation expansion.'''
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = expand_abbreviations(text)
    return text


def english_cleaner_pipe(text):
    text = ipa.convert(text)
    text = text.replace('ˈ', '').replace('ˌ', '')
    text = text.replace('j', 'y').replace('ɑ', 'a').replace('eɪ', 'ɛɪ')

    return text


'''Trilingual cleaner'''
def trilingual_cleaner(text, lang):
    if lang == 'ch':
        return chinese_cleaner_pipe(text)
    elif lang == 'ja':
        return japanese_cleaner_pipe(text)
    elif lang == 'en':
        return english_cleaner_pipe(text)
    else:
        raise ValueError ('Unsupported language type!')

'''Phoneme encoder'''

def phoneme_encoder(text, lang):
  phones = text.split(' ')
  vectors = []
  for phone in phones:
    for symbol in phone:
      vector = []
      if symbol not in _tones:
        vector.append(symbol)

        # dimension of language
        if lang == "en":
          vector.extend([0, 0])
        elif lang == "ja":
          vector.extend([0, 1])
        elif lang == "ch":
          vector.extend([1, 0])
        else:
          raise ValueError ('Unsupported language type!')

        # dimension of tone
        if phone[-1] in _tones:
          tone = phone[-1]
          if tone == "1":
            vector.extend([1, 0, 0, 0])
          elif tone == "2":
            vector.extend([0, 1, 0, 0])
          elif tone == "3":
            vector.extend([0, 0, 1, 0])
          else:
            vector.extend([0, 0, 0, 1])
        else:
          vector.extend([0, 0, 0, 0])

        vectors.append(vector)
  return vectors
