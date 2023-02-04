import psycopg2
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()


def create_candidate(user_id: int, name: str, birth: date, gender: str, is_quota_holder: bool, specialty: str) -> None:
    conn = get_connection()
    cur = conn.cursor()

    sql = "INSERT INTO candidate(id, name, birth, gender, is_quota_holder, specialty) VALUES(%s, %s, %s, %s, %s, %s)"
    cur.execute(sql, (user_id, name, birth, gender, is_quota_holder, specialty))

    conn.commit()

    cur.close()
    conn.close()


def create_general_result(user_id: int, port_avg: float, math_avg: float, hist_geo_avg: float,
                          eng_avg: float, final_avg: float) -> None:
    conn = get_connection()
    cur = conn.cursor()

    sql = '''INSERT INTO general_result(user_id, port_avg, math_avg, hist_geo_avg, eng_avg, final_avg) 
    VALUES(%s, %s, %s, %s, %s, %s)'''

    cur.execute(sql, (user_id, port_avg, math_avg, hist_geo_avg, eng_avg, final_avg))

    conn.commit()

    cur.close()
    conn.close()


def get_candidate_result(user_id: int):
    conn = get_connection()
    cur = conn.cursor()

    sql = 'SELECT specialty FROM candidate WHERE id=%s'
    cur.execute(sql, (user_id, ))

    specialty = cur.fetchone()[0]

    if specialty == 'G':
        sql = '''SELECT port_avg, math_avg, hist_geo_avg, eng_avg, final_avg 
        FROM general_result 
        WHERE user_id=%s'''

    elif specialty == 'S':
        sql = '''SELECT port_avg, math_avg, hist_geo_avg, eng_avg, final_avg, specific_avg 
        FROM health_result 
        WHERE user_id=%s'''

    else:
        return

    cur.execute(sql, (user_id, ))

    user_result: list = list(cur.fetchone())
    print(user_result)
    user_result.insert(0, specialty)

    conn.commit()

    cur.close()
    conn.close()

    return user_result


def create_health_result(user_id: int, port_avg: float, math_avg: float, hist_geo_avg: float,
                         eng_avg: float, specific_avg: float, final_avg: float) -> None:
    conn = get_connection()
    cur = conn.cursor()

    sql = '''INSERT INTO health_result(user_id, port_avg, math_avg, hist_geo_avg, eng_avg, specific_avg, final_avg) 
    VALUES(%s, %s, %s, %s, %s, %s, %s)'''

    cur.execute(sql, (user_id, port_avg, math_avg, hist_geo_avg, eng_avg, specific_avg, final_avg))

    conn.commit()

    cur.close()
    conn.close()


def get_all_results() -> list:
    conn = get_connection()
    cur = conn.cursor()

    sql = '''SELECT * FROM general_result'''
    cur.execute(sql)

    rows = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return rows


