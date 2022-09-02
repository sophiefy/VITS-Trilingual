""" from https://github.com/keithito/tacotron """
from text import cleaners
from text.symbols import symbols
from text.cleaners import phoneme_encoder


# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}
_id_to_symbol = {i: s for i, s in enumerate(symbols)}


def text_to_sequence(text, cleaner_names, lang):

  sequence = []
  clean_text = _clean_text(text, cleaner_names,lang)
  vectors = phoneme_encoder(clean_text, lang)

  for vector in vectors:
    symbol = vector[0]
    if symbol not in _symbol_to_id.keys():
      continue
    symbol_id = _symbol_to_id[symbol]
    vector[0] = symbol_id
    sequence.append(vector)
  return sequence


def cleaned_text_to_sequence(cleaned_text, lang):
  '''Converts a string of text to a sequence of IDs corresponding to the symbols in the text.
    Args:
      text: string to convert to a sequence
    Returns:
      List of integers corresponding to the symbols in the text
  '''
  sequence = []
  vectors = phoneme_encoder(clean_text, lang)

  for vector in vectors:
    symbol = vector[0]
    if symbol not in _symbol_to_id.keys():
      continue
    symbol_id = _symbol_to_id[symbol]
    vector[0] = symbol_id
    sequence.append(vector)
  return sequence


def sequence_to_text(sequence):
  '''Converts a sequence of IDs back to a string'''
  result = ''
  for symbol_id in sequence:
    s = _id_to_symbol[symbol_id]
    result += s
  return result


def _clean_text(text, cleaner_names, lang):
  for name in cleaner_names:
    cleaner = getattr(cleaners, name)
    if not cleaner:
      raise Exception('Unknown cleaner: %s' % name)
    text = cleaner(text, lang)
  return text
