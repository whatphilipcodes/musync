from beets import plugins
from beets.util import displayable_path
from beets.importer import ImportSession
import subprocess


class Musync(plugins.BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.register_listener("import_task_files", self.import_task)
        self.register_listener("item_removed", self.delete_task)

    def import_task(self, session: ImportSession):
        for path in session.paths:
            posix = displayable_path(path)
            self._log.info("Adding '" + posix + "' to Music App...")

            # AppleScript to import a track
            import_script = f"""
            tell application "Music"
                add POSIX file "{posix}" to library playlist 1
            end tell
            """

            # Run the script via osascript
            subprocess.run(["osascript", "-e", import_script])

    def delete_task(self, item):
        self._log.info(
            "Removing '" + item.title + "' by '" + item.artist + "' from Music App..."
        )

        # AppleScript to import a track
        remove_script = f"""
        tell application "Music"
	        set trackToDelete to (first track of library playlist 1 whose artist is "{item.artist}" and name is "{item.title}")
	        delete trackToDelete
        end tell
        """

        # Run the script via osascript
        subprocess.run(["osascript", "-e", remove_script])
