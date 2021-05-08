import PyPDF2
import fitz
path='F:/Data_Science/sample resume/Abhijit-Manepatil.pdf'
path1='F:/Study/Resume/MitulTandon_Resume.pdf'

doc_text=[]
FileObj = open(path1,'rb')
doc = fitz.open('pdf',FileObj.read())
pages = len(doc)
print(pages)
for p in range(0,pages):
    text = doc[p].getText("text")
    doc_text.append(text)
doc_text=",".join(doc_text)
print(doc_text)

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
