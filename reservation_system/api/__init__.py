from .languages import Languages
from .notices import Notices
from .periods import Periods
from .reservations import Reservations, ResvPrivacy, ResvStatus
from .rooms import Rooms, RoomStatus, RoomTypes
from .sessions import Sessions
from .settings import Settings
from .users import UserRoles, Users


def init_api(app, spec):
    for path, view in (
        ('reservations'              , Reservations  ),
        ('reservations/status'       , ResvStatus    ),
        ('reservations/privacy'      , ResvPrivacy   ),
        ('users'                     , Users         ),
        ('users/roles'               , UserRoles     ),
        ('rooms'                     , Rooms         ),
        ('rooms/types'               , RoomTypes     ),
        ('rooms/status'              , RoomStatus    ),
        ('languages'                 , Languages     ),
        ('sessions'                  , Sessions      ),
        ('notices'                   , Notices       ),
        ('periods'                   , Periods       ),
        ('settings'                  , Settings      ),
    ): register_view(app, spec, path, view)

def register_view(app, spec, path, view):
    url = f'/api/{path}'
    method_view = view.as_view(path)

    app.add_url_rule(url, view_func=method_view)

    with app.test_request_context():
        spec.path(view=method_view)

__all__ = [
    'init_api', 'register_view',
    'Reservations', 'ResvPrivacy', 'ResvStatus',
    'Users', 'UserRoles',
    'Rooms', 'RoomTypes', 'RoomStatus',
    'Languages',
    'Sessions',
    'Notices',
    'Periods',
    'Settings',
]
