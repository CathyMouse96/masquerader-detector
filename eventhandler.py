import logging

from watchdog.events import FileSystemEventHandler

class CustomFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.created = 0
        self.deleted = 0
        self.modified = 0
        self.moved = 0
    
    def on_created(self, event):
        logging.debug("Created: " + event.src_path)
        self.created += 1
    
    def on_deleted(self, event):
        logging.debug("Deleted: " + event.src_path)
        self.deleted += 1
    
    def on_modified(self, event):
        logging.debug("Modified: " + event.src_path)
        if event.is_directory: # Ignore dir modify events
            pass
        else:
            self.modified += 1
    
    def on_moved(self, event):
        logging.debug("Moved: " + event.src_path)
        self.moved += 1
    
    def clear(self):
        self.__init__()
