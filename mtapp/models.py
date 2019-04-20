from mtapp import db


class Timings(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    time_fazr = db.Column(db.DateTime)
    time_zohr = db.Column(db.DateTime)
    time_asr = db.Column(db.DateTime)
    time_maghrib = db.Column(db.DateTime)
    time_isha = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return f'ID {self.id}'
