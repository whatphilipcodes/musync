from beets import plugins


class Musync(plugins.BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.register_listener("pluginload", self.loaded)

    def loaded(self):
        self._log.info("Plugin loaded!")
