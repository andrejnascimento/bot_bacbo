from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains  # Importar ActionChains para controlar o mouse
from time import sleep
from datetime import date
from selenium.common.exceptions import TimeoutException, NoSuchElementException 
import requests
import undetected_chromedriver as uc
from dados import bot_token
from dados import chat_id
from dados import chat_id2
from dados import chat_id3


link_bacbo = 'https://www.estrelabet.com/pb/gameplay/bac-bo-ao-vivo/real-game'

def enviar_mensagem_telegram(texto, chat_id):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    dados = {
        'chat_id': chat_id,
        'text': texto
    }

    resposta = requests.post(url, data=dados)

    if resposta.status_code == 200:
        print(f'Mensagem enviada com sucesso: {texto}')
    else:
        print(f'Erro ao enviar mensagem: {resposta.status_code}, {resposta.text}')

def enviar_mensagem_telegram2(texto):
    enviar_mensagem_telegram(texto, chat_id2)

def enviar_mensagem_telegram3(texto):
    enviar_mensagem_telegram(texto, chat_id3)

options = uc.ChromeOptions()
options.add_argument('--disable-logging')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-gpu')
options.add_argument('--disable-infobars')
options.add_argument('--disable-blink-features=AutomationControlled')

# Adiciona um user-agent personalizado
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = uc.Chrome(options=options)

driver.maximize_window()

driver.get(link_bacbo)

print('Aguardando botão para aceitar cookies...')

cookies = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/app-root/div[2]/app-cookie-policy/div/div/div/span/button'))
    )
cookies.click()
print('Cookies ok.')

input('Pressione enter para continuar...')

# Captura dos iframes apenas uma vez
def capturar_iframes():
    try:
        print("Procurando pelo primeiro iframe do jogo...")
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'gamePlayIframe'))
        )
        driver.switch_to.frame(iframe)
        print('Mudou para o contexto do primeiro iframe.')

        print("Procurando pelo segundo iframe dentro do primeiro...")
        iframe2 = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[2]/iframe'))
        )
        driver.switch_to.frame(iframe2)
        print('Mudou para o contexto do segundo iframe.')

    except Exception as e:
        print(f'Erro ao capturar iframes: {e}')
        driver.save_screenshot('erro_captura_iframes.png')  # Capturar a tela para ajudar na depuração

# Chama a função para capturar os iframes uma vez no início
capturar_iframes()

# Função para verificar se o jogo está em pausa
def jogo_em_pausa():
    try:


        # Esperar até que o botão de saída da pausa seja clicável
        pause_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[11]/div[1]/button'))
        )
        
        # Clicar no botão de saída da pausa
        pause_button.click()
        
        print("Saída da pausa realizada com sucesso.")
        
        return True
    except TimeoutException:
        print('Tempo limite excedido ao esperar pelo botão de saída da pausa.')
        return False
    except Exception as e:
        print(f'Erro ao sair da pausa: {e}')
        return False

# Função para capturar os resultados do jogo
def capturar_resultado():
    try:
        jogo_em_pausa()

        print("Monitorando o elemento de resultado do jogo...")
        resultados_element = WebDriverWait(driver, 180).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'winner--0dde2'))
        )

        resultados_texto = resultados_element.text.strip()

        if resultados_texto:
            print(f'Texto do resultado capturado: {resultados_texto}')
            enviar_mensagem_telegram(f'Resultado encontrado: {resultados_texto}', chat_id)
            resultados_lista = resultados_texto.split()
            resultados = [float(resultado) for resultado in resultados_lista if resultado.replace('.', '', 1).isdigit()]
            print(f'Resultados capturados: {resultados}')
            return resultados
        else:
            print('Texto do resultado vazio ou não encontrado.')
            return []
    except TimeoutException:
        print('Tempo limite excedido ao esperar pelo elemento de resultado.')
        return []
    except NoSuchElementException:
        print('Elemento de resultado não encontrado no DOM.')
        return []
    except Exception as e:
        print(f'Erro ao capturar resultados: {e}')
        driver.save_screenshot('erro_captura_resultado.png')  # Capturar a tela para ajudar na depuração
        return []



# Loop principal para capturar resultados periodicamente
while True:
    resultados = capturar_resultado()
    if resultados:
        mensagem = f' resultado: {resultados}'
        enviar_mensagem_telegram(mensagem, chat_id)
    sleep(10)  # Esperar 10 segundos antes de capturar novamente
