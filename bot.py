from models.selenium import SeleniumBot


def main():
    
    bot = SeleniumBot()
    bot.abrir_navegador('https://www.lme.com/en/Account/Login')

    bot.action()



if __name__ == '__main__':
    main()