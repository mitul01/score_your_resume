import PyPDF2
import pathlib
from docx import Document
import docx2txt
import re
from difflib import get_close_matches
import math
from textblob import TextBlob
import spacy
from spacy.matcher import Matcher
import math
from collections import Counter
from flask_app.utils.grammar import extract_grammar_words
from flask_app.utils.active_voice import ActiveVoice

class ScoreResume:
    def __init__(self,file,file_ext,career):
        self.file_ext=file_ext
        self.file=file
        self.career=career

    def __repr__(self):
        return repr("FileObj:"+ str(self.file))

    def range_score(self,input,output_start,output_end,input_start,input_end):
        output = output_start + ((output_end - output_start) / (input_end - input_start)) * (input - input_start)
        return output

    def range_value(self,input,max_input):
        scaled_input=max_input*(1-math.exp(-input))/2
        return scaled_input

    def get_file_text(self):
        # Read PDF file
        if self.file_ext==".pdf":
            doc_text=[]
            pdfReader = PyPDF2.PdfFileReader(self.file)
            pages=pdfReader.numPages
            for p in range(0,pages):
                pageObj=pdfReader.getPage(p)
                text=pageObj.extractText()
                text=str(text)
                text=self.clean_text(text)
                doc_text.append(text)
            doc_text=",".join(doc_text)
            return doc_text
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

    def get_verbs(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        return(extract_grammar_words(text).get())

    def voice(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        av=ActiveVoice()
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        sents = list(doc.sents)
        count_passive=0
        for s in sents:
            passive=av.is_passive(str(s))
            if passive:
                count_passive=count_passive+1

        scaled_passive_score=self.range_score(output_start=0,output_end=100,
                                        input_start=0,input_end=len(sents),input=count_passive)
        return scaled_passive_score

    def sentiment(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        polarity,subjectivity = TextBlob(text).sentiment
        scaled_polarity=self.range_score(output_start=0,output_end=100,
                                input_start=-1,input_end=1,input=polarity)
        scaled_subjectivity=self.range_score(output_start=0,output_end=100,
                                input_start=0,input_end=1,input=subjectivity)

        return (scaled_polarity,scaled_subjectivity)

    def quantifier_score(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        numbers = re.findall('[0-9]+', text)
        signs = re.findall(r'%', text)
        scaled_quant_score=self.range_score(output_start=0,output_end=100,
                                input_start=0,input_end=len(text.split(' '))/6,input=len(numbers)+len(signs))
        return scaled_quant_score


    def points(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        # Calculating length Score
        len_score=len(text)
        len_score=self.range_value(len_score,500)
        len_score=self.range_score(output_start=0,output_end=100,
                                input_start=0,input_end=500,input=len_score)

        # Calculating General Score
        gen_points_scaled=0
        gen_points=0
        keyword_match=[]
        general_keyword={'certifications':1,'experience':1,'skills':1,
                        'voluntary':2,'specialist':1,'knowledge':1,'exceptional':1,
                        'satisfaction':1,'school':1,'degree':1,'college':1,'university':1,
                        'responsibilities':1,'achievements':2,}
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
        if self.career=="Data Science":
            points_dict={'python':1,'c++':1,'machine learning':2,'data science':5,'data':1}
        #2) Software engginering
        elif self.career=="Software engginering":
            points_dict={'python':1,'c++':1,'machine learning':2,'data science':5,'data':1}
        #3)
        elif self.career=="Software engginering":
            points_dict={'python':1,'c++':1,'machine learning':2,'data science':5,'data':1}
        #4)
        elif self.career=="Software engginering":
            points_dict={'python':1,'c++':1,'machine learning':2,'data science':5,'data':1}
        else:
            return "error"

        match_career_keywords=[]
        special_points=0
        scaled_special_points=0
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

        return round(final_keyword_points),round(len_score)


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
