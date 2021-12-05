# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 20:33:10 2021
@author: Yunxin
"""

# -*- coding: utf-8 -*-
"""contextual_search_Hong Kong.ipynb
Automatically generated by Colaboratory.
Original file is located at
    https://colab.research.google.com/drive/1d6Vjg6BERqtqqu-EFFaDASdk6Jaje6qr
"""

#!pip install -U spacy
#first install the library that would help us use BERT in an easy to use interface
#https://github.com/UKPLab/sentence-transformers/tree/master/sentence_transformers
#!pip install -U sentence-transformers

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest
import streamlit as st

#!python -m spacy download en_core_web_sm

## Use this to import spacy directly if using the Brain colab runtime or a custom colab runtime that includes spacy in its build.
import os
import spacy
nlp = spacy.load("en_core_web_sm")
from spacy import displacy

stopwords=list(STOP_WORDS)
from string import punctuation
punctuation=punctuation+ '\n'

import pandas as pd

from sentence_transformers import SentenceTransformer
import scipy.spatial
import pickle as pkl




st.title("Hong Kong Hotel Recommender")
st.subheader('Overview')
st.markdown("Yunxin Liu - HW3")
st.markdown("A Hong Kong hotel recommendation system aims at suggesting properties/hotels to a user such that they would prefer the recommended property over others.")
st.sidebar.text_input('Where would you like to visit?')
queries = [str(userinput)]
embedder = SentenceTransformer('all-MiniLM-L6-v2')

df = pd.read_csv("clean_data.csv")

df['Hotel'].drop_duplicates()

df_combined = df.sort_values(['Hotel']).groupby('Hotel', sort=False).review.apply(''.join).reset_index(name='all_review')

df_combined
import re

df_combined['all_review'] = df_combined['all_review'].apply(lambda x: re.sub('[^a-zA-z0-9\s]','',x))

def lower_case(input_str):
    input_str = input_str.lower()
    return input_str

df_combined['all_review']= df_combined['all_review'].apply(lambda x: lower_case(x))

df = df_combined

df_sentences = df_combined.set_index("all_review")

df_sentences.head()

df_sentences = df_sentences["Hotel"].to_dict()
df_sentences_list = list(df_sentences.keys())
len(df_sentences_list)

list(df_sentences.keys())[:5]

import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util

df_sentences_list = [str(d) for d in tqdm(df_sentences_list)]

# Corpus with example sentences
corpus = df_sentences_list
corpus_embeddings = embedder.encode(corpus,show_progress_bar=True)

model = SentenceTransformer('all-MiniLM-L6-v2')
paraphrases = util.paraphrase_mining(model, corpus)

query_embeddings_p =  util.paraphrase_mining(model, queries, show_progress_bar=True)

import pickle as pkl

with open("corpus_embeddings.pkl" , "wb") as file_:
    pkl.dump(corpus_embeddings, file_)

query_embeddings = embedder.encode(queries,show_progress_bar=True)

# Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
closest_n = 5
st.write("\nTop 5 most similar sentences in corpus:")
for query, query_embedding in zip(queries, query_embeddings):
    distances = scipy.spatial.distance.cdist([query_embedding], corpus_embeddings, "cosine")[0]

    results = zip(range(len(distances)), distances)
    results = sorted(results, key=lambda x: x[1])

    st.write("\n\n=========================================================")
    st.write("==========================Query==============================")
    st.write("===",query,"=====")
    st.write("=========================================================")


    for idx, distance in results[0:closest_n]:
        st.write("Score:   ", "(Score: %.4f)" % (1-distance) , "\n" )
        st.write("Paragraph:   ", corpus[idx].strip(), "\n" )
        row_dict = df.loc[df['all_review']== corpus[idx]]
        st.write("paper_id:  " , row_dict['Hotel'] , "\n")
        # print("Title:  " , row_dict["title"][corpus[idx]] , "\n")
        # print("Abstract:  " , row_dict["abstract"][corpus[idx]] , "\n")
        # print("Abstract_Summary:  " , row_dict["abstract_summary"][corpus[idx]] , "\n")
        st.write("-------------------------------------------")

from sentence_transformers import SentenceTransformer, util
import torch
embedder = SentenceTransformer('all-MiniLM-L6-v2')
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
