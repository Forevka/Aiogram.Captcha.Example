from config import Lang


class TranslationHolder:
    def __init__(
        self,
        translations: dict,
        lang_id: int,
    ):
        self.lang_id = lang_id
        self.lang_code = Lang(lang_id).name
        self.terms_dict = dict(translations[self.lang_code])  # copy terms

    def get(self, key):
        translation = self.terms_dict[key]
        if not translation:
            return f"No translation defined\nIf you see this message please contact with support"
        return translation

    def __getitem__(self, item):
        return self.get(item)
