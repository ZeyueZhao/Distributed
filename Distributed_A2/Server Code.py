from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xml.etree.ElementTree as ET
import datetime
import requests  

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class NotebookServer:
    def __init__(self):
        self.database_path = "notebook.xml"
        self.load_database()

    def load_database(self):
        try:
            self.tree = ET.parse(self.database_path)
        except FileNotFoundError:
            self.tree = ET.ElementTree(ET.Element('data'))

    def save_database(self):
        self.tree.write(self.database_path)

    def process_client_input(self, topic, text):
        root = self.tree.getroot()

        # Check if the topic exists
        topic_element = root.find(f"topic[@name='{topic}']")
        if topic_element is None:
            # If not, create a new topic
            topic_element = ET.SubElement(root, 'topic', {'name': topic})

        # Create a new note
        note_element = ET.SubElement(topic_element, 'note', {'name': f"{topic} - {len(topic_element.findall('note')) + 1}"})
        text_element = ET.SubElement(note_element, 'text')
        text_element.text = text
        timestamp_element = ET.SubElement(note_element, 'timestamp')
        timestamp_element.text = datetime.datetime.now().strftime("%m/%d/%y - %H:%M:%S")

        # Save the changes to the database
        self.save_database()

        return f"Note added successfully to the topic: {topic}"

    def get_contents_by_topic(self, topic):
        root = self.tree.getroot()

        # Check if the topic exists
        topic_element = root.find(f"topic[@name='{topic}']")
        if topic_element is not None:
            # If yes, retrieve notes
            notes = []
            for note_element in topic_element.findall('note'):
                note = {
                    'name': note_element.get('name'),
                    'text': note_element.find('text').text,
                    'timestamp': note_element.find('timestamp').text
                }
                notes.append(note)
            return notes
        else:
            return f"No notes found for the topic: {topic}"

    def query_wikipedia(self, topic):
        wikipedia_api_url = "https://en.wikipedia.org/w/api.php"
        params = {
            'action': 'opensearch',
            'format': 'json',
            'search': topic
        }

        response = requests.get(wikipedia_api_url, params=params)
        data = response.json()

        if len(data[1]) > 0:
            # Add relevant information to user-submitted topic
            root = self.tree.getroot()
            topic_element = root.find(f"topic[@name='{topic}']")

            if topic_element is None:
                topic_element = ET.SubElement(root, 'topic', {'name': topic})

            # Add link to Wikipedia article
            wikipedia_link = data[3][0]
            info_element = ET.SubElement(topic_element, 'info', {'source': 'Wikipedia', 'link': wikipedia_link})
            info_element.text = f"Wikipedia article: {wikipedia_link}"

            # Save the changes to the database
            self.save_database()

            return f"Wikipedia information added to the topic: {topic}"

        else:
            return f"No Wikipedia article found for the topic: {topic}"

if __name__ == '__main__':
    server = SimpleXMLRPCServer(('2.0.0.1', 8000), requestHandler=RequestHandler)
    server.register_introspection_functions()

    notebook_server = NotebookServer()
    server.register_instance(notebook_server)

    print("Notebook Server is running on port 8000...")
    server.serve_forever()
