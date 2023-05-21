from reservation_system.api import register_view
from reservation_system.user_api import reservation, user, views


def init_api(app, spec):
    for path, view in (
        ('user'                                        , views.User                ),
        ('user/reservation'                            , views.GetPostReservation  ),
        ('user/reservation/<int:resv_id>'              , views.PatchReservation    ),
        ('user/reservation/<int:resv_id>/<int:slot_id>', views.PatchReservationSlot),
        ('user/reservation/advanced'                   , views.AdvancedResv        ),
    ): register_view(app, spec, path, view)

__all__ = ['init_api', 'user', 'reservation']