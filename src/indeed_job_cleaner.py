from __future__ import print_function
import mysql.connector
from nltk.corpus import stopwords
import h1b_normalizer
from nltk.tokenize import sent_tokenize

normalizer = h1b_normalizer.Name_Normalizer()
out_path = '../input'


# I/O: sql --> list
def keyword_vs_description(query, header, type='description'):
    cnx = mysql.connector.connect(user='root', password='C071401www!!', database='MentorX_Project')
    cursor = cnx.cursor()
    cursor.execute(query)
    to_return = [header]

    # whole job description as a document
    if type == 'description':
        for each in cursor:
            if len(each[0].split()) > 20:
                to_return.append(each)
    # each sentence as a document
    elif type == 'sentence':
        for each in cursor:
            if len(each[0].split()) > 20:
                l = sent_tokenize(each[0])
                for item in l:
                    to_return.append([str(item.decode('utf-8')), str(each[1])])
    # 3-sentence paragraph as a document
    elif type == 'paragraph':
        for each in cursor:
            if len(each[0].split()) > 20:
                l = sent_tokenize(each[0])
                size = len(l)
                for i in range(size-2):
                    paragraph = [str(l[i].decode('utf-8')
                                 + l[i+1].decode('utf-8')
                                 + l[i+2].decode('utf-8'))]
                    paragraph.append(str(each[1].decode('utf-8')))
                    to_return.append(paragraph)
    cnx.close()
    cursor.close()
    return to_return


# copy n paste the following for function where s_w_t is embedded in
# Tokenizer: tokenize a sentence/paragraph with stop words from NLTK package
def stop_word_tokenize(raw_description, stop_word_set, company):
    # split description into words with symbols attached + lower case
    raw_tokenized = raw_description.lower().split()

    # handle special characters
    ex_char = [':', ';',
               ',', '&',
               '(', ')',
               '"', '!',
               '?', '*',
               '-']
    exclude = set(ex_char)
    no_punc_tokenzied = []
    # for every element in string.split()
    # go through every character
    for each in raw_tokenized:
        if '/' not in each:
            s = ''.join(ch for ch in each if ch not in exclude)
            no_punc_tokenzied.append(s)
        else:
            s = ''.join(ch for ch in each if ch not in exclude)
            l = s.split('/')
            for item in l:
                no_punc_tokenzied.append(item)

    # get company name and normalize
    clean_name = normalizer.normalize_company_name(company).lower()
    # generate stop words from company names
    # eg: Lockheed Martin, INC. --> [lockheed, martin, martin's]
    exclude = clean_name.split()
    if len(exclude) > 0:
        last = list(exclude[-1])
        last.append("'s")
        exclude.append("".join(last))

    clean_list = []
    for item in no_punc_tokenzied:
        if item not in exclude:
            clean_list.append(item)
    clean_description = ' '.join(clean_list)

    # clean stop words
    filtered = []
    for w in clean_description.split():
        if w not in stop_word_set:
            filtered.append(w)
    return filtered


if __name__ == "__main__":
    query = """SELECT job_description, company FROM indeed_jobs WHERE keyword = 'ACCOUNTANT'"""
    # query = """SELECT job_description, company FROM indeed_jobs"""
    header = ('job description','company')
    data = keyword_vs_description(query, header,'paragraph')
    out_put = []
    count = 0
    # import stop words set from NLTK package
    stop_word_set = set(stopwords.words('english'))

    # import data from SQL server and customize
    for each in data:
        print(each)
        out_put.append(" ".join(stop_word_tokenize(each[0], stop_word_set, each[1])))
        out_put.append("\n")
        out_put.append("\n")

    # with open('%s/SOFTWARE ENGINEER_DESCRIPTIONS.txt'%(out_path), 'w') as source:
    with open('%s/ACCOUNTANT_DESCRIPTIONS.txt' % (out_path), 'w') as source:
        for each in out_put:
            source.write(each)
        source.close()