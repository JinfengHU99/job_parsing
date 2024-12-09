import pandas as pd
import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import settings

# Load spacy model for text processing
nlp = spacy.load("fr_core_news_sm")

def remove_stopwords(text):
    # Function to remove stopwords from text
    doc = nlp(text)
    filtered_tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(filtered_tokens)

def remove_html(html_content):
    # Function to remove HTML tags from content
    cleaned_text = re.sub(r'</?\w+[^>]*>','', html_content)
    cleaned_text = re.sub(r'<br>','', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    return cleaned_text.strip()

def remove_gender(title):
    # Function to remove gender information from job title
    title_clean = re.sub(r'[ ]?[(]?[HhFf][/]?[HhFf][)]?[ ]?', '', title)
    return title_clean

def detect_duplicate(df):
    # Function to detect and remove duplicate job titles
    threshold = 0.9
    duplicates_to_drop = set()
    for i in range(len(df)):
        for j in range(i+1, len(df)):
            title_i = remove_gender(str(df.iloc[i]["job-title"]).lower())
            title_j = remove_gender(str(df.iloc[j]["job-title"]).lower())
            if title_i == title_j:                   
                desc1_clean = df.iloc[i]["job-description-html"]
                desc2_clean = df.iloc[j]["job-description-html"]
                vectorizer = CountVectorizer().fit_transform([desc1_clean, desc2_clean])
                vectors = vectorizer.toarray()
                similarity = cosine_similarity(vectors)
                if similarity[0][1] >= threshold:                        
                    # Concatenate
                    if str(df.at[i, "platform"]) != str(df.at[j, "platform"]):
                        df.at[i, "job-url"] += '\n' + df.at[j, "job-url"]
                        df.at[i, "import-date"] += '\n' + df.at[j, "import-date"]
                        df.at[i, "platform"] += '\n' + df.at[j, "platform"]
                    duplicates_to_drop.add(j)

    # Drop rows marked for deletion
    df.drop(index=duplicates_to_drop, inplace=True)
    df.reset_index(drop=True, inplace=True)  # Reset index after dropping rows

    return df
