from app.app import App

number_of_tests = 3

if __name__ == "__main__":
    for i in range(number_of_tests):
        app = App(server_url="http://server:8000", test_name=f"test_{i}")
        app.do_matchmaking()
