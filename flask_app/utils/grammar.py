import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
lemmatizer = nltk.WordNetLemmatizer()

class extract_grammar_words:

    def __init__(self,text):
        self.text=text
        self.tokens = [nltk.word_tokenize(sent) for sent in [self.text]]
        self.postag = [nltk.pos_tag(sent) for sent in self.tokens][0]

# {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
        self.grammar = r"""
                    NBAR:
                    {<RB.?>*<VB.?>*<JJ>*<VB.?>+<VB>?} # Verbs and Verb Phrases
                    NP:
                    {<NBAR>}
                    {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
                    """
        self.cp = nltk.RegexpParser(self.grammar)
        self.tree = self.cp.parse(self.postag)

    def leaves(self):
        """Finds NP (nounphrase) leaf nodes of a chunk tree."""
        for subtree in self.tree.subtrees(filter = lambda t: t.label() =='NP'):
            yield subtree.leaves()

    def get_word_postag(self,word):
        if pos_tag([word])[0][1].startswith('J'):
            return wordnet.ADJ
        if pos_tag([word])[0][1].startswith('V'):
            return wordnet.VERB
        if pos_tag([word])[0][1].startswith('N'):
            return wordnet.NOUN
        else:
            return wordnet.NOUN

    def normalise(self,word):
        """Normalises words to lowercase and stems and lemmatizes it."""
        word = word.lower()
        postag = self.get_word_postag(word)
        word = lemmatizer.lemmatize(word,postag)
        return word

    def get_terms(self):
        for leaf in self.leaves():
            terms = [self.normalise(w) for w,t in leaf]
            yield terms

    def get(self):
        terms = self.get_terms()
        features = []
        for term in terms:
            _term = ''
        for word in term:
            _term += ' ' + word
        features.append(_term.strip())
        return features
