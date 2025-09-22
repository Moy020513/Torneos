from django.core.management.base import BaseCommand
from django.conf import settings
import os
from PIL import Image
from ...models import Torneo

class Command(BaseCommand):
    help = 'Comprime todas las imágenes existentes en el directorio media y actualiza colores de torneos'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        self.stdout.write(f'Comenzando compresión de imágenes en {media_root}')
        
        compressed_count = 0
        for root, dirs, files in os.walk(media_root):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    filepath = os.path.join(root, file)
                    try:
                        img = Image.open(filepath)
                        # Comprimir
                        if img.format == 'JPEG':
                            img.save(filepath, quality=85, optimize=True)
                        elif img.format == 'PNG':
                            img.save(filepath, optimize=True)
                        compressed_count += 1
                        self.stdout.write(f'Comprimido: {filepath}')
                    except Exception as e:
                        self.stderr.write(f'Error al comprimir {filepath}: {e}')
        
        self.stdout.write(f'Compresión completada. {compressed_count} imágenes procesadas.')
        
        # Actualizar colores de torneos
        torneos = Torneo.objects.filter(logo__isnull=False)
        updated = 0
        for torneo in torneos:
            try:
                img = Image.open(torneo.logo.path)
                img_rgb = img.convert('RGB')
                img_quant = img_rgb.quantize(colors=256)
                colors = img_quant.getcolors()
                palette = img_quant.getpalette()
                if colors and palette:
                    colors.sort(reverse=True, key=lambda x: x[0])
                    unique_colors = []
                    seen = set()
                    for count, index in colors:
                        rgb = (palette[index*3], palette[index*3+1], palette[index*3+2])
                        if rgb not in seen:
                            unique_colors.append(rgb)
                            seen.add(rgb)
                        if len(unique_colors) == 3:
                            break
                    color1 = '#%02x%02x%02x' % unique_colors[0] if len(unique_colors) >= 1 else None
                    color2 = '#%02x%02x%02x' % unique_colors[1] if len(unique_colors) >= 2 else (color1 if color1 else None)
                    color3 = '#%02x%02x%02x' % unique_colors[2] if len(unique_colors) >= 3 else color2
                else:
                    color1 = color2 = color3 = None
                torneo.__class__.objects.filter(pk=torneo.pk).update(color1=color1, color2=color2, color3=color3)
                updated += 1
                self.stdout.write(f'Colores actualizados para torneo: {torneo.nombre}')
            except Exception as e:
                self.stderr.write(f'Error al actualizar colores para {torneo.nombre}: {e}')
        
        self.stdout.write(f'Actualización de colores completada. {updated} torneos actualizados.')