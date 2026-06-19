import requests
from bs4 import BeautifulSoup
import json
import time
import os

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

# Salary ranges above 1000 USD
salary_ranges = {
    "560618": "$1001 - $1500",
    "560619": "$1501 - $2000",
    "562154": "$2001 - $2500",
    "562155": "$2501 - $3000",
    "562156": "$3001 - $4000",
    "562157": "$4001 - $5000",
    "562158": "Más de $ 5001"
}

# Excluded keywords in titles (we don't have matching professional degrees/licenses)
excluded_keywords = [
    "enfermero", "enfermera", "medico", "médico", "odontologo", "odontóloga", 
    "psicologo", "psicóloga", "chofer", "conductor", "obstetriz", "obstetra",
    "terapista", "fisioterapeuta", "odontología", "enfermería", "médica",
    "parvulario", "educación inicial", "mecanico", "mecánico", "soldador",
    "electricista", "albañil", "guardia", "policia", "policía", "militar"
]

def get_initial_view_state():
    with open("search_page.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    view_state_el = soup.find('input', id=lambda x: x and 'ViewState' in x)
    return view_state_el.get('value') if view_state_el else ""

def get_view_state_from_xml(xml_text):
    xml_soup = BeautifulSoup(xml_text, 'xml')
    for upd in xml_soup.find_all('update'):
        if 'ViewState' in upd.get('id', ''):
            return upd.text
    return None

def parse_jobs_from_html(html_soup, salary_code, salary_label, page_num):
    jobs = []
    fieldsets = html_soup.find_all('fieldset', class_=lambda val: val and 'fieldsetOferta' in val)
    for idx, fs in enumerate(fieldsets):
        text = fs.get_text(separator="|").strip()
        parts = [p.strip() for p in text.split('|') if p.strip()]
        
        # Determine the trigger element (the <a> link wrapping the fieldset or inside it)
        a_tag = fs.find_parent('a') or fs.find('a')
        if not a_tag:
            # Let's search surrounding elements
            a_tag = fs.find_previous('a')
            
        link_id = a_tag.get('id') if a_tag else f"formBuscaOferta:listResult:{idx}:j_idt65" # fallback guess
        
        title = ""
        company = ""
        code = ""
        location = ""
        
        if len(parts) >= 4:
            company = parts[0]
            title = parts[1]
            code = parts[2]
            # Find salary and location
            for p in parts[3:]:
                if "remuneración" in p.lower() or "remuneracion" in p.lower():
                    pass
                elif "hace:" in p.lower() or "dias" in p.lower():
                    location = p.split("HACE:")[0].strip()
        
        # Clean title & company
        title = title.strip()
        company = company.strip()
        code = code.strip()
        location = location.strip()
        
        # Check exclusion
        title_lower = title.lower()
        excluded = False
        for kw in excluded_keywords:
            if kw in title_lower:
                excluded = True
                break
                
        # Determine suitability
        suitability = "Alto"
        reason = "Alineado con perfil profesional e instrucción superior."
        
        title_words = ["desarrollador", "sistemas", "computación", "tecnología", "informática", "programación", "redes", "seguridad", "ciberseguridad", "docente", "profesor", "analista", "proyecto", "coordinador", "director", "administrador", "lider", "líder", "jefe"]
        is_it_or_mgmt = any(w in title_lower for w in title_words)
        
        if not is_it_or_mgmt:
            suitability = "Medio"
            reason = "Rol no especializado en TI, pero realizable con destrezas profesionales generales."
            
        if excluded:
            suitability = "Excluido"
            reason = "Requiere título especializado o licencia que no posee el candidato."
            
        jobs.append({
            "title": title,
            "company": company,
            "code": code,
            "location": location,
            "salary_range": salary_label,
            "salary_code": salary_code,
            "page": page_num,
            "link_id": link_id,
            "suitability": suitability,
            "reason": reason,
            "details": {}
        })
    return jobs

def fetch_job_details(job, current_view_state):
    payload = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": job["link_id"],
        "javax.faces.partial.execute": job["link_id"],
        "javax.faces.partial.render": "formVerOferta",
        job["link_id"]: job["link_id"],
        "formBuscaOferta": "formBuscaOferta",
        "formBuscaOferta:pagina_focus": "",
        "formBuscaOferta:pagina_input": str(job["page"]),
        "javax.faces.ViewState": current_view_state
    }
    
    print(f"  Fetching details for {job['title']} ({job['code']})...")
    res = requests.post(url, data=payload, cookies=cookies, headers=headers, timeout=15)
    
    new_view_state = get_view_state_from_xml(res.text) or current_view_state
    
    xml_soup = BeautifulSoup(res.text, 'xml')
    update_tags = xml_soup.find_all('update', id='formVerOferta')
    if update_tags:
        html_content = update_tags[0].text
        html_soup = BeautifulSoup(html_content, 'html.parser')
        
        # Parse fields from the modal
        details = {}
        
        # Helper to find fields based on text labels
        for label_text in ["Cargo solicitado:", "Tipo Contrato:", "Ciudad:", "Parroquia:", "Sector:", "Fecha inicio publicación:", "Fecha finalización:", "Contacto:", "Teléfono:", "Correo electrónico:", "Instrucción:", "Experiencia:", "Conocimientos del cargo:", "Actividades a Desempeñar:", "Número de cargos solicitados:"]:
            label_el = html_soup.find(text=lambda t: t and label_text in t)
            if label_el:
                # The value is usually in the next cell or sibling element
                parent = label_el.parent
                val = ""
                # Let's find the text sibling or next td
                tds = parent.find_next_siblings('td') or parent.find_parent('td').find_next_siblings('td') if parent.name != 'td' else parent.find_next_siblings('td')
                if tds:
                    val = tds[0].text.strip()
                else:
                    # try next element
                    val = parent.get_text().replace(label_text, "").strip()
                details[label_text.replace(":", "").strip()] = val
                
        # Also extract postulation button IDs inside formVerOferta
        apply_btn = html_soup.find('button', text=lambda t: t and 'Aplicar' in t)
        if apply_btn:
            details["apply_button_id"] = apply_btn.get('id')
            details["apply_button_onclick"] = apply_btn.get('onclick')
            
        accept_btn = html_soup.find('button', text=lambda t: t and 'Aceptar' in t)
        if accept_btn:
            details["accept_button_id"] = accept_btn.get('id')
            details["accept_button_onclick"] = accept_btn.get('onclick')
            
        job["details"] = details
        
    return new_view_state

