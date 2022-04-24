import requests

def consultar_libro(isbn):
    #isbn = "0061351423"
    url = f'https://www.googleapis.com/books/v1/volumes?q='+isbn
    r = requests.get(url).json()

    #data = json.loads(r.text)

    infob = {}

    if int(r["totalItems"]) < 1:
        infob["contador"] = 0
        return infob
    
    infob["contador"] = 1
    info_libro = r["items"][0]["volumeInfo"]
    print(info_libro)

    infob["averagerating"] = info_libro.get("averageRating")
    infob["ratingscount"] = info_libro.get("ratingsCount")

    infob["image"] = info_libro["imageLinks"]["thumbnail"]

    return infob