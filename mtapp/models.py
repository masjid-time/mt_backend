from mtapp import db


class Timings(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    fajr = db.Column(db.DateTime)
    dhuhr = db.Column(db.DateTime)
    asr = db.Column(db.DateTime)
    maghrib = db.Column(db.DateTime)
    isha = db.Column(db.DateTime)
    juma = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return f'ID {self.id}'
