from beets import plugins, library
from beets.util import displayable_path
from beets.importer import ImportTask
import subprocess
from collections import Counter


def get_apple_music_track_paths():
    """Get the paths to all tracks in the local Apple Music Library"""
    get_apple_track_paths = """
    tell application "Music"
        set all_tracks to tracks of library playlist 1
        set output to ""
        repeat with a_track in all_tracks
            set track_path to location of a_track
            if track_path is not missing value then
                set output to output & POSIX path of track_path & linefeed
            end if
        end repeat
    end tell
    return output
    """
    # Run the AppleScript using osascript and capture the output
    result = subprocess.run(
        ["osascript", "-e", get_apple_track_paths], stdout=subprocess.PIPE, text=True
    )

    # The result contains the file paths as a single string
    paths = result.stdout.strip()

    # Split the result by linefeed to get a list of file paths
    track_paths = paths.split("\n")

    return track_paths


def lib_to_paths(lib: library.Library):
    """Helper to get all tracks in the beets library as legible paths"""
    paths = []
    for item in lib.items():
        paths.append(displayable_path(item.path))
    return paths


class Musync(plugins.BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.register_listener("library_opened", self.sync_changes)
        self.register_listener("import_task_files", self.import_task)
        self.register_listener("item_removed", self.delete_task)

    def sync_changes(self, lib: library.Library):
        """Compares the Music App Library with the Beets Library and adds missing tracks to the Music App"""
        difference = list(
            (
                Counter(lib_to_paths(lib)) - Counter(get_apple_music_track_paths())
            ).elements()
        )
        for path in difference:
            self._log.info("Track missing! Adding '" + path + "' to Music App...")

            # AppleScript to import a track
            import_script = f"""
            tell application "Music"
                add POSIX file "{path}" to library playlist 1
            end tell
            """

            # Run the script via osascript
            subprocess.run(["osascript", "-e", import_script])

    def import_task(self, task: ImportTask):
        for item in task.imported_items():
            posix = displayable_path(item.path)
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
