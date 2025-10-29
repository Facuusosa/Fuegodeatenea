import os
import django
import cloudinary
import cloudinary.uploader

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Miprimerapaginafsosa.settings')
django.setup()

from appcoder.models import Sahumerio

# Configurar Cloudinary con el cloud_name CORRECTO
cloudinary.config(
    cloud_name='dp127mtyg',  # <-- CORRECCIÓN AQUÍ
    api_key='457672287445357',
    api_secret='M0yCtiC0xjONbxM00K00zhsrr58'
)

def subir_imagenes():
    productos = Sahumerio.objects.all()
    
    print(f"📦 Encontrados {productos.count()} productos")
    
    for producto in productos:
        if producto.imagen_file:
            try:
                ruta_local = producto.imagen_file.path
                
                if os.path.exists(ruta_local):
                    print(f"⬆️  Subiendo: {producto.nombre}...")
                    
                    # Subir a Cloudinary
                    resultado = cloudinary.uploader.upload(
                        ruta_local,
                        folder="productos",
                        public_id=producto.nombre.replace(' ', '_')
                    )
                    
                    # Actualizar el producto con la URL de Cloudinary
                    producto.imagen_url = resultado['secure_url']
                    producto.save()
                    
                    print(f"✅ {producto.nombre} subido correctamente")
                    print(f"   URL: {resultado['secure_url']}")
                else:
                    print(f"⚠️  Archivo no encontrado: {producto.nombre}")
                    
            except Exception as e:
                print(f"❌ Error con {producto.nombre}: {str(e)}")
    
    print("\n🎉 ¡Proceso completado!")

if __name__ == '__main__':
    subir_imagenes()
