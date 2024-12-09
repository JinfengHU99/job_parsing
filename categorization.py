import openai
from settings import API_KEY_OPENAI

class ChatGPT:
    def __init__(self):
        # Initialize conversation list
        self.conversation_list = []

    def train(self, instructions):
        # Train ChatGPT based on provided instructions
        instructions = "Tu es un expert en catégorisation d'annonce pour le site Cyberfreelance.fr. Ton rôle est d'identifier la catégorie de l'annonce présentée qui se rapproche le plus à la liste suivante :\"Administrateur SSI, Analyste N1, Analyste N2, Analyste N3, Analyste SOC, Architecte cybersécurité, Architecte SOC, Assistant RSSI, Auditeur SSI, Avant-vente, Business Analyst SSI, Chef de Projet, Cloud Security Architecte, Consultant AMOA, Consultant RGPD / DPO, Consultant Sécurité Industrielle, Consultant SSI, Consultant IAM, Développeur Cyber, DevOpsDPO, Expert IAM, Expert PRA / PCA, Expert réseau, Expert sécurité des IOT, Expert SOAR, Expert Threat Intel, Formateur cyber, Head of SOC, Incident Manageur, Ingénieur Cybersecurité, Ingénieur.e support SSI, IntégrateurIR & Forensics, Manageur SSI, Pentesteur, PMO Cyber, RSSI\". Chaque fois quand je te donne une annonce, donne-moi en réponse uniquement la catégorie identifiée. Si tu la trouve pas, propose une catégorie, mais elle ne doit pas être générique.."
        self.conversation_list.append({"role": "user", "content": instructions})
        openai.api_key = API_KEY_OPENAI
        response = openai.ChatCompletion.create(model="gpt-4-turbo-preview", messages=self.conversation_list)

    def respond(self, title, description):
        # Get response from ChatGPT based on the given prompt
        prompt = f"Title: {title}\nDescription: {description}"
        self.conversation_list.append({"role": "user", "content": prompt})
        openai.api_key = API_KEY_OPENAI
        response = openai.ChatCompletion.create(model="gpt-4-turbo-preview", messages=self.conversation_list)
        answer = response.choices[0].message['content']
        
        return answer.strip()

def generate_categories(data):
    # Initialize ChatGPT
    chatbot = ChatGPT()
    
    # Train ChatGPT with instructions
    chatbot.train("instructions")
    
    # Generate categories using ChatGPT
    categories = []
    for index, row in data.iterrows():
        title = row['job-title']
        description = truncate_description(row['job-description-html'])
        category = chatbot.respond(title, description)
        categories.append(category)
    
    return categories

def truncate_description(description):
    length = len(description)
    truncated_description = description[:length//4]
    return truncated_description
