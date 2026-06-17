from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (800, 600), 'white')
draw = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("DejaVuSans.ttf", 40)
except:
    font = ImageFont.load_default()
draw.text((50, 50), "NOM DUPONT\nPrénom Jean\nDate de naissance 12/05/1980\nSalaire net : 500 000 FCFA\nEmployeur : ACME Corp", fill='black', font=font)
img.save('tests/good_document.png')
