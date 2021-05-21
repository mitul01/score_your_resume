from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import io
import pathlib
from docx import Document
import docx2txt
import re
from difflib import get_close_matches
import math
from textblob import TextBlob
import spacy
from spacy.matcher import Matcher
from collections import Counter
from nltk.util import ngrams
# from flask_app.utils.grammar import extract_grammar_words
from flask_app.utils.active_voice import ActiveVoice

class ScoreResume:
    def __init__(self,file,file_ext):
        self.file=file
        self.file_ext=file_ext

    def __repr__(self):
        return repr("FileObj:"+ str(self.file))

    def range_score(self,input,output_start,output_end,input_start,input_end):
        output = output_start + (((output_end - output_start) / (input_end - input_start))) * (input - input_start)
        return output

    def range_value(self,input,max_input):
        scaled_input=max_input*(1-math.exp(-input))/2
        return scaled_input

    def get_file_text(self):
        # Read PDF file
        if self.file_ext==".pdf":
            output_string = StringIO()
            parser = PDFParser(self.file)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)
            return output_string.getvalue()
    # Read docx file
        elif self.file_ext==".docx":
            text = docx2txt.process(self.file)
            return text

    def clean_text(self,text):
        text=text.replace("\n"," ")
        text=re.sub(' +', ' ',text)
        text=text.lower()
        text=text.strip()
        return text

    def closeMatches(self,patterns, word):
        return(get_close_matches(word, patterns))

    # def get_verbs(self):
    #     text=self.get_file_text()
    #     text=self.clean_text(text)
    #     return(extract_grammar_words(text).get())

    def check(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        return text


    def get_career(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        ds_careers=['data science','deep learning','machine learning','sql']
        se_carrers=['software engginering','software development']
        tech_others=['web development','cyber forensics','app development']
        non_tech=['desgining','research and','and development','economist','writing','finance','marketing']

        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        tokens = [token for token in text.split(" ") if token != ""]
        ngrams_t = list(ngrams(tokens, 2))
        ngrams_text=[" ".join(ngram) for ngram in ngrams_t]

        count={'Data Science':0,'Software Engginering':0,'Freelancing Tech':0,'Non Tech':0}
        for t in tokens:
            if t in ds_careers:
                count['Data Science']+=1
            if t in se_carrers:
                count['Software Engginering']+=1
            if t in tech_others:
                count['Freelancing Tech']+=1
            if t in non_tech:
                count['Non Tech']+=1

        for t in ngrams_text:
            if t in ds_careers:
                count['Data Science']+=1
            if t in se_carrers:
                count['Software Engginering']+=1
            if t in tech_others:
                count['Freelancing Tech']+=1
            if t in non_tech:
                count['Non Tech']+=1


        career = max(count, key= lambda x: count[x])
        return career


    def voice(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        av=ActiveVoice()
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        sents = list(doc.sents)
        count_passive=1
        for s in sents:
            passive=av.is_passive(str(s))
            if passive:
                count_passive=count_passive+1

        active_score = round(len(sents)/4)+ (len(sents)-count_passive)
        scaled_active_score=self.range_score(output_start=0,output_end=100,
                                        input_start=0,input_end=(len(sents)+round(len(sents)/4)),input=active_score)
        return round(scaled_active_score)

    def polarity(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        polarity,subjectivity = TextBlob(text).sentiment
        scaled_polarity=self.range_score(output_start=0,output_end=100,
                                input_start=-1,input_end=1,input=polarity)

        return round(scaled_polarity)

    def subjectivity(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        polarity,subjectivity = TextBlob(text).sentiment
        scaled_subjectivity=self.range_score(output_start=0,output_end=100,
                                input_start=0,input_end=1,input=subjectivity)

        return round(scaled_subjectivity)

    def quantifier_score(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        links=re.findall(URL_REGEX,text)
        numbers = re.findall('[0-9]+', text)
        signs = re.findall(r'%', text)
        scaled_quant_score=self.range_score(output_start=0,output_end=100,
                                input_start=0,input_end=len(text.split(' '))/6,input=len(numbers)+len(signs)+len(links))
        return round(scaled_quant_score)


    def points(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        # Calculating General Score
        gen_points_scaled=1
        gen_points=1
        keyword_match=[]
        general_keyword={'certifications':1,'experience':1,'skills':1,
                        'voluntary':2,'specialist':1,'knowledge':1,'exceptional':1,
                        'satisfaction':1,'school':1,'degree':1,'college':1,'university':1,
                        'responsibilities':1,'achievements':2,'projects':2,'academic':1,'internship':3}
        for t in text.split(" "):
            match=self.closeMatches(list(general_keyword.keys()),t)
            if match!=[]:
                for m in match:
                    keyword_match.append(m)

        keyword_match=Counter(keyword_match)
        gen_points=sum(keyword_match.values())
        for k in keyword_match.keys():
            gen_points_scaled=gen_points_scaled+self.range_value(keyword_match[k],general_keyword[k])

        scaled_gen_points=self.range_score(output_start=0,output_end=100,
                                input_start=0,input_end=sum(general_keyword.values()),input=gen_points_scaled)

        # Calculating points on basis of career
        #1) Data Science
        if self.get_career()=="Data Science":
            points_dict={'python':1,'c++':1,'machine learning':2,'data science':5,'data':1,
                            'linux':4,'aws':4,'heroku':2,'flask':2,'api':3,'github':4,'git':4}
        #2) Software engginering
        elif self.get_career()=="Software Engginering":
            points_dict={'c++':1,'c':1,'java':2,'devops':3,'python':2,'oops':4,'programming':3,'github':4,'git':4,
                            'software':5,'sdlc':1,'algorithms':5,'dbms':4,'sql':2,'linux':4,'operating':2,'systems':2}
        #3)
        elif self.get_career()=="Freelancing Tech":
            points_dict={'java':1,'andriod':5,'javascript':5,'css':3,'html':3,'python':3,'c':3,'linux':3,'c++':2,'api':3,
                                'studio':2,'github':4,'git':4}
        #4)
        elif self.get_career()=="Non Tech":
            points_dict={'marketing':1,'finance':2,'economics':2,'blog':1,'writing':3,'designing':2,
                            'adobe':3,'debate':5,'mnu':4,'law':4}
        else:
            points_dict={''}

        match_career_keywords=[]
        special_points=1
        scaled_special_points=1
        for t in text.split(" "):
            match=self.closeMatches(list(points_dict.keys()),t)
            if match!=[]:
                for m in match:
                    match_career_keywords.append(m)

        match_career_keywords=Counter(match_career_keywords)
        for k in match_career_keywords.keys():
            special_points=special_points+self.range_value(match_career_keywords[k],points_dict[k])

        scaled_special_points=self.range_score(output_start=0,output_end=100,
                                input_start=0,input_end=sum(points_dict.values()),input=special_points)

        final_keyword_points=(scaled_gen_points+scaled_special_points)/2

        return round(final_keyword_points)

    def word_count(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        len_score=len(text.split(" "))
        len_score_scaled=self.range_score(output_start=0,output_end=100,
                                    input_start=0,input_end=2000,input=len_score)
        return round(len_score_scaled)

    def get_all_scores(self):
            # text=self.get_file_text()
            # text=self.clean_text(text)
            keywords_score=self.points()
            word_count_score=self.word_count()
            polarity_score=self.polarity()
            subjectivity_score=self.subjectivity()
            passive_score=self.voice()
            quantify_score=self.quantifier_score()
            career=self.get_career()

            return [keywords_score,word_count_score,polarity_score,subjectivity_score,passive_score,quantify_score,career]

# weighted score generator
def weighted_score(keywords_score,
        word_count_score,subjectivity_score,
        polarity_score,passive_score,quantify_score):
            """
            Defualt weights
            # words count 0.1
            # keywords 0.3
            # subjectivity 0.1
            # polarity 0.2
            # active/passive 0.1
            # quantify 0.2
            """

            weights={'word_count_score':0.1,'keywords_score':0.3,'subjectivity_score':0.1,
                    'polarity_score':0.2,'passive_score':0.1,'quantify_score':0.2}

            scores={'word_count_score':word_count_score,'keywords_score':keywords_score,'subjectivity_score':subjectivity_score,
                    'polarity_score':polarity_score,'passive_score':passive_score,'quantify_score':quantify_score}

            total_score=0
            for k in weights.keys():
                if k in scores.keys():
                    total_score=total_score+(weights[k]*scores[k])

            return round(total_score)

# run all
def run_all(sr):
    scores=sr.get_all_scores()
    return scores
