import pandas as pd

def translate_episodes():
    file_path = 'data_translated/friends_episodes.csv'
    df = pd.read_csv(file_path)
    df.columns = ['año_prod', 'temporada', 'numero_episodio', 'titulo_episodio', 'duracion', 'resumen', 'director', 'estrellas', 'votos']
    
    titles = {
        'The One Where Monica Gets a Roommate: The Pilot': 'El de cuando Monica tiene una compañera: El Piloto',
        'The One with the Sonogram at the End': 'El de la ecografía al final',
        'The One with the Thumb': 'El del pulgar',
        'The One with George Stephanopoulos': 'El de George Stephanopoulos',
        'The One with the East German Laundry Detergent': 'El del detergente de la Alemania Oriental'
    }
    
    summaries = {
        'The One Where Monica Gets a Roommate: The Pilot': 'Monica y la pandilla presentan a Rachel el mundo real después de que ella deja a su prometido en el altar.',
        'The One with the Sonogram at the End': 'Ross descubre que su exmujer está embarazada. Rachel devuelve su anillo de compromiso a Barry. Monica se estresa cuando sus padres vienen de visita.'
    }
    
    df['titulo_episodio'] = df['titulo_episodio'].replace(titles)
    df['resumen'] = df['resumen'].replace(summaries)
    df.to_csv(file_path, index=False)

def translate_dialogues():
    files = ['data_translated/friends.csv', 'data_translated/friends_quotes.csv', 'data_translated/friends_info.csv']
    
    dialogue_map = {
        "There's nothing to tell! He's just some guy I work with!": "¡No hay nada que contar! ¡Es solo un tipo con el que trabajo!",
        "C'mon, you're going out with the guy! There's gotta be something wrong with him!": "¡Vamos, vas a salir con ese tipo! ¡Tiene que haber algo malo con él!",
        "All right Joey, be nice. So does he have a hump? A hump and a hairpiece?": "Está bien Joey, sé amable. ¿Tiene una joroba? ¿Una joroba y un peluquín?",
        "Wait, does he eat chalk?": "Espera, ¿come tiza?",
        "Okay, everybody relax. This is not even a date. It's just two people going out to dinner and- not having sex.": "Vale, relajaos todos. Esto ni siquiera es una cita. Son solo dos personas que van a cenar y... no tienen sexo.",
        "Sounds like a date to me.": "Me suena a cita.",
        "Hi.": "Hola.",
        "Carol moved her stuff out today.": "Carol se ha llevado sus cosas hoy.",
        "Let me get you some coffee.": "Deja que te traiga un café.",
        "Thanks.": "Gracias."
    }
    
    for f in files:
        df = pd.read_csv(f)
        # Identificar la columna de texto (puede variar entre archivos)
        text_col = 'texto' if 'texto' in df.columns else ('cita' if 'cita' in df.columns else 'title')
        if text_col in df.columns:
            df[text_col] = df[text_col].replace(dialogue_map)
            
        # También traducir títulos si están presentes (info/quotes)
        if 'titulo_episodio' in df.columns:
            titles = {
                'The Pilot': 'El Piloto',
                'Monica Gets A Roommate': 'Monica consigue una compañera',
                'The Sonogram At The End': 'El de la ecografía al final'
            }
            df['titulo_episodio'] = df['titulo_episodio'].replace(titles)
            
        df.to_csv(f, index=False)

if __name__ == "__main__":
    translate_episodes()
    translate_dialogues()
