from geocoding import Geocoding

if __name__ == '__main__':

    # open Google Maps page with Firefox
    geocoder = Geocoding()

    addresses = [
        "https://goo.gl/maps/NEZ53Y5JMVNWMRk96",
        "https://www.google.com/maps/place/Manuel+Pires+Farias,+Lda./@40.345946,-8.432881,17z/data=!4m13!1m7!3m6!1s0x0:0x0!2zNDDCsDIwJzQ1LjQiTiA4wrAyNSc1OC40Ilc!3b1!8m2!3d40.345946!4d-8.432881!3m4!1s0xd2301cfc629b10b:0x1d54da10acaca039!8m2!3d40.3456717!4d-8.4333305?hl=pt-PT",
        "R. São João de Deus 12, 3430-009 Carregal do Sal",
        "3430-039 Carregal do Sal",
        "R. São João de Deus 19, 3430-035 Carregal do Sal",
        "Av. Estação 69, 3430-399 Carregal do Sal",
        "Av. Estação 69"
    ]

    for a in addresses:
        # search for a place on Google Maps
        coordinates = geocoder.search(a)

        # compute geohash
        geohash = geocoder.compute_geohash(coordinates[0], coordinates[1])
        
        print(f"\n\nAddress: {a}, \nCoordinates: {coordinates}, Geohash: {geohash}")
    
    geocoder.close_browser()
