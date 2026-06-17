import re
text = "NOM DUPONT\nPrénom Jean\nDate de naissance 12/05/1980\nSalaire net : 500 000 FCFA\nEmployeur : ACME Corp"

nom_match = re.search(r'\bnom[\s:]*([A-Za-zÀ-ÿ]+)', text, re.IGNORECASE)
prenom_match = re.search(r'\bpr[eéè]nom[\s:]*([A-Za-zÀ-ÿ]+)', text, re.IGNORECASE)
emp_match = re.search(r'(?:employeur|raison sociale)[\s:]*([A-Za-z0-9\sÀ-ÿ]+)', text, re.IGNORECASE)
rev_match = re.search(r'(?:salaire|net[ \w]*payer|revenu)[^\d]*([\d\s]+)', text, re.IGNORECASE)

print("NOM:", nom_match.group(1) if nom_match else None)
print("PRENOM:", prenom_match.group(1) if prenom_match else None)
print("EMPLOYEUR:", emp_match.group(1) if emp_match else None)
print("REVENUS:", rev_match.group(1) if rev_match else None)
