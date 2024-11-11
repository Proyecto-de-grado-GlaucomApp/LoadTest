import time
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """API configuration settings loaded from environment variables"""
    
    @staticmethod
    def get_env_or_raise(key: str) -> str:
        """
        Get environment variable or raise error if not found
        
        Args:
            key (str): Environment variable key
            
        Returns:
            str: Environment variable value
            
        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Environment variable {key} is not set. Please check your .env file.")
        return value

    @classmethod
    def initialize(cls) -> None:
        """Initialize configuration from environment variables"""
        # API Configuration
        host = cls.get_env_or_raise("API_HOST")
        port = cls.get_env_or_raise("API_PORT")
        
        # Build URLs
        cls.BASE_URL_AUTH = f'http://{host}:{port}/mobile/auth'
        cls.BASE_URL = f'http://{host}:{port}/mobile/glaucoma-screening/process'
        
        # Authentication
        cls.USERNAME = cls.get_env_or_raise("API_USERNAME")
        cls.PASSWORD = cls.get_env_or_raise("API_PASSWORD")
        
        # Test Configuration
        cls.IMAGE_PATH = cls.get_env_or_raise("TEST_IMAGE_PATH")
        
        # Optional configurations with defaults
        cls.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

class AuthenticationHandler:
    """Handles authentication and token management"""
    @staticmethod
    def login_and_get_header() -> Optional[dict]:
        """
        Authenticates with the API and returns headers with JWT token
        
        Returns:
            dict: Headers containing the JWT token or None if authentication fails
        """
        payload = {
            "username": Config.USERNAME,
            "password": Config.PASSWORD
        }
        
        try:
            response = requests.post(f'{Config.BASE_URL_AUTH}/login', json=payload)
            if response.status_code == 200:
                jwt = response.cookies.get('jwtToken')
                print(f"JWT Token obtained successfully")
                return {'Authorization': f'Bearer {jwt}'}
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None

class RequestHandler:
    """Handles individual API requests"""
    @staticmethod
    def send_request(headers: dict, start_event: Event, request_number: int) -> dict:
        """
        Sends a single request to the API with image processing
        
        Args:
            headers (dict): Request headers including authentication
            start_event (Event): Synchronization event for concurrent requests
            request_number (int): Identifier for the current request
            
        Returns:
            dict: Result containing request metrics and response data
        """
        start_time = time.time()
        
        try:
            with open(Config.IMAGE_PATH, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post(
                    Config.BASE_URL,
                    files=files,
                    headers=headers,
                    timeout=Config.REQUEST_TIMEOUT
                )

            end_time = time.time()
            response_time = end_time - start_time
            
            # Process response
            response_data = response.json() if response.status_code == 200 else None
            answer = response_data.get('answer', 'No response') if response.status_code == 200 else None
            
            # Check for successful response
            success = (
                response.status_code == 200 and 
                answer != "We are resolving some issues. Please try again in a few minutes."
            )

            result = {
                "request_number": request_number,
                "success": success,
                "status_code": response.status_code,
                "response_time": response_time,
                "response_data": response_data,
                "answer": answer
            }
            
            print(f"Request #{request_number}: {result['success']} "
                  f"(Code: {result['status_code']}, "
                  f"Time: {result['response_time']:.4f}s, "
                  f"Response: {result['answer']})")
            
            return result
            
        except Exception as e:
            print(f"Error in request #{request_number}: {str(e)}")
            return {
                "request_number": request_number,
                "success": False,
                "status_code": None,
                "response_time": time.time() - start_time,
                "response_data": None,
                "answer": f"Error: {str(e)}"
            }

class LoadTester:
    """Manages load testing execution and results"""
    def __init__(self, headers: dict):
        self.headers = headers
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.result_file_path = os.path.join(
            self.current_directory,
            'GlauApp_LoadTestsResults.txt'
        )

    def run_load_test(self, num_requests: int, concurrency: int) -> None:
        """
        Executes load test with specified parameters
        
        Args:
            num_requests (int): Total number of requests to send
            concurrency (int): Number of concurrent requests
        """
        if self.headers is None:
            print("Authentication failed. Test aborted.")
            return

        response_times = []
        errors = 0
        results = []
        start_event = Event()

        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(RequestHandler.send_request, self.headers, start_event, i + 1)
                for i in range(num_requests)
            ]

            start_event.set()

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

                if result["success"]:
                    response_times.append(result["response_time"])
                else:
                    errors += 1

        # Calculate statistics
        self._calculate_and_save_results(
            response_times,
            errors,
            num_requests,
            concurrency
        )

    def _calculate_and_save_results(self, response_times: list, errors: int, 
                                  num_requests: int, concurrency: int) -> None:
        """
        Calculates and saves test results
        
        Args:
            response_times (list): List of response times
            errors (int): Number of failed requests
            num_requests (int): Total number of requests
            concurrency (int): Number of concurrent requests
        """
        if response_times:
            stats = {
                'avg': sum(response_times) / len(response_times),
                'max': max(response_times),
                'min': min(response_times)
            }
        else:
            stats = {'avg': 0, 'max': 0, 'min': 0}

        # Save results to file
        with open(self.result_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\nLoad Test Results - {num_requests} requests with {concurrency} threads:\n")
            f.write(f"Response times: min={stats['min']:.4f}s, max={stats['max']:.4f}s, "
                   f"avg={stats['avg']:.4f}s\n")
            f.write(f"Successful requests: {len(response_times)}\n")
            f.write(f"Failed requests: {errors}\n")

        # Display results
        print(f"\nLoad Test Results - {num_requests} requests with {concurrency} threads:")
        print(f"Response times: min={stats['min']:.4f}s, max={stats['max']:.4f}s, "
              f"avg={stats['avg']:.4f}s")
        print(f"Successful requests: {len(response_times)}")
        print(f"Failed requests: {errors}")

def main():
    """Main execution function"""
    try:
        # Initialize configuration from environment variables
        Config.initialize()
        
        # Initialize authentication
        headers = AuthenticationHandler.login_and_get_header()
        
        # Test configuration
        num_requests = 100
        concurrency_levels = [1, 5, 10, 25, 50, 75, 100]
        
        # Initialize load tester
        load_tester = LoadTester(headers)
        
        # Clear previous results file
        with open(load_tester.result_file_path, 'w', encoding='utf-8') as f:
            f.write("Load Test Results Log:\n")
        
        # Run tests for each concurrency level
        for concurrency in concurrency_levels:
            load_tester.run_load_test(num_requests, concurrency)
            
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()