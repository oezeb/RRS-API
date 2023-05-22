from reservation_system.util import register_blueprint

from . import (
    languages, 
    notices, 
    periods, 
    reservations, 
    rooms, 
    sessions,
    settings, 
    users,
)

def init_api(app, spec):
    for module in (
        languages, 
        notices, 
        periods, 
        reservations, 
        rooms, 
        sessions,
        settings, 
        users,
    ): register_blueprint(app, spec, module)

__all__ = ['init_api']
