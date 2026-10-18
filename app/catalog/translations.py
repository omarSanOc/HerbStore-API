CATEGORY_NAMES = {
    "vitamins": ("Vitamins", "Vitaminas"),
    "minerals": ("Minerals", "Minerales"),
    "protein": ("Protein", "Proteína"),
    "botanicals": ("Botanicals", "Botánicos"),
    "wellness": ("Wellness", "Bienestar"),
}

SUBCATEGORY_NAMES = {
    "multivitamins": ("Multivitamins", "Multivitamínicos"),
    "vitamin-c": ("Vitamin C", "Vitamina C"),
    "vitamin-d": ("Vitamin D", "Vitamina D"),
    "magnesium": ("Magnesium", "Magnesio"),
    "zinc": ("Zinc", "Zinc"),
    "calcium": ("Calcium", "Calcio"),
    "plant-protein": ("Plant Protein", "Proteína vegetal"),
    "whey-protein": ("Whey Protein", "Proteína de suero"),
    "amino-blends": ("Amino Blends", "Mezclas de aminoácidos"),
    "herbal-blends": ("Herbal Blends", "Mezclas herbales"),
    "mushroom-blends": ("Mushroom Blends", "Mezclas de hongos"),
    "root-extracts": ("Root Extracts", "Extractos de raíces"),
    "probiotics": ("Probiotics", "Probióticos"),
    "omegas": ("Omegas", "Omegas"),
    "sleep-support": ("Sleep Support", "Apoyo para el sueño"),
}

FORMAT_TRANSLATIONS = {
    "Capsules": "Cápsulas",
    "Powder": "Polvo",
    "Tablets": "Tabletas",
    "Softgels": "Cápsulas blandas",
}

SERVING_TRANSLATIONS = {
    "2 capsules": "2 cápsulas",
    "1 scoop (20 g)": "1 medida (20 g)",
    "1 tablet": "1 tableta",
    "2 softgels": "2 cápsulas blandas",
}


def product_name_es(name: str) -> str:
    translated = name
    for source, target in FORMAT_TRANSLATIONS.items():
        if translated.endswith(source):
            translated = f"{translated.removesuffix(source).strip()} {target}"
            break
    return translated


def product_description_es(name: str) -> str:
    return f"{product_name_es(name)} para una rutina diaria de bienestar sencilla."
