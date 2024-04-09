from Modules.article_tree import ArticleTree
from Modules.reader import get_tree_from_article_pdf
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, BartForConditionalGeneration

model_sum = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

model_sim = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
tree = get_tree_from_article_pdf("Device_to_Device_Communication_using_Stackelberg_Game_Theory_approach.pdf")
str = tree.get_article_tree_as_string()
print(tree.get_context("as  D2D  users  can  share/reuse  the  UL  or  DL  (uplink/  downlink)  resource  blocks  (RBs)  of  the  cellular  users",5,model_sim))



