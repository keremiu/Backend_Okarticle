from Modules.article_tree import ArticleTree
from Modules.reader import get_tree_from_article_pdf
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, BartForConditionalGeneration

model_sum = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")


tree = get_tree_from_article_pdf("Device_to_Device_Communication_using_Stackelberg_Game_Theory_approach.pdf")
tree.calculate_count_of_words()
#str = tree.get_article_tree_as_string()
#print(str)
result = tree.summarize_parts(0.4, tokenizer, model_sum)
print(result)


