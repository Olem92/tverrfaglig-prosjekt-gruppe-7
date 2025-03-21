from database import VarehusDatabase

class App:
    def __init__(self):
        self.db = VarehusDatabase()

    def start(self):
        print("Starting the app")

        #Simple database connection test
        self.db.connect()
        self.db.close()

if __name__ == "__main__":
    app = App()
    app.start()