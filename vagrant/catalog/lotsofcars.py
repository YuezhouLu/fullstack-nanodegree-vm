from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import *
import datetime

engine = create_engine('sqlite:///mygarage.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete Categories if exisitng.
session.query(Maker).delete()
# Delete Items if exisitng.
session.query(Model).delete()
# Delete Users if exisitng.
session.query(User).delete()


# Create fake users
user1 = User(name = "Karl Benz",
             email = "karlbenz@gmail.com",
             picture = "https://upload.wikimedia.org/wikipedia/commons/5/58/Carl_Benz.png")
session.add(user1)
session.commit()

user2 = User(name = "Karl Rapp",
             email = "karlrapp@gmail.com",
             picture = "https://upload.wikimedia.org/wikipedia/en/2/20/Portrait_of_Karl_Rapp_1911.jpg")
session.add(user2)
session.commit()

user3 = User(name = "August Horch",
             email = "augusthorch@gmail.com",
             picture = "https://upload.wikimedia.org/wikipedia/commons/0/0e/Horch.gif")
session.add(user3)
session.commit()

user4 = User(name = "Ferdinand Porsche",
             email = "ferdinandporsche@gmail.com",
             picture = "https://upload.wikimedia.org/wikipedia/commons/f/fb/Bundesarchiv_Bild_183-2005-1017-525%2C_Dr._Ferdinand_Porsche.jpg")
session.add(user4)
session.commit()

user5 = User(name = "Alfieri Maserati",
             email = "alfierimaserati@gmail.com",
             picture = "https://upload.wikimedia.org/wikipedia/it/3/3b/Alfieri_Maserati.JPG")
session.add(user5)
session.commit()


# Create fake makers
maker1 = Maker(name = "Mercedes-Benz",
               user_id = 1,
               logo = "https://cdn.freebiesupply.com/logos/large/2x/mercedes-benz-9-logo-png-transparent.png")
session.add(maker1)
session.commit()

maker2 = Maker(name = "BMW",
               user_id = 2,
               logo = "https://cdn.freebiesupply.com/logos/large/2x/bmw-logo-png-transparent.png")
session.add(maker2)
session.commit()

maker3 = Maker(name = "Audi",
               user_id = 3,
               logo = "https://listcarbrands.com/wp-content/uploads/2015/10/logo-Audi-600x203.png")
session.add(maker3)
session.commit()

maker4 = Maker(name = "Porsche",
               user_id = 4,
               logo = "http://www.car-logos.org/wp-content/uploads/2011/09/porsche.png")
session.add(maker4)
session.commit()

maker5 = Maker(name = "Maserati",
               user_id = 5,
               logo = "https://cdn.freebiesupply.com/logos/large/2x/maserati-4-logo-png-transparent.png")
session.add(maker5)
session.commit()


# Create fake models
model1 = Model(name = "S63",
               date = datetime.datetime.now(),
               description = "AMG S Class Coupe",
               photo = "https://www.mercedes-amg.com/dam/hq/model-pages/Vehicles/S-class/Coupe/S63/Facelift/C217_ext_AMG16220_sx027_ext_comp_v007_an_hd.jpg/_jcr_content/renditions/original.image_file.1920.1080.file/C217_ext_AMG16220_sx027_ext_comp_v007_an_hd.jpg",
               maker_id = 1,
               user_id = 1)
session.add(model1)
session.commit()

model2 = Model(name = "G63",
               date = datetime.datetime.now(),
               description = "AMG G Class Wagon",
               photo = "https://hips.hearstapps.com/amv-prod-cad-assets.s3.amazonaws.com/images/18q1/699329/2019-mercedes-amg-g63-official-photos-and-info-news-car-and-driver-photo-702294-s-original.jpg?crop=1xw:1xh;center,center&resize=900:*",
               maker_id = 1,
               user_id = 1)
session.add(model2)
session.commit()

model3 = Model(name = "GT63",
               date = datetime.datetime.now(),
               description = "AMG GT 4-Door Coupe",
               photo = "https://www.mercedes-benz.com/wp-content/uploads/sites/3/2018/03/01-mercedes-benz-gims-2018-mercedes-amg-gt-63-s-4matic-4-door-coupe-x-290-3400x1440.jpg",
               maker_id = 1,
               user_id = 1)
session.add(model3)
session.commit()

model4 = Model(name = "M850i",
               date = datetime.datetime.now(),
               description = "8 Series Coupe",
               photo = "https://hips.hearstapps.com/hmg-prod/images/2019-bmw-8-series-placement-1529009458.jpg?crop=1xw:1xh;center,center&resize=900:*",
               maker_id = 2,
               user_id = 2)
session.add(model4)
session.commit()

model5 = Model(name = "M760Li xDrive",
               date = datetime.datetime.now(),
               description = "7 Series Saloon",
               photo = "https://i.ytimg.com/vi/z4mST1T1RTw/maxresdefault.jpg",
               maker_id = 2,
               user_id = 2)
session.add(model5)
session.commit()

model6 = Model(name = "i8",
               date = datetime.datetime.now(),
               description = "i Model 8 Series Roadster",
               photo = "http://cdni.autocarindia.com/Galleries/20180430104048_24-bmw-i8-roadster-2018-review-static-front-doors.jpg",
               maker_id = 2,
               user_id = 2)
session.add(model6)
session.commit()

model7 = Model(name = "R8",
               date = datetime.datetime.now(),
               description = "R8 V10 Plus Coupe",
               photo = "https://carwow-uk-wp-3.imgix.net/R8_Lead_2.jpg",
               maker_id = 3,
               user_id = 3)
session.add(model7)
session.commit()

model8 = Model(name = "Q8",
               date = datetime.datetime.now(),
               description = "Q Series SUV",
               photo = "https://cdn.gearpatrol.com/wp-content/uploads/2018/06/2019-Audi-Q8-SUV-gear-patrol-slide-1-1940x1300.jpg",
               maker_id = 3,
               user_id = 3)
session.add(model8)
session.commit()

model9 = Model(name = "A7",
               date = datetime.datetime.now(),
               description = "A Series 4-Door Coupe",
               photo = "https://car-images.bauersecure.com/pagefiles/77040/audi-a7-021.jpg",
               maker_id = 3,
               user_id = 3)
session.add(model9)
session.commit()

model10 = Model(name = "911 Turbo S",
                date = datetime.datetime.now(),
                description = "911 Coupe",
                photo = "https://robbreportedit.files.wordpress.com/2017/06/118.jpg?w=1024",
                maker_id = 4,
                user_id = 4)
session.add(model10)
session.commit()

model11 = Model(name = "Cayenne S",
                date = datetime.datetime.now(),
                description = "Cayenne SUV",
                photo = "https://autoweek.com/sites/default/files/styles/gen-1200-675/public/p-1_15.jpg?itok=_kL-hcgb",
                maker_id = 4,
                user_id = 4)
session.add(model11)
session.commit()

model12 = Model(name = "Panamera 4S",
                date = datetime.datetime.now(),
                description = "Panamera 4WD Sport Turismo Sedan",
                photo = "https://autoweek.com/sites/default/files/styles/gen-1200-675/public/p16_0380_a5_rgb_0.jpg?itok=RCxa78_6",
                maker_id = 4,
                user_id = 4)
session.add(model12)
session.commit()

model13 = Model(name = "GranTurismo MC",
                date = datetime.datetime.now(),
                description = "GranTourismo - The Purest form of excitement Coupe",
                photo = "https://s3.caradvice.com.au/thumb/960/500/wp-content/uploads/2015/10/Maserati-GranTurismo-MC-Sportline-4.jpg",
                maker_id = 5,
                user_id = 5)
session.add(model13)
session.commit()

model14 = Model(name = "Quattraporte GTS GranLusso",
                date = datetime.datetime.now(),
                description = "Quattroporte - The Original Race-bred Fullsize Luxury Sedan",
                photo = "https://recombu-content.imgix.net/app/uploads/maserati-quattroporte-gts-review-2018-1.jpg?auto=format%2Cenhance%2Ccompress",
                maker_id = 5,
                user_id = 5)
session.add(model14)
session.commit()

model15 = Model(name = "Ghibli SQ4 GranSport",
                date = datetime.datetime.now(),
                description = "Ghibli - Midsize 4WD Luxury Sedan",
                photo = "https://5592772ccb70adb2913a-68db0d70b18191ad4280569d1f5de99f.ssl.cf1.rackcdn.com/ZAM57YTS8J1260067/c5d6a582895aeb0a896fb4793cd582e3.jpg",
                maker_id = 5,
                user_id = 5)
session.add(model15)
session.commit()


print "Your Garage is fully loaded!!!"