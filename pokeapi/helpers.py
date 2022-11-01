import httpx

def flatten_list(l):
    """Flatten list of lists to a single list"""
    return [item for sublist in l for item in sublist]

def get_version_id_and_version_group(client: httpx.Client, version_name: str) -> tuple[str,int]:
    """For a given Pokemon game name return it's ID"""
    r = client.get(f"/version/{version_name}")
    assert r.status_code == 200, f"error calling /version. Code {r.status_code}"
    json_response = r.json()
    result = json_response['id'], json_response["version_group"]["name"]
    return result

def get_version_group_pokedexs(client: httpx.Client, version_group_name: str) -> str:
    """for a given pokemon version name, return it's associated pokedexs"""
    r = client.get(f"/version-group/{version_group_name}")
    assert r.status_code == 200, f"error calling /version_group. Code {r.status_code}"
    result = [n['name'] for n in r.json()['pokedexes']]
    return result

def get_pokemon_species(client: httpx.Client, pokedex_name: str) -> list[str]:
    r = client.get(f"/pokedex/{pokedex_name}")
    assert r.status_code == 200, f"error calling /pokedex. Code {r.status_code}"
    return [p['pokemon_species']['name'] for p in r.json()['pokemon_entries']]

async def get_default_pokemon(client, pokemon_species: str):
    species_resp = await client.get(f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_species}')
    species_result = species_resp.json()

    default_pokemon_name = [v for v in species_result['varieties'] if v['is_default'] is True][0]['pokemon']['name']

    pokemon_resp = await client.get(f'https://pokeapi.co/api/v2/pokemon/{default_pokemon_name}')
    pokemon_result = pokemon_resp.json()
    return pokemon_result