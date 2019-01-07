import string
from nltk.tokenize import sent_tokenize
from deft.nlp.tokenize import word_tokenize


class Processor(object):
    def __init__(self, shortform, exclude=None):
        self.shortform = shortform
        if exclude is None:
            exclude = set([])
        self.exclude = exclude

    def extract(self, text):
        """Find maximal candidate longforms co-occuring with shortform in text

        Parameters
        ----------
        text: str
            A text document

        Returns
        -------
        candidates: list of list
            list of lists of tokens in maximal candidate longforms co-occuring
            with the given shortform in the standard pattern

        str:
            Concatentation of all sentences in the original fulltext containing
            the given shortform with the exception of the defining sentences
            that contain the standard pattern. For use in training ML models.
            This is included in the processor even though it is orthogonal to
            save the cost of sentence splitting.
        """
        # Split text into a list of sentences
        sentences = sent_tokenize(text)

        # extract sentences defining shortform using parenthetic pattern
        defining_sentences = []
        other_sentences = []
        for sentence in sentences:
            if '(%s)' % self.shortform in sentence:
                defining_sentences.append(sentence)
            else:
                other_sentences.append(sentence)

        candidates = [self._get_candidate(sentence)
                      for sentence in defining_sentences]
        return candidates, ' '.join(sent for sent in other_sentences
                                    if self.shortform in sent)

    def _get_candidate(self, sentence):
        """Returns maximal candidate longform from a list of tokens.

        Parameters
        ----------
        sentence: str
            A sentence containing the pattern <longform> (<shortform>)

        Returns
        -------
        candidate: list of str
            Sublist of input list containing tokens between start of sentence
            and first occurence of the shortform in parentheses, or between
            a stop word and the first occurence of the shortform in parentheses
            if there is a set of stop words to exclude from longforms.
        """
        # tokenize sentence into list of words
        tokens = word_tokenize(sentence)

        # Loop through tokens. The nltk word tokenizer used will split off
        # the parentheses surrounding the shortform into separate tokens.
        for index in range(len(tokens) - 2):
            if tokens[index] == '(' and tokens[index+1] == self.shortform \
               and tokens[index+2] == ')':
                # The shortform has been found in parentheses

                # Capture all tokens in the sentence up until but excluding
                # the left parenthese containing the shortform, excluding
                # punctuation
                candidate = [token for token in tokens[:index]
                             if token not in string.punctuation]

                # convert tokens to lower case
                candidate = [token.lower() for token in candidate]
                # Keep only the tokens preceding the left parenthese up until
                # but not including the first stop word
                i = len(candidate)-1
                while i >= 0 and candidate[i] not in self.exclude:
                    i -= 1
                candidate = candidate[i+1:]
                return candidate