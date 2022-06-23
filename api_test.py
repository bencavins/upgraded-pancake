import requests


response = requests.get("https://pokeapi.co/api/v2/pokemon/pikachu")
data = response.json()