import requests
from bs4 import BeautifulSoup

url = "https://encuentraempleo.trabajo.gob.ec/socioEmpleo-war/paginas/aspirante/busquedaOferta.jsf"
cookies = {
    "JSESSIONID": "4028344d4bca14e9ca71fd0ff9e0",
    "NSC_JOmnkwatc53jecrcfmkoaierrq1sab2": "ffffffffc3a0560845525d5f4f58455e445a4a42378b"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Faces-Request": "partial/ajax",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://encuentraempleo.trabajo.gob.ec",
    "Referer": url
}

# Read ViewState from initial search_page.html
with open("search_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

view_state_el = soup.find('input', id=lambda x: x and 'ViewState' in x)
view_state = view_state_el.get('value') if view_state_el else ""
print("ViewState:", view_state[:50] + "...")

payload = {
    "javax.faces.partial.ajax": "true",
    "javax.faces.source": "FormSearch:j_idt128",
    "javax.faces.partial.execute": "FormSearch:todosLosFiltros",
    "javax.faces.partial.render": "formBuscaOferta",
    "FormSearch:j_idt128": "FormSearch:j_idt128",
    "FormSearch": "FormSearch",
    "FormSearch:ofertaNumero": "",
    "FormSearch:vacante": "",
    "FormSearch:fechaDesdeCal_input": "",
    "FormSearch:fechaHastaCal_input": "",
    "FormSearch:provincia_focus": "",
    "FormSearch:provincia_input": "-1",
    "FormSearch:tieneDiscapacidad": "2",
    "FormSearch:areaLaboral_focus": "",
    "FormSearch:areaLaboral_input": "-1",
    "FormSearch:remuneracion_focus": "",
    "FormSearch:remuneracion_input": "560618", # $1001 - $1500
    "FormSearch:conocimientosCargo": "",
    "FormSearch:entrevistaOnline": "false",
    "FormSearch:empleoVerdeId": "",
    "javax.faces.ViewState": view_state
}

print("Posting search request...")
response = requests.post(url, data=payload, cookies=cookies, headers=headers, timeout=20)
print("Status Code:", response.status_code)

with open("search_response.xml", "w", encoding="utf-8") as f:
    f.write(response.text)

if "<partial-response" in response.text:
    print("Success: Received partial response!")
    xml_soup = BeautifulSoup(response.text, 'xml')
    updates = xml_soup.find_all('update')
    for upd in updates:
        upd_id = upd.get('id')
        print(f"Update ID: {upd_id}")
        content = upd.text
        filename = f"update_{upd_id.replace(':', '_')}.html"
        with open(filename, "w", encoding="utf-8") as uf:
            uf.write(content)
        print(f"  Saved update content to {filename}")
else:
    print("Failed to receive partial response.")
