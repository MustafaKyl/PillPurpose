import pandas as pd
import numpy as np
from google.cloud import vision
from google.oauth2.service_account import Credentials
import streamlit as st
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import json

credentials = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

client = vision.ImageAnnotatorClient(credentials=credentials)


pd.set_option("display.max_columns",1000)
pd.set_option("display.width",500)
pd.set_option("display.max_rows",50)
#df = pd.read_csv("drug_information.csv")
#df.dropna(inplace=True)
#df.isnull().sum()
#df.drop("Unnamed: 0", axis=1, inplace=True)
#df["condition"].unique()
#df.drop(df.loc[df["condition"].str.contains("</span>")].index, inplace=True)
#df.loc[df["condition"].str.contains("</span>"), "condition"].count()
#df = df[["drugName", "condition"]]
#df.to_csv("clean_drug_information.csv")
#df= df.drop_duplicates(subset="drugName")
#df["drugName"] = df["drugName"].apply(lambda x:x.lower())
#df.to_csv("uniqueDrugInformation.csv")


df = pd.read_csv("uniqueDrugInformation.csv")
df.drop("Unnamed: 0", axis=1, inplace=True)
downloadImage = st.file_uploader("Bir resim yükleyin")


if downloadImage is not None:
    st.image(downloadImage.getvalue())

    image = vision.Image(content=downloadImage.getvalue())

    response = client.text_detection(image=image)
    texts = response.text_annotations


    if texts:
        print(f"Tanımlanan metin: {texts[0].description}")
    else:
        print("Hiçbir metin tespit edilemedi.")

    text = texts[0].description


    condition =df.loc[(df["drugName"].apply(lambda x: x.lower() in text.lower())) &
                      (~df["condition"].str.contains("Not Listed")), "condition"].unique()[0]

    translated_condition = GoogleTranslator(source="en", target="tr").translate(condition)

    st.title("Kullanım Amacı: " + translated_condition)


    def get_side_effects(drug_name):
        url = f"https://www.drugs.com/{drug_name}.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        start_point = soup.find(id="uses")
        end_point = soup.find(class_="ddc-related-link-group")

        # Başlangıç noktasından sonraki tüm kardeş öğeleri al
        content = []
        for sibling in start_point.find_next_siblings():
            if sibling == end_point:
                break  # Bitiş noktasına geldiğinde döngüyü sonlandır
             #Metin yerine ham HTML'yi al

            for a_tag in sibling.find_all('a'):
                a_tag.unwrap()
            content.append(str(sibling))
                # Sonuçları birleştir
        result = "\n".join(content)
        return result



    drug_name = df.loc[df["drugName"].apply(lambda x:x.lower() in text.lower()),"drugName"].iloc[0]
    side_effects = get_side_effects(drug_name)
    #5000 karakter sınırı olduğu için 2 parçaya bölüp öyle çeviriyorum
    translated_content = GoogleTranslator(source='en', target='tr').translate(side_effects[:4000])
    translated_content2 = GoogleTranslator(source="en", target="tr").translate(side_effects[4000:])

    st.header(drug_name.title() + " nedir")

    #html etiketlerini uygulamak için unsafe_allow_html=True yapıyorum
    st.write(translated_content + translated_content2, unsafe_allow_html=True)




