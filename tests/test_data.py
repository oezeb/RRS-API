from data import insert_data
def test_data(app):
    with app.app_context():
        insert_data()