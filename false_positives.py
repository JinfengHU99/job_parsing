import openai
import pandas as pd
from settings import API_KEY_OPENAI

def delete_no_freelance(df):
    df_freelance = df[df['job-type'].str.contains('freelance', case=False)]
    return df_freelance.reset_index(drop=True)

class CyberProcessor:
    def __init__(self):
        self.conversation_list = []
        openai.api_key = API_KEY_OPENAI

    def train(self, instructions):
        # Train ChatGPT based on provided instructions
        instructions = "Tu es un expert en catégorisation d'annonce pour le site Cyberfreelance.fr. Ton rôle est d'enlever des annonces en faux positif, c'est-à-dire qui ne sont pas dans le domaine de cyber sécurité. En général, vous pouvez les identifier selon les titres des postes des annonces"
        self.conversation_list.append({"role": "user", "content": instructions})        
        response = openai.ChatCompletion.create(model="gpt-4-turbo-preview", messages=self.conversation_list)
    
    def is_cyber_security_job(self, job_title):
        prompt = f"Est-ce que ce poste est lié à la cybersécurité ? Titre du poste : {job_title}"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=50,
            language="fr"
        )

        return 'oui' in response['choices'][0]['text'].lower()


    def delete_no_cyber(self, data):
       filtered_ads = [ad for ad in data if self.is_cyber_security_job(ad['job-title'])]
       return pd.DataFrame(filtered_ads)

    
