import json
from os import listdir
from os.path import isfile, join, splitext
from typing import Dict

from third_party.poeditor.client import PoeditorClient

def dict_to_poeditor_locale(data: Dict[str, Dict], locale: str):
    '''
    [
        {
            "term": "app.name",
            "definition": "TODO List"
        }
    ]
    '''
    return [{"term": term, "definition": translation} for term, translation in data[locale].items()]

async def pull_translations(poeditor_id: int, poeditor_token: str,):
    translations = {}

    async with PoeditorClient(poeditor_token, poeditor_id,) as client:
        langs = await client.get_available_languages()
        if (langs):
            for lang in langs.result.languages:
                translation_file = await client.get_language_file_url(lang.code)
                if (translation_file):
                    translation = await client.download_translation_file(translation_file.result.url)
                    if translation:
                        translations[lang.code] = json.loads(translation)

    return translations


async def load_translations_from_file():
    translations = {}

    path = 'locales/import'
    for f in (f for f in listdir(path) if isfile(join(path, f))):
        ff = open(join(path, f), 'r')
        translations[splitext(f)[0]] = json.loads(ff.read())

    return translations

