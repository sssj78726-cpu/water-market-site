from app import db, Product, app

with app.app_context():
    if Product.query.count() == 3:
        products = [
            Product(name='pepsi', price=2, image='pepsi.png'),
        ]
        db.session.add_all(products)
        db.session.commit()
        print("pop")
    else:
        print("not pop")