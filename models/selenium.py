
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from botcity.maestro import *
from time import sleep
from dotenv import load_dotenv
import os
import pandas as pd

BotMaestroSDK.RAISE_NOT_CONNECTED = False
load_dotenv()

class SeleniumBot:
 
    def __init__(self, headless:bool = False) -> None:
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
            close_btn = WebDriverWait(self.navegador, 10).until(
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

    
    def mesclar_excluir(self, opcao: str, caminho_path: str, dataframes: list = None) -> None:
        arquivos = os.listdir(caminho_path)

        if opcao.lower() == 'mesclar':
            for arquivo in arquivos:
                if arquivo.endswith('.xlsx'):
                    # Cria o caminho completo
                    caminho_arquivo = os.path.join(caminho_path, arquivo)
                    df = pd.read_excel(caminho_arquivo)
                    dataframes.append(df)
        
        elif opcao.lower() == 'excluir':
            for arquivo in arquivos:
                if arquivo.endswith('.xlsx'):
                    os.remove(os.path.join('downloaded_files', arquivo))
                    print(f'{arquivo} foi excluído.')

    def action(self, execution = None) -> None:
        try:
            maestro = BotMaestroSDK.from_sys_args()
            execution = maestro.get_execution()
            
            # Informações da tarefa que está sendo executada
            print(f"Task ID is: {execution.task_id}")
            print(f"Task Parameters are: {execution.parameters}")

            diretorio = 'downloaded_files'
            dataframes = []

            maestro.alert(
                task_id=execution.task_id,
                title="Iniciando automação",
                message="Automação iniciando conforme planejado",
                alert_type=AlertType.INFO
            )

            self.fazer_login(str(self.api_key), str(self.senha))
            sleep(3)
            self.buscar_relatorios()
            sleep(4)
            self.baixar_arquivos()

            sleep(2)

            self.mesclar_excluir('mesclar', diretorio, dataframes)

            if dataframes:
                arquivo_consolidado = pd.concat(dataframes, ignore_index=True)
                # Salva o DataFrame combinado em um novo arquivo .xlsx
                arquivo_consolidado.to_excel('arquivo_mesclado.xlsx', index=False)
            else:
                print("Nenhum arquivo para combinar.")

            self.mesclar_excluir('excluir', diretorio)

            # A extensão é CSV
            maestro.post_artifact(
                task_id=execution.task_id,
                artifact_name="arquivo_mesclado",
                filepath="arquivo_mesclado.xlsx"
            )


            status_finish = AutomationTaskFinishStatus.SUCCESS,
            message_finish = "Tarefa foi concluída com sucesso.",

        except Exception as ex:
            print(ex)
            maestro.alert(
                task_id=execution.task_id,
                title="Erro na automação",
                message=f"Nossa automação finalizou com erro: {ex}",
                alert_type=AlertType.INFO
            )
            status_finish = AutomationTaskFinishStatus.FAILED,
            message_finish = "Tarefa foi concluída com erro.",
        
            maestro.error(task_id=execution.task_id, exception=ex)
            
        finally:
            self.navegador.quit()  # Garante que o navegador seja fechado

            maestro.finish_task(
                task_id= execution.task_id,
                status= status_finish,
                message= message_finish
            )