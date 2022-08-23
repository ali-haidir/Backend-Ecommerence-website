from marshmallow import (
    Schema, pre_load, pre_dump, post_load, post_dump, validates_schema,
    validates, fields, ValidationError
)


class User(Schema):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    age = db.Column(db.Integer)


class UserSchema(Schema):

    email = fields.Str(required=True)
    age = fields.Integer(required=True)

    @post_load
    def lowerstrip_email(self, item, many, **kwargs):
        item['email'] = item['email'].lower().strip()
        return item

    @pre_load(pass_many=True)
    def remove_envelope(self, data, many, **kwargs):
        namespace = 'results' if many else 'result'
        return data[namespace]

    @post_dump(pass_many=True)
    def add_envelope(self, data, many, **kwargs):
        namespace = 'results' if many else 'result'
        return {namespace: data}

    @validates_schema
    def validate_email(self, data, **kwargs):
        if len(data['email']) < 3:
            raise ValidationError(
                'Email must be more than 3 characters', 'email')

    @validates('age')
    def validate_age(self, data, **kwargs):
        if data < 14:
            raise ValidationError('Too young!')
