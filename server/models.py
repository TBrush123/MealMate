from sqlalchemy.dialects.postgresql import JSONB
from extensions import db

user_dietary_restrictions = db.Table('user_dietary_restrictions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('restriction_id', db.Integer, db.ForeignKey('dietary_restrictions.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    dietary_restrictions = db.relationship(
        'DietaryRestriction', 
        secondary=user_dietary_restrictions, 
        backref='users'
    )

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
        return f'<FridgeItem {self.quantity} {self.unit} of {self.ingredient.name} for {self.user.username}>'

class DietaryRestriction(db.Model):
    __tablename__ = 'dietary_restrictions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

    def __repr__(self):
        return f'<DietaryRestriction {self.name}>'

class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    user_id = db.Column(db.Integer, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<RevokedToken {self.jti} for user {self.user_id}>'