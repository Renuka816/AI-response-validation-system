from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_similarity(vec1, vec2):
    similarity = cosine_similarity([vec1], [vec2])[0][0]
    return round(float(similarity), 4)

def normalize_score(value):
    return round(value * 100, 2)