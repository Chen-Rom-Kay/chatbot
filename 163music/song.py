class Song:
    def __init__(self,name,url,play_url):
        self.url = url
        self.name = name
        self.play_url = play_url

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url

    def get_play_url(self):
        return self.play_url