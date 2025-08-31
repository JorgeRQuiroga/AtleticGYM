# AtleticGYM  
## Intrucciones para el git clone  
Primero ejecutar  
'''
git clone https://github.com/JorgeRQuiroga/AtleticGYM
'''  

Despues crear el entorno virtual  

'''
python -m venv "nombre del entorno virtual"
'''  

Para activar el entorno virtual  

'''
source nombre_del_entorno/Script/activate
'''

En el entorno virtual ejecutar

'''
pip install -r requirements.txt
'''  

Por ultimo cambien el settings.py lo de la base de datos para que no les genere errores  

# Para añadir los modelos a la base de datos  

'''
    python manage.py inspectdb > nombre_de_la_app/models.py
'''

