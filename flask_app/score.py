import PyPDF2
import pathlib
from docx import Document
import docx2txt
import re
from difflib import get_close_matches
import math

PATH="F:/Study/Resume/Resume.docx"

class ScoreResume:
    def __init__(self,file_path,career):
        self.file_path=file_path
        self.career=career

    def __repr__(self):
        return repr("Path:"+ str(self.file_path))

    def get_file_text(self):
        file_extension = pathlib.Path(self.file_path).suffix
        FileObj = open(self.file_path, 'rb')
        doc_text=[]
        # Read PDF file
        if file_extension==".pdf":
            pdfReader = PyPDF2.PdfFileReader(FileObj)
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
        elif file_extension==".docx":
            text = docx2txt.process(self.file_path)
            return text

    def clean_text(self,text):
        text=text.replace("\n"," ")
        text=re.sub(' +', ' ',text)
        text=text.lower()
        text=text.strip()
        return text

    def closeMatches(self,patterns, word):
        return(get_close_matches(word, patterns))

    def points(self):
        text=self.get_file_text()
        text=self.clean_text(text)
        # Calculating length Score
        len_score=round(math.log(len(text)))
        # Calculating General Score
        gen_points=0
        general_keyword={'certifications':1,'experience':1,'skills':1,
                        'voluntary':2,'specialist':1,'knowledge':1,'exceptional':1,
                        'satisfaction':1,'school':1,'degree':1,'college':1,'university':1,
                        'responsibilities':1,'achievements':2,}
        for t in text.split(" "):
            match=self.closeMatches(list(general_keyword.keys()),t)
            if match!=[]:
                for m in match:
                    gen_points=gen_points+general_keyword[m]

        # Calculating points on basis of career
        #1) Data Science
        points=0
        if self.career=="Data Science":
            points_dict={'python':1,'c++':1,'machine learning':2,'data science':5,'data':1}
            for keyword in points_dict.keys():
                c=text.count(keyword)
                points=points+(c*points_dict[keyword])
        #2) Other fields
        else:
            return "Error"
            # Load error

        return points,gen_points,len_score

# sr=ScoreResume(PATH,"Data Science")
# print(sr.points())
