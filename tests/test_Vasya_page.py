import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    # driver.implicitly_wait(10)
    # Переходим на страницу авторизации
    driver.get('https://petfriends.skillfactory.ru/login')

    yield driver

    driver.quit()


def test_show_my_pets(driver):
    # Вводим email
    driver.find_element(By.ID, 'email').send_keys('vasya@mail.com')
    # Вводим пароль
    driver.find_element(By.ID, 'pass').send_keys('12345')
    # Нажимаем на кнопку входа в аккаунт
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert driver.find_element(By.TAG_NAME, 'h1').text == "PetFriends"

    # Переход на страницу питомцев
    driver.find_element(By.XPATH, "//a[@href='/my_pets']").click()

    # Получение статистики пользователя
    stats = driver.find_element(By.CSS_SELECTOR, "div.left").text
    pets_count = int(stats.split("Питомцев: ")[1].split()[0])
    # print(pets_count)

    # Если нет питомцев - пропускаем остальные проверки
    if pets_count == 0:
        pytest.skip("У пользователя нет питомцев")

    # Получаем все карточки питомцев
    driver.implicitly_wait(10)
    pets = driver.find_elements(By.XPATH, "//tbody/tr")
    # print(len(pets))

    # 1. Проверяем, что все питомцы присутствуют
    assert len(pets) == pets_count
    print(f'\nОжидалось: {pets_count} Фактически: {len(pets)}')

    # 2. Проверяем, что есть фото хотя бы у половины питомцев
    images = driver.find_elements(By.XPATH, "//tbody/tr/th/img")
    photos_count = 0

    for img in images:
        src = img.get_attribute('src')
        if src != '':
            photos_count += 1

    assert photos_count >= pets_count / 2
    print(f'Фото есть у {photos_count} из {pets_count} питомцев')

    # 3. Проверяем, что у всех питомцев есть имя, возраст и порода
    names = []
    breeds = []
    ages = []
    pets_data = []

    for pet in pets:
        # Разделяем текст карточки на элементы
        parts = pet.text.split()

        # Проверяем наличие всех данных
        assert len(parts) >= 3  # "В карточке питомца недостаточно данных"
        assert parts[0] != ""  # "Имя питомца не может быть пустым"
        assert parts[1] != ""  # "Порода питомца не может быть пустой"
        assert parts[2] != ""  # "Возраст питомца не может быть пустым"

        names.append(parts[0])
        breeds.append(parts[1])
        ages.append(parts[2])

        pets_data.append((parts[0], parts[1], parts[2]))
        # print(pets_data)

    # Проверяем, что у всех питомцев разные имена
    assert len(names) == len(set(names))

    # Проверяем, что в списке нет повторяющихся питомцев
    assert len(pets_data) == len(set(pets_data))
    print(f'Дубликаты отсутствуют')

    print("\nВсе проверки пройдены успешно")