def is_candidate_already_registered(user_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    sql = 'SELECT exists(SELECT 1 FROM general_result WHERE user_id=%s)'
    cur.execute(sql, (user_id, ))

    first_result: bool = cur.fetchone()[0]
    print(first_result)

    sql = 'SELECT exists(SELECT 1 FROM health_result WHERE user_id=%s)'
    cur.execute(sql, (user_id, ))

    second_result: bool = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return first_result or second_result


def update_general_result(user_id: int, port_avg: float, math_avg: float, hist_geo_avg: float,
                          eng_avg: float, final_avg: float) -> int:
    conn = get_connection()
    cur = conn.cursor()

    sql: str = '''UPDATE general_result 
    SET port_avg=%s, math_avg=%s, hist_geo_avg=%s, eng_avg=%s, final_avg=%s 
    WHERE user_id=%s'''

    cur.execute(sql, (port_avg, math_avg, hist_geo_avg, eng_avg, final_avg, user_id))

    updated_rows: int = cur.rowcount

    conn.commit()

    cur.close()
    conn.close()

    return updated_rows


def update_health_result(user_id: int, port_avg: float, math_avg: float, hist_geo_avg: float,
                         eng_avg: float, specific_avg: float, final_avg: float) -> int:
    conn = get_connection()
    cur = conn.cursor()

    sql: str = '''UPDATE health_result 
    SET port_avg=%s, math_avg=%s, hist_geo_avg=%s, eng_avg=%s, specific_avg=%s, final_avg=%s 
    WHERE user_id=%s'''

    cur.execute(sql, (port_avg, math_avg, hist_geo_avg, eng_avg, specific_avg, final_avg, user_id))

    updated_rows: int = cur.rowcount

    conn.commit()

    cur.close()
    conn.close()

    return updated_rows


def get_general_men_ranking() -> list:
    conn = get_connection()
    cur = conn.cursor()

    sql = ('SELECT c.name, r.final_avg, r.port_avg, r.math_avg, r.hist_geo_avg, r.eng_avg, '
           'to_char(c.birth, \'DD/MM/YYYY\'), '
           'CASE WHEN is_quota_holder=true THEN \'SIM\' ELSE \'\' END AS Cotista '
           'FROM candidate c '
           'JOIN general_result r '
           'ON c.id = r.user_id '
           'WHERE c.gender = \'M\''
           'ORDER BY r.final_avg DESC, r.port_avg DESC, '
           'r.math_avg DESC, r.hist_geo_avg DESC, r.eng_avg DESC, c.birth')

    cur.execute(sql)
    result = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return result


def get_general_quota_men_result() -> list:
    conn = get_connection()
    cur = conn.cursor()

    sql = ('SELECT c.name, r.final_avg, r.port_avg, r.math_avg, r.hist_geo_avg, r.eng_avg, '
           'to_char(c.birth, \'DD/MM/YYYY\'), '
           'CASE WHEN c.is_quota_holder=true THEN \'SIM\' ELSE \'\' END AS Cotista '
           'FROM candidate c '
           'JOIN general_result r '
           'ON c.id = r.user_id '
           'WHERE c.gender = \'M\' and c.is_quota_holder=true '
           'ORDER BY r.final_avg DESC, r.port_avg DESC, '
           'r.math_avg DESC, r.hist_geo_avg DESC, r.eng_avg DESC, c.birth')

    cur.execute(sql)
    result = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return result


def get_general_quota_woman_result() -> list:
    conn = psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'))
    cur = conn.cursor()

    sql = ('SELECT c.name, r.final_avg, r.port_avg, r.math_avg, r.hist_geo_avg, r.eng_avg, '
           'to_char(c.birth, \'DD/MM/YYYY\'), '
           'CASE WHEN c.is_quota_holder=true THEN \'SIM\' ELSE \'\' END AS Cotista '
           'FROM candidate c '
           'JOIN general_result r '
           'ON c.id = r.user_id '
           'WHERE c.gender = \'F\' and c.is_quota_holder=true '
           'ORDER BY r.final_avg DESC, r.port_avg DESC, '
           'r.math_avg DESC, r.hist_geo_avg DESC, r.eng_avg DESC, c.birth')

    cur.execute(sql)
    result = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return result


def get_general_woman_result() -> list:
    conn = get_connection()
    cur = conn.cursor()

    sql = ('SELECT c.name, r.final_avg, r.port_avg, r.math_avg, r.hist_geo_avg, r.eng_avg, '
           'to_char(c.birth, \'DD/MM/YYYY\'), '
           'CASE WHEN is_quota_holder=true THEN \'SIM\' ELSE \'\' END AS Cotista '
           'FROM candidate c '
           'JOIN general_result r '
           'ON c.id = r.user_id '
           'WHERE c.gender = \'F\''
           'ORDER BY r.final_avg DESC, r.port_avg DESC, '
           'r.math_avg DESC, r.hist_geo_avg DESC, r.eng_avg DESC, c.birth')

    cur.execute(sql)
    result = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return result


def get_health_result() -> list:
    conn = get_connection()
    cur = conn.cursor()

    sql = ('SELECT c.name, r.final_avg, r.specific_avg, r.port_avg, r.math_avg, r.hist_geo_avg, r.eng_avg, '
           'to_char(c.birth, \'DD/MM/YYYY\'), '
           'CASE WHEN is_quota_holder=true THEN \'SIM\' ELSE \'\' END AS Cotista '
           'FROM candidate c '
           'JOIN health_result r '
           'ON c.id = r.user_id '
           'ORDER BY r.final_avg DESC, r.specific_avg DESC, r.port_avg DESC, '
           'r.math_avg DESC, r.hist_geo_avg DESC, r.eng_avg DESC, c.birth')

    cur.execute(sql)
    result = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return result


def get_connection():
    return psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'))
