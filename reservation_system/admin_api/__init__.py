from reservation_system.api import register_view
from reservation_system.admin_api import views
from reservation_system.api import views as api_views
from reservation_system import db

# def init_api(app, spec):
#     for path, view in (
#         ('reservations'              , views.GetPostReservations  ),
#         ('reservations/<int:resv_id>', views.PatchReservation    ),
#         ('reservations/<int:resv_id>/<int:slot_id>', views.PatchReservationSlot),
#         ('reservations/status'       , views.GetReservationStatus ),
#         ('reservations/status/<int:status>', views.PatchReservationStatus),
#         ('reservations/privacy'      , views.GetReservationPrivacy),
#         ('reservations/privacy/<int:privacy>', views.PatchReservationPrivacy),
#         ('users'                     , views.GetPostUsers         ),
#         ('users/<string:username>'   , views.PatchUser            ),
#         ('users/roles'               , views.GetUserRoles        ),
#         ('users/roles/<int:role>'    , views.PatchUserRole       ),
#         # ('users/roles'               , UserRoles     ),
#         # ('rooms'                     , Rooms         ),
#         # ('rooms/types'               , RoomTypes     ),
#         # ('rooms/status'              , RoomStatus    ),
#         # ('languages'                 , Languages     ),
#         # ('sessions'                  , Sessions      ),
#         # ('notices'                   , Notices       ),
#         ('periods'                   , views.GetPostPeriods      ),
#         # ('periods/<int:id>'          , PatchDeletePeriod   ),
#         ('settings'                  , views.GetSettings      ),
#         ('settings/<int:id>'         , views.PatchSetting   ),
#     ): register_view(app, spec, 'admin/'+path, view)

def init_api(app, spec):
    for path, view in (
        ('reservations'              , views.GetPostReservations  ),
        ('reservations/status'       , api_views.ResvStatus    ),
        ('reservations/privacy'      , api_views.ResvPrivacy   ),
        ('users'                     , views.GetPostUsers         ),
        ('users/roles'               , api_views.UserRoles     ),
        ('rooms'                     , api_views.Rooms         ),
        ('rooms/types'               , api_views.RoomTypes     ),
        ('rooms/status'              , api_views.RoomStatus    ),
        ('languages'                 , api_views.Languages     ),
        ('sessions'                  , api_views.Sessions      ),
        ('notices'                   , api_views.Notices       ),
        ('periods'                   , api_views.Periods       ),
        ('settings'                  , api_views.Settings      ),
    ): register_view(app, spec, 'admin/'+path, view)

def update(table, data, **where):
    if len(data) > 0:
        db.update(table, data, **where)
    return {}, 204

def delete(table, **where):
    db.delete(table, **where)
    return {}, 204

__all__ = ['init_api', 'update', 'delete']
