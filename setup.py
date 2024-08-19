from setuptools import setup, find_packages

setup(
    name='opdproblem',  # Cambia esto por el nombre de tu paquete
    version='0.1',              # Cambia esto por la versión inicial de tu paquete
    author='Carlos Lazo',         # Cambia esto por tu nombre
    author_email='clazo2018@udec.cl',  # Cambia esto por tu email
    description='Implmentation of the Optimal Path Discovery problem with networkX and experiments with some algorithms to solve it.',  # Descripción corta del paquete
    long_description=open('README.md').read(),  # Lee el archivo README.md para la descripción larga
    long_description_content_type='text/markdown',
    url='https://github.com/clazo2018/OPD-problem-',  # URL a la página del proyecto (opcional)
    packages=find_packages(),  # Encuentra todos los paquetes en el proyecto
    classifiers=[  # Clasificadores para ayudar a otros a encontrar tu paquete
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.11',  # Especifica la versión mínima de Python requerida
    install_requires=[  # Lista de dependencias necesarias para tu paquete
        'networkx',
        'pandas',
        'matplotlib',
        'tqdm',
        # Agrega aquí otras dependencias necesarias
    ],
)