def run():
    current_view_state = get_initial_view_state()
    all_jobs = []
    
    for sal_code, sal_label in salary_ranges.items():
        print(f"\nSearching for salary range: {sal_label} (code {sal_code})...")
        
        # Initial search for this salary range
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
            "FormSearch:remuneracion_input": sal_code,
            "FormSearch:conocimientosCargo": "",
            "FormSearch:entrevistaOnline": "false",
            "FormSearch:empleoVerdeId": "",
            "javax.faces.ViewState": current_view_state
        }
        
        res = requests.post(url, data=payload, cookies=cookies, headers=headers, timeout=15)
        new_vs = get_view_state_from_xml(res.text)
        if new_vs:
            current_view_state = new_vs
            
        # Parse search results page 1
        xml_soup = BeautifulSoup(res.text, 'xml')
        update_tag = xml_soup.find('update', id='formBuscaOferta')
        if not update_tag:
            print("  No search results container found.")
            continue
            
        html_soup = BeautifulSoup(update_tag.text, 'html.parser')
        
        # Find how many pages there are
        select_pages = html_soup.find('select', id='formBuscaOferta:pagina_input')
        total_pages = 1
        if select_pages:
            options = select_pages.find_all('option')
            total_pages = len(options)
            
        print(f"  Found {total_pages} pages of results.")
        
        # Parse Page 1 jobs
        jobs_p1 = parse_jobs_from_html(html_soup, sal_code, sal_label, 1)
        print(f"  Parsed {len(jobs_p1)} jobs on Page 1.")
        all_jobs.extend(jobs_p1)
        
        # Loop through pages 2 to total_pages
        for p in range(2, total_pages + 1):
            print(f"  Navigating to Page {p}...")
            page_payload = {
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": "formBuscaOferta:pagina",
                "javax.faces.partial.event": "valueChange",
                "javax.faces.partial.execute": "formBuscaOferta:pagina",
                "javax.faces.partial.render": "formBuscaOferta",
                "formBuscaOferta:pagina_input": str(p),
                "formBuscaOferta:pagina_focus": "",
                "formBuscaOferta": "formBuscaOferta",
                "javax.faces.ViewState": current_view_state
            }
            res_page = requests.post(url, data=page_payload, cookies=cookies, headers=headers, timeout=15)
            
            new_vs = get_view_state_from_xml(res_page.text)
            if new_vs:
                current_view_state = new_vs
                
            xml_soup_page = BeautifulSoup(res_page.text, 'xml')
            update_tag_page = xml_soup_page.find('update', id='formBuscaOferta')
            if update_tag_page:
                html_soup_page = BeautifulSoup(update_tag_page.text, 'html.parser')
                jobs_pn = parse_jobs_from_html(html_soup_page, sal_code, sal_label, p)
                print(f"  Parsed {len(jobs_pn)} jobs on Page {p}.")
                all_jobs.extend(jobs_pn)
            
            time.sleep(1) # politely sleep
            
    print(f"\nTotal jobs parsed: {len(all_jobs)}")
    
    # Let's filter candidates (Suitability: Alto or Medio)
    candidates = [j for j in all_jobs if j["suitability"] in ["Alto", "Medio"]]
    print(f"Candidate jobs matching suitability (Alto/Medio): {len(candidates)}")
    
    # Fetch details for candidates
    for i, job in enumerate(candidates):
        try:
            current_view_state = fetch_job_details(job, current_view_state)
            time.sleep(1)
        except Exception as e:
            print(f"  Error fetching details for {job['title']}: {e}")
            
    # Save the parsed jobs to data/high_salary_jobs.json
    os.makedirs("data", exist_ok=True)
    with open("data/high_salary_jobs.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    print("\nSaved jobs list to data/high_salary_jobs.json")
    
    # Generate markdown report
    report_path = "reports/high_salary_jobs.md"
    os.makedirs("reports", exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Reporte de Ofertas Laborales (+1000 USD)\n\n")
        f.write(f"**Fecha de Análisis:** 2026-06-04\n")
        f.write(f"**Residencia Candidato:** Loja, Loja, Ecuador (con disponibilidad de traslado)\n\n")
        
        f.write("## Candidatos de Alta Idoneidad (TI, Educación, Gestión)\n\n")
        high_jobs = [j for j in candidates if j["suitability"] == "Alto"]
        if not high_jobs:
            f.write("*No se encontraron ofertas de alta idoneidad.*\n")
        for j in high_jobs:
            details = j["details"]
            f.write(f"### {j['title']} ({j['code']})\n")
            f.write(f"- **Empresa/Institución:** {j['company']}\n")
            f.write(f"- **Remuneración:** {j['salary_range']}\n")
            f.write(f"- **Ubicación:** {j['location']}\n")
            f.write(f"- **Contacto:** {details.get('Contacto', 'N/A')} - Tel: {details.get('Teléfono', 'N/A')} - Email: {details.get('Correo electrónico', 'N/A')}\n")
            f.write(f"- **Requisitos de Experiencia:** {details.get('Experiencia', 'N/A')}\n")
            f.write(f"- **Instrucción Mínima:** {details.get('Instrucción', 'N/A')}\n")
            f.write(f"- **Actividades:** {details.get('Actividades a Desempeñar', 'N/A')}\n")
            f.write(f"- **Conocimientos:** {details.get('Conocimientos del cargo', 'N/A')}\n")
            if "apply_button_id" in details:
                f.write(f"- **Postulación Directa:** Disponible (`{details['apply_button_id']}`)\n")
            f.write("\n")
            
        f.write("## Candidatos de Idoneidad Media (Administrativos, Gestión General)\n\n")
        mid_jobs = [j for j in candidates if j["suitability"] == "Medio"]
        if not mid_jobs:
            f.write("*No se encontraron ofertas de idoneidad media.*\n")
        for j in mid_jobs:
            details = j["details"]
            f.write(f"### {j['title']} ({j['code']})\n")
            f.write(f"- **Empresa/Institución:** {j['company']}\n")
            f.write(f"- **Remuneración:** {j['salary_range']}\n")
            f.write(f"- **Ubicación:** {j['location']}\n")
            f.write(f"- **Contacto:** {details.get('Contacto', 'N/A')} - Tel: {details.get('Teléfono', 'N/A')} - Email: {details.get('Correo electrónico', 'N/A')}\n")
            f.write(f"- **Requisitos de Experiencia:** {details.get('Experiencia', 'N/A')}\n")
            f.write(f"- **Instrucción Mínima:** {details.get('Instrucción', 'N/A')}\n")
            f.write(f"- **Actividades:** {details.get('Actividades a Desempeñar', 'N/A')}\n")
            f.write(f"- **Conocimientos:** {details.get('Conocimientos del cargo', 'N/A')}\n")
            if "apply_button_id" in details:
                f.write(f"- **Postulación Directa:** Disponible (`{details['apply_button_id']}`)\n")
            f.write("\n")
            
        f.write("## Ofertas Excluidas (No corresponden al perfil)\n\n")
        ex_jobs = [j for j in all_jobs if j["suitability"] == "Excluido"]
        f.write(f"Se excluyeron **{len(ex_jobs)}** ofertas debido a requisitos especializados (por ejemplo, salud, conducción profesional o metalmecánica).\n")
        
    print(f"Generated report at {report_path}")

if __name__ == "__main__":
    run()
