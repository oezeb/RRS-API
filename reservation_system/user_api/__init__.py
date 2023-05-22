from reservation_system.util import register_blueprint

from . import user, reservation

def init_api(app, spec):
    for module in (
        user, 
        reservation,
    ): register_blueprint(app, spec, module)

__all__ = ['init_api']