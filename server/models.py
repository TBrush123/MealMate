from sqlalchemy.dialects.postgresql import JSONB
from extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    dietary_restrictions = db.Column(JSONB, default=list)

    def __repr__(self):
        return f'<User {self.username}>'

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(60), nullable=False)


    def __repr__(self):
        return f'<Ingredient {self.name}>'

class FridgeItem(db.Model):
    __tablename__ = 'fridgeItems'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    user = db.relationship('User', backref=db.backref('fridgeItems', lazy=True))
    ingredient = db.relationship('Ingredient', backref=db.backref('fridgeItems', lazy=True))

    def __repr__(self):
        return f'<FridgeItem {self.quantity} {self.unit} of {self.ingredient.name} for {self.user.name}>'