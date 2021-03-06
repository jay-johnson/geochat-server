import json

import geoalchemy2
import geoalchemy2.shape
import sqlalchemy
import sqlalchemy.orm

import geochat.ormbase
import geochat.user


def get_all(session):
    return session.query(
        Message,
        # sqlalchemy.func.ST_AsGeoJSON(Message.location).label('location'),
    )


def get_local(session, location):
    return session.query(
        Message,
        # sqlalchemy.func.ST_AsGeoJSON(Message.location).label('location'),
    ).filter(
        sqlalchemy.func.ST_DWITHIN(Message.location, location, 1000)
    )


class Message(geochat.ormbase.Base):
    """A chat message."""

    __tablename__ = 'messages'

    id = sqlalchemy.Column(
        sqlalchemy.BigInteger,
        sqlalchemy.Sequence('messages_id_seq'),
        primary_key=True,
    )
    user_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    created = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))
    body = sqlalchemy.Column(sqlalchemy.Text)
    location = sqlalchemy.Column(geoalchemy2.Geography(geometry_type='POINT', srid=4326))

    user = sqlalchemy.orm.relationship(
        geochat.user.User,
        backref=sqlalchemy.orm.backref('messages', order_by=id),
    )

    def location_as_shape(self):
        return geoalchemy2.shape.to_shape(self.location)

    def to_json_object(self):
        return {
            'data_type': 'message',
            'data': {
                'id': self.id,
                'created': self.created.ctime(),
                'author': self.user.name,
                'body': self.body,
                'location_wkt': str(self.location_as_shape()),
            }
        }
