from ..base_op import OPERATORS, Mapper


@OPERATORS.register_module('remove_incomplete_sentence_mapper')
class RemoveIncompleteSentenceMapper(Mapper):
    """Mapper to remove incomplete sentences. """

    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        
        self.eos_puncts = [
            "?", "!", '.', ")",  "，", "。", "?", "!", ")", ":"
        ]
    
    def is_complete_sentence(self, sentence: str):
        # EOS
        
        return any([sentence.endswith(punct) for punct in self.eos_puncts])
    
    def process(self, sample):

        sentences = sample[self.text_key].split('\n')
        sentences = [sentence for sentence in sentences if self.is_complete_sentence(sentence)]
        sample[self.text_key] = '\n'.join(sentences)
        return sample
