from beets import plugins, IncludeLazyConfig

from typing import Any, Dict


# config setup
JSONDict = Dict[str, Any]
DEFAULT_CONFIG: JSONDict = {
    "add_to_music_path": "~/Music/Music/Media/Automatically Add to Music.localized"
}


class Musync(plugins.BeetsPlugin):
    beets_config: IncludeLazyConfig

    def __init__(self):
        super().__init__()
        self.config.add(DEFAULT_CONFIG.copy())
        self.register_listener("import_task_end", self.sync_task)

    def sync_task(self):
        self._log.info("after import")
