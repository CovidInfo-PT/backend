import json
import unicodedata

f = open("saved_outputs/counties_by_district_geohashed_completed.json", "r")
encoding = "utf-8"

def remove_accents(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")

m_json = json.loads(f.read())
for k in m_json:
    m_json[k] = sorted(m_json[k], key = lambda el : remove_accents(el[0]))  



print(m_json)


writable_json = json.dumps(m_json, ensure_ascii=False).encode('utf8').decode("utf8")


# save to files
f_out = open("saved_outputs/counties_by_district_geohashed_completed.json", "w")
f_out.write(writable_json)
f_out.close()