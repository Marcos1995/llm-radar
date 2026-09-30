"""Escribe data/items.json. Es LO UNICO especifico de cada proyecto: reemplaza este fichero entero.

Contrato: lista de objetos
  {"slug": "kebab-case", "title": str, "summary": str,
   "facts": [["etiqueta", "valor"], ...],   # >=3 datos propios por pagina o se marca noindex
   "group": str (opcional), "updated": "YYYY-MM-DD" (opcional), "source": url (opcional)}

Reglas: solo fuentes publicas y estables, stdlib (urllib) salvo necesidad real, una peticion
ligera por recurso, sin claves de pago. Si una fuente falla: sys.exit(1) y NO tocar data/.
Historico (tendencias): lee el data/items.json anterior antes de sobrescribirlo.
Escribe con json.dumps(ensure_ascii=False, indent=1).
"""
print("fetch.py sin implementar; el workflow no despliega hasta que exista data/items.json")
