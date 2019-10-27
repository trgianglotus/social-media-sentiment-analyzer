#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 15:20:14 2019

@author: adithyavh
"""
import os
import pickle
import spacy
import re
import numpy as np
import nltk

from nltk.tokenize import word_tokenize
from tensorflow import keras
from wordcloud import STOPWORDS
STOPWORDS = [word for word in STOPWORDS if word !="over"]

import os
 
dirpath = os.getcwd()
print("current directory is : " + dirpath)

class SentimentAnalyser:
    contractions = pickle.load(open("data/contractions.pkl", "rb"))
    spacy_nlp = spacy.load('en_core_web_sm')
    common_words = list(spacy.lang.en.stop_words.STOP_WORDS)
    stopwords = list(STOPWORDS)
    p_list = [1, 3, 5]
    
    def __init__ (self):
        self.model = keras.models.load_model("data/sigmoid_binary_900_2x1000_nodes")
        self.embedding_dict = pickle.load(open( "data/twitter_vectors.pkl", "rb" ))
        self.input_text = None
        self.tokenized_text = None
        self.vector_representation = None
        self.prediction = [[1]]

    def predict(self, text):
        self.input_and_process(text)
        self.predict_()
        return True if self.prediction[0][0] > .5 else False
    
    def input_and_process (self, text):
        self.input_text = text
        self.tokenized_text = SentimentAnalyser.filter_and_tokenise(
                    SentimentAnalyser.clean_text(self.input_text, 
                                        self.contractions), self.stopwords)

    def predict_(self):
        if not self.tokenized_text:
            print ("Invalid, no tokenized text available")
            
        else:
            try:
                self.vector_representation = self.vector_representation = SentimentAnalyser.get_Pmean_vector(self.tokenized_text, self.embedding_dict, self.p_list)
                self.vector_representation = self.vector_representation.reshape(1,300*len(self.p_list))
                self.prediction = self.model.predict(self.vector_representation)
            except:
                print ("Failure; No word representation available")

    #---------------------#
    #---Preprocessing-----#
    #---------------------#
    
    @staticmethod
    def to_ascii (text):
        
        ret = ''
        for char in text:
            if char in "!\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ":
                ret+=char
            else:
                ret+=" "+char
        return ret
    
    @staticmethod
    def clean_text(text, contractions):
        
        if type(text)==str:
            
            # Add closest word 
             
            text = SentimentAnalyser.to_ascii(text)
            text = text.lower()
    
            text = text.replace(";"," ") 
            text = text.replace("&"," and ")
    
            text = re.sub("[?!]+",".",text) # should these be filtered out?
            text = re.sub("@[\w]*"," ",text)
            text = re.sub("\#[\w]*"," ",text)
            text = re.sub("http:[^ ]*"," ",text)
            text = re.sub("[\.]+",".",text)
            text = re.sub("[()]"," ",text)
            text = re.sub("[\s]+"," ",text)
            text = re.sub("[y]{2,}","y",text)
            text = re.sub("[r]{2,}","r",text)
            for ch in "abcdefghijklmnopqrstuvwxyz":
                rep_pattern = "[" + ch + "]{3,}"
                text = re.sub(rep_pattern, ch, text) 
            
            text = re.sub("\."," ",text) #Only for single sentences 
    
            for contraction in contractions.keys():
                contraction_alpha = " "+ "".join(re.findall("[a-zA-Z]+", contraction))+" "
                text = text.replace(contraction,contractions[contraction]) 
                text = text.replace(contraction_alpha," " + contractions[contraction] + " ") 
            
            text = text.replace(" ta "," ") 
            text = text.replace(" quot "," ") 
            
            return text
        
    @staticmethod
    def filter_and_tokenise(sent, stopwords):
        res_sent = []
        for word in word_tokenize(sent):
            if word not in stopwords and word.isalpha() and len(word)>1:
                res_sent.append(word)

        return res_sent

    #---------------------------#
    #---Using Trained Model-----#
    #---------------------------#
    
    @staticmethod
    def get_mean_vector(tweet, dict_of_vecs):
        # remove out-of-vocabulary words
        if (len(tweet)==0):
            return None
        
        list_of_vecs = []
        
        
        for word in tweet:
            try:
                list_of_vecs.append(dict_of_vecs[word])
            except KeyError:
                continue
        return np.array(np.mean(list_of_vecs, axis = 0))
    
    @staticmethod
    def get_Pmean_vector(tweet, dict_of_vecs, p_list = [1,3,5]):
    # remove out-of-vocabulary words
        if (len(tweet)==0):
            return None
        
        list_of_vecs = []
        
        for word in tweet:
            try:
                list_of_vecs.append(dict_of_vecs[word])
            except KeyError:
                continue
        
        if (len(list_of_vecs)==0):
            return None

        all_p_means_vec = []
        for p in p_list:
            curr_p_means_vec = []
            for vec in list_of_vecs:
                curr_p_means_vec.append(SentimentAnalyser.p_power(vec, p))
                
            curr_p_means_vec = np.array(np.mean(curr_p_means_vec,axis=0))
            curr_p_means_vec = SentimentAnalyser.p_power(curr_p_means_vec, 1/p)
            
            all_p_means_vec.extend(curr_p_means_vec)
            
        return np.array(all_p_means_vec)
    
    @staticmethod       
    def p_power (single_vector, p):
        signs = np.sign (single_vector)
        single_vector = np.power(np.abs(single_vector),p)
        return single_vector*signs
        
