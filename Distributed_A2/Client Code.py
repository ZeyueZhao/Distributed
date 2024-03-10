import xmlrpc.client

class NotebookClient:
    def __init__(self, server_url):
        self.server = xmlrpc.client.ServerProxy(server_url)

    def add_note(self, topic, text):
        response = self.server.process_client_input(topic, text)
        print(response)

    def get_notes_by_topic(self, topic):
        notes = self.server.get_contents_by_topic(topic)
        if isinstance(notes, list):
            for note in notes:
                print(f"Note: {note['name']}\nText: {note['text']}\nTimestamp: {note['timestamp']}\n")
        else:
            print(notes)

    def query_wikipedia(self, topic):
        response = self.server.query_wikipedia(topic)
        print(response)

if __name__ == '__main__':
    server_url = 'http://2.0.0.1:8000/RPC2'
    client = NotebookClient(server_url)

    while True:
        print("\n1. Add Note\n2. Get Notes by Topic\n3. Query Wikipedia\n4. Exit")
        choice = input("Enter your choice (1/2/3/4): ")

        if choice == '1':
            topic = input("Enter the topic: ")
            text = input("Enter the note text: ")
            client.add_note(topic, text)
        elif choice == '2':
            topic = input("Enter the topic to retrieve notes: ")
            client.get_notes_by_topic(topic)
        elif choice == '3':
            topic = input("Enter the topic to query Wikipedia: ")
            client.query_wikipedia(topic)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")


