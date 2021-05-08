import PyPDF2
import fitz
import pdftotext
import spacy
path='F:/Data_Science/sample resume/Abhijit-Manepatil.pdf'
path1='F:/Study/Resume/MitulTandon_Resume.pdf'

doc_text=[]
with open(path, "rb") as f:
    pdf = pdftotext.PDF(f)
for page in pdf:
    text = page
    doc_text.append(text)
doc_text=",".join(doc_text)

from flask_app.utils.active_voice import ActiveVoice
def voice(text):
        av=ActiveVoice()
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        sents = list(doc.sents)
        print(len(sents))
        count_passive=0
        for s in sents:
            passive=av.is_passive(str(s))
            if passive:
                count_passive=count_passive+1

        return round(len(sents)/4)+ (len(sents)-count_passive)

print(voice(doc_text))

            # doc_text=[]
            # pdfReader = PyPDF2.PdfFileReader(self.file)
            # pages=pdfReader.numPages
            # # doc = fitz.open('pdf',self.file.read())
            # # pages = len(doc)
            # for p in range(0,pages):
            #     pageObj=pdfReader.getPage(p)
            #     text=pageObj.extractText()
            #     # text = doc[p].getText("text")
            #     text=str(text)
            #     doc_text.append(text)
            # doc_text=",".join(doc_text)
            # print(doc_text)
                        #
                        # for p in range(0,pages):
                        #     text = doc[p].getText("text")
                        #     doc_text.append(text)
                        # doc_text=",".join(doc_text)
                        # return doc_text
