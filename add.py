from app import db, Product, app

with app.app_context():
    if Product.query.count() == 0:
        products = [
            Product(name='pepsi', price=2, image='pepsi.png'),
            Product(name='water 1L', price=1, image='water1.png'),
            Product(name='water 5L', price=5, image='water2.png'),
            Product(name='sprite', price=2, image='spriteW.png'),
            
        ]
        db.session.add_all(products)
        db.session.commit()
        print("pop")
    else:
        print("not pop")