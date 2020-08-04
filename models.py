from app import db


class Texts_For_Index(db.Model):
    __tablename__ = 'texts_for_index'
    id_ = db.Column(db.Integer, primary_key=True, name="id")
    title = db.Column(db.String())
    description = db.Column(db.String())
    button_name = db.Column(db.String())


class Text_For_Indexes:
    def __init__(self, title, description, button_name):
        self.title = title
        self.description = description
        self.button_name = button_name
