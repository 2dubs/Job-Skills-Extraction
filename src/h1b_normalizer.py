import unicodecsv as csv
import re


class Name_Normalizer():
    """
    An object -- name normalizer that imports support data for cleaning H1B company names
    """

    def __init__(self):
        self.stop_word_set = self.read_stop_word_set('company_stop_words.csv')
        self.special_name_set = self.read_special_name_list('special_companies.txt')
        self.acronym_original_set = self.read_acronym_list('Suffix_Acronyms.csv')

    def read_stop_word_set(self, filename):
        # read company name stop word into set
        result = set()
        with open(filename, str('rb')) as source:
            rdr = csv.reader(source, encoding='utf-8')
            for row in rdr:
                result.add(row[0])
        return result

    def read_special_name_list(self, filename):
        # read special company name list
        with open(filename, str('r')) as source:
            result = source.read().splitlines()
        return result

    def read_acronym_list(self, filename):
        # read company name stop word into set
        result = []
        with open(filename, str('rb')) as source:
            rdr = csv.reader(source, encoding='utf-8')
            for row in rdr:
                result.append(row)
        return result

    def multireplace(self, string, replacements):
        """
        Given a string and a replacement map, it returns the replaced string.

        :param str string: string to execute replacements on
        :param dict replacements: replacement dictionary {value to find: value to replace}
        :rtype: str
        """
        # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
        # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
        # 'hey ABC' and not 'hey ABc'
        substrs = sorted(replacements, key=len, reverse=True)

        # Create a big OR regex that matches any of the substrings to replace
        regexp = re.compile('|'.join(map(re.escape, substrs)))

        # For each match, look up the new string in the replacements
        return regexp.sub(lambda match: replacements[match.group(0)], string)

    def remove_html_escape_chars(self, input_str):
        """
        remove or substitute HTML escape characters

        :param input_str: str
        :return: str
        """
        html_ansi_char_dict = {'&QUOT;': '"',
                               '&AMP;': '&',
                               '&LT;': '<',
                               '&GT;': '>',
                               '&SBQUO;': "'",
                               '&BDQUO;': '"',
                               '&HELLIP;': '...',
                               '&SCARON;': 'S',
                               '&ZCARON;': 'Z',
                               '&LSQUO;': "'",
                               '&RSQUO;': "'",
                               '&LDQUO;': '"',
                               '&RDQUO;': '"',
                               '&NDASH;': '-',
                               '&MDASH;': '-',
                               '&TILDE;': '~',
                               '&AACUTE;': 'A',
                               '&AGRAVE;': 'A',
                               '&ACIRC;': 'A',
                               '&ATILDE;': 'A',
                               '&AUML;': 'A',
                               '&ARING;': 'A',
                               '&EGRAVE;': 'E',
                               '&EACUTE;': 'E',
                               '&ECIRC;': 'E',
                               '&EUML;': 'E',
                               '&IGRAVE;': 'I',
                               '&IACUTE;': 'I',
                               '&ICIRC;': 'I',
                               '&IUML;': 'I',
                               '&NTILDE;': 'N',
                               '&OGRAVE;': 'O',
                               '&OACUTE;': 'O',
                               '&OCIRC;': 'O',
                               '&OTILDE;': 'O',
                               '&OUML;': 'O',
                               '&OSLASH;': 'O',
                               '&UGRAVE;': 'U',
                               '&UACUTE;': 'U',
                               '&UCIRC;': 'U',
                               '&UUML;': 'U',
                               '&YACUTE;': 'Y',
                               '&YUML;': 'Y'}
        return self.multireplace(input_str.upper(), html_ansi_char_dict)

    def normalize_company_name(self, origin_name):
        """
        Working function to normalize company name in data files
        stop_word_set and special_name_list are hand picked dictionary that is loaded from file
        """
        if origin_name is None:
            return None
        # handle html characters
        origin_name = self.remove_html_escape_chars(origin_name)
        # handle semicolons
        origin_name = origin_name.replace(';', ' ')
        # handle commas and extra white space
        origin_name = ' '.join(origin_name.replace(',', ' ').split())

        # get rid of content in () and after partial "("
        words_list = origin_name.split('(')[0].split()

        # remove stop words and recompose name
        rslt_list = []
        for word in words_list:
            if word.upper() not in self.stop_word_set:
                rslt_list.append(word)
        if len(rslt_list) > 0 and (rslt_list[-1] == '&' or rslt_list[-1].upper() == 'AND'):
            del rslt_list[-1]
        return u' '.join(rslt_list).encode('utf-8')