import pytest
import requests
from typing import Dict, Any, Optional


class APIClient:
    """
    Клиент-обертка для API сервиса JSONPlaceholder.
    Управляет жизненным циклом сессии и предоставляет базовую конфигурацию URL.
    """
    
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    def __init__(self):
        """Инициализирует API клиент с постоянной сессией."""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        # Таймаут для избежания "висячих" запросов.
        self.timeout = 30
    
    def _build_url(self, endpoint: str) -> str:
        """
        Формирует полный URL для запроса.
        
        Args:
            endpoint: Путь к конечной точке API.
            
        Returns:
            Полный URL.
        """
        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"
    
    def _handle_response(self, response: requests.Response) -> requests.Response:
        """
        Обрабатывает ответ API, выбрасывая исключения при ошибках.
        
        Args:
            response: Объект ответа requests.
            
        Returns:
            Объект ответа, если статус успешный.
            
        Raises:
            requests.exceptions.HTTPError: При статусе 4xx или 5xx.
        """
        response.raise_for_status()
        return response
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Отправляет GET запрос к указанному endpoint.
        
        Args:
            endpoint: Путь к конечной точке API.
            params: Параметры запроса (опционально).
            
        Returns:
            Объект ответа.
            
        Raises:
            requests.exceptions.HTTPError: При ошибке HTTP.
        """
        response = self.session.get(
            self._build_url(endpoint),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Отправляет POST запрос к указанному endpoint.
        
        Args:
            endpoint: Путь к конечной точке API.
            data: Тело запроса (опционально).
            
        Returns:
            Объект ответа.
            
        Raises:
            requests.exceptions.HTTPError: При ошибке HTTP.
        """
        response = self.session.post(
            self._build_url(endpoint),
            json=data,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Отправляет PUT запрос к указанному endpoint.
        
        Args:
            endpoint: Путь к конечной точке API.
            data: Тело запроса (опционально).
            
        Returns:
            Объект ответа.
            
        Raises:
            requests.exceptions.HTTPError: При ошибке HTTP.
        """
        response = self.session.put(
            self._build_url(endpoint),
            json=data,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Отправляет PATCH запрос к указанному endpoint.
        
        Args:
            endpoint: Путь к конечной точке API.
            data: Тело запроса (опционально).
            
        Returns:
            Объект ответа.
            
        Raises:
            requests.exceptions.HTTPError: При ошибке HTTP.
        """
        response = self.session.patch(
            self._build_url(endpoint),
            json=data,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def delete(self, endpoint: str) -> requests.Response:
        """
        Отправляет DELETE запрос к указанному endpoint.
        
        Args:
            endpoint: Путь к конечной точке API.
            
        Returns:
            Объект ответа.
            
        Raises:
            requests.exceptions.HTTPError: При ошибке HTTP.
        """
        response = self.session.delete(
            self._build_url(endpoint),
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def close(self):
        """Закрывает сессию."""
        if self.session:
            self.session.close()


@pytest.fixture(scope='session')
def api_client():
    """
    Фикстура, создающая и управляющая сессией API клиента.
    
    Returns:
        APIClient: Настроенный экземпляр API клиента.
        
    Yields:
        APIClient: API клиент для выполнения тестов.
    """
    client = APIClient()
    yield client
    client.close()


@pytest.fixture(scope='function')
def test_post_data() -> Dict[str, Any]:
    """
    Фикстура предоставляет тестовые данные для создания постов.
    
    Returns:
        Dict: Словарь с тестовыми данными для поста.
        
    Example:
        def test_create_post(api_client, test_post_data):
            response = api_client.post('posts', test_post_data)
            assert response.status_code == 201
    """
    return {
        "userId": 1,
        "title": "Test Post Title",
        "body": "Test post content body for validation purposes."
    }


@pytest.fixture(scope='function')
def updated_post_data() -> Dict[str, Any]:
    """
    Фикстура предоставляет тестовые данные для обновления постов.
    
    Returns:
        Dict: Словарь с обновленными тестовыми данными для поста.
        
    Example:
        def test_update_post(api_client, updated_post_data):
            response = api_client.put('posts/1', updated_post_data)
            assert response.status_code == 200
    """
    return {
        "id": 1,
        "userId": 1,
        "title": "Updated Test Post Title",
        "body": "Updated test post content body."
    }


@pytest.fixture(scope='function')
def post_id() -> int:
    """
    Фикстура для тестирования операций с существующим постом.
    
    Returns:
        int: ID поста для тестирования.
    """
    return 1


@pytest.fixture(scope='function')
def invalid_post_id() -> int:
    """
    Фикстура с несуществующим ID поста для негативных тестов.
    
    Returns:
        int: Несуществующий ID поста.
    """
    return 99999


# Опционально: фикстура для очистки тестовых данных.
@pytest.fixture(scope='function')
def cleanup_test_data(api_client):
    """
    Фикстура для автоматической очистки тестовых данных после теста.
    
    Использование:
        def test_with_cleanup(api_client, cleanup_test_data):
            # Тестовый код.
            pass
    """
    created_ids = []
    
    def create_and_track(data):
        """Создает пост и запоминает его ID для последующего удаления."""
        response = api_client.post('posts', data)
        if response.status_code == 201:
            created_ids.append(response.json().get('id'))
        return response
    
    yield create_and_track
    
    # Очистка: удаляет все созданные посты.
    for post_id in created_ids:
        try:
            api_client.delete(f'posts/{post_id}')
        except requests.exceptions.HTTPError:
            pass  # Игнорирует ошибки при очистке.
        