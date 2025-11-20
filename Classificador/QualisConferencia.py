import pandas as pd
import Levenshtein

def _conferenceNameSimilarity(str1, str2):
    if len(str1) >= 10 and len(str2) >= 10:
        return Levenshtein.ratio(str1, str2)
    return 0

class QualisConferencia():

    def __init__(self, qualis_path) -> None:
        self.dict = self.readQualisConference(qualis_path)

    def readQualisConference(self, qualis_path):
        d = {}
        with open(qualis_path) as f:
            for line in f:
                short, conference, qualis = line.strip().split('\t')
                d[short.lower()] = qualis
                d[conference.lower()] = qualis
        return d
    
    def get_estrato(self, venue: str):
        venue = venue.lower()
        if venue in self.dict:
            return self.dict[venue]
        else:
            maxkey = None
            maxsim = -1
            for key in self.dict.keys():
                sim = _conferenceNameSimilarity(key, venue)
                if sim > maxsim:
                    maxsim = sim
                    maxkey = key
            if maxsim >= 0.85:
                return self.dict[maxkey]
            else:
                return None