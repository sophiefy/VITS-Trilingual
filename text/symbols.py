""" from https://github.com/keithito/tacotron """

'''
Defines the set of symbols used in text input to the model.
'''
_pad        = '_'
_punctuation = ',.!?-'
_letters_en = 'iɪɛæaoɔuʊʌəɜptkfsθʃhbdgvzðʒmnŋlryw'
_letters_ch = 'üIjqx'
_letters_ja = ''

# Export all symbols:
symbols = [_pad] + list(_punctuation) + list(_letters_en) + list(_letters_ch) + list(_letters_ja)

# Special symbol ids
SPACE_ID = symbols.index(" ")
