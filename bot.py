from models.selenium import SeleniumBot
import os

def main():

    try:
        
        bot = SeleniumBot()
        bot.abrir_navegador('https://www.lme.com/en/Account/Login')
        bot.action()

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()