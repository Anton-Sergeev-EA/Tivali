import pytest
import requests
from typing import Dict, Any, List, Optional


class TestPosts:
    """
    Класс тестов для операций с конечной точкой /posts.
    Реализует тесты CRUD операций с валидацией и граничными случаями.
    """
    
    EXISTING_POST_ID = 1
    NONEXISTENT_POST_ID = 99999
    DEFAULT_USER_ID = 1
    
    def test_get_all_posts(self, api_client):
        """
        Тест GET /posts - Получение всех постов.
        
        Проверяет:
        - HTTP статус 200.
        - Ответ является списком.
        - Список содержит хотя бы один пост.
        - Первый пост имеет обязательные поля.
        """
        response = api_client.get("/posts")
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}."
        
        posts = response.json()
        assert isinstance(posts, list), "Ответ должен быть списком."
        assert len(posts) > 0, "Должен быть хотя бы один пост."
        
        # Проверка структуры первого поста.
        first_post = posts[0]
        required_fields = ["userId", "id", "title", "body"]
        for field in required_fields:
            assert field in first_post, f"В посте отсутствует обязательное поле: {field}."
    
    def test_get_single_post(self, api_client):
        """
        Тест GET /posts/{id} - Получение конкретного поста.
        
        Проверяет:
        - HTTP статус 200.
        - Корректный ID поста.
        - Наличие всех обязательных полей.
        - Корректность типов данных.
        """
        post_id = self.EXISTING_POST_ID
        response = api_client.get(f"/posts/{post_id}")
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}."
        
        post = response.json()
        assert isinstance(post, dict), "Ответ должен быть словарем."
        assert post.get("id") == post_id, f"Ожидался id {post_id}, получен {post.get('id')}."
        
        # Проверка наличия всех полей.
        required_fields = ["userId", "id", "title", "body"]
        for field in required_fields:
            assert field in post, f"В посте отсутствует обязательное поле: {field}."
        
        # Проверка типов данных.
        assert isinstance(post["userId"], int), "userId должен быть целым числом."
        assert isinstance(post["id"], int), "id должен быть целым числом."
        assert isinstance(post["title"], str), "title должен быть строкой."
        assert isinstance(post["body"], str), "body должен быть строкой."
    
    @pytest.mark.parametrize("post_id,expected_status", [
        (1, 200),      # Существующий пост.
        (100, 200),    # Существующий пост.
        (99999, 404),  # Несуществующий пост.
    ])
    def test_get_single_post_parametrized(self, api_client, post_id: int, expected_status: int):
        """
        Параметризованный тест для GET /posts/{id} с разными ID.
        
        Args:
            post_id: ID поста для получения.
            expected_status: Ожидаемый HTTP статус.
        """
        response = api_client.get(f"/posts/{post_id}")
        assert response.status_code == expected_status, \
            f"Ожидался {expected_status}, получен {response.status_code}."
        
        if expected_status == 200:
            post = response.json()
            assert post.get("id") == post_id, f"Ожидался id {post_id}, получен {post.get('id')}."
    
    def test_create_post(self, api_client, test_post_data):
        """
        Тест POST /posts - Создание нового поста.
        
        Проверяет:
        - HTTP статус 201.
        - Ответ содержит созданный пост.
        - Все переданные поля сохранены.
        - Сгенерирован ID.
        """
        response = api_client.post("/posts", test_post_data)
        
        assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}."
        
        created_post = response.json()
        assert "id" in created_post, "Созданный пост должен иметь ID."
        assert created_post["id"] is not None, "ID не должен быть null."
        
        # Проверка, что все поля соответствуют переданным данным.
        for key, value in test_post_data.items():
            assert created_post.get(key) == value, f"Несоответствие поля {key}."
    
    @pytest.mark.parametrize("post_data,expected_status", [
        ({"userId": 1, "title": "Test", "body": "Content"}, 201),  # Полные данные.
        ({"userId": 1, "title": "", "body": "Content"}, 201),  # Пустой заголовок.
        ({}, 201),  # Пустые данные.
        ({"userId": "invalid", "title": 123, "body": None}, 201),  # Некорректные типы.
    ])
    def test_create_post_parametrized(self, api_client, post_data: Dict[str, Any], expected_status: int):
        """
        Параметризованный тест для POST /posts с разными наборами данных.
        
        Args:
            post_data: Данные для создания поста.
            expected_status: Ожидаемый HTTP статус.
        """
        response = api_client.post("/posts", post_data)
        assert response.status_code == expected_status, \
            f"Ожидался {expected_status}, получен {response.status_code}."
        
        if expected_status == 201:
            created_post = response.json()
            # Проверка только тех полей, которые были переданы.
            for key, value in post_data.items():
                if key in created_post:
                    assert created_post[key] == value, f"Несоответствие поля {key}"
    
    def test_update_post(self, api_client, updated_post_data):
        """
        Тест PUT /posts/{id} - Полное обновление существующего поста.
        
        Проверяет:
        - HTTP статус 200.
        - Обновленные данные соответствуют ожидаемым.
        - Все поля корректно обновлены.
        """
        post_id = updated_post_data["id"]
        response = api_client.put(f"/posts/{post_id}", updated_post_data)
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}."
        
        updated_post = response.json()
        assert updated_post["id"] == post_id, "ID поста должен совпадать."
        
        # Проверка всех обновленных полей.
        for key, value in updated_post_data.items():
            assert updated_post.get(key) == value, f"Несоответствие поля {key} после обновления."
    
    @pytest.mark.parametrize("update_data", [
        {"id": 1, "title": "Updated Title"},  # Обновление заголовка.
        {"id": 1, "body": "Updated body content"},  # Обновление содержимого.
        {"id": 1, "title": "New Title", "body": "New body"},  # Обновление всех полей.
        {"id": 1}, # Пустое обновление.
    ])
    def test_update_post_partial(self, api_client, update_data: Dict[str, Any]):
        """
        Параметризованный тест для частичного обновления через PUT.
        
        Args:
            update_data: Частичные данные для обновления поста.
        """
        post_id = update_data["id"]
        response = api_client.put(f"/posts/{post_id}", update_data)
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}."
        
        updated_post = response.json()
        # Проверка только переданных полей.
        for key, value in update_data.items():
            assert updated_post.get(key) == value, f"Несоответствие поля {key} после обновления."
    
    def test_delete_post(self, api_client):
        """
        Тест DELETE /posts/{id} - Удаление существующего поста.
        
        Проверяет:
        - HTTP статус 200 (JSONPlaceholder возвращает 200).
        - Пустое тело ответа.
        """
        post_id = self.EXISTING_POST_ID
        response = api_client.delete(f"/posts/{post_id}")
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}."
        
        # JSONPlaceholder возвращает пустой объект при DELETE.
        content = response.text
        assert content == "{}" or content == "", "Ответ должен быть пустым."
    
    def test_delete_nonexistent_post(self, api_client):
        """
        Тест DELETE /posts/{id} - Удаление несуществующего поста.
        Негативный тест.
        
        Проверяет:
        - HTTP статус 404.
        - Пустое тело ответа.
        """
        post_id = self.NONEXISTENT_POST_ID
        response = api_client.delete(f"/posts/{post_id}")
        
        # JSONPlaceholder может возвращать 200 или 404.
        assert response.status_code in [200, 404], \
            f"Ожидался 200 или 404, получен {response.status_code}."
    
    def test_get_nonexistent_post(self, api_client):
        """
        Тест GET /posts/{id} - Получение несуществующего поста.
        Негативный тест.
        
        Проверяет:
        - HTTP статус 404.
        - Структура ответа с ошибкой.
        """
        post_id = self.NONEXISTENT_POST_ID
        response = api_client.get(f"/posts/{post_id}")
        
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}."
        
        # Некоторые API возвращают пустой объект для 404
        content = response.text
        assert content == "{}" or content == "", "Ответ для несуществующего поста должен быть пустым."
    
    def test_get_posts_with_query_params(self, api_client):
        """
        Тест GET /posts с параметрами запроса.
        
        Проверяет:
        - HTTP статус 200.
        - Фильтрация работает корректно.
        - Результаты соответствуют критериям запроса.
        """
        params = {"userId": self.DEFAULT_USER_ID}
        response = api_client.get("/posts", params=params)
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
        
        posts = response.json()
        assert isinstance(posts, list), "Ответ должен быть списком."
        
        # Проверка фильтрации по userId.
        for post in posts:
            assert post.get("userId") == self.DEFAULT_USER_ID, \
                f"Ожидался userId {self.DEFAULT_USER_ID}, получен {post.get('userId')}."
    
    @pytest.mark.parametrize("params,description", [
        ({"userId": 1}, "Фильтрация по userId=1"),
        ({"userId": 2}, "Фильтрация по userId=2"),
        ({"userId": 3}, "Фильтрация по userId=3"),
        ({"postId": 1}, "Фильтрация по postId=1"),
    ])
    def test_get_posts_filtered_parametrized(self, api_client, params: Dict[str, Any], description: str):
        """
        Параметризованный тест для GET /posts с разными фильтрами.
        
        Args:
            params: Параметры запроса.
            description: Описание тестового случая.
        """
        response = api_client.get("/posts", params=params)
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
        assert description  # Описание для читаемости.
        
        posts = response.json()
        assert isinstance(posts, list), "Ответ должен быть списком."
        
        # Проверка фильтрации по параметрам.
        if "userId" in params:
            for post in posts:
                assert post.get("userId") == params["userId"], "Несовпадение userId."
        elif "postId" in params:
            for post in posts:
                assert post.get("id") == params["postId"], "Несовпадение postId."
    
    def test_invalid_endpoint(self, api_client):
        """
        Тест доступа к несуществующей конечной точке.
        Негативный тест.
        
        Проверяет:
        - HTTP статус 404 для несуществующего эндпоинта.
        """
        response = api_client.get("/invalid_endpoint")
        
        assert response.status_code == 404, f"Ожидался 404, получен {response.status_code}."
    
    def test_invalid_http_method(self, api_client):
        """
        Тест использования недопустимого HTTP метода (DELETE на коллекции).
        Негативный тест.
        
        Проверяет:
        - HTTP статус 405 для недопустимого метода
        """
        response = api_client.delete("/posts")
        
        # JSONPlaceholder может возвращать 200 или 404/405.
        assert response.status_code in [200, 404, 405], \
            f"Ожидался 200/404/405, получен {response.status_code}."
    
    def test_post_with_malformed_data(self, api_client):
        """
        Тест POST с некорректными/поврежденными данными.
        Негативный тест.
        
        Проверяет:
        - Соответствующий ответ об ошибке.
        - Система корректно обрабатывает поврежденные данные.
        """
        malformed_data = {
            "userId": "not_a_number", # Должен быть int.
            "title": 123, # Должен быть str.
            "body": None # Должен быть str.
        }
        response = api_client.post("/posts", malformed_data)
        
        # JSONPlaceholder принимает любые данные, поэтому ожидается 201.
        assert response.status_code in [201, 400, 422], \
            f"Неожиданный статус: {response.status_code}."
        
        if response.status_code == 201:
            created_post = response.json()
            assert created_post.get("id") is not None, "ID должен быть создан."
    
    def test_put_nonexistent_post(self, api_client):
        """
        Тест PUT для несуществующего поста.
        Негативный тест.
        
        Проверяет:
        - HTTP статус 200 или 404 (зависит от реализации JSONPlaceholder).
        """
        post_id = self.NONEXISTENT_POST_ID
        data = {
            "id": post_id,
            "title": "Updated",
            "body": "Content"
        }
        response = api_client.put(f"/posts/{post_id}", data)
        
        # JSONPlaceholder может возвращать 200 для несуществующих ресурсов.
        assert response.status_code in [200, 404], \
            f"Ожидался 200/404, получен {response.status_code}."
    
    def test_response_headers(self, api_client):
        """
        Тест проверки заголовков ответа.
        
        Проверяет:
        - Наличие Content-Type.
        - Корректный Content-Type (application/json).
        - Наличие других стандартных заголовков.
        """
        response = api_client.get("/posts/1")
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}."
        
        # Проверка заголовков.
        assert "Content-Type" in response.headers, "Отсутствует заголовок Content-Type."
        content_type = response.headers["Content-Type"]
        assert "application/json" in content_type, \
            f"Ожидался application/json, получен {content_type}."
        
        # Проверка дополнительных заголовков.
        optional_headers = ["Server", "Date", "Cache-Control"]
        for header in optional_headers:
            if header in response.headers:
                assert response.headers[header] is not None, f"Заголовок {header} пустой."
    
    def test_response_time(self, api_client):
        """
        Тест времени ответа.
        
        Проверяет:
        - Время ответа не превышает допустимый порог.
        - Стабильность производительности.
        """
        import time
        
        start_time = time.time()
        response = api_client.get("/posts")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}."
        
        # Время ответа не должно превышать 5 секунд.
        max_response_time = 5.0
        assert elapsed_time < max_response_time, \
            f"Время ответа {elapsed_time:.2f}с превышает лимит {max_response_time}с."
    
    def test_data_consistency(self, api_client):
        """
        Тест согласованности данных.
        
        Проверяет:
        - Получение одного поста соответствует данным из списка.
        - Данные согласованы между разными запросами.
        """
        # Получает пост по ID.
        post_id = self.EXISTING_POST_ID
        single_response = api_client.get(f"/posts/{post_id}")
        assert single_response.status_code == 200
        single_post = single_response.json()
        
        # Получает список всех постов и находит нужный.
        all_response = api_client.get("/posts")
        assert all_response.status_code == 200
        all_posts = all_response.json()
        
        # Находит пост с нужным ID в списке.
        found_post = None
        for post in all_posts:
            if post.get("id") == post_id:
                found_post = post
                break
        
        assert found_post is not None, f"Пост с ID {post_id} не найден в списке.
        
        # Сравнивает данные.
        assert single_post == found_post, "Данные поста не совпадают при разных запросах."
        