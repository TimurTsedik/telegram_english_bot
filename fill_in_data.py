import psycopg2


with psycopg2.connect(database="Telegram_English", user="postgres", password="postgres") as conn:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO e_words (word)
            VALUES 
            ('Car'),
            ('Green'),
            ('White'),
            ('Peace'),
            ('Apple'),
            ('Orange'),
            ('Water'),
            ('Milk'),
            ('Banana'),
            ('Hello'),
            ('World')
            ;
        """)
        cur.execute("""
            INSERT INTO r_words (word)
            VALUES 
            ('Машина'),
            ('Зеленый'),
            ('Белый'),
            ('Мир'),
            ('Яблоко'),
            ('Апельсин'),
            ('Вода'),
            ('Молоко'),
            ('Банан'),
            ('Привет')
            ;
        """)
        cur.execute("""
            INSERT INTO e_r_words (e_word_id, r_word_id)
            VALUES 
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 4)
            ;
        """)
        conn.commit()
