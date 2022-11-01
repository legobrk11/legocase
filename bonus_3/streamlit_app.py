import sys
import asyncio
import time
import httpx 
import pprint
import pandas as pd
import streamlit as st
import numpy as np
from urllib.parse import urljoin
from functools import reduce

sys.path.insert(0,'.')
from pokeapi import helpers as ph

BASE_URL= "https://pokeapi.co/api/v2/"
VERSIONS_OF_INTEREST = ['red', 'blue', 'leafgreen', 'white']

st.title('Pokemon App')

async def main(target_pokemon=[]):
    client = httpx.AsyncClient()
    tasks = []
    for p in target_pokemon:
        tasks.append(asyncio.ensure_future(ph.get_default_pokemon(client, pokemon_species=p)))
        
    pokemon_raw_json = await asyncio.gather(*tasks)
    _ = client.aclose()
    return pokemon_raw_json

@st.cache()
def load_master_df():

    pokemon_species = []

    for vn in VERSIONS_OF_INTEREST:
        with httpx.Client(base_url=BASE_URL) as client:
            version_id, version_group = ph.get_version_id_and_version_group(client=client, version_name=vn)
            version_group_pokedexs = ph.get_version_group_pokedexs(client=client, version_group_name=version_group)
            for pokedex in version_group_pokedexs:
                pokemon_species.append(ph.get_pokemon_species(client=client, pokedex_name=pokedex))

    unique_target_pokemon = set(ph.flatten_list(pokemon_species)) 

    pokemon_raw_json = asyncio.run(main(target_pokemon=unique_target_pokemon))

    raw_df = pd.DataFrame(pokemon_raw_json)
    raw_df['slot_1'] = raw_df['types'].str[0].str['type'].str['name']
    raw_df['slot_2'] = raw_df['types'].str[1].str['type'].str['name']

    raw_df['body_mass_index'] = (raw_df['weight'] / raw_df['height']).round(2)

    raw_df['name'] = raw_df['name'].str.title()

    raw_df['front_default_sprite_url'] = raw_df['sprites'].str['front_default']

    columns_subset = ["name", "id", "base_experience", "weight", "height", "body_mass_index", "order", "slot_1", "slot_2", "front_default_sprite_url"]

    df = raw_df[columns_subset].sort_values('order')

    df = df.rename(columns={
            "height": "Height (decimetres)",
            "weight": "Weight (hectograms)",
            "body_mass_index": "Body Mass Index",
            "slot_1": "Slot 1",
            "slot_2": "Slot 2",
            "base_experience": 'Base Experience',
            "order":"Order",
            "name":"Name"
        }
    )

    
    df["Slot 2"] = df["Slot 2"].replace({np.nan:''})
    return df


master_df = load_master_df()


selected_pokemon = st.selectbox(label='select a Pokemon:', options=master_df["Name"])

selected_pokemon_df = master_df.loc[master_df['Name'] == selected_pokemon]

col1, col2 = st.columns(2)

with col1:
    st.image(
                selected_pokemon_df['front_default_sprite_url'].item(),
                width=300,
            )
with col2:
    summary_card_cols = ['Name', 'id', "Order", 'Base Experience', "Height (decimetres)", 
    "Weight (hectograms)",  "Body Mass Index", "Slot 1", "Slot 2", ]
    card_df = selected_pokemon_df[summary_card_cols].T
    card_df.columns=['Data']
    st.dataframe(card_df, width=400)