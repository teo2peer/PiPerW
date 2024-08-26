


class AppInterface:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name} {self.version}"
    
    def run(self):
        pass