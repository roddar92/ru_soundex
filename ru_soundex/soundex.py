import re
from abc import ABC, abstractmethod
import pymorphy2


class Soundex(ABC):
    _vowels = ''
    _table = str.maketrans('', '')
    _reduce_regex = re.compile(r'(\w)(\1)+', re.IGNORECASE)
    _vowels_regex = re.compile(r'(0+)', re.IGNORECASE)

    def __init__(self, delete_first_letter=False, delete_first_coded_letter=False,
                 delete_zeros=False, cut_result=False, seq_cutted_len=4):
        """
        Initialization of Soundex object
        :param delete_first_letter: remove the first letter from the result code (A169 -> 169)
        :param delete_first_coded_letter: remove the first coded letter from the result code (A0169 -> A169)
        :param delete_zeros: remove vowels from the result code
        :param cut_result: cut result core till N symbols
        :param seq_cutted_len: length of the result code
        """
        self.delete_first_letter = delete_first_letter
        self.delete_first_coded_letter = delete_first_coded_letter
        self.delete_zeros = delete_zeros
        self.cut_result = cut_result
        self.seq_cutted_len = seq_cutted_len

    def _is_vowel(self, letter):
        return letter in self._vowels

    def _reduce_seq(self, seq):
        return self._reduce_regex.sub(r'\1', seq)

    def _translate_vowels(self, word):
        return ''.join('0' if self._is_vowel(letter) else letter for letter in word)

    def _remove_vowels_and_paired_sounds(self, seq):
        seq = self._vowels_regex.sub('', seq)
        seq = self._reduce_seq(seq)
        return seq

    def _apply_soundex_algorithm(self, word):
        word = word.lower()
        first, last = word[0], word
        last = last.translate(self._table)
        last = self._translate_vowels(last)
        last = self._reduce_seq(last)
        if self.delete_zeros:
            last = self._remove_vowels_and_paired_sounds(last)
        if self.cut_result:
            last = last[:self.seq_cutted_len] if len(last) >= self.seq_cutted_len else last
            last += ('0' * (self.seq_cutted_len - len(last)))
        if self.delete_first_coded_letter:
            last = last[1:]
        first_char = '' if self.delete_first_letter else first.capitalize()
        return first_char + last.upper()

    def get_vowels(self):
        return self._vowels

    def is_delete_first_coded_letter(self):
        return self.delete_first_coded_letter

    def is_delete_first_letter(self):
        return self.delete_first_letter

    @abstractmethod
    def transform(self, word):
        """
        Converts a given word th Soundex code
        :param word: string
        :return: Soundex string code
        """
        return None


class RussianSoundex(Soundex):
    _vowels = 'аэиоуыеёюя'
    _vowels_table = str.maketrans('аяоыиеёэюу', 'AAABBBBBCC')
    _table = str.maketrans('бпвфгкхдтжшчщзсцлмнр', '11223334455556667889')
    _ego_ogo_endings = re.compile(r'([ео])(г)(о$)', re.IGNORECASE)

    _replacement_map = {
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(я)', re.IGNORECASE): 'jа',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(ю)', re.IGNORECASE): 'jу',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(е)', re.IGNORECASE): 'jэ',
        re.compile(r'(^|ъ|ь|' + r'|'.join(_vowels) + r')(ё)', re.IGNORECASE): 'jо',
        re.compile(r'й', re.IGNORECASE): 'j',
        re.compile(r'([тсзжцчшщ])([жцчшщ])', re.IGNORECASE): r'\2',
        re.compile(r'(с)(т)([лнц])', re.IGNORECASE): r'\1\3',
        re.compile(r'(н)([тд])(ств)', re.IGNORECASE): r'\1\3',
        re.compile(r'([нс])([тд])(ск)', re.IGNORECASE): r'\1\3',
        re.compile(r'(р)(д)([чц])', re.IGNORECASE): r'\1\3',
        re.compile(r'(з)(д)([нц])', re.IGNORECASE): r'\1\3',
        re.compile(r'(в)(ств)', re.IGNORECASE): r'\2',
        re.compile(r'(л)(нц)', re.IGNORECASE): r'\2',
        re.compile(r'[ъь]', re.IGNORECASE): '',
        re.compile(r'([дт][зсц])', re.IGNORECASE): 'ц'
    }

    def __init__(self, delete_first_letter=False, delete_first_coded_letter=False,
                 delete_zeros=False, cut_result=False, seq_cutted_len=4,
                 code_vowels=False, use_morph_analysis=False):
        """
        Initialization of Russian Soundex object
        :param delete_first_letter:
        :param delete_first_coded_letter:
        :param delete_zeros:
        :param cut_result:
        :param seq_cutted_len:
        :param use_morph_analysis: use morphological grammems for phonemes analysis
        :param code_vowels: group and code vowels as ABC letters
        """
        super(RussianSoundex, self).__init__(delete_first_letter, delete_first_coded_letter,
                                             delete_zeros, cut_result, seq_cutted_len)

        self.code_vowels = code_vowels
        self.use_morph_analysis = use_morph_analysis
        self._moprh = pymorphy2.MorphAnalyzer()

    def _translate_vowels(self, word):
        if self.code_vowels:
            return word.translate(self._vowels_table)
        else:
            return super(RussianSoundex, self)._translate_vowels(word)

    def _replace_ego_ogo_endings(self, word):
        return self._ego_ogo_endings.sub(r'\1в\3', word)

    def _use_morph_for_phoneme_replace(self, word):
        parse = self._moprh.parse(word)
        if parse and ('ADJF' in parse[0].tag or 'NUMB' in parse[0].tag or 'NPRO' in parse[0].tag):
            word = self._replace_ego_ogo_endings(word)
        return word

    def transform(self, word):
        if self.use_morph_analysis:
            word = self._use_morph_for_phoneme_replace(word)
        for replace, result in self._replacement_map.items():
            word = replace.sub(result, word)
        if self.code_vowels:
            word = re.sub(r'и[еио]', 'и', word)
            word = re.sub(r'[еи][ая]', 'я', word)
        return self._apply_soundex_algorithm(word)