import spacy


nlp = spacy.load('en_core_web_sm')
# nlp("this is my tweet").vector
nlp.to_disk('my_model')