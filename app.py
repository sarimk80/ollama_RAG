import ollama
from pydantic import BaseModel
import pdfplumber
import chromadb
import streamlit

data = []
table_data = []
embedd_result = ''

client = chromadb.Client()
collection = client.create_collection(name="docs")

def ask_deepseek(prompt,data):
    response = ollama.chat(
        model = 'deepseek-r1:1.5b',
        messages=[
            {
                'role':'user',
                "content":f'Using this data: {data}. Respond to this prompt: {prompt}'
            }
            
        ]
    )
    # response = ollama.generate(
    #     model='deepseek-r1:1.5b',
    #     prompt = f'Using this data: {data}. Respond to this prompt: {prompt}'
        
    # )
        
    #print(response['response'])
    print(response['message']['content'])

def prompt_input():
    prompt = "WHY SHOULD AI MEET HUMAN “STUPIDITY”?"

    prompt_embedd = ollama.embed(
        model = 'nomic-embed-text:latest',
        input = prompt
    )
    result = collection.query(
        query_embeddings=prompt_embedd['embeddings'],
        n_results=2
    )

    

    # Safely access nested data
    if result is not None \
    and 'documents' in result \
    and isinstance(result['documents'], list) \
    and len(result['documents']) > 0 \
    and isinstance(result['documents'][0], list) \
    and len(result['documents'][0]) > 0:
        data = result['documents'][0][0]
        embedd_result = ' '.join(str(item) for sublist in data for item in sublist)
        ask_deepseek(prompt,embedd_result)
        
    else:
        data = None  # or raise an error/handle missing data
    
        

def emdedd_text(text):
    for i , d in enumerate(text):

        embedd_response = ollama.embed(
            model='nomic-embed-text:latest',
            input= d
        )
        embeddings = embedd_response["embeddings"]
        collection.add(
            ids=[str(i)],
            embeddings=embeddings,
            documents=[d]
        )
        #return embedd_response['embeddings']
        prompt_input()

def chunk_text(text,chunk_size=131000):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    


with pdfplumber.open('research_paper.pdf') as pdf:
    pages = pdf.pages
    for p in pages:
        data.append(p.extract_text())
        table_data.append(p.extract_table())
    chunk_of_text = chunk_text(''.join(data))
    emdedd_text(chunk_of_text)







# response = chat(
#     model="deepseek-r1:1.5b",
#     messages=[
#         {
#             'role':'user',
#             'content':'can you update the content of the resume and make it look good'
#         },
#         {
#             'role':'assistant',
#             'content':f"{data}"
#         }
#     ],
#     options={'temperature':0}

# )

# print(response['message']['content'])