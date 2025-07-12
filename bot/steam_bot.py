import os
import time
import requests
import mysql.connector
import logging
import sys
import traceback

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Получение переменных окружения
def get_env_vars():
    config = {
        'api_key': os.getenv('STEAM_API_KEY'),
        'appid': os.getenv('APP_ID', '570'),
        'db_host': os.getenv('DB_HOST'),
        'db_user': os.getenv('DB_USER'),
        'db_password': os.getenv('DB_PASSWORD'),
        'db_name': os.getenv('DB_NAME'),
        'interval': int(os.getenv('INTERVAL_MINUTES', '5')) * 60
    }
    
    # Проверка обязательных переменных
    required_vars = ['api_key', 'db_host', 'db_user', 'db_password', 'db_name']
    missing = [var for var in required_vars if not config[var]]
    
    if missing:
        logging.error(f"Missing required environment variables: {', '.join(missing)}")
        exit(1)
        
    return config

# Запрос к Steam API
def get_player_count(api_key, appid):
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
    params = {
        'key': api_key,
        'appid': appid
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'response' in data and 'player_count' in data['response']:
            return {
                'success': True,
                'count': data['response']['player_count']
            }
        else:
            return {
                'success': False,
                'error': f"Invalid API response: {data}"
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Request failed: {str(e)}"
        }
    except ValueError as e:
        return {
            'success': False,
            'error': f"JSON decode error: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }

# Сохранение в базу данных
def save_to_db(data, config):
    conn = None
    try:
        conn = mysql.connector.connect(
            host=config['db_host'],
            user=config['db_user'],
            password=config['db_password'],
            database=config['db_name']
        )
        cursor = conn.cursor()
        
        if data['success']:
            query = """
                INSERT INTO steam_stats (appid, player_count)
                VALUES (%s, %s)
            """
            values = (config['appid'], data['count'])
        else:
            query = """
                INSERT INTO steam_stats (appid, player_count, error_message)
                VALUES (%s, NULL, %s)
            """
            values = (config['appid'], data['error'][:255])
        
        cursor.execute(query, values)
        conn.commit()
        logging.info("Data saved to DB" if data['success'] else "Error saved to DB")
        
    except mysql.connector.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"General error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Основной цикл с системой перезапуска
def main():
    while True:  # Внешний цикл для полного перезапуска
        try:
            config = get_env_vars()
            
            logging.info("Starting Steam monitoring bot")
            logging.info(f"Monitoring AppID: {config['appid']}")
            logging.info(f"Update interval: {config['interval'] // 60} minutes")
            
            # Внутренний рабочий цикл
            while True:
                try:
                    logging.info("Fetching player count...")
                    data = get_player_count(config['api_key'], config['appid'])
                    
                    if data['success']:
                        logging.info(f"Current players: {data['count']}")
                    else:
                        logging.error(f"API error: {data['error']}")
                    
                    save_to_db(data, config)
                    logging.info(f"Sleeping for {config['interval']} seconds")
                    time.sleep(config['interval'])
                    
                except KeyboardInterrupt:
                    logging.info("Bot stopped by user")
                    return  # Выход из программы
                except Exception as e:
                    logging.error(f"Error in main loop: {str(e)}")
                    logging.debug(traceback.format_exc())
                    logging.info("Restarting main loop after 60 seconds")
                    time.sleep(60)  # Пауза перед перезапуском цикла
                    
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
            return  # Выход из программы
        except Exception as e:
            logging.critical(f"Critical error: {str(e)}")
            logging.debug(traceback.format_exc())
            logging.info("Attempting full restart in 60 seconds")
            time.sleep(60)  # Пауза перед полным перезапуском

if __name__ == "__main__":
    main()