
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from time import sleep
from dotenv import load_dotenv
import os


load_dotenv()
class SeleniumBot:
 
    def __init__(self, headless:bool = False) -> None:
        #Opções de download no navegador
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": r'resources',  # Define o diretório de download
            "download.prompt_for_download": False,       # Desabilita o prompt de download
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True                 # Evita avisos de 
        })

        self.navegador = Driver(uc=True, headless=headless)
        self.wait = WebDriverWait(self.navegador, 20)
        #Carregando credencias
        self.api_key = os.getenv('USER')
        self.senha = os.getenv('PASSWORD')


    def abrir_navegador(self, url = 'https:www.google.com.br') -> None:
        """Abre a URL do navegador"""
        self.navegador.get(url)
        self.navegador.maximize_window()

    def fechar_popup(self):
        """Fecha o banner de privacidade, se estiver aberto"""
        try:
            close_btn =WebDriverWait(self.navegador, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))
            )
            close_btn.click()
            print('Fechando o botão do cookie')
        
        except (NoSuchElementException, TimeoutException):
            print("Banner de privacidade não encontrado ou já fechado.")

    def fazer_login(self, email, senha) -> None:
        """"Realiza Login com as credencias fornecidas"""
        
        self.fechar_popup()
        
        while True:
            try:
                email_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="Email"]')))
                email_input.send_keys(email)

                password_input = self.navegador.find_element(By.XPATH, '//*[@id="Password"]')
                password_input.send_keys(senha)

                # Verifica se o botão de login está clicável e clica
                login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div/div[1]/div/form/div[3]/button')))
                login_button.click()
                break
         
            except NoSuchElementException:
                print("Tentando fechar o banner de privacidade novamente.")
                self.fechar_popup()
                sleep(1)

    def buscar_relatorios(self) -> None:
        try:
            market_data = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/button')))
            market_data.click()

            reports = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/div/ul/li[3]/button/span')))
            reports.click()

            averages = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="meganav-drawer"]/nav/ul/li[4]/div/ul/li[3]/div/div[2]/ul/li[2]/a')))
            averages.click()
        except TimeoutException:
            print("O elemento não estava disponível.")

    def baixar_arquivos(self):
        sleep(2)
        for n in range(1, 4):
            try:
                download = self.navegador.find_element(By.XPATH, f'/html/body/main/div/div[1]/div[1]/div[2]/div/p[{n}]/a')
                download.click()
                print(f"Arquivo {n} baixado com sucesso.")
                sleep(2)
            except NoSuchElementException:
                print(f"Arquivo {n} não encontrado.")


    def action(self) -> None:
        try:
            self.fazer_login(str(self.api_key), str(self.senha))
            sleep(3)
            self.buscar_relatorios()
            sleep(4)
            self.baixar_arquivos()
        finally:
            self.navegador.quit()  # Garante que o navegador seja fechado