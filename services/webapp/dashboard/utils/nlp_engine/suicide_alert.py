#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 13:00:43 2019

@author: adithyavh
"""


import numpy as np
import pickle
import os

# extra = '/dashboard/npl_engine'

# path = os.getcwd()

# src_path = path[:len(path) - len(extra)] + '/data'
# print(src_path)

# os.chdir(src_path)
loaded_dict = pickle.load(open("/Users/nguyengiang/workspace/singagpore_india_hackathon/services/webapp/data/twitter_vectors.pkl","rb"))
# os.chdir(path)

from scipy.spatial.distance import cosine

def get_mean_vec(tokenised_tweet, dict_of_vecs):
    
    if (len(tokenised_tweet)==0):
        return None
        
    list_of_vecs = []
    
    for word in tokenised_tweet:
        try:
            list_of_vecs.append(dict_of_vecs[word])
        except KeyError:
            continue

    if (len(list_of_vecs)==0):
        return None
    
    return np.array(np.mean(list_of_vecs, axis=0))

def get_self_harm(tokenised_tweet, dict_of_vecs=loaded_dict):
    
    vector = get_mean_vec(tokenised_tweet, dict_of_vecs)
    try:
        cluster_happy = ["happy","laugh","amazing","play","fun", "love", "marry", "party", "celebrate", "smile"]
        cluster_middle= ["eat", "sleep", "run", "dry", "fight", "learn", "study", "work", "pray", "hot"]
        cluster_self_harm = ["kill", "die", "suicide", "jump", "harm", "end", 'cutting', 'save']
        
        smallest_dist = 1
        self_harm = False
        for word in cluster_happy:
            dist = cosine(dict_of_vecs[word], vector)
    #        print (dist)
            if dist<=smallest_dist:
                smallest_dist = dist
                
    #    print ()
        
        for word in cluster_middle:
            dist = cosine(dict_of_vecs[word], vector)
    #        print (dist)
            if dist<=smallest_dist:
                smallest_dist = dist
    #    print ()
        
        for word in cluster_self_harm:
            dist = cosine(dict_of_vecs[word], vector)
    #        print (dist)
            if dist<=smallest_dist:
                self_harm = True
    #            print (word)
                return self_harm
        
        return self_harm
                
    except:
        return False


